import pkg from 'electron';
const { ipcMain, dialog, shell, app } = pkg;
import type { PythonBridge } from './python-bridge.js';
import type { MainWindow } from './main-window.js';
import type { BackendCommand, BackendResponse } from '../src/types/backend';
import { IPC_CHANNELS } from './ipc-channels.js';

export { IPC_CHANNELS };

export function setupIPCHandlers(
  pythonBridge: PythonBridge,
  mainWindow: MainWindow
): void {
  console.log('🔧 Setting up IPC handlers...');

  // Main command handler - bridge to Python backend
  ipcMain.handle(IPC_CHANNELS.SEND_COMMAND, async (_event, command: BackendCommand): Promise<BackendResponse> => {
    try {
      // Validate command
      if (!command.type) {
        throw new Error('Command type is required');
      }

      if (!command.id) {
        command.id = `cmd-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      }

      if (!command.payload) {
        command.payload = {};
      }

      // Send command to Python backend
      const response = await pythonBridge.sendCommand(command);
      return response;

    } catch (error) {
      console.error('❌ Command execution failed:', error);

      return {
        id: command.id || 'unknown',
        type: `${command.type}_RESPONSE`,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
        error_code: 'EXECUTION_ERROR',
        timestamp: Date.now()
      };
    }
  });

  // Window management handlers
  ipcMain.handle(IPC_CHANNELS.WINDOW_MINIMIZE, () => {
    const window = mainWindow.getInstance();
    if (window) {
      window.minimize();
      return { success: true };
    }
    return { success: false, error: 'Window not available' };
  });

  ipcMain.handle(IPC_CHANNELS.WINDOW_MAXIMIZE, () => {
    const window = mainWindow.getInstance();
    if (window) {
      if (window.isMaximized()) {
        window.unmaximize();
      } else {
        window.maximize();
      }
      return { success: true, isMaximized: window.isMaximized() };
    }
    return { success: false, error: 'Window not available' };
  });

  ipcMain.handle(IPC_CHANNELS.WINDOW_CLOSE, () => {
    const window = mainWindow.getInstance();
    if (window) {
      window.close();
      return { success: true };
    }
    return { success: false, error: 'Window not available' };
  });

  // App information handlers
  ipcMain.handle(IPC_CHANNELS.GET_APP_VERSION, () => {
    return app.getVersion();
  });

  ipcMain.handle(IPC_CHANNELS.GET_PLATFORM, () => {
    return process.platform;
  });

  // File operation handlers
  ipcMain.handle(IPC_CHANNELS.SELECT_DIRECTORY, async () => {
    const window = mainWindow.getInstance();
    if (!window) {
      throw new Error('Window not available');
    }

    const result = await dialog.showOpenDialog(window, {
      properties: ['openDirectory'],
      title: 'Select Directory'
    });

    return result.canceled ? null : result.filePaths[0];
  });

  ipcMain.handle(IPC_CHANNELS.SELECT_FILE, async (_event, filters) => {
    const window = mainWindow.getInstance();
    if (!window) {
      throw new Error('Window not available');
    }

    const result = await dialog.showOpenDialog(window, {
      properties: ['openFile'],
      filters: filters || [
        { name: 'All Files', extensions: ['*'] }
      ],
      title: 'Select File'
    });

    return result.canceled ? null : result.filePaths[0];
  });

  ipcMain.handle(IPC_CHANNELS.OPEN_EXTERNAL, async (_, url: string) => {
    try {
      await shell.openExternal(url);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to open external URL'
      };
    }
  });

  // Development tools handlers
  ipcMain.handle(IPC_CHANNELS.OPEN_DEV_TOOLS, () => {
    const window = mainWindow.getInstance();
    if (window) {
      window.webContents.openDevTools();
    }
  });

  ipcMain.handle(IPC_CHANNELS.RELOAD_APP, () => {
    const window = mainWindow.getInstance();
    if (window) {
      window.webContents.reload();
    }
  });

  // Setup Python bridge event forwarding
  setupPythonEventForwarding(pythonBridge, mainWindow);

  console.log('✅ IPC handlers ready');
}

/**
 * Setup event forwarding from Python bridge to renderer process
 */
function setupPythonEventForwarding(pythonBridge: PythonBridge, mainWindow: MainWindow): void {
  // Forward progress events
  pythonBridge.on('QUEUE_PROGRESS', (event) => {
    mainWindow.send(IPC_CHANNELS.PROGRESS_UPDATE, event);
  });

  pythonBridge.on('BATCH_PROGRESS', (event) => {
    mainWindow.send(IPC_CHANNELS.PROGRESS_UPDATE, event);
  });

  pythonBridge.on('SONG_PROGRESS', (event) => {
    mainWindow.send(IPC_CHANNELS.PROGRESS_UPDATE, event);
  });

  pythonBridge.on('DOWNLOAD_PROGRESS', (event) => {
    mainWindow.send(IPC_CHANNELS.PROGRESS_UPDATE, event);
  });

  pythonBridge.on('BATCH_DOWNLOAD_PROGRESS', (event) => {
    mainWindow.send(IPC_CHANNELS.PROGRESS_UPDATE, event);
  });

  pythonBridge.on('SONG_CREATION_PROGRESS', (event) => {
    mainWindow.send(IPC_CHANNELS.PROGRESS_UPDATE, event);
  });

  // Forward error events
  pythonBridge.on('ERROR_UPDATE', (event) => {
    mainWindow.send(IPC_CHANNELS.ERROR_UPDATE, event);
  });

  pythonBridge.on('WARNING_UPDATE', (event) => {
    mainWindow.send(IPC_CHANNELS.WARNING_UPDATE, event);
  });

  // Forward backend responses (for unsolicited responses)
  pythonBridge.on('BACKEND_RESPONSE', (response) => {
    mainWindow.send(IPC_CHANNELS.BACKEND_RESPONSE, response);
  });

  // Forward backend ready signal
  pythonBridge.on('BACKEND_READY', (event) => {
    console.log('🟢 Python backend is ready');
    mainWindow.send('PYTHON_BACKEND_READY', event);
  });
}

/**
 * Cleanup IPC handlers (call during app shutdown)
 */
export function cleanupIPCHandlers(): void {
  console.log('🧹 Cleaning up IPC handlers...');

  // Remove all handlers
  const channels = Object.values(IPC_CHANNELS);
  channels.forEach(channel => {
    ipcMain.removeAllListeners(channel);
  });

  console.log('✅ IPC handlers cleaned up');
}