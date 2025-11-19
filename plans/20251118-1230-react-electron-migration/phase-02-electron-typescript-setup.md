# Phase 2: Electron + TypeScript Setup

## Context
**Parent Plan:** [plan.md](plan.md)
**Dependencies:** [Phase 1](phase-01-python-communication-layer.md) - Python Communication Layer
**Duration:** 1-2 weeks
**Priority:** High

## Overview

Create Electron main process with TypeScript support, secure IPC communication, and Python backend integration while establishing development environment with hot reload capabilities.

## Key Insights

- Electron provides robust security features through context isolation and preload scripts
- TypeScript configuration differs between main and renderer processes
- Python child process management requires careful error handling and lifecycle management
- Development environment setup needs both hot reload for React and restart capability for Python

## Requirements

### Functional Requirements
1. **Electron Main Process:** Manage application lifecycle and Python backend
2. **Secure IPC:** ContextBridge for secure main-renderer communication
3. **Python Integration:** Child process management with stdin/stdout communication
4. **TypeScript Support:** Separate TypeScript configs for main and renderer
5. **Development Environment:** Hot reload for React, restart handling for Python
6. **Window Management:** Application window with proper sizing and theming

### Technical Requirements
1. **Type Safety:** Full TypeScript coverage for main and renderer processes
2. **Security:** Proper context isolation and API exposure
3. **Performance:** Efficient process management and memory usage
4. **Debugging:** Integrated debugging for both Electron and Python
5. **Build System:** Optimized build pipeline for production

## Architecture

### Electron Process Structure

```
┌─────────────────────────────────────────────────────────┐
│                Main Process (TypeScript)                   │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Application Lifecycle                      │  │
│  │  • Window management                                 │  │
│  │  • Menu creation                                      │  │
│  │  • Event handling                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Python Backend Bridge                      │  │
│  │  • Child process management                         │  │
│  │  • Stdin/stdout communication                        │  │
│  │  • Progress event routing                            │  │
│  │  • Error handling                                     │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              IPC Handlers                             │  │
│  │  • Command routing                                   │  │
│  │  • Response handling                                  │  │
│  │  • Event broadcasting                                 │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼ IPC Bridge
┌─────────────────────────────────────────────────────────┐
│            Renderer Process (React + TypeScript)          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │               React Application                        │  │
│  │  • Components                                        │  │
│  │  • State Management                                  │  │
│  │  • Real-time Updates                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Preload Script (Secure Bridge)            │  │
│  │  • API exposure                                      │  │
│  │  • Context isolation                                 │  │
│  │  • Type safety                                        │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### IPC Communication Architecture

```typescript
// Main process IPC handler
ipcMain.handle('SEND_COMMAND', async (event, command: BackendCommand) => {
  try {
    const response = await pythonBridge.sendCommand(command);
    return response;
  } catch (error) {
    return {
      success: false,
      error: error.message,
      timestamp: Date.now()
    };
  }
});

// Renderer process usage
const response = await window.electronAPI.sendCommand({
  type: 'CREATE_ACCOUNT',
  payload: { name: 'test', email: 'test@example.com' }
});
```

## Related Code Files

### Files to Create
- `electron/main.ts` - Main Electron process
- `electron/preload.ts` - Secure preload script
- `electron/python-bridge.ts` - Python backend integration
- `electron/ipc-handlers.ts` - IPC event handlers
- `types/backend.d.ts` - Shared TypeScript types
- `types/electron.d.ts` - Electron API types

### Files to Modify
- `package.json` - Add Electron dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `vite.config.ts` - Vite configuration for Electron

### Configuration Files
- `electron-builder.json` - Build configuration
- `electron/tsconfig.main.json` - Main process TypeScript config
- `electron/tsconfig.preload.json` - Preload script TypeScript config

## Implementation Steps

### Step 1: Project Setup and Dependencies (Day 1-2)
1. **Create Electron directory structure**
   ```bash
   mkdir -p electron
   touch electron/main.ts
   touch electron/preload.ts
   touch electron/python-bridge.ts
   touch electron/ipc-handlers.ts
   ```

2. **Configure package.json for Electron**
   ```json
   {
     "name": "suno-react-app",
     "version": "3.0.0",
     "main": "dist/electron/main.js",
     "scripts": {
       "dev": "concurrently \"npm run dev:renderer\" \"npm run dev:main\"",
       "dev:renderer": "vite",
       "dev:main": "tsc -p electron/tsconfig.main.json && electron dist/electron/main.js",
       "build": "npm run build:renderer && npm run build:main",
       "build:renderer": "vite build",
       "build:main": "tsc -p electron/tsconfig.main.json",
       "pack": "electron-builder",
       "dist": "npm run build && electron-builder"
     },
     "dependencies": {
       "react": "^18.2.0",
       "react-dom": "^18.2.0",
       "zustand": "^4.4.7",
       "@headlessui/react": "^1.7.17",
       "clsx": "^2.0.0"
     },
     "devDependencies": {
       "@types/react": "^18.2.43",
       "@types/react-dom": "^18.2.17",
       "@types/node": "^20.9.0",
       "electron": "^28.1.0",
       "electron-builder": "^24.6.4",
       "typescript": "^5.3.2",
       "vite": "^5.0.0",
       "concurrently": "^8.2.2"
     }
   }
   ```

3. **Create TypeScript configurations**
   ```json
   // tsconfig.json
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
       "noFallthroughCasesInSwitch": true
     },
     "include": ["src", "electron"],
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
       "types": ["node"]
     },
     "include": ["main.ts", "python-bridge.ts", "ipc-handlers.ts"]
   }
   ```

### Step 2: Main Process Implementation (Day 3-4)
1. **Create main Electron process**
   ```typescript
   // electron/main.ts
   import { app, BrowserWindow, ipcMain, Menu } from 'electron';
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
       this.pythonBridge.start();

       // Handle Python events
       this.pythonBridge.on('BACKEND_READY', () => {
         console.log('Python backend ready');
       });

       this.pythonBridge.on('PROGRESS_UPDATE', (progress) => {
         if (this.mainWindow) {
           this.mainWindow.webContents.send('PROGRESS_UPDATE', progress);
         }
       });

       this.pythonBridge.on('ERROR_UPDATE', (error) => {
         if (this.mainWindow) {
           this.mainWindow.webContents.send('ERROR_UPDATE', error);
         }
       });
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

     async shutdown(): Promise<void> {
       await this.pythonBridge.stop();
       await app.quit();
     }
   }

   const electronApp = new ElectronApp();
   electronApp.initialize();

   // Handle process termination
   process.on('SIGTERM', () => electronApp.shutdown());
   process.on('SIGINT', () => electronApp.shutdown());
   ```

2. **Implement Python backend bridge**
   ```typescript
   // electron/python-bridge.ts
   import { spawn, ChildProcess } from 'child_process';
   import { EventEmitter } from 'events';
   import * as path from 'path';

   export interface PythonCommand {
     id: string;
     type: string;
     payload?: any;
   }

   export interface PythonResponse {
     id: string;
     type: string;
     success: boolean;
     data?: any;
     error?: string;
   }

   export class PythonBridge extends EventEmitter {
     private pythonProcess: ChildProcess | null = null;
     private pendingCommands: Map<string, {
       resolve: (value: any) => void;
       reject: (reason: any) => void;
       timeout: NodeJS.Timeout;
     }> = new Map();

     constructor() {
       super();
     }

     start(): void {
       const pythonPath = process.platform === 'win32' ? 'python' : 'python3';
       const scriptPath = path.join(__dirname, '../../backend/main.py');

       this.pythonProcess = spawn(pythonPath, [scriptPath], {
         cwd: process.cwd(),
         stdio: ['pipe', 'pipe', 'inherit'],
         env: { ...process.env, PYTHONPATH: path.join(__dirname, '../../src') }
       });

       if (!this.pythonProcess) {
         throw new Error('Failed to start Python backend');
       }

       this.setupProcessHandlers();
       console.log('Python backend started');
     }

     private setupProcessHandlers(): void {
       if (!this.pythonProcess) return;

       // Handle Python stdout (responses and events)
       this.pythonProcess.stdout.on('data', (data: Buffer) => {
         const messages = data.toString().split('\n').filter(msg => msg.trim());
         messages.forEach(msg => {
           if (msg) {
             try {
               const response = JSON.parse(msg);
               this.handleResponse(response);
             } catch (error) {
               console.error('Invalid JSON from Python:', error, msg);
             }
           }
         });
       });

       // Handle Python errors
       this.pythonProcess.on('error', (error: Error) => {
         console.error('Python backend error:', error);
         this.emit('ERROR_UPDATE', {
           type: 'PYTHON_ERROR',
           message: error.message
         });
       });

       // Handle Python process exit
       this.pythonProcess.on('close', (code: number, signal: string) => {
         console.log(`Python backend exited with code ${code}, signal ${signal}`);
         if (code !== 0) {
           this.emit('ERROR_UPDATE', {
             type: 'PYTHON_EXIT',
             message: `Backend exited with code ${code}`
           });
         }
       });
     }

     private handleResponse(response: any): void {
       // Handle progress events (no ID)
       if (response.id === 'progress-event' || response.type === 'PROGRESS_UPDATE') {
         this.emit('PROGRESS_UPDATE', response);
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
       }
     }

     async sendCommand(command: PythonCommand): Promise<any> {
       if (!this.pythonProcess) {
         throw new Error('Python backend not started');
       }

       return new Promise((resolve, reject) => {
         const timeout = setTimeout(() => {
           this.pendingCommands.delete(command.id);
           reject(new Error('Command timeout'));
         }, 30000); // 30 second timeout

         this.pendingCommands.set(command.id, { resolve, reject, timeout });

         const commandStr = JSON.stringify(command) + '\n';
         this.pythonProcess!.stdin.write(commandStr, (error) => {
           if (error) {
             clearTimeout(timeout);
             this.pendingCommands.delete(command.id);
             reject(error);
           }
         });
       });
     }

     async stop(): Promise<void> {
       if (this.pythonProcess) {
         return new Promise((resolve) => {
           this.pythonProcess!.on('close', resolve);
           this.pythonProcess!.kill('SIGTERM');
         });
       }
     }
   }
   ```

3. **Create secure preload script**
   ```typescript
   // electron/preload.ts
   import { contextBridge, ipcRenderer } from 'electron';
   import { PythonCommand } from './python-bridge';

   export interface ElectronAPI {
     sendCommand: (command: PythonCommand) => Promise<any>;
     onBackendResponse: (callback: (response: any) => void) => void;
     onProgressUpdate: (callback: (progress: any) => void) => void;
     onErrorUpdate: (callback: (error: any) => void) => void;
     removeListener: (channel: string, callback: Function) => void;
   }

   const electronAPI: ElectronAPI = {
     sendCommand: (command: PythonCommand) => ipcRenderer.invoke('SEND_COMMAND', command),

     onBackendResponse: (callback: (response: any) => void) => {
       ipcRenderer.on('BACKEND_RESPONSE', (_event, response) => callback(response));
     },

     onProgressUpdate: (callback: (progress: any) => void) => {
       ipcRenderer.on('PROGRESS_UPDATE', (_event, progress) => callback(progress));
     },

     onErrorUpdate: (callback: (error: any) => void) => {
       ipcRenderer.on('ERROR_UPDATE', (_event, error) => callback(error));
     },

     removeListener: (channel: string, callback: Function) => {
       ipcRenderer.removeListener(channel, callback);
     }
   };

   contextBridge.exposeInMainWorld('electronAPI', electronAPI);

   // Type declarations for renderer process
   declare global {
     interface Window {
       electronAPI: ElectronAPI;
     }
   }
   ```

### Step 3: IPC Handlers and Window Management (Day 5-6)
1. **Create IPC handlers**
   ```typescript
   // electron/ipc-handlers.ts
   import { ipcMain } from 'electron';
   import { PythonBridge } from './python-bridge';

   export function setupIPCHandlers(pythonBridge: PythonBridge): void {
     // Main command handler
     ipcMain.handle('SEND_COMMAND', async (event, command) => {
       try {
         const response = await pythonBridge.sendCommand(command);
         return response;
       } catch (error) {
         return {
           success: false,
           error: error.message,
           timestamp: Date.now()
         };
       }
     });

     // Menu command handlers
     ipcMain.handle('MENU_NEW_ACCOUNT', () => {
       // Handle menu command for new account
       return { success: true };
     });

     // Window management handlers
     ipcMain.handle('WINDOW_MINIMIZE', (event) => {
       const window = event.sender.getOwnerBrowserWindow();
       window.minimize();
       return { success: true };
     });

     ipcMain.handle('WINDOW_MAXIMIZE', (event) => {
       const window = event.sender.getOwnerBrowserWindow();
       if (window.isMaximized()) {
         window.unmaximize();
       } else {
         window.maximize();
       }
       return { success: true, isMaximized: window.isMaximized() };
     });

     ipcMain.handle('WINDOW_CLOSE', (event) => {
       const window = event.sender.getOwnerBrowserWindow();
       window.close();
       return { success: true };
     });
   }
   ```

2. **Create main window class**
   ```typescript
   // electron/main-window.ts
   import { BrowserWindow, screen } from 'electron';
   import * as path from 'path';

   export class MainWindow {
     private window: BrowserWindow | null = null;

     create(): void {
       const { width, height } = screen.getPrimaryDisplay().workAreaSize;

       this.window = new BrowserWindow({
         width: Math.min(1400, width - 100),
         height: Math.min(850, height - 100),
         minWidth: 1200,
         minHeight: 700,
         webPreferences: {
           preload: path.join(__dirname, 'preload.js'),
           contextIsolation: true,
           enableRemoteModule: false,
           nodeIntegration: false,
         },
         icon: path.join(__dirname, '../../assets/icon.png'),
         show: false,
         titleBarStyle: 'default',
       });

       // Handle window state
       this.window.once('ready-to-show', () => {
         this.window!.show();
       });

       this.window.on('closed', () => {
         this.window = null;
       });
     }

     getInstance(): BrowserWindow | null {
       return this.window;
     }
   }
   ```

### Step 4: Development Environment Setup (Day 7-10)
1. **Configure Vite for Electron**
   ```typescript
   // vite.config.ts
   import { defineConfig } from 'vite';
   import react from '@vitejs/plugin-react';

   export default defineConfig({
     plugins: [react()],
     base: './',
     build: {
       outDir: 'dist/renderer',
       emptyOutDir: true,
       rollupOptions: {
         input: {
           main: './index.html'
         }
       }
     },
     server: {
       port: 5173,
       strictPort: true,
       hmr: {
         port: 5173
       }
     },
     optimizeDeps: {
       exclude: ['electron']
     }
   });
   ```

2. **Create development script**
   ```bash
   #!/bin/bash
   # scripts/dev.sh
   echo "Starting Suno React App development..."

   # Start backend in background
   echo "Starting Python backend..."
   cd backend && python main.py &
   BACKEND_PID=$!
   echo "Backend PID: $BACKEND_PID"

   # Start frontend
   echo "Starting React + Electron..."
   npm run dev

   # Cleanup
   kill $BACKEND_PID 2>/dev/null
   ```

3. **Configure Electron Builder**
   ```json
   // electron-builder.json
   {
     "appId": "com.suno.app.manager",
     "productName": "Suno Account Manager",
     "directories": {
       "output": "dist-electron"
     },
     "files": [
       "dist/**/*",
       "backend/**/*",
       "node_modules/**/*",
       "package.json"
     ],
     "mac": {
       "category": "public.app-category.productivity",
       "target": [
         {
           "target": "dmg",
           "arch": ["x64", "arm64"]
         }
       ]
     },
     "win": {
       "target": [
         {
           "target": "nsis",
           "arch": ["x64"]
         }
       ]
     },
     "linux": {
       "target": [
         {
           "target": "AppImage",
           "arch": ["x64"]
         }
       ]
     }
   }
   ```

## Todo List

- [ ] Create Electron directory structure
- [ ] Configure package.json for Electron dependencies
- [ ] Setup TypeScript configurations (main, preload, renderer)
- [ ] Implement main Electron process
- [ ] Create Python backend bridge
- [ ] Implement secure preload script
- [ ] Setup IPC handlers
- [ ] Create main window management
- [ ] Configure Vite for Electron
- [ ] Setup development environment
- [ ] Configure Electron Builder
- [ ] Test Python backend integration
- [ ] Test IPC communication
- [ ] Test development hot reload

## Success Criteria

- ✅ Electron application launches successfully
- ✅ Python backend starts and communicates via stdin/stdout
- ✅ IPC communication works between main and renderer processes
- ✅ React application loads in Electron window
- ✅ Development environment supports hot reload
- ✅ TypeScript compilation works for all processes
- ✅ Security sandboxing prevents direct Node access
- ✅ Error handling and logging works properly

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Python process lifecycle** | Medium | High | Robust process management with proper cleanup |
| **IPC security vulnerabilities** | Low | High | Context isolation and API restrictions |
| **TypeScript compilation issues** | Medium | Medium | Separate configs and thorough testing |
| **Development environment complexity** | Low | Medium | Comprehensive documentation and scripts |
| **Performance overhead** | Low | Low | Efficient communication and lazy loading |

## Security Considerations

1. **Context Isolation:** Use contextBridge for secure API exposure
2. **Node Integration:** Disable in renderer process
3. **Remote Module:** Disable to prevent security risks
4. **API Restrictions:** Only expose necessary APIs through preload
5. **Input Validation:** Validate all IPC communications

## Next Steps

1. **Phase 3 Development:** Begin React frontend component development
2. **TypeScript Integration:** Create shared type definitions
3. **State Management:** Implement Zustand stores
4. **Component Architecture:** Design component hierarchy
5. **Integration Testing:** End-to-end testing with Python backend

---

*This phase establishes the Electron foundation with secure IPC communication and Python backend integration while providing a modern development environment.*