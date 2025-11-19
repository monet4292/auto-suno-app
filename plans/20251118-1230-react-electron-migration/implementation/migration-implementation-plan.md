# Suno Account Manager - React + Electron Migration Implementation Plan

**Version:** 1.0
**Date:** 2025-11-18
**Status:** Ready for Implementation
**Estimated Timeline:** 6-8 weeks

## Executive Summary

This comprehensive plan details the migration of Suno Account Manager from CustomTkinter to a modern React + TypeScript + Electron architecture while maintaining full feature parity and improving developer experience. The migration will preserve all existing Python backend functionality with minimal changes, replacing only the GUI layer with a modern web-based frontend.

## Migration Overview

### Current Architecture
- **Frontend:** CustomTkinter (Python) with 6 tabs
- **Backend:** Python with Clean Architecture
- **Communication:** Direct Python method calls
- **Features:** Account management, queue system, batch creation, downloads, history

### Target Architecture
- **Frontend:** React 18 + TypeScript + Tailwind CSS + Headless UI
- **Desktop Runtime:** Electron with Node.js backend bridge
- **Communication:** Stdin/stdout pipes between Electron and Python
- **State Management:** Zustand for UI state, React Query for server state
- **Python Backend:** Unchanged (just add stdin/stdout layer)

### Success Criteria
1. **100% Feature Parity** - All CustomTkinter functionality preserved
2. **Type Safety** - Full TypeScript coverage for all interfaces
3. **Performance** - Better UI responsiveness than CustomTkinter
4. **Developer Experience** - Hot reload, debugging tools, type checking
5. **Migration Path** - Seamless data migration from current JSON files

---

## Phase 1: Python Backend Communication Layer

### Duration: 1-2 weeks

### Objectives
- Add stdin/stdout JSON command/response protocol
- Define type-safe interfaces for all operations
- Implement real-time progress callbacks via Electron IPC
- Maintain all existing functionality unchanged

### 1.1 Communication Protocol Design

#### Command/Response Protocol
```python
# Communication Protocol Specification
@dataclass
class Command:
    id: str
    type: str
    payload: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class Response:
    id: str
    type: str
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class ProgressEvent:
    operation_id: str
    type: str
    progress: int
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)
```

#### Command Types
```python
# Account Management Commands
ACCOUNT_CREATE = "account:create"
ACCOUNT_GET_ALL = "account:get_all"
ACCOUNT_RENAME = "account:rename"
ACCOUNT_DELETE = "account:delete"
ACCOUNT_GET_SESSION = "account:get_session"

# Queue Management Commands
QUEUE_LOAD_PROMPTS = "queue:load_prompts"
QUEUE_ADD_ENTRY = "queue:add_entry"
QUEUE_GET_ALL = "queue:get_all"
QUEUE_UPDATE_PROGRESS = "queue:update_progress"
QUEUE_DELETE_ENTRY = "queue:delete_entry"

# Song Creation Commands
SONG_CREATE_BATCH = "song:create_batch"
SONG_CREATE_SINGLE = "song:create_single"
SONG_GET_HISTORY = "song:get_history"
SONG_STOP_CREATION = "song:stop_creation"

# Download Commands
DOWNLOAD_START = "download:start"
DOWNLOAD_GET_HISTORY = "download:get_history"
DOWNLOAD_GET_CLIPS = "download:get_clips"
```

### 1.2 Backend Communication Server

#### New File: `src/backend/communication_server.py`
```python
import json
import sys
import uuid
from typing import Dict, Any, Optional
from dataclasses import asdict
from ..core.account_manager import AccountManager
from ..core.queue_manager import QueueManager
from ..core.session_manager import SessionManager
from ..core.download_manager import DownloadManager
from ..core.batch_song_creator import BatchSongCreator

class CommunicationServer:
    """JSON stdin/stdout communication server for Electron integration."""

    def __init__(self):
        self.managers = self._initialize_managers()
        self.pending_operations: Dict[str, Dict] = {}

    def _initialize_managers(self):
        """Initialize all core managers."""
        return {
            'account': AccountManager(),
            'queue': QueueManager(),
            'session': SessionManager(),
            'download': DownloadManager(),
            'batch_creator': BatchSongCreator(progress_callback=self._on_progress)
        }

    def start(self):
        """Start the communication server."""
        for line in sys.stdin:
            try:
                command = json.loads(line.strip())
                response = self._handle_command(command)
                print(json.dumps(asdict(response)), flush=True)
            except Exception as e:
                error_response = Response(
                    id=command.get('id', 'unknown'),
                    type='error',
                    success=False,
                    error=str(e)
                )
                print(json.dumps(asdict(error_response)), flush=True)

    def _handle_command(self, command: Dict) -> Response:
        """Route command to appropriate handler."""
        command_type = command.get('type')
        command_id = command.get('id')
        payload = command.get('payload', {})

        handlers = {
            # Account commands
            'account:create': self._handle_account_create,
            'account:get_all': self._handle_account_get_all,
            'account:rename': self._handle_account_rename,
            'account:delete': self._handle_account_delete,
            'account:get_session': self._handle_account_get_session,

            # Queue commands
            'queue:load_prompts': self._handle_queue_load_prompts,
            'queue:add_entry': self._handle_queue_add_entry,
            'queue:get_all': self._handle_queue_get_all,
            'queue:update_progress': self._handle_queue_update_progress,
            'queue:delete_entry': self._handle_queue_delete_entry,

            # Song creation commands
            'song:create_batch': self._handle_song_create_batch,
            'song:create_single': self._handle_song_create_single,
            'song:get_history': self._handle_song_get_history,
            'song:stop_creation': self._handle_song_stop_creation,

            # Download commands
            'download:start': self._handle_download_start,
            'download:get_history': self._handle_download_get_history,
            'download:get_clips': self._handle_download_get_clips,
        }

        handler = handlers.get(command_type)
        if handler:
            return handler(command_id, payload)
        else:
            return Response(
                id=command_id,
                type='error',
                success=False,
                error=f'Unknown command type: {command_type}'
            )

    def _handle_account_create(self, command_id: str, payload: Dict) -> Response:
        """Handle account creation."""
        try:
            name = payload['name']
            email = payload.get('email', '')
            success = self.managers['account'].add_account(name, email)

            return Response(
                id=command_id,
                type='account:create',
                success=success,
                data={'account_created': success}
            )
        except Exception as e:
            return Response(
                id=command_id,
                type='account:create',
                success=False,
                error=str(e)
            )

    # Implement other handlers...

    def _on_progress(self, operation_id: str, progress: int, message: str, data: Dict = None):
        """Handle progress updates from operations."""
        progress_event = ProgressEvent(
            operation_id=operation_id,
            type='progress',
            progress=progress,
            message=message,
            data=data
        )

        # Send progress event to stderr to avoid mixing with responses
        print(json.dumps(asdict(progress_event)), file=sys.stderr, flush=True)

if __name__ == "__main__":
    server = CommunicationServer()
    server.start()
```

### 1.3 TypeScript Interface Definitions

#### New File: `frontend/src/types/api.ts`
```typescript
// Command and Response interfaces
export interface BaseCommand<T = any> {
  id: string;
  type: string;
  payload?: T;
  timestamp: number;
}

export interface BaseResponse<T = any> {
  id: string;
  type: string;
  success: boolean;
  data?: T;
  error?: string;
  timestamp: number;
}

export interface ProgressEvent {
  operation_id: string;
  type: 'progress' | 'error' | 'complete';
  progress: number;
  message: string;
  data?: any;
  timestamp: number;
}

// Account interfaces
export interface Account {
  name: string;
  email: string;
  created_at: string;
  last_used?: string;
  status: 'active' | 'inactive';
}

export interface AccountCreatePayload {
  name: string;
  email?: string;
}

// Queue interfaces
export interface QueueEntry {
  id: string;
  account_name: string;
  total_songs: number;
  songs_per_batch: number;
  prompts_range: [number, number];
  status: 'pending' | 'running' | 'completed' | 'failed';
  completed_count: number;
  created_at: string;
}

export interface SunoPrompt {
  title: string;
  lyrics: string;
  style: string;
}

// Song creation interfaces
export interface AdvancedOptions {
  weirdness: number;
  creativity: number;
  clarity: number;
  model: 'v4' | 'v3.5' | 'v3';
  vocal_gender: 'auto' | 'male' | 'female';
  lyrics_mode: 'auto' | 'manual';
  style_influence: number;
}

export interface SongCreateBatchPayload {
  account_name: string;
  prompts: SunoPrompt[];
  songs_per_batch: number;
  advanced_options: AdvancedOptions;
  auto_submit: boolean;
}

// Download interfaces
export interface SongClip {
  id: string;
  title: string;
  audio_url?: string;
  image_url?: string;
  tags: string;
  created_at?: string;
  duration?: string;
}

export interface DownloadStartPayload {
  account_name: string;
  profile_name?: string;
  use_create_page: boolean;
  limit: number;
  output_dir: string;
  with_thumbnails: boolean;
  append_uuid: boolean;
}
```

### 1.4 IPC Communication Service

#### New File: `backend/src/ipc-service.ts`
```typescript
import { spawn, ChildProcess } from 'child_process';
import { EventEmitter } from 'events';

export class IPCService extends EventEmitter {
  private pythonProcess: ChildProcess | null = null;
  private pendingCommands: Map<string, {
    resolve: (value: any) => void;
    reject: (error: any) => void;
  }> = new Map();

  constructor(private pythonScriptPath: string) {
    super();
  }

  async start(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.pythonProcess = spawn('python', [this.pythonScriptPath]);

      if (!this.pythonProcess.stdin || !this.pythonProcess.stdout || !this.pythonProcess.stderr) {
        reject(new Error('Failed to spawn Python process'));
        return;
      }

      this.pythonProcess.stdout.on('data', (data: Buffer) => {
        const lines = data.toString().split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const response = JSON.parse(line);
            this.handleResponse(response);
          } catch (error) {
            console.error('Failed to parse response:', line, error);
          }
        }
      });

      this.pythonProcess.stderr.on('data', (data: Buffer) => {
        const lines = data.toString().split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const event = JSON.parse(line);
            if (event.type === 'progress') {
              this.emit('progress', event);
            }
          } catch (error) {
            console.error('Failed to parse event:', line, error);
          }
        }
      });

      this.pythonProcess.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(`Python process exited with code ${code}`));
        }
      });

      this.pythonProcess.on('error', (error) => {
        reject(error);
      });

      resolve();
    });
  }

  async sendCommand<T, R>(type: string, payload?: T): Promise<R> {
    return new Promise((resolve, reject) => {
      if (!this.pythonProcess?.stdin) {
        reject(new Error('Python process not available'));
        return;
      }

      const id = this.generateId();
      const command = {
        id,
        type,
        payload,
        timestamp: Date.now()
      };

      // Store promise resolvers for response handling
      this.pendingCommands.set(id, { resolve, reject });

      // Send command
      this.pythonProcess.stdin.write(JSON.stringify(command) + '\n');

      // Set timeout for command
      setTimeout(() => {
        if (this.pendingCommands.has(id)) {
          this.pendingCommands.delete(id);
          reject(new Error(`Command timeout: ${type}`));
        }
      }, 30000); // 30 second timeout
    });
  }

  private handleResponse(response: any): void {
    const { id } = response;
    const pending = this.pendingCommands.get(id);

    if (pending) {
      this.pendingCommands.delete(id);

      if (response.success) {
        pending.resolve(response.data);
      } else {
        pending.reject(new Error(response.error || 'Unknown error'));
      }
    }
  }

  private generateId(): string {
    return `cmd_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  async stop(): Promise<void> {
    return new Promise((resolve) => {
      if (this.pythonProcess) {
        this.pythonProcess.on('close', () => resolve());
        this.pythonProcess.kill();
        this.pythonProcess = null;
      } else {
        resolve();
      }
    });
  }
}
```

### Phase 1 Deliverables
1. ✅ **Communication Protocol** - Defined JSON command/response format
2. ✅ **Backend Server** - Python stdin/stdout server implementation
3. ✅ **TypeScript Types** - Complete type definitions for all interfaces
4. ✅ **IPC Service** - Node.js IPC communication layer
5. ✅ **Progress System** - Real-time progress callback mechanism

### Testing Strategy
- Unit tests for communication protocol
- Integration tests for command/response flow
- Progress event testing
- Error handling validation

---

## Phase 2: Electron + TypeScript Setup

### Duration: 1-2 weeks

### Objectives
- Create Electron main process with Python child process management
- Implement secure preload script for IPC communication
- Setup TypeScript configuration and build system
- Configure hot-reload development environment

### 2.1 Project Structure

```
frontend/
├── public/
│   ├── index.html
│   └── assets/
├── src/
│   ├── main/                   # Electron main process
│   │   ├── main.ts
│   │   ├── preload.ts
│   │   └── ipc-handlers.ts
│   ├── renderer/               # React frontend
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── stores/
│   │   ├── services/
│   │   └── types/
│   └── shared/                 # Shared types and utilities
│       ├── types/
│       └── constants/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── electron-builder.json
└── resources/
```

### 2.2 Main Process Configuration

#### New File: `frontend/src/main/main.ts`
```typescript
import { app, BrowserWindow, ipcMain, dialog } from 'electron';
import path from 'path';
import { IPCService } from './ipc-service';
import { setupIPCHandlers } from './ipc-handlers';

class MainProcess {
  private mainWindow: BrowserWindow | null = null;
  private ipcService: IPCService | null = null;

  constructor() {
    this.initializeApp();
  }

  private initializeApp(): void {
    app.whenReady().then(() => {
      this.createWindow();
      this.setupIPCServices();
      this.setupEventHandlers();
    });

    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });
  }

  private createWindow(): void {
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 850,
      minWidth: 1200,
      minHeight: 700,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js')
      },
      icon: path.join(__dirname, '../../assets/icon.png'),
      show: false
    });

    // Load the app
    if (process.env.NODE_ENV === 'development') {
      this.mainWindow.loadURL('http://localhost:5173');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
    }

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
    });
  }

  private async setupIPCServices(): Promise<void> {
    const pythonScriptPath = path.join(
      __dirname,
      '../../../backend/communication_server.py'
    );

    this.ipcService = new IPCService(pythonScriptPath);

    try {
      await this.ipcService.start();
      console.log('Python backend service started successfully');

      // Setup IPC handlers
      setupIPCHandlers(this.ipcService, ipcMain);

      // Setup progress event forwarding
      this.ipcService.on('progress', (event) => {
        this.mainWindow?.webContents.send('progress-event', event);
      });

    } catch (error) {
      console.error('Failed to start Python backend:', error);
      dialog.showErrorBox('Backend Error', 'Failed to start Python backend service');
    }
  }

  private setupEventHandlers(): void {
    ipcMain.handle('app:get-version', () => {
      return app.getVersion();
    });

    ipcMain.handle('app:quit', () => {
      app.quit();
    });

    ipcMain.handle('app:minimize', () => {
      this.mainWindow?.minimize();
    });

    ipcMain.handle('app:maximize', () => {
      if (this.mainWindow?.isMaximized()) {
        this.mainWindow.unmaximize();
      } else {
        this.mainWindow?.maximize();
      }
    });
  }

  async shutdown(): Promise<void> {
    if (this.ipcService) {
      await this.ipcService.stop();
    }
  }
}

const mainProcess = new MainProcess();

app.on('before-quit', async () => {
  await mainProcess.shutdown();
});
```

### 2.3 Preload Script (Security Bridge)

#### New File: `frontend/src/main/preload.ts`
```typescript
import { contextBridge, ipcRenderer } from 'electron';

// Expose secure APIs to renderer process
contextBridge.exposeInMainWorld('electronAPI', {
  // Application APIs
  getAppVersion: () => ipcRenderer.invoke('app:get-version'),
  quitApp: () => ipcRenderer.invoke('app:quit'),
  minimizeWindow: () => ipcRenderer.invoke('app:minimize'),
  maximizeWindow: () => ipcRenderer.invoke('app:maximize'),

  // Account Management APIs
  account: {
    create: (name: string, email?: string) =>
      ipcRenderer.invoke('account:create', { name, email }),
    getAll: () => ipcRenderer.invoke('account:get_all'),
    rename: (oldName: string, newName: string) =>
      ipcRenderer.invoke('account:rename', { oldName, newName }),
    delete: (name: string, deleteProfile: boolean = false) =>
      ipcRenderer.invoke('account:delete', { name, deleteProfile }),
    getSession: (name: string) =>
      ipcRenderer.invoke('account:get_session', { name })
  },

  // Queue Management APIs
  queue: {
    loadPrompts: (filePath: string) =>
      ipcRenderer.invoke('queue:load_prompts', { filePath }),
    addEntry: (accountName: string, totalSongs: number, songsPerBatch: number, promptsRange: [number, number]) =>
      ipcRenderer.invoke('queue:add_entry', { accountName, totalSongs, songsPerBatch, promptsRange }),
    getAll: () => ipcRenderer.invoke('queue:get_all'),
    updateProgress: (queueId: string, completedCount: number, status: string) =>
      ipcRenderer.invoke('queue:update_progress', { queueId, completedCount, status }),
    deleteEntry: (queueId: string) =>
      ipcRenderer.invoke('queue:delete_entry', { queueId })
  },

  // Song Creation APIs
  song: {
    createBatch: (payload: any) =>
      ipcRenderer.invoke('song:create_batch', payload),
    createSingle: (payload: any) =>
      ipcRenderer.invoke('song:create_single', payload),
    getHistory: (accountName?: string) =>
      ipcRenderer.invoke('song:get_history', { accountName }),
    stopCreation: () =>
      ipcRenderer.invoke('song:stop_creation')
  },

  // Download APIs
  download: {
    start: (payload: any) =>
      ipcRenderer.invoke('download:start', payload),
    getHistory: (accountName?: string) =>
      ipcRenderer.invoke('download:get_history', { accountName }),
    getClips: (accountName: string, profileName?: string) =>
      ipcRenderer.invoke('download:get_clips', { accountName, profileName })
  },

  // Event listeners
  onProgressEvent: (callback: (event: any) => void) => {
    ipcRenderer.on('progress-event', (event, data) => callback(data));
  },

  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Type definitions for exposed APIs
declare global {
  interface Window {
    electronAPI: {
      getAppVersion: () => Promise<string>;
      quitApp: () => Promise<void>;
      minimizeWindow: () => Promise<void>;
      maximizeWindow: () => Promise<void>;
      account: {
        create: (name: string, email?: string) => Promise<any>;
        getAll: () => Promise<any[]>;
        rename: (oldName: string, newName: string) => Promise<boolean>;
        delete: (name: string, deleteProfile?: boolean) => Promise<boolean>;
        getSession: (name: string) => Promise<string | null>;
      };
      queue: {
        loadPrompts: (filePath: string) => Promise<any>;
        addEntry: (accountName: string, totalSongs: number, songsPerBatch: number, promptsRange: [number, number]) => Promise<any>;
        getAll: () => Promise<any[]>;
        updateProgress: (queueId: string, completedCount: number, status: string) => Promise<boolean>;
        deleteEntry: (queueId: string) => Promise<boolean>;
      };
      song: {
        createBatch: (payload: any) => Promise<any>;
        createSingle: (payload: any) => Promise<any>;
        getHistory: (accountName?: string) => Promise<any[]>;
        stopCreation: () => Promise<void>;
      };
      download: {
        start: (payload: any) => Promise<any>;
        getHistory: (accountName?: string) => Promise<any[]>;
        getClips: (accountName: string, profileName?: string) => Promise<any[]>;
      };
      onProgressEvent: (callback: (event: any) => void) => void;
      removeAllListeners: (channel: string) => void;
    };
  }
}
```

### 2.4 IPC Handlers

#### New File: `frontend/src/main/ipc-handlers.ts`
```typescript
import { ipcMain } from 'electron';
import { IPCService } from './ipc-service';

export function setupIPCHandlers(ipcService: IPCService, ipcMainInstance: typeof ipcMain): void {
  // Account Management Handlers
  ipcMainInstance.handle('account:create', async (event, { name, email }) => {
    return await ipcService.sendCommand('account:create', { name, email });
  });

  ipcMainInstance.handle('account:get_all', async () => {
    return await ipcService.sendCommand('account:get_all');
  });

  ipcMainInstance.handle('account:rename', async (event, { oldName, newName }) => {
    return await ipcService.sendCommand('account:rename', { oldName, newName });
  });

  ipcMainInstance.handle('account:delete', async (event, { name, deleteProfile }) => {
    return await ipcService.sendCommand('account:delete', { name, deleteProfile });
  });

  ipcMainInstance.handle('account:get_session', async (event, { name }) => {
    return await ipcService.sendCommand('account:get_session', { name });
  });

  // Queue Management Handlers
  ipcMainInstance.handle('queue:load_prompts', async (event, { filePath }) => {
    return await ipcService.sendCommand('queue:load_prompts', { filePath });
  });

  ipcMainInstance.handle('queue:add_entry', async (event, { accountName, totalSongs, songsPerBatch, promptsRange }) => {
    return await ipcService.sendCommand('queue:add_entry', {
      accountName,
      totalSongs,
      songsPerBatch,
      promptsRange
    });
  });

  ipcMainInstance.handle('queue:get_all', async () => {
    return await ipcService.sendCommand('queue:get_all');
  });

  ipcMainInstance.handle('queue:update_progress', async (event, { queueId, completedCount, status }) => {
    return await ipcService.sendCommand('queue:update_progress', {
      queueId,
      completedCount,
      status
    });
  });

  ipcMainInstance.handle('queue:delete_entry', async (event, { queueId }) => {
    return await ipcService.sendCommand('queue:delete_entry', { queueId });
  });

  // Song Creation Handlers
  ipcMainInstance.handle('song:create_batch', async (event, payload) => {
    return await ipcService.sendCommand('song:create_batch', payload);
  });

  ipcMainInstance.handle('song:create_single', async (event, payload) => {
    return await ipcService.sendCommand('song:create_single', payload);
  });

  ipcMainInstance.handle('song:get_history', async (event, { accountName }) => {
    return await ipcService.sendCommand('song:get_history', { accountName });
  });

  ipcMainInstance.handle('song:stop_creation', async () => {
    return await ipcService.sendCommand('song:stop_creation');
  });

  // Download Handlers
  ipcMainInstance.handle('download:start', async (event, payload) => {
    return await ipcService.sendCommand('download:start', payload);
  });

  ipcMainInstance.handle('download:get_history', async (event, { accountName }) => {
    return await ipcService.sendCommand('download:get_history', { accountName });
  });

  ipcMainInstance.handle('download:get_clips', async (event, { accountName, profileName }) => {
    return await ipcService.sendCommand('download:get_clips', { accountName, profileName });
  });
}
```

### 2.5 TypeScript Configuration

#### New File: `frontend/tsconfig.json`
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "allowJs": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@/main/*": ["src/main/*"],
      "@/renderer/*": ["src/renderer/*"],
      "@/shared/*": ["src/shared/*"]
    }
  },
  "include": [
    "src/**/*"
  ],
  "exclude": [
    "node_modules",
    "dist",
    "build"
  ]
}
```

#### New File: `frontend/vite.config.ts`
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react()],
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
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@/main': resolve(__dirname, 'src/main'),
      '@/renderer': resolve(__dirname, 'src/renderer'),
      '@/shared': resolve(__dirname, 'src/shared')
    }
  },
  server: {
    port: 5173,
    strictPort: true
  }
});
```

### 2.6 Package Configuration

#### New File: `frontend/package.json`
```json
{
  "name": "suno-account-manager",
  "version": "3.0.0",
  "description": "Suno Account Manager - React + Electron version",
  "main": "dist/main/main.js",
  "homepage": "./",
  "scripts": {
    "dev": "concurrently \"npm run dev:renderer\" \"npm run dev:main\"",
    "dev:renderer": "vite",
    "dev:main": "tsc -p tsconfig.main.json && electron dist/main/main.js",
    "build": "npm run build:renderer && npm run build:main",
    "build:renderer": "vite build",
    "build:main": "tsc -p tsconfig.main.json",
    "build:all": "npm run build && electron-builder",
    "preview": "vite preview",
    "electron": "electron dist/main/main.js",
    "pack": "electron-builder --dir",
    "dist": "electron-builder",
    "dist:win": "electron-builder --win",
    "dist:mac": "electron-builder --mac",
    "dist:linux": "electron-builder --linux"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "zustand": "^4.3.6",
    "@tanstack/react-query": "^4.24.6",
    "axios": "^1.3.4",
    "clsx": "^1.2.1",
    "tailwind-merge": "^1.10.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.28",
    "@types/react-dom": "^18.0.11",
    "@types/node": "^18.14.6",
    "@vitejs/plugin-react": "^3.1.0",
    "typescript": "^4.9.4",
    "vite": "^4.1.4",
    "electron": "^23.1.0",
    "electron-builder": "^23.6.0",
    "concurrently": "^7.6.0",
    "tailwindcss": "^3.2.7",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.21",
    "@headlessui/react": "^1.7.13",
    "@heroicons/react": "^2.0.16",
    "react-hook-form": "^7.43.5",
    "react-hot-toast": "^2.4.0"
  },
  "build": {
    "appId": "com.suno.account-manager",
    "productName": "Suno Account Manager",
    "directories": {
      "output": "release"
    },
    "files": [
      "dist/**/*",
      "node_modules/**/*"
    ],
    "extraResources": [
      {
        "from": "../backend",
        "to": "backend"
      }
    ],
    "win": {
      "target": "nsis",
      "icon": "assets/icon.ico"
    },
    "mac": {
      "target": "dmg",
      "icon": "assets/icon.icns"
    },
    "linux": {
      "target": "AppImage",
      "icon": "assets/icon.png"
    }
  }
}
```

### Phase 2 Deliverables
1. ✅ **Electron Main Process** - Complete main process setup with Python integration
2. ✅ **Security Bridge** - Preload script with secure API exposure
3. ✅ **TypeScript Config** - Complete TypeScript setup for all processes
4. ✅ **Build System** - Vite + Electron builder configuration
5. ✅ **Development Environment** - Hot reload and debugging setup

### Testing Strategy
- Main process unit tests
- Preload script security tests
- IPC communication tests
- Build process validation

---

## Phase 3: React Frontend Development

### Duration: 2-3 weeks

### Objectives
- Build React components mirroring CustomTkinter tabs
- Implement Zustand stores for state management
- Create Tailwind CSS styling system
- Build real-time progress components
- Maintain exact feature parity with existing UI

### 3.1 Component Architecture

```
src/renderer/
├── components/
│   ├── common/                   # Reusable components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   ├── ProgressBar.tsx
│   │   └── Toast.tsx
│   ├── layout/                   # Layout components
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   ├── TabContainer.tsx
│   │   └── MainContent.tsx
│   ├── panels/                   # Main feature panels
│   │   ├── AccountPanel.tsx
│   │   ├── CreateMusicPanel.tsx
│   │   ├── MultipleSongsPanel.tsx
│   │   ├── DownloadPanel.tsx
│   │   ├── DownloadHistoryPanel.tsx
│   │   └── SongCreationHistoryPanel.tsx
│   └── features/                 # Feature-specific components
│       ├── AccountCard.tsx
│       ├── QueueEntry.tsx
│       ├── SongItem.tsx
│       ├── ProgressIndicator.tsx
│       └── PreviewWidget.tsx
├── hooks/                        # Custom React hooks
│   ├── useElectronAPI.ts
│   ├── useProgress.ts
│   ├── useAccounts.ts
│   └── useQueues.ts
├── stores/                       # Zustand stores
│   ├── accountStore.ts
│   ├── queueStore.ts
│   ├── songStore.ts
│   └── downloadStore.ts
├── services/                     # API services
│   ├── accountService.ts
│   ├── queueService.ts
│   ├── songService.ts
│   └── downloadService.ts
├── styles/                       # Styling
│   ├── globals.css
│   └── components.css
└── utils/                        # Utilities
    ├── formatters.ts
    ├── validators.ts
    └── constants.ts
```

### 3.2 Main App Component

#### New File: `frontend/src/renderer/App.tsx`
```typescript
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

import { Layout } from './components/layout/Layout';
import { AccountPanel } from './components/panels/AccountPanel';
import { CreateMusicPanel } from './components/panels/CreateMusicPanel';
import { MultipleSongsPanel } from './components/panels/MultipleSongsPanel';
import { DownloadPanel } from './components/panels/DownloadPanel';
import { DownloadHistoryPanel } from './components/panels/DownloadHistoryPanel';
import { SongCreationHistoryPanel } from './components/panels/SongCreationHistoryPanel';

import { useElectronAPI } from './hooks/useElectronAPI';
import { useProgressEvents } from './hooks/useProgressEvents';

function App() {
  const { isReady, error } = useElectronAPI();

  // Setup global progress event handler
  useProgressEvents();

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-500 mb-2">
            Application Error
          </h1>
          <p className="text-gray-300">
            Failed to initialize application: {error.message}
          </p>
        </div>
      </div>
    );
  }

  if (!isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-300">Loading Suno Account Manager...</p>
        </div>
      </div>
    );
  }

  return (
    <Router>
      <div className="h-screen bg-gray-900 text-white overflow-hidden">
        <Layout>
          <Routes>
            <Route path="/" element={<AccountPanel />} />
            <Route path="/accounts" element={<AccountPanel />} />
            <Route path="/create-music" element={<CreateMusicPanel />} />
            <Route path="/multiple-songs" element={<MultipleSongsPanel />} />
            <Route path="/download" element={<DownloadPanel />} />
            <Route path="/download-history" element={<DownloadHistoryPanel />} />
            <Route path="/song-history" element={<SongCreationHistoryPanel />} />
          </Routes>
        </Layout>

        {/* Global toast notifications */}
        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1f2937',
              color: '#f3f4f6',
              border: '1px solid #374151',
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#f3f4f6',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#f3f4f6',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

export default App;
```

### 3.3 Zustand Store Architecture

#### New File: `frontend/src/renderer/stores/accountStore.ts`
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Account } from '@/shared/types/api';

interface AccountState {
  accounts: Account[];
  selectedAccount: Account | null;
  isLoading: boolean;
  error: string | null;
}

interface AccountActions {
  setAccounts: (accounts: Account[]) => void;
  addAccount: (account: Account) => void;
  updateAccount: (name: string, updates: Partial<Account>) => void;
  removeAccount: (name: string) => void;
  selectAccount: (account: Account | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
}

export const useAccountStore = create<AccountState & AccountActions>()(
  persist(
    (set, get) => ({
      // Initial state
      accounts: [],
      selectedAccount: null,
      isLoading: false,
      error: null,

      // Actions
      setAccounts: (accounts) => set({ accounts }),

      addAccount: (account) => set((state) => ({
        accounts: [...state.accounts, account]
      })),

      updateAccount: (name, updates) => set((state) => ({
        accounts: state.accounts.map(acc =>
          acc.name === name ? { ...acc, ...updates } : acc
        ),
        selectedAccount: state.selectedAccount?.name === name
          ? { ...state.selectedAccount, ...updates }
          : state.selectedAccount
      })),

      removeAccount: (name) => set((state) => ({
        accounts: state.accounts.filter(acc => acc.name !== name),
        selectedAccount: state.selectedAccount?.name === name
          ? null
          : state.selectedAccount
      })),

      selectAccount: (account) => set({ selectedAccount: account }),

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      clearError: () => set({ error: null })
    }),
    {
      name: 'account-store',
      partialize: (state) => ({
        accounts: state.accounts,
        selectedAccount: state.selectedAccount
      })
    }
  )
);
```

#### New File: `frontend/src/renderer/stores/queueStore.ts`
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { QueueEntry, SunoPrompt } from '@/shared/types/api';

interface QueueState {
  prompts: SunoPrompt[];
  queues: QueueEntry[];
  selectedQueues: string[];
  isLoading: boolean;
  isProcessing: boolean;
  processingQueueId: string | null;
  error: string | null;
  lastPromptCount: number;
}

interface QueueActions {
  setPrompts: (prompts: SunoPrompt[]) => void;
  setQueues: (queues: QueueEntry[]) => void;
  addQueue: (queue: QueueEntry) => void;
  updateQueue: (queueId: string, updates: Partial<QueueEntry>) => void;
  removeQueue: (queueId: string) => void;
  toggleQueueSelection: (queueId: string) => void;
  selectAllQueues: () => void;
  deselectAllQueues: () => void;
  setLoading: (loading: boolean) => void;
  setProcessing: (isProcessing: boolean, queueId?: string) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  reset: () => void;
}

export const useQueueStore = create<QueueState & QueueActions>()(
  persist(
    (set, get) => ({
      // Initial state
      prompts: [],
      queues: [],
      selectedQueues: [],
      isLoading: false,
      isProcessing: false,
      processingQueueId: null,
      error: null,
      lastPromptCount: 0,

      // Actions
      setPrompts: (prompts) => set({
        prompts,
        lastPromptCount: prompts.length
      }),

      setQueues: (queues) => set({ queues }),

      addQueue: (queue) => set((state) => ({
        queues: [...state.queues, queue]
      })),

      updateQueue: (queueId, updates) => set((state) => ({
        queues: state.queues.map(queue =>
          queue.id === queueId ? { ...queue, ...updates } : queue
        )
      })),

      removeQueue: (queueId) => set((state) => ({
        queues: state.queues.filter(queue => queue.id !== queueId),
        selectedQueues: state.selectedQueues.filter(id => id !== queueId)
      })),

      toggleQueueSelection: (queueId) => set((state) => ({
        selectedQueues: state.selectedQueues.includes(queueId)
          ? state.selectedQueues.filter(id => id !== queueId)
          : [...state.selectedQueues, queueId]
      })),

      selectAllQueues: () => set((state) => ({
        selectedQueues: state.queues.map(queue => queue.id)
      })),

      deselectAllQueues: () => set({ selectedQueues: [] }),

      setLoading: (isLoading) => set({ isLoading }),

      setProcessing: (isProcessing, queueId) => set({
        isProcessing,
        processingQueueId: queueId || null
      }),

      setError: (error) => set({ error }),

      clearError: () => set({ error: null }),

      reset: () => set({
        prompts: [],
        queues: [],
        selectedQueues: [],
        isLoading: false,
        isProcessing: false,
        processingQueueId: null,
        error: null,
        lastPromptCount: 0
      })
    }),
    {
      name: 'queue-store',
      partialize: (state) => ({
        prompts: state.prompts,
        queues: state.queues,
        lastPromptCount: state.lastPromptCount
      })
    }
  )
);
```

### 3.4 Custom Hooks

#### New File: `frontend/src/renderer/hooks/useElectronAPI.ts`
```typescript
import { useState, useEffect } from 'react';

export function useElectronAPI() {
  const [isReady, setIsReady] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Check if Electron API is available
    if (!window.electronAPI) {
      setError(new Error('Electron API not available'));
      return;
    }

    // Test API connectivity
    const testConnection = async () => {
      try {
        const version = await window.electronAPI.getAppVersion();
        console.log('Connected to Suno Account Manager v', version);
        setIsReady(true);
      } catch (err) {
        setError(err instanceof Error ? err : new Error('Unknown error'));
      }
    };

    testConnection();
  }, []);

  return { isReady, error };
}
```

#### New File: `frontend/src/renderer/hooks/useProgressEvents.ts`
```typescript
import { useCallback } from 'react';
import { toast } from 'react-hot-toast';

export function useProgressEvents() {
  const handleProgressEvent = useCallback((event: any) => {
    const { type, operation_id, progress, message, data } = event;

    switch (type) {
      case 'progress':
        // Update progress indicators in stores
        // This would be handled by individual components
        break;

      case 'error':
        toast.error(`Operation failed: ${message}`);
        break;

      case 'complete':
        toast.success(`Operation completed: ${message}`);
        break;

      default:
        console.log('Unknown progress event:', event);
    }
  }, []);

  // Setup progress event listener
  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.onProgressEvent(handleProgressEvent);

      return () => {
        window.electronAPI.removeAllListeners('progress-event');
      };
    }
  }, [handleProgressEvent]);
}
```

### 3.5 Key Panel Components

#### New File: `frontend/src/renderer/components/panels/AccountPanel.tsx`
```typescript
import React, { useState, useEffect } from 'react';
import { PlusIcon, TrashIcon, PencilIcon, PlayIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

import { useAccountStore } from '@/renderer/stores/accountStore';
import { Button } from '@/renderer/components/common/Button';
import { Input } from '@/renderer/components/common/Input';
import { Modal } from '@/renderer/components/common/Modal';
import { AccountCard } from '@/renderer/components/features/AccountCard';

export function AccountPanel() {
  const {
    accounts,
    selectedAccount,
    isLoading,
    error,
    setAccounts,
    addAccount,
    updateAccount,
    removeAccount,
    selectAccount,
    setLoading,
    setError
  } = useAccountStore();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isRenameModalOpen, setIsRenameModalOpen] = useState(false);
  const [accountToRename, setAccountToRename] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    email: ''
  });

  // Load accounts on mount
  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const accountsData = await window.electronAPI.account.getAll();
      setAccounts(accountsData || []);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = async () => {
    if (!formData.name.trim()) {
      toast.error('Account name is required');
      return;
    }

    try {
      setLoading(true);
      const result = await window.electronAPI.account.create(
        formData.name.trim(),
        formData.email.trim() || undefined
      );

      if (result.account_created) {
        const newAccount = {
          name: formData.name.trim(),
          email: formData.email.trim(),
          created_at: new Date().toISOString(),
          last_used: null,
          status: 'active' as const
        };

        addAccount(newAccount);
        setIsCreateModalOpen(false);
        setFormData({ name: '', email: '' });
        toast.success(`Account "${formData.name}" created successfully`);
      } else {
        toast.error('Failed to create account');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  const handleUseAccount = async (accountName: string) => {
    try {
      setLoading(true);
      selectAccount(accounts.find(acc => acc.name === accountName) || null);

      // This will launch Chrome and get session token
      await window.electronAPI.account.getSession(accountName);

      toast.success(`Account "${accountName}" is now active`);

      // Reload accounts to update last_used timestamp
      await loadAccounts();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to activate account');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async (accountName: string) => {
    if (!confirm(`Are you sure you want to delete account "${accountName}"?`)) {
      return;
    }

    try {
      setLoading(true);
      const success = await window.electronAPI.account.delete(accountName, false);

      if (success) {
        removeAccount(accountName);
        toast.success(`Account "${accountName}" deleted successfully`);
      } else {
        toast.error('Failed to delete account');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to delete account');
    } finally {
      setLoading(false);
    }
  };

  const handleRenameAccount = async () => {
    if (!accountToRename || !formData.name.trim()) {
      toast.error('New name is required');
      return;
    }

    try {
      setLoading(true);
      const success = await window.electronAPI.account.rename(
        accountToRename,
        formData.name.trim()
      );

      if (success) {
        updateAccount(accountToRename, { name: formData.name.trim() });
        setIsRenameModalOpen(false);
        setAccountToRename(null);
        setFormData({ name: '', email: '' });
        toast.success('Account renamed successfully');
      } else {
        toast.error('Failed to rename account');
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to rename account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full">
      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold">Account Management</h1>
          <Button
            onClick={() => setIsCreateModalOpen(true)}
            className="flex items-center gap-2"
          >
            <PlusIcon className="h-5 w-5" />
            Add Account
          </Button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-900/50 border border-red-700 rounded-lg">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          </div>
        ) : accounts.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-300 mb-2">
              No accounts found
            </h3>
            <p className="text-gray-500 mb-4">
              Get started by adding your first Suno account
            </p>
            <Button
              onClick={() => setIsCreateModalOpen(true)}
              className="flex items-center gap-2 mx-auto"
            >
              <PlusIcon className="h-5 w-5" />
              Add Account
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {accounts.map((account) => (
              <AccountCard
                key={account.name}
                account={account}
                isSelected={selectedAccount?.name === account.name}
                onUse={() => handleUseAccount(account.name)}
                onRename={() => {
                  setAccountToRename(account.name);
                  setFormData({ name: account.name, email: account.email });
                  setIsRenameModalOpen(true);
                }}
                onDelete={() => handleDeleteAccount(account.name)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Create Account Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => {
          setIsCreateModalOpen(false);
          setFormData({ name: '', email: '' });
        }}
        title="Add New Account"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Account Name *
            </label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., my_main_account"
              disabled={isLoading}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Email (Optional)
            </label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="your@email.com"
              disabled={isLoading}
            />
          </div>

          <div className="bg-gray-800 rounded-lg p-4">
            <h4 className="font-medium text-gray-300 mb-2">Next Steps:</h4>
            <ol className="text-sm text-gray-400 space-y-1 list-decimal list-inside">
              <li>Chrome browser will open automatically</li>
              <li>Login to your Suno.com account</li>
              <li>Close the browser when login is complete</li>
              <li>Your account will be saved and ready to use</li>
            </ol>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleCreateAccount}
              disabled={isLoading || !formData.name.trim()}
              className="flex-1"
            >
              {isLoading ? 'Creating...' : 'Create Account'}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setIsCreateModalOpen(false);
                setFormData({ name: '', email: '' });
              }}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>

      {/* Rename Account Modal */}
      <Modal
        isOpen={isRenameModalOpen}
        onClose={() => {
          setIsRenameModalOpen(false);
          setAccountToRename(null);
          setFormData({ name: '', email: '' });
        }}
        title="Rename Account"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              New Account Name *
            </label>
            <Input
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="Enter new account name"
              disabled={isLoading}
            />
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              onClick={handleRenameAccount}
              disabled={isLoading || !formData.name.trim()}
              className="flex-1"
            >
              {isLoading ? 'Renaming...' : 'Rename Account'}
            </Button>
            <Button
              variant="outline"
              onClick={() => {
                setIsRenameModalOpen(false);
                setAccountToRename(null);
                setFormData({ name: '', email: '' });
              }}
              disabled={isLoading}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
```

### 3.6 Tailwind CSS Configuration

#### New File: `frontend/tailwind.config.js`
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        gray: {
          800: '#1f2937',
          900: '#111827',
        }
      },
      animation: {
        'spin-slow': 'spin 3s linear infinite',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Phase 3 Deliverables
1. ✅ **Component Architecture** - Complete React component structure
2. ✅ **State Management** - Zustand stores for all application state
3. ✅ **Panel Components** - All 6 main panels matching CustomTkinter functionality
4. ✅ **Common Components** - Reusable UI components (Button, Input, Modal, etc.)
5. ✅ **Styling System** - Tailwind CSS configuration and design system
6. ✅ **Custom Hooks** - API integration and state management hooks

### Testing Strategy
- Component unit tests with React Testing Library
- Store integration tests
- UI interaction tests
- Feature parity validation against CustomTkinter version

---

## Phase 4: Integration & Testing

### Duration: 1-2 weeks

### Objectives
- End-to-end testing of all workflows
- Performance optimization
- Error handling and recovery mechanisms
- Build and packaging process
- Data migration validation

### 4.1 End-to-End Testing

#### New File: `frontend/src/tests/e2e/account-management.test.ts`
```typescript
import { test, expect } from '@playwright/test';

test.describe('Account Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');
  });

  test('should create new account', async ({ page }) => {
    // Navigate to account panel
    await page.click('[data-testid="nav-accounts"]');

    // Click add account button
    await page.click('[data-testid="add-account-btn"]');

    // Fill account form
    await page.fill('[data-testid="account-name-input"]', 'test_account');
    await page.fill('[data-testid="account-email-input"]', 'test@example.com');

    // Submit form
    await page.click('[data-testid="create-account-btn"]');

    // Verify account appears in list
    await expect(page.locator('[data-testid="account-card-test_account"]')).toBeVisible();
    await expect(page.locator('[data-testid="account-email-test_account"]')).toHaveText('test@example.com');
  });

  test('should rename existing account', async ({ page }) => {
    // Setup: Create account first
    await page.click('[data-testid="nav-accounts"]');
    await page.click('[data-testid="add-account-btn"]');
    await page.fill('[data-testid="account-name-input"]', 'old_name');
    await page.click('[data-testid="create-account-btn"]');

    // Rename account
    await page.click('[data-testid="rename-account-old_name"]');
    await page.fill('[data-testid="account-name-input"]', 'new_name');
    await page.click('[data-testid="rename-account-btn"]');

    // Verify renamed account
    await expect(page.locator('[data-testid="account-card-new_name"]')).toBeVisible();
    await expect(page.locator('[data-testid="account-card-old_name"]')).not.toBeVisible();
  });

  test('should delete account', async ({ page }) => {
    // Setup: Create account first
    await page.click('[data-testid="nav-accounts"]');
    await page.click('[data-testid="add-account-btn"]');
    await page.fill('[data-testid="account-name-input"]', 'to_delete');
    await page.click('[data-testid="create-account-btn"]');

    // Delete account
    await page.click('[data-testid="delete-account-to_delete"]');

    // Confirm deletion in modal
    await page.click('[data-testid="confirm-delete-btn"]');

    // Verify account is deleted
    await expect(page.locator('[data-testid="account-card-to_delete"]')).not.toBeVisible();
  });
});
```

#### New File: `frontend/src/tests/e2e/queue-system.test.ts`
```typescript
import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Queue System', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');

    // Setup: Create test account
    await page.click('[data-testid="nav-accounts"]');
    await page.click('[data-testid="add-account-btn"]');
    await page.fill('[data-testid="account-name-input"]', 'queue_test_account');
    await page.click('[data-testid="create-account-btn"]');

    // Activate account
    await page.click('[data-testid="use-account-queue_test_account"]');
  });

  test('should load XML prompts and create queue', async ({ page }) => {
    // Navigate to multiple songs panel
    await page.click('[data-testid="nav-multiple-songs"]');

    // Upload XML file
    const testXmlPath = path.join(__dirname, '../fixtures/test-prompts.xml');
    await page.setInputFiles('[data-testid="xml-upload-input"]', testXmlPath);

    // Verify prompts are loaded
    await expect(page.locator('[data-testid="prompts-loaded-count"]')).toContainText('3 prompts loaded');

    // Create queue entry
    await page.selectOption('[data-testid="account-select"]', 'queue_test_account');
    await page.fill('[data-testid="total-songs-input"]', '3');
    await page.selectOption('[data-testid="songs-per-batch-select"]', '2');
    await page.click('[data-testid="add-queue-btn"]');

    // Verify queue appears
    await expect(page.locator('[data-testid="queue-entry"]')).toHaveCount(1);
    await expect(page.locator('[data-testid="queue-account"]')).toHaveText('queue_test_account');
    await expect(page.locator('[data-testid="queue-total-songs"]')).toHaveText('3');
  });

  test('should start and monitor queue execution', async ({ page }) => {
    // Setup: Create queue first
    await page.click('[data-testid="nav-multiple-songs"]');

    const testXmlPath = path.join(__dirname, '../fixtures/test-prompts.xml');
    await page.setInputFiles('[data-testid="xml-upload-input"]', testXmlPath);
    await page.selectOption('[data-testid="account-select"]', 'queue_test_account');
    await page.fill('[data-testid="total-songs-input"]', '2');
    await page.selectOption('[data-testid="songs-per-batch-select"]', '1');
    await page.click('[data-testid="add-queue-btn"]');

    // Select queue and start execution
    await page.check('[data-testid="queue-checkbox"]');
    await page.click('[data-testid="start-queues-btn"]');

    // Monitor progress
    await expect(page.locator('[data-testid="progress-bar"]')).toBeVisible();
    await expect(page.locator('[data-testid="status-running"]')).toBeVisible();

    // Wait for completion (this might take a while in real tests)
    // await expect(page.locator('[data-testid="status-completed"]')).toBeVisible({ timeout: 300000 });
  });
});
```

### 4.2 Performance Testing

#### New File: `frontend/src/tests/performance/app-performance.test.ts`
```typescript
import { test, expect } from '@playwright/test';

test.describe('Application Performance', () => {
  test('should load within acceptable time', async ({ page }) => {
    const startTime = Date.now();

    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);

    console.log(`Application loaded in ${loadTime}ms`);
  });

  test('should handle large number of accounts efficiently', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');

    // Measure time to load account panel
    const startTime = Date.now();
    await page.click('[data-testid="nav-accounts"]');
    await page.waitForSelector('[data-testid="account-list"]');

    const loadTime = Date.now() - startTime;

    // Should load within 2 seconds
    expect(loadTime).toBeLessThan(2000);

    // Check memory usage (if possible)
    const metrics = await page.evaluate(() => {
      if ('memory' in performance) {
        return {
          used: (performance as any).memory.usedJSHeapSize,
          total: (performance as any).memory.totalJSHeapSize
        };
      }
      return null;
    });

    if (metrics) {
      console.log(`Memory usage: ${Math.round(metrics.used / 1024 / 1024)}MB`);
      // Should use less than 200MB
      expect(metrics.used).toBeLessThan(200 * 1024 * 1024);
    }
  });

  test('should maintain responsiveness during operations', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.waitForLoadState('networkidle');

    // Start a long-running operation (e.g., large queue)
    await page.click('[data-testid="nav-multiple-songs"]');

    // UI should remain responsive during operation
    const navigationStartTime = Date.now();
    await page.click('[data-testid="nav-accounts"]');
    await page.waitForSelector('[data-testid="account-list"]');

    const navigationTime = Date.now() - navigationStartTime;

    // Navigation should complete quickly even during operations
    expect(navigationTime).toBeLessThan(1000);
  });
});
```

### 4.3 Error Handling Tests

#### New File: `frontend/src/tests/error-handling.test.ts`
```typescript
import { test, expect } from '@playwright/test';

test.describe('Error Handling', () => {
  test('should handle backend disconnection gracefully', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Simulate backend disconnection (this would need to be implemented in test setup)
    await page.evaluate(() => {
      // Simulate backend going offline
      window.electronAPI = undefined;
    });

    // Should show error state
    await expect(page.locator('[data-testid="error-state"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Application Error');
  });

  test('should handle invalid XML file upload', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.click('[data-testid="nav-multiple-songs"]');

    // Upload invalid XML
    await page.setInputFiles('[data-testid="xml-upload-input"]', 'invalid.xml');

    // Should show error message
    await expect(page.locator('[data-testid="upload-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="upload-error"]')).toContainText('Invalid XML format');
  });

  test('should handle network timeouts', async ({ page }) => {
    // This test would require mocking network timeouts
    // Implementation depends on testing strategy chosen
  });
});
```

### 4.4 Build and Packaging

#### Enhanced `package.json` scripts
```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:renderer\" \"npm run dev:main\"",
    "dev:renderer": "vite",
    "dev:main": "tsc -p tsconfig.main.json && electron dist/main/main.js",
    "build": "npm run build:renderer && npm run build:main",
    "build:renderer": "vite build",
    "build:main": "tsc -p tsconfig.main.json",
    "build:all": "npm run build && npm run build:backend && electron-builder",
    "build:backend": "cd ../backend && python -m PyInstaller --onefile communication_server.py --name backend.exe",
    "preview": "vite preview",
    "electron": "electron dist/main/main.js",
    "test": "npm run test:unit && npm run test:e2e",
    "test:unit": "vitest",
    "test:e2e": "playwright test",
    "test:performance": "playwright test --config playwright.performance.config.ts",
    "lint": "eslint src --ext .ts,.tsx",
    "lint:fix": "eslint src --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit"
  }
}
```

### 4.5 Data Migration

#### New File: `tools/migrate-data.py`
```python
#!/usr/bin/env python3
"""
Data migration script from CustomTkinter version to React + Electron version.
Migrates JSON data files to maintain continuity.
"""

import json
import os
import shutil
from pathlib import Path
from datetime import datetime

class DataMigrator:
    """Handles migration of data from old to new application format."""

    def __init__(self, old_data_dir: Path, new_data_dir: Path):
        self.old_data_dir = old_data_dir
        self.new_data_dir = new_data_dir
        self.migration_log = []

    def migrate_all(self):
        """Perform complete data migration."""
        print("Starting data migration...")

        # Create new data directory if it doesn't exist
        self.new_data_dir.mkdir(parents=True, exist_ok=True)

        # Migrate each data file
        self.migrate_accounts()
        self.migrate_queue_state()
        self.migrate_download_history()
        self.migrate_song_creation_history()

        # Copy Chrome profiles
        self.migrate_chrome_profiles()

        # Generate migration report
        self.generate_migration_report()

        print(f"Migration completed. See {self.new_data_dir}/migration_report.json")

    def migrate_accounts(self):
        """Migrate accounts data."""
        old_file = self.old_data_dir / 'suno_accounts.json'
        new_file = self.new_data_dir / 'suno_accounts.json'

        if old_file.exists():
            try:
                # Read old data
                with open(old_file, 'r', encoding='utf-8') as f:
                    old_data = json.load(f)

                # Convert to new format if needed
                new_data = self.convert_accounts_format(old_data)

                # Write new data
                with open(new_file, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, indent=2, ensure_ascii=False)

                self.migration_log.append({
                    'file': 'suno_accounts.json',
                    'status': 'success',
                    'accounts_migrated': len(new_data),
                    'timestamp': datetime.now().isoformat()
                })

                print(f"✅ Migrated {len(new_data)} accounts")

            except Exception as e:
                self.migration_log.append({
                    'file': 'suno_accounts.json',
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ Failed to migrate accounts: {e}")
        else:
            print("⚠️  No accounts file found")

    def migrate_queue_state(self):
        """Migrate queue state data."""
        old_file = self.old_data_dir / 'queue_state.json'
        new_file = self.new_data_dir / 'queue_state.json'

        if old_file.exists():
            try:
                shutil.copy2(old_file, new_file)

                self.migration_log.append({
                    'file': 'queue_state.json',
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })

                print("✅ Migrated queue state")

            except Exception as e:
                self.migration_log.append({
                    'file': 'queue_state.json',
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ Failed to migrate queue state: {e}")
        else:
            print("⚠️  No queue state file found")

    def migrate_download_history(self):
        """Migrate download history data."""
        old_file = self.old_data_dir / 'download_history.json'
        new_file = self.new_data_dir / 'download_history.json'

        if old_file.exists():
            try:
                shutil.copy2(old_file, new_file)

                self.migration_log.append({
                    'file': 'download_history.json',
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })

                print("✅ Migrated download history")

            except Exception as e:
                self.migration_log.append({
                    'file': 'download_history.json',
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ Failed to migrate download history: {e}")
        else:
            print("⚠️  No download history file found")

    def migrate_song_creation_history(self):
        """Migrate song creation history data."""
        old_file = self.old_data_dir / 'song_creation_history.json'
        new_file = self.new_data_dir / 'song_creation_history.json'

        if old_file.exists():
            try:
                shutil.copy2(old_file, new_file)

                self.migration_log.append({
                    'file': 'song_creation_history.json',
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })

                print("✅ Migrated song creation history")

            except Exception as e:
                self.migration_log.append({
                    'file': 'song_creation_history.json',
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ Failed to migrate song creation history: {e}")
        else:
            print("⚠️  No song creation history file found")

    def migrate_chrome_profiles(self):
        """Copy Chrome profiles directory."""
        old_profiles = self.old_data_dir.parent / 'profiles'
        new_profiles = self.new_data_dir.parent / 'profiles'

        if old_profiles.exists():
            try:
                if new_profiles.exists():
                    shutil.rmtree(new_profiles)
                shutil.copytree(old_profiles, new_profiles)

                self.migration_log.append({
                    'directory': 'profiles',
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })

                print("✅ Migrated Chrome profiles")

            except Exception as e:
                self.migration_log.append({
                    'directory': 'profiles',
                    'status': 'error',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ Failed to migrate Chrome profiles: {e}")
        else:
            print("⚠️  No Chrome profiles directory found")

    def convert_accounts_format(self, old_data: dict) -> dict:
        """Convert accounts data to new format if needed."""
        # The format should be the same, but this allows for future changes
        return old_data

    def generate_migration_report(self):
        """Generate migration report."""
        report = {
            'migration_date': datetime.now().isoformat(),
            'old_data_dir': str(self.old_data_dir),
            'new_data_dir': str(self.new_data_dir),
            'log': self.migration_log,
            'summary': {
                'total_files': len(self.migration_log),
                'successful': len([log for log in self.migration_log if log['status'] == 'success']),
                'failed': len([log for log in self.migration_log if log['status'] == 'error'])
            }
        }

        report_file = self.new_data_dir / 'migration_report.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

def main():
    """Main migration function."""
    # Get paths from command line or use defaults
    import sys

    if len(sys.argv) > 2:
        old_dir = Path(sys.argv[1])
        new_dir = Path(sys.argv[2])
    else:
        # Default paths
        old_dir = Path(__file__).parent.parent / 'data'
        new_dir = Path(__file__).parent.parent / 'frontend' / 'data'

    migrator = DataMigrator(old_dir, new_dir)
    migrator.migrate_all()

if __name__ == '__main__':
    main()
```

### Phase 4 Deliverables
1. ✅ **E2E Test Suite** - Complete end-to-end test coverage
2. ✅ **Performance Tests** - Application performance validation
3. ✅ **Error Handling** - Comprehensive error scenario testing
4. ✅ **Build Process** - Automated build and packaging
5. ✅ **Data Migration** - Seamless data transfer from old version
6. ✅ **Deployment Package** - Ready-to-distribute application

### Success Criteria Validation
- All CustomTkinter features reproduced in React
- Performance benchmarks met (faster UI response)
- Zero data loss during migration
- Comprehensive test coverage (>90%)
- Successful build and packaging

---

## Risk Assessment & Mitigation

### High-Risk Areas

#### 1. Python Backend Compatibility
**Risk:** Changes to Python managers could break existing functionality
**Mitigation:**
- Minimal changes to existing Python code
- Comprehensive regression testing
- Maintain backward compatibility
- Keep original codebase as backup

#### 2. IPC Communication Reliability
**Risk:** Stdin/stdout communication could be unstable
**Mitigation:**
- Robust error handling and reconnection logic
- Connection health monitoring
- Graceful fallback mechanisms
- Comprehensive logging and debugging

#### 3. Feature Parity
**Risk:** Missing functionality compared to CustomTkinter version
**Mitigation:**
- Detailed feature comparison matrix
- User acceptance testing
- Parallel development and validation
- Regular milestone reviews

#### 4. Performance Degradation
**Risk:** Electron app could be slower than native Python GUI
**Mitigation:**
- Performance benchmarks and optimization
- Efficient React rendering patterns
- Memory usage monitoring
- Lazy loading and code splitting

### Medium-Risk Areas

#### 5. Development Complexity
**Risk:** Multi-process architecture could be complex to debug
**Mitigation:**
- Comprehensive debugging setup
- Clear logging and error reporting
- Development documentation
- Team training and knowledge sharing

#### 6. Data Migration
**Risk:** Data loss during migration from old to new version
**Mitigation:**
- Automated migration scripts
- Data validation and backup
- Rollback procedures
- User testing with sample data

---

## Timeline & Milestones

### Week 1-2: Phase 1 - Backend Communication
- **Week 1:** Protocol design, communication server, IPC service
- **Week 2:** TypeScript types, progress system, integration testing

### Week 3-4: Phase 2 - Electron Setup
- **Week 3:** Main process, preload script, TypeScript config
- **Week 4:** IPC handlers, build system, development environment

### Week 5-7: Phase 3 - React Frontend
- **Week 5:** Component architecture, stores, common components
- **Week 6:** Main panels (Account, Create Music, Multiple Songs)
- **Week 7:** Remaining panels (Download, History), styling system

### Week 8-9: Phase 4 - Integration & Testing
- **Week 8:** End-to-end testing, performance optimization
- **Week 9:** Error handling, data migration, packaging

### Final Week: Deployment & Documentation
- Build and packaging validation
- User documentation
- Deployment preparation
- Post-launch monitoring

---

## Success Metrics

### Technical Metrics
- **Performance:** UI response time <200ms (vs. CustomTkinter ~500ms)
- **Stability:** <1% crash rate, 99% uptime during testing
- **Memory Usage:** <200MB baseline (vs. CustomTkinter ~150MB)
- **Test Coverage:** >90% code coverage
- **Build Time:** <2 minutes for full build

### User Experience Metrics
- **Feature Parity:** 100% of CustomTkinter features available
- **Migration Success:** 100% data migration without loss
- **User Satisfaction:** Target >4.5/5 in user feedback
- **Learning Curve:** <30 minutes for existing users

### Development Metrics
- **Developer Productivity:** Hot reload reduces iteration time by 70%
- **Bug Reduction:** TypeScript catches 80% of runtime errors
- **Maintenance:** Code complexity reduced by 40%
- **Documentation:** 100% API documentation coverage

---

## Conclusion

This migration plan provides a comprehensive roadmap for transitioning Suno Account Manager from CustomTkinter to a modern React + Electron + TypeScript architecture while maintaining 100% feature parity and improving overall performance and developer experience.

### Key Benefits of Migration

1. **Modern Technology Stack:** React 18, TypeScript, Electron, Tailwind CSS
2. **Better Developer Experience:** Hot reload, debugging tools, type safety
3. **Improved Performance:** Faster UI responsiveness, better memory management
4. **Future-Proof:** Easier maintenance, extension, and cross-platform support
5. **Professional UI:** Modern, responsive design with better UX

### Critical Success Factors

1. **Maintain Feature Parity:** Every CustomTkinter feature must be reproduced
2. **Zero Data Loss:** Seamless migration of existing user data
3. **Performance Improvement:** New version must be faster than old version
4. **Stability:** Robust error handling and recovery mechanisms
5. **User Experience:** Intuitive transition for existing users

### Next Steps

1. **Review and Approval:** Stakeholder review of this migration plan
2. **Resource Allocation:** Assign development team members
3. **Environment Setup:** Prepare development and testing environments
4. **Phase 1 Kickoff:** Begin with backend communication layer
5. **Regular Checkpoints:** Weekly progress reviews and adjustments

This migration represents a significant technical upgrade that will position Suno Account Manager for future growth and development while maintaining the reliability and functionality that users depend on.