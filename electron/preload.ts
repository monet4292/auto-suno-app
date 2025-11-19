import { contextBridge, ipcRenderer } from 'electron';
import { ElectronAPI } from '../src/types/electron';
import { IPC_CHANNELS } from './ipc-channels';
import { BackendCommand, BackendResponse, ProgressEvent } from '../src/types/backend';

// Define FileFilter interface to match Electron's type
interface FileFilter {
  name: string;
  extensions: string[];
}

/**
 * Create secure ElectronAPI with contextBridge
 */
const electronAPI: ElectronAPI = {
  // Backend communication
  async sendCommand(command: BackendCommand): Promise<BackendResponse> {
    try {
      const response = await ipcRenderer.invoke(IPC_CHANNELS.SEND_COMMAND, command);
      return response;
    } catch (error) {
      console.error('Failed to send command:', error);
      throw error;
    }
  },

  // Event listeners
  onBackendResponse(callback: (response: BackendResponse) => void): void {
    ipcRenderer.on(IPC_CHANNELS.BACKEND_RESPONSE, (_event, response) => {
      callback(response);
    });
  },

  onProgressUpdate(callback: (progress: ProgressEvent) => void): void {
    ipcRenderer.on(IPC_CHANNELS.PROGRESS_UPDATE, (_event, progress) => {
      callback(progress);
    });
  },

  onErrorUpdate(callback: (error: ProgressEvent) => void): void {
    ipcRenderer.on(IPC_CHANNELS.ERROR_UPDATE, (_event, error) => {
      callback(error);
    });
  },

  onWarningUpdate(callback: (warning: ProgressEvent) => void): void {
    ipcRenderer.on(IPC_CHANNELS.WARNING_UPDATE, (_event, warning) => {
      callback(warning);
    });
  },

  // Remove listeners
  removeListener(channel: string, callback: (...args: any[]) => void): void {
    ipcRenderer.removeListener(channel, callback);
  },

  removeAllListeners(channel?: string): void {
    if (channel) {
      ipcRenderer.removeAllListeners(channel);
    } else {
      // Remove all our channels
      const channels = [
        IPC_CHANNELS.BACKEND_RESPONSE,
        IPC_CHANNELS.PROGRESS_UPDATE,
        IPC_CHANNELS.ERROR_UPDATE,
        IPC_CHANNELS.WARNING_UPDATE
      ];
      channels.forEach(ch => ipcRenderer.removeAllListeners(ch));
    }
  },

  // Window management
  async minimizeWindow(): Promise<{ success: boolean }> {
    return await ipcRenderer.invoke(IPC_CHANNELS.WINDOW_MINIMIZE);
  },

  async maximizeWindow(): Promise<{ success: boolean; isMaximized: boolean }> {
    return await ipcRenderer.invoke(IPC_CHANNELS.WINDOW_MAXIMIZE);
  },

  async closeWindow(): Promise<{ success: boolean }> {
    return await ipcRenderer.invoke(IPC_CHANNELS.WINDOW_CLOSE);
  },

  // App information
  async getAppVersion(): Promise<string> {
    return await ipcRenderer.invoke(IPC_CHANNELS.GET_APP_VERSION);
  },

  async platform(): Promise<string> {
    return await ipcRenderer.invoke(IPC_CHANNELS.GET_PLATFORM);
  },

  // File operations
  async selectDirectory(): Promise<string | null> {
    return await ipcRenderer.invoke(IPC_CHANNELS.SELECT_DIRECTORY);
  },

  async selectFile(filters?: FileFilter[]): Promise<string | null> {
    return await ipcRenderer.invoke(IPC_CHANNELS.SELECT_FILE, filters);
  },

  async openExternal(url: string): Promise<{ success: boolean }> {
    return await ipcRenderer.invoke(IPC_CHANNELS.OPEN_EXTERNAL, url);
  },

  // Development tools
  openDevTools(): void {
    ipcRenderer.invoke(IPC_CHANNELS.OPEN_DEV_TOOLS);
  },

  reload(): void {
    ipcRenderer.invoke(IPC_CHANNELS.RELOAD_APP);
  }
};

// Expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Additional utility functions for convenience
contextBridge.exposeInMainWorld('appUtils', {
  // Format bytes to human readable format
  formatBytes: (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  // Format duration to human readable format
  formatDuration: (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else if (minutes > 0) {
      return `${minutes}:${secs.toString().padStart(2, '0')}`;
    } else {
      return `0:${secs.toString().padStart(2, '0')}`;
    }
  },

  // Format date to local string
  formatDate: (date: string | Date): string => {
    const d = new Date(date);
    return d.toLocaleString();
  },

  // Generate unique ID
  generateId: (): string => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  },

  // Validate email format
  isValidEmail: (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Sanitize filename
  sanitizeFilename: (filename: string): string => {
    return filename.replace(/[<>:"/\\|?*]/g, '_').trim();
  },

  // Debounce function
  debounce: <T extends (...args: any[]) => any>(
    func: T,
    wait: number
  ): (...args: Parameters<T>) => void => {
    let timeout: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeout);
      timeout = setTimeout(() => func.apply(null, args), wait);
    };
  },

  // Deep clone object
  deepClone: <T>(obj: T): T => {
    return JSON.parse(JSON.stringify(obj));
  }
});

// Console logging override for development
if (process.env.NODE_ENV === 'development') {
  const originalLog = console.log;
  const originalWarn = console.warn;
  const originalError = console.error;

  console.log = (...args: any[]) => {
    originalLog('[Renderer]', ...args);
  };

  console.warn = (...args: any[]) => {
    originalWarn('[Renderer]', ...args);
  };

  console.error = (...args: any[]) => {
    originalError('[Renderer]', ...args);
  };
}

// Security: Prevent certain APIs
if (process.env.NODE_ENV === 'production') {
  // Remove access to some dangerous APIs in production
  Object.defineProperty(window, 'eval', {
    get: () => {
      throw new Error('eval() is disabled in production');
    }
  });

  // Remove access to Function constructor
  Object.defineProperty(window, 'Function', {
    get: () => {
      throw new Error('Function constructor is disabled in production');
    }
  });
}

// Notify main process that preload script is ready
ipcRenderer.send('PRELOAD_READY');

console.log('🔌 Preload script loaded successfully');