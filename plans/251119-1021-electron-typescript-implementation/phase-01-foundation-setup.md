# Phase 1: Foundation Setup - Electron + TypeScript Infrastructure

**Phase ID:** 251119-1021-P1
**Duration:** 5 days
**Priority:** Critical
**Dependencies:** Phase 1 - Python Communication Layer (Complete)

## Overview

Establish the Electron + TypeScript foundation with secure IPC communication, Python backend integration, and development environment setup. This phase creates the core infrastructure that will support the React frontend in subsequent phases.

## Objectives

1. **Electron Main Process**: Set up TypeScript-enabled Electron main process
2. **Python Backend Bridge**: Create secure stdin/stdout communication with Python backend
3. **IPC Security**: Implement secure preload script with context isolation
4. **Development Environment**: Configure hot reload and debugging capabilities
5. **Build System**: Set up TypeScript compilation and Vite integration

## Daily Breakdown

### Day 1: Project Structure and Dependencies

#### Morning (4 hours)
**Task: Setup Electron project structure**

```bash
# Create directory structure
mkdir -p electron src/types/{shared,api} src/{components,stores,hooks,utils}
mkdir -p tests/{unit,integration,e2e} build/assets

# Initialize package.json modifications
npm install --save-dev electron@latest electron-builder
npm install --save-dev typescript@latest @types/node@latest
npm install --save-dev vite@latest @vitejs/plugin-react
npm install react@latest react-dom@latest @types/react@latest @types/react-dom@latest
npm install zustand@latest
npm install concurrently@latest
```

**Key Deliverables:**
- ✅ Directory structure created
- ✅ Package.json updated with Electron dependencies
- ✅ Basic project files in place

#### Afternoon (4 hours)
**Task: Configure TypeScript for multiple processes**

```json
// tsconfig.json (root)
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/types/*": ["src/types/*"],
      "@/components/*": ["src/components/*"],
      "@/stores/*": ["src/stores/*"]
    }
  },
  "include": ["src"],
  "references": [
    { "path": "./electron/tsconfig.main.json" },
    { "path": "./electron/tsconfig.preload.json" }
  ]
}
```

```json
// electron/tsconfig.main.json
{
  "extends": "../tsconfig.json",
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "outDir": "dist/electron",
    "noEmit": false,
    "moduleResolution": "node",
    "types": ["node"],
    "skipLibCheck": true
  },
  "include": ["*.ts"],
  "exclude": ["node_modules", "dist"]
}
```

**Key Deliverables:**
- ✅ TypeScript configurations for main and preload processes
- ✅ Path mapping configured for clean imports
- ✅ Strict mode enabled for type safety

### Day 2: Main Process Implementation

#### Morning (4 hours)
**Task: Create Electron main process**

```typescript
// electron/main.ts
import { app, BrowserWindow, ipcMain, Menu, dialog } from 'electron';
import { join } from 'path';
import { PythonBridge } from './python-bridge';
import { setupIPCHandlers } from './ipc-handlers';
import { MainWindow } from './main-window';

class ElectronApp {
  private mainWindow: BrowserWindow | null = null;
  private pythonBridge: PythonBridge;

  constructor() {
    this.pythonBridge = new PythonBridge();
  }

  async initialize(): Promise<void> {
    await app.whenReady();
    this.setupPythonBackend();
    this.createMainWindow();
    this.setupMenu();
    this.setupEventHandlers();
  }

  private setupPythonBackend(): void {
    try {
      this.pythonBridge.start();
      console.log('Python backend started successfully');

      // Handle backend events
      this.pythonBridge.on('BACKEND_READY', () => {
        console.log('Python backend is ready');
        this.mainWindow?.webContents.send('BACKEND_READY');
      });

      this.pythonBridge.on('PROGRESS_UPDATE', (progress) => {
        if (this.mainWindow) {
          this.mainWindow.webContents.send('PROGRESS_UPDATE', progress);
        }
      });

      this.pythonBridge.on('ERROR_UPDATE', (error) => {
        console.error('Backend error:', error);
        if (this.mainWindow) {
          this.mainWindow.webContents.send('ERROR_UPDATE', error);
        }
      });

    } catch (error) {
      console.error('Failed to start Python backend:', error);
      this.showStartupError(error);
    }
  }

  private createMainWindow(): void {
    this.mainWindow = new MainWindow();
    this.mainWindow.create();

    // Load React app
    if (process.env.NODE_ENV === 'development') {
      this.mainWindow.loadURL('http://localhost:5173');
    } else {
      this.mainWindow.loadFile(join(__dirname, '../renderer/index.html'));
    }

    // Open DevTools in development
    if (process.env.NODE_ENV === 'development') {
      this.mainWindow.webContents.openDevTools();
    }
  }

  private setupMenu(): void {
    const template: Electron.MenuItemConstructorOptions[] = [
      {
        label: 'File',
        submenu: [
          {
            label: 'New Account',
            accelerator: 'CmdOrCtrl+N',
            click: () => {
              this.mainWindow?.webContents.send('MENU_NEW_ACCOUNT');
            }
          },
          { type: 'separator' },
          {
            label: 'Exit',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => {
              app.quit();
            }
          }
        ]
      },
      {
        label: 'View',
        submenu: [
          { role: 'reload' },
          { role: 'forceReload' },
          { role: 'toggleDevTools' },
          { type: 'separator' },
          { role: 'resetZoom' },
          { role: 'zoomIn' },
          { role: 'zoomOut' }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
  }

  private setupEventHandlers(): void {
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createMainWindow();
      }
    });
  }

  private showStartupError(error: any): void {
    dialog.showErrorBox(
      'Startup Error',
      `Failed to start Python backend: ${error.message}`
    );
  }

  async shutdown(): Promise<void> {
    try {
      await this.pythonBridge.stop();
      await app.quit();
    } catch (error) {
      console.error('Error during shutdown:', error);
      app.quit();
    }
  }
}

// Initialize application
const electronApp = new ElectronApp();

// Handle startup
electronApp.initialize().catch((error) => {
  console.error('Failed to initialize application:', error);
  app.quit();
});

// Handle process termination
process.on('SIGTERM', () => electronApp.shutdown());
process.on('SIGINT', () => electronApp.shutdown());
```

#### Afternoon (4 hours)
**Task: Implement Python backend bridge**

```typescript
// electron/python-bridge.ts
import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';
import * as path from 'path';

export interface PythonCommand {
  id: string;
  type: string;
  payload?: any;
  timestamp: number;
}

export interface PythonResponse {
  id: string;
  type: string;
  success: boolean;
  data?: any;
  error?: string;
  timestamp: number;
}

export class PythonBridge extends EventEmitter {
  private pythonProcess: ChildProcess | null = null;
  private pendingCommands: Map<string, {
    resolve: (value: any) => void;
    reject: (reason: any) => void;
    timeout: NodeJS.Timeout;
  }> = new Map();
  private commandTimeout = 30000; // 30 seconds
  private isShuttingDown = false;

  constructor() {
    super();
  }

  start(): void {
    if (this.pythonProcess) {
      throw new Error('Python backend is already running');
    }

    const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(__dirname, '../../backend/main.py');

    console.log(`Starting Python backend: ${pythonPath} ${scriptPath}`);

    this.pythonProcess = spawn(pythonPath, [scriptPath], {
      cwd: process.cwd(),
      stdio: ['pipe', 'pipe', 'inherit'], // stderr inherits for debugging
      env: {
        ...process.env,
        PYTHONPATH: path.join(__dirname, '../../src'),
        PYTHONUNBUFFERED: '1' // Ensure unbuffered output
      }
    });

    if (!this.pythonProcess) {
      throw new Error('Failed to start Python backend process');
    }

    this.setupProcessHandlers();
    console.log('Python backend process started');
  }

  private setupProcessHandlers(): void {
    if (!this.pythonProcess) return;

    // Handle Python stdout (responses and events)
    this.pythonProcess.stdout?.on('data', (data: Buffer) => {
      const messages = data.toString()
        .split('\n')
        .filter(msg => msg.trim())
        .map(msg => msg.trim());

      messages.forEach(msg => {
        if (msg && !this.isShuttingDown) {
          try {
            const response = JSON.parse(msg);
            this.handleResponse(response);
          } catch (error) {
            console.error('Invalid JSON from Python:', error, 'Message:', msg);
            this.emit('ERROR_UPDATE', {
              type: 'PARSE_ERROR',
              message: `Invalid JSON from backend: ${msg.substring(0, 100)}`
            });
          }
        }
      });
    });

    // Handle Python errors
    this.pythonProcess.on('error', (error: Error) => {
      console.error('Python backend process error:', error);
      this.emit('ERROR_UPDATE', {
        type: 'PYTHON_PROCESS_ERROR',
        message: error.message
      });
    });

    // Handle Python process exit
    this.pythonProcess.on('close', (code: number, signal: string) => {
      console.log(`Python backend exited with code ${code}, signal ${signal}`);

      if (!this.isShuttingDown && code !== 0) {
        this.emit('ERROR_UPDATE', {
          type: 'PYTHON_EXIT_UNEXPECTED',
          message: `Backend exited unexpectedly with code ${code}`
        });
      }

      // Clean up pending commands
      this.pendingCommands.forEach(({ reject, timeout }) => {
        clearTimeout(timeout);
        reject(new Error('Python backend exited'));
      });
      this.pendingCommands.clear();
    });

    // Handle stdin errors
    this.pythonProcess.stdin?.on('error', (error: Error) => {
      console.error('Python stdin error:', error);
      this.emit('ERROR_UPDATE', {
        type: 'STDIN_ERROR',
        message: error.message
      });
    });
  }

  private handleResponse(response: any): void {
    // Handle progress events (no ID)
    if (response.type === 'PROGRESS_UPDATE' || response.type === 'progress') {
      this.emit('PROGRESS_UPDATE', response);
      return;
    }

    // Handle backend ready event
    if (response.type === 'BACKEND_READY') {
      this.emit('BACKEND_READY', response);
      return;
    }

    // Handle error events
    if (response.type === 'ERROR_UPDATE') {
      this.emit('ERROR_UPDATE', response);
      return;
    }

    // Handle command responses
    const pendingCommand = this.pendingCommands.get(response.id);
    if (pendingCommand) {
      clearTimeout(pendingCommand.timeout);
      this.pendingCommands.delete(response.id);

      if (response.success) {
        pendingCommand.resolve(response);
      } else {
        pendingCommand.reject(new Error(response.error || 'Unknown error'));
      }
    } else {
      console.warn('Received response for unknown command:', response.id);
    }
  }

  async sendCommand(command: PythonCommand): Promise<any> {
    if (!this.pythonProcess) {
      throw new Error('Python backend not started');
    }

    if (this.isShuttingDown) {
      throw new Error('Python backend is shutting down');
    }

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        this.pendingCommands.delete(command.id);
        reject(new Error(`Command timeout after ${this.commandTimeout}ms`));
      }, this.commandTimeout);

      this.pendingCommands.set(command.id, { resolve, reject, timeout });

      const commandStr = JSON.stringify(command) + '\n';

      this.pythonProcess?.stdin.write(commandStr, (error) => {
        if (error) {
          clearTimeout(timeout);
          this.pendingCommands.delete(command.id);
          reject(error);
        }
      });
    });
  }

  async stop(): Promise<void> {
    this.isShuttingDown = true;

    if (this.pythonProcess) {
      return new Promise((resolve) => {
        const process = this.pythonProcess!;

        // Send shutdown command
        try {
          const shutdownCommand: PythonCommand = {
            id: 'shutdown-' + Date.now(),
            type: 'SHUTDOWN',
            timestamp: Date.now()
          };

          process.stdin.write(JSON.stringify(shutdownCommand) + '\n');
        } catch (error) {
          console.error('Failed to send shutdown command:', error);
        }

        // Force kill after 5 seconds
        const killTimeout = setTimeout(() => {
          if (process && !process.killed) {
            process.kill('SIGTERM');
          }
        }, 5000);

        process.on('close', () => {
          clearTimeout(killTimeout);
          resolve();
        });

        // Immediate kill for development
        if (process.env.NODE_ENV === 'development') {
          process.kill('SIGTERM');
        }
      });
    }
  }

  isRunning(): boolean {
    return this.pythonProcess !== null && !this.pythonProcess.killed;
  }

  getPendingCommandsCount(): number {
    return this.pendingCommands.size;
  }
}
```

### Day 3: IPC Security and Preload Script

#### Morning (4 hours)
**Task: Create secure preload script**

```typescript
// electron/preload.ts
import { contextBridge, ipcRenderer } from 'electron';
import { PythonCommand } from './python-bridge';

// Define API interface for type safety
export interface ElectronAPI {
  // Command operations
  sendCommand: (command: PythonCommand) => Promise<any>;

  // Event listeners
  onBackendReady: (callback: () => void) => void;
  onProgressUpdate: (callback: (progress: any) => void) => void;
  onErrorUpdate: (callback: (error: any) => void) => void;
  onMenuAction: (callback: (action: string, data?: any) => void) => void;

  // Event cleanup
  removeListener: (channel: string, callback: Function) => void;
  removeAllListeners: (channel: string) => void;

  // Window operations
  minimizeWindow: () => Promise<void>;
  maximizeWindow: () => Promise<{ isMaximized: boolean }>;
  closeWindow: () => Promise<void>;

  // File operations
  selectDirectory: () => Promise<string | null>;
  selectFile: (filters?: Electron.FileFilter[]) => Promise<string | null>;
  showSaveDialog: (options: Electron.SaveDialogOptions) => Promise<string | null>;

  // Application info
  getAppVersion: () => Promise<string>;
  getPlatform: () => Promise<string>;
}

// Create secure API object
const electronAPI: ElectronAPI = {
  // Command operations
  sendCommand: (command: PythonCommand) => {
    // Validate command structure
    if (!command.id || !command.type) {
      return Promise.reject(new Error('Invalid command structure'));
    }

    return ipcRenderer.invoke('SEND_COMMAND', command);
  },

  // Event listeners
  onBackendReady: (callback: () => void) => {
    ipcRenderer.on('BACKEND_READY', callback);
  },

  onProgressUpdate: (callback: (progress: any) => void) => {
    ipcRenderer.on('PROGRESS_UPDATE', (_event, progress) => callback(progress));
  },

  onErrorUpdate: (callback: (error: any) => void) => {
    ipcRenderer.on('ERROR_UPDATE', (_event, error) => callback(error));
  },

  onMenuAction: (callback: (action: string, data?: any) => void) => {
    ipcRenderer.on('MENU_NEW_ACCOUNT', () => callback('NEW_ACCOUNT'));
  },

  // Event cleanup
  removeListener: (channel: string, callback: Function) => {
    ipcRenderer.removeListener(channel, callback);
  },

  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  },

  // Window operations
  minimizeWindow: () => ipcRenderer.invoke('WINDOW_MINIMIZE'),

  maximizeWindow: () => ipcRenderer.invoke('WINDOW_MAXIMIZE'),

  closeWindow: () => ipcRenderer.invoke('WINDOW_CLOSE'),

  // File operations
  selectDirectory: () => ipcRenderer.invoke('DIALOG_SELECT_DIRECTORY'),

  selectFile: (filters?: Electron.FileFilter[]) =>
    ipcRenderer.invoke('DIALOG_SELECT_FILE', filters),

  showSaveDialog: (options: Electron.SaveDialogOptions) =>
    ipcRenderer.invoke('DIALOG_SHOW_SAVE', options),

  // Application info
  getAppVersion: () => ipcRenderer.invoke('APP_GET_VERSION'),

  getPlatform: () => Promise.resolve(process.platform)
};

// Expose API to renderer process
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Type declarations for renderer process
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

// Development debugging
if (process.env.NODE_ENV === 'development') {
  console.log('Preload script loaded successfully');

  // Expose debugging functions in development
  contextBridge.exposeInMainWorld('debugAPI', {
    log: (...args: any[]) => console.log('[Renderer]', ...args),
    error: (...args: any[]) => console.error('[Renderer]', ...args),
    warn: (...args: any[]) => console.warn('[Renderer]', ...args)
  });
}
```

#### Afternoon (4 hours)
**Task: Implement IPC handlers**

```typescript
// electron/ipc-handlers.ts
import { ipcMain, dialog, app } from 'electron';
import { PythonBridge } from './python-bridge';
import { PythonCommand } from './python-bridge';

export function setupIPCHandlers(pythonBridge: PythonBridge): void {

  // Main command handler
  ipcMain.handle('SEND_COMMAND', async (event, command: PythonCommand) => {
    try {
      // Validate command structure
      if (!command.id || !command.type) {
        throw new Error('Invalid command structure: missing id or type');
      }

      // Add timestamp if not present
      if (!command.timestamp) {
        command.timestamp = Date.now();
      }

      // Forward to Python backend
      const response = await pythonBridge.sendCommand(command);
      return response;

    } catch (error) {
      console.error('IPC command error:', error);
      return {
        id: command.id,
        type: command.type,
        success: false,
        error: error.message || 'Unknown error occurred',
        timestamp: Date.now()
      };
    }
  });

  // Window management handlers
  ipcMain.handle('WINDOW_MINIMIZE', (event) => {
    const window = event.sender.getOwnerBrowserWindow();
    if (window) {
      window.minimize();
      return { success: true };
    }
    return { success: false, error: 'Window not found' };
  });

  ipcMain.handle('WINDOW_MAXIMIZE', (event) => {
    const window = event.sender.getOwnerBrowserWindow();
    if (window) {
      if (window.isMaximized()) {
        window.unmaximize();
        return { success: true, isMaximized: false };
      } else {
        window.maximize();
        return { success: true, isMaximized: true };
      }
    }
    return { success: false, error: 'Window not found' };
  });

  ipcMain.handle('WINDOW_CLOSE', (event) => {
    const window = event.sender.getOwnerBrowserWindow();
    if (window) {
      window.close();
      return { success: true };
    }
    return { success: false, error: 'Window not found' };
  });

  // File dialog handlers
  ipcMain.handle('DIALOG_SELECT_DIRECTORY', async () => {
    try {
      const result = await dialog.showOpenDialog({
        properties: ['openDirectory'],
        title: 'Select Directory'
      });

      return result.canceled ? null : result.filePaths[0];
    } catch (error) {
      console.error('Directory selection error:', error);
      return null;
    }
  });

  ipcMain.handle('DIALOG_SELECT_FILE', async (event, filters?: Electron.FileFilter[]) => {
    try {
      const result = await dialog.showOpenDialog({
        properties: ['openFile'],
        filters: filters || [
          { name: 'All Files', extensions: ['*'] }
        ],
        title: 'Select File'
      });

      return result.canceled ? null : result.filePaths[0];
    } catch (error) {
      console.error('File selection error:', error);
      return null;
    }
  });

  ipcMain.handle('DIALOG_SHOW_SAVE', async (event, options: Electron.SaveDialogOptions) => {
    try {
      const result = await dialog.showSaveDialog(options);
      return result.canceled ? null : result.filePath;
    } catch (error) {
      console.error('Save dialog error:', error);
      return null;
    }
  });

  // Application info handlers
  ipcMain.handle('APP_GET_VERSION', () => {
    return app.getVersion();
  });

  // Menu action handlers
  ipcMain.handle('MENU_NEW_ACCOUNT', () => {
    return { success: true, action: 'NEW_ACCOUNT' };
  });

  // Development-only handlers
  if (process.env.NODE_ENV === 'development') {
    ipcMain.handle('DEV_RELOAD_PYTHON', async () => {
      try {
        await pythonBridge.stop();
        pythonBridge.start();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    });

    ipcMain.handle('DEV_GET_PYTHON_STATUS', () => {
      return {
        isRunning: pythonBridge.isRunning(),
        pendingCommands: pythonBridge.getPendingCommandsCount()
      };
    });
  }

  console.log('IPC handlers setup complete');
}
```

### Day 4: Window Management and Build System

#### Morning (4 hours)
**Task: Create main window class and Vite configuration**

```typescript
// electron/main-window.ts
import { BrowserWindow, screen } from 'electron';
import * as path from 'path';

export class MainWindow {
  private window: BrowserWindow | null = null;

  create(): void {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize;

    // Calculate window size (80% of screen, max 1400x850)
    const windowWidth = Math.min(1400, Math.floor(width * 0.8));
    const windowHeight = Math.min(850, Math.floor(height * 0.8));

    this.window = new BrowserWindow({
      width: windowWidth,
      height: windowHeight,
      minWidth: 1200,
      minHeight: 700,
      show: false, // Don't show until ready-to-show
      autoHideMenuBar: false,
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'),
        contextIsolation: true,
        enableRemoteModule: false,
        nodeIntegration: false,
        nodeIntegrationInWorker: false,
        nodeIntegrationInSubFrames: false,
        sandbox: false, // Required for preload scripts
        webSecurity: true,
        allowRunningInsecureContent: false,
        experimentalFeatures: false
      },
      icon: this.getIconPath(),
      title: 'Suno Account Manager',
      backgroundColor: '#1a1a1a'
    });

    this.setupEventHandlers();
  }

  private getIconPath(): string {
    // Icon paths for different platforms
    const iconExtensions = {
      win32: '.ico',
      darwin: '.icns',
      linux: '.png'
    };

    const ext = iconExtensions[process.platform as keyof typeof iconExtensions] || '.png';
    return path.join(__dirname, '../../assets/icon' + ext);
  }

  private setupEventHandlers(): void {
    if (!this.window) return;

    // Handle window state
    this.window.once('ready-to-show', () => {
      if (this.window) {
        this.window.show();
        this.window.focus();

        if (process.env.NODE_ENV === 'development') {
          // Center window in development
          this.window.center();
        }
      }
    });

    this.window.on('closed', () => {
      this.window = null;
    });

    // Handle focus/blur events
    this.window.on('focus', () => {
      // Window focused
    });

    this.window.on('blur', () => {
      // Window lost focus
    });

    // Handle unresponsive
    this.window.on('unresponsive', () => {
      console.log('Window became unresponsive');
    });

    this.window.on('responsive', () => {
      console.log('Window became responsive again');
    });
  }

  loadURL(url: string): void {
    if (this.window) {
      this.window.loadURL(url);
    }
  }

  loadFile(filePath: string): void {
    if (this.window) {
      this.window.loadFile(filePath);
    }
  }

  getInstance(): BrowserWindow | null {
    return this.window;
  }

  isDestroyed(): boolean {
    return this.window ? this.window.isDestroyed() : true;
  }

  focus(): void {
    if (this.window && !this.window.isDestroyed()) {
      this.window.focus();
    }
  }

  show(): void {
    if (this.window && !this.window.isDestroyed()) {
      this.window.show();
    }
  }

  hide(): void {
    if (this.window && !this.window.isDestroyed()) {
      this.window.hide();
    }
  }
}
```

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],

  // Build configuration
  base: './',
  build: {
    outDir: 'dist/renderer',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html')
      }
    }
  },

  // Development server
  server: {
    port: 5173,
    strictPort: true,
    host: 'localhost',
    hmr: {
      port: 5173
    }
  },

  // Dependencies optimization
  optimizeDeps: {
    exclude: ['electron']
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/types': resolve(__dirname, 'src/types'),
      '@/components': resolve(__dirname, 'src/components'),
      '@/stores': resolve(__dirname, 'src/stores'),
      '@/hooks': resolve(__dirname, 'src/hooks'),
      '@/utils': resolve(__dirname, 'src/utils')
    }
  },

  // Define global constants
  define: {
    __IS_ELECTRON__: 'true',
    __DEV__: JSON.stringify(process.env.NODE_ENV === 'development')
  }
});
```

#### Afternoon (4 hours)
**Task: Update package.json with scripts and build configuration**

```json
{
  "name": "suno-account-manager",
  "version": "3.0.0",
  "description": "Suno Account Manager with React + Electron",
  "main": "dist/electron/main.js",
  "homepage": "./",
  "scripts": {
    "dev": "concurrently \"npm run dev:renderer\" \"npm run dev:main\"",
    "dev:renderer": "vite",
    "dev:main": "tsc -p electron/tsconfig.main.json && electron dist/electron/main.js",
    "build": "npm run build:renderer && npm run build:main",
    "build:renderer": "vite build",
    "build:main": "tsc -p electron/tsconfig.main.json",
    "pack": "npm run build && electron-builder --dir",
    "dist": "npm run build && electron-builder",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint src --ext ts,tsx --fix",
    "type-check": "tsc --noEmit",
    "type-check:main": "tsc -p electron/tsconfig.main.json --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "zustand": "^4.4.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/react-dom": "^18.2.17",
    "@types/node": "^20.9.0",
    "@typescript-eslint/eslint-plugin": "^6.13.2",
    "@typescript-eslint/parser": "^6.13.2",
    "@vitejs/plugin-react": "^4.2.1",
    "concurrently": "^8.2.2",
    "electron": "^28.1.0",
    "electron-builder": "^24.8.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react": "^7.33.2",
    "eslint-plugin-react-hooks": "^4.6.0",
    "typescript": "^5.3.2",
    "vite": "^5.0.8",
    "vitest": "^1.0.4"
  },
  "build": {
    "appId": "com.suno.accountmanager",
    "productName": "Suno Account Manager",
    "directories": {
      "output": "dist-electron"
    },
    "files": [
      "dist/**/*",
      "electron/**/*",
      "backend/**/*",
      "package.json"
    ],
    "win": {
      "target": [
        {
          "target": "nsis",
          "arch": ["x64"]
        }
      ],
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": [
        {
          "target": "dmg",
          "arch": ["x64", "arm64"]
        }
      ],
      "icon": "assets/icon.icns",
      "category": "public.app-category.productivity"
    },
    "linux": {
      "target": [
        {
          "target": "AppImage",
          "arch": ["x64"]
        }
      ],
      "icon": "assets/icon.png",
      "category": "Office"
    }
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### Day 5: Development Environment and Testing

#### Morning (4 hours)
**Task: Create basic React application and development setup**

```typescript
// src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/main.css';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

```typescript
// src/App.tsx
import { useEffect, useState } from 'react';
import { electronAPI } from './types/electron';

function App() {
  const [backendStatus, setBackendStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [progress, setProgress] = useState<any>(null);

  useEffect(() => {
    // Listen for backend events
    electronAPI.onBackendReady(() => {
      setBackendStatus('ready');
    });

    electronAPI.onProgressUpdate((progressData) => {
      setProgress(progressData);
    });

    electronAPI.onErrorUpdate((error) => {
      console.error('Backend error:', error);
      setBackendStatus('error');
    });

    // Cleanup listeners
    return () => {
      electronAPI.removeAllListeners('BACKEND_READY');
      electronAPI.removeAllListeners('PROGRESS_UPDATE');
      electronAPI.removeAllListeners('ERROR_UPDATE');
    };
  }, []);

  const testConnection = async () => {
    try {
      const response = await electronAPI.sendCommand({
        id: 'test-' + Date.now(),
        type: 'PING',
        timestamp: Date.now()
      });

      console.log('Test response:', response);
    } catch (error) {
      console.error('Test failed:', error);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Suno Account Manager v3.0</h1>
        <div className="status-indicator">
          Status: {backendStatus}
        </div>
      </header>

      <main className="app-main">
        <div className="test-section">
          <h2>Development Testing</h2>
          <button onClick={testConnection}>Test Backend Connection</button>

          {progress && (
            <div className="progress-display">
              <h3>Progress Update:</h3>
              <pre>{JSON.stringify(progress, null, 2)}</pre>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
```

#### Afternoon (4 hours)
**Task: Create development scripts and basic testing**

```bash
#!/bin/bash
# scripts/dev.sh
echo "Starting Suno Account Manager development environment..."

# Check if Python backend exists
if [ ! -f "backend/main.py" ]; then
    echo "Error: Python backend not found at backend/main.py"
    exit 1
fi

# Check dependencies
echo "Checking dependencies..."
npm list electron > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start development
echo "Starting development servers..."
npm run dev
```

```typescript
// tests/setup.ts
import { vi } from 'vitest';

// Mock electronAPI for testing
const mockElectronAPI = {
  sendCommand: vi.fn(),
  onBackendReady: vi.fn(),
  onProgressUpdate: vi.fn(),
  onErrorUpdate: vi.fn(),
  removeListener: vi.fn(),
  removeAllListeners: vi.fn(),
  minimizeWindow: vi.fn(),
  maximizeWindow: vi.fn(),
  closeWindow: vi.fn(),
  selectDirectory: vi.fn(),
  selectFile: vi.fn(),
  showSaveDialog: vi.fn(),
  getAppVersion: vi.fn(),
  getPlatform: vi.fn()
};

// Setup global mocks
Object.defineProperty(window, 'electronAPI', {
  value: mockElectronAPI,
  writable: true
});
```

## Success Criteria

### Technical Requirements
- ✅ Electron application launches and shows React interface
- ✅ Python backend starts and communicates via JSON protocol
- ✅ IPC communication works between main and renderer processes
- ✅ TypeScript compilation successful for all processes
- ✅ Development environment supports hot reload
- ✅ Security sandboxing prevents direct Node access

### Performance Requirements
- ✅ Application startup time: <3 seconds
- ✅ Memory usage: <100MB idle
- ✅ IPC response time: <100ms
- ✅ Python process starts within 2 seconds

### Security Requirements
- ✅ Context isolation enabled
- ✅ Node integration disabled in renderer
- ✅ Preload script only exposes necessary APIs
- ✅ All IPC communications validated

## Testing Plan

### Unit Tests
```typescript
// tests/unit/python-bridge.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { PythonBridge } from '../../electron/python-bridge';

describe('PythonBridge', () => {
  let pythonBridge: PythonBridge;

  beforeEach(() => {
    pythonBridge = new PythonBridge();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should create bridge instance', () => {
    expect(pythonBridge).toBeDefined();
  });

  it('should handle command sending', async () => {
    const command = {
      id: 'test-1',
      type: 'TEST_COMMAND',
      timestamp: Date.now()
    };

    // Mock implementation
    vi.spyOn(pythonBridge, 'sendCommand').mockResolvedValue({
      id: 'test-1',
      type: 'TEST_COMMAND',
      success: true
    });

    const result = await pythonBridge.sendCommand(command);
    expect(result.success).toBe(true);
  });
});
```

### Integration Tests
```typescript
// tests/integration/ipc-communication.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { PythonBridge } from '../../electron/python-bridge';

describe('IPC Communication', () => {
  let pythonBridge: PythonBridge;

  beforeAll(() => {
    pythonBridge = new PythonBridge();
  });

  afterAll(async () => {
    if (pythonBridge.isRunning()) {
      await pythonBridge.stop();
    }
  });

  it('should establish communication with Python backend', async () => {
    pythonBridge.start();

    // Wait for backend to be ready
    await new Promise(resolve => {
      pythonBridge.once('BACKEND_READY', resolve);
      setTimeout(resolve, 5000); // Timeout after 5 seconds
    });

    expect(pythonBridge.isRunning()).toBe(true);
  });
});
```

## Risk Mitigation

### High-Risk Areas
1. **Python Process Management**
   - Risk: Process hanging or crashes
   - Mitigation: Proper cleanup, timeout handling, error recovery

2. **IPC Communication**
   - Risk: Message loss or corruption
   - Mitigation: Message validation, error handling, retry logic

3. **Security Vulnerabilities**
   - Risk: Exposed Node APIs
   - Mitigation: Context isolation, minimal API exposure

### Contingency Plans
- **Python backend fails**: Graceful fallback with error UI
- **TypeScript compilation fails**: Clear error messages and build diagnostics
- **Development environment issues**: Dockerized development environment

## Deliverables Checklist

### Code Files
- [ ] `electron/main.ts` - Main Electron process
- [ ] `electron/preload.ts` - Secure preload script
- [ ] `electron/python-bridge.ts` - Python backend integration
- [ ] `electron/ipc-handlers.ts` - IPC event handlers
- [ ] `electron/main-window.ts` - Window management
- [ ] `src/App.tsx` - Basic React application
- [ ] `src/main.tsx` - React entry point
- [ ] `vite.config.ts` - Vite configuration

### Configuration Files
- [ ] `package.json` - Updated dependencies and scripts
- [ ] `tsconfig.json` - Root TypeScript configuration
- [ ] `electron/tsconfig.main.json` - Main process TypeScript config
- [ ] `electron/tsconfig.preload.json` - Preload TypeScript config
- [ ] `electron-builder.json` - Build configuration

### Development Tools
- [ ] `scripts/dev.sh` - Development startup script
- [ ] `tests/setup.ts` - Test setup and mocks
- [ ] Basic unit and integration tests

### Documentation
- [ ] Development setup instructions
- [ ] Architecture documentation
- [ ] Security guidelines

---

*This phase establishes the foundation for the Electron + TypeScript architecture with secure IPC communication and Python backend integration.*