# TypeScript + React + Electron Architecture Research Report

## Research Scope
Best practices for Suno Account Manager migration from Python to TypeScript/React/Electron with Python backend stdin/stdout communication.

## 1. Electron Architecture Patterns

### Main vs Renderer Process Communication

**IPC Communication Patterns:**
- **One-way**: `ipcRenderer.send()` + `ipcMain.on()`
- **Two-way**: `ipcRenderer.invoke()` + `ipcMain.handle()` (preferred)
- **Main-to-Renderer**: `webContents.send()`
- **Named Channels**: Use namespaced channels (e.g., `dialog:openFile`)

**Security Best Practices:**
- **Never directly expose entire Electron APIs**
- Use `contextBridge.exposeInMainWorld()` for controlled API exposure
- **Avoid synchronous methods** like `sendSync`
- **Limit renderer access** to Electron APIs

### Preload Scripts

**Secure Preload Pattern:**
```typescript
// preload.ts
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  invoke: (channel: string, ...args: any[]) => ipcRenderer.invoke(channel, ...args),
  send: (channel: string, ...args: any[]) => ipcRenderer.send(channel, ...args),
  on: (channel: string, callback: Function) => {
    ipcRenderer.on(channel, (_event, ...args) => callback(...args))
  },
  removeAllListeners: (channel: string) => ipcRenderer.removeAllListeners(channel)
})
```

### Child Process Management

**Python Backend Integration:**
```typescript
// main.ts
import { spawn } from 'child_process'
import { app, BrowserWindow, ipcMain } from 'electron'

const pythonProcess = spawn('python', ['backend/main.py'], {
  stdio: ['pipe', 'pipe', 'pipe']
})

pythonProcess.stdout.on('data', (data) => {
  // Handle stdout from Python backend
})

pythonProcess.stderr.on('data', (data) => {
  // Handle errors
})

pythonProcess.stdin.write(JSON.stringify(command))
```

## 2. TypeScript Integration

### Configuration Setup

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

**Shared Types Between Processes:**
```typescript
// src/shared/types.ts
export interface Account {
  id: string
  name: string
  email: string
  created_at: string
  last_used?: string
  status: 'active' | 'inactive'
}

export interface SongPrompt {
  title: string
  lyrics: string
  style: string
  advanced_options?: AdvancedOptions
}

export interface AdvancedOptions {
  weirdness: number
  creativity: number
  clarity: number
  model: 'v4' | 'v3.5' | 'v3'
  vocal_gender: 'auto' | 'male' | 'female'
  lyrics_mode: 'auto' | 'manual'
  style_influence: number
  persona_name?: string
}
```

## 3. Python Communication Layer

### stdin/stdout JSON Protocol

**Protocol Design:**
```typescript
// Command format
interface Command<T = any> {
  id: string
  type: string
  payload?: T
  timestamp: number
}

// Response format
interface Response<T = any> {
  id: string
  type: string
  success: boolean
  data?: T
  error?: string
  timestamp: number
}

// Example commands
const commands = {
  CREATE_ACCOUNT: 'account:create',
  GET_SESSION_TOKEN: 'session:get-token',
  CREATE_SONGS: 'songs:create-batch',
  DOWNLOAD_SONGS: 'songs:download',
  GET_HISTORY: 'history:get'
}
```

**Real-time Progress Callbacks:**
```typescript
// Progress protocol
interface ProgressEvent {
  type: 'progress'
  operation_id: string
  progress: number
  message: string
  data?: any
}

// Example implementation
class PythonBackend {
  async createSongs(prompts: SongPrompt[], options: CreateOptions) {
    return new Promise((resolve, reject) => {
      const operationId = generateId()

      this.process.stdin.write(JSON.stringify({
        id: operationId,
        type: commands.CREATE_SONGS,
        payload: { prompts, options }
      }))

      const handler = (data: string) => {
        const response: Response | ProgressEvent = JSON.parse(data)

        if (response.type === 'progress') {
          this.emit('progress', response)
        } else if (response.id === operationId) {
          this.process.off('message', handler)
          if (response.success) {
            resolve(response.data)
          } else {
            reject(new Error(response.error))
          }
        }
      }

      this.process.on('message', handler)
    })
  }
}
```

### Error Handling and Timeout Management

```typescript
class PythonBackend {
  private timeout = 30000 // 30 seconds
  private retryAttempts = 3

  async executeWithRetry<T>(command: Command): Promise<T> {
    for (let attempt = 1; attempt <= this.retryAttempts; attempt++) {
      try {
        return await this.executeCommand<T>(command)
      } catch (error) {
        if (attempt === this.retryAttempts) throw error
        await this.delay(1000 * attempt)
      }
    }
    throw new Error('Max retry attempts reached')
  }

  private executeCommand<T>(command: Command): Promise<T> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error('Command timeout'))
      }, this.timeout)

      // ... implementation
    })
  }
}
```

## 4. React + Electron Integration

### Component Architecture

```typescript
// src/components/AccountManager.tsx
import { useState, useEffect } from 'react'
import { electronAPI } from '../electron-api'

export function AccountManager() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadAccounts = async () => {
      setLoading(true)
      try {
        const result = await electronAPI.invoke('account:list')
        setAccounts(result)
      } catch (error) {
        console.error('Failed to load accounts:', error)
      } finally {
        setLoading(false)
      }
    }

    loadAccounts()
  }, [])

  const handleCreateAccount = async (accountData: Omit<Account, 'id' | 'created_at'>) => {
    try {
      const newAccount = await electronAPI.invoke('account:create', accountData)
      setAccounts(prev => [...prev, newAccount])
    } catch (error) {
      console.error('Failed to create account:', error)
    }
  }

  return (
    <div className="account-manager">
      {/* UI implementation */}
    </div>
  )
}
```

### State Management (Zustand Pattern)

```typescript
// src/stores/accountStore.ts
import { create } from 'zustand'
import { electronAPI } from '../electron-api'

interface AccountState {
  accounts: Account[]
  currentAccount: Account | null
  isLoading: boolean
  error: string | null

  actions: {
    loadAccounts: () => Promise<void>
    createAccount: (data: AccountData) => Promise<void>
    selectAccount: (account: Account) => void
    refreshSession: () => Promise<boolean>
  }
}

export const useAccountStore = create<AccountState>((set, get) => ({
  accounts: [],
  currentAccount: null,
  isLoading: false,
  error: null,

  actions: {
    loadAccounts: async () => {
      set({ isLoading: true, error: null })
      try {
        const accounts = await electronAPI.invoke('account:list')
        set({ accounts, isLoading: false })
      } catch (error) {
        set({ error: error.message, isLoading: false })
      }
    },

    createAccount: async (data: AccountData) => {
      const newAccount = await electronAPI.invoke('account:create', data)
      set(prev => ({ accounts: [...prev.accounts, newAccount] }))
    },

    selectAccount: (account: Account) => {
      set({ currentAccount: account })
    },

    refreshSession: async () => {
      const account = get().currentAccount
      if (!account) return false

      const success = await electronAPI.invoke('session:refresh', account.id)
      return success
    }
  }
}))
```

### File System Access via IPC

```typescript
// preload.ts
contextBridge.exposeInMainWorld('electronAPI', {
  // File operations
  selectDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  selectFile: (filters?: FileFilter[]) => ipcRenderer.invoke('dialog:openFile', filters),

  // Directory operations
  readDirectory: (path: string) => ipcRenderer.invoke('fs:readDirectory', path),
  createDirectory: (path: string) => ipcRenderer.invoke('fs:createDirectory', path),

  // File operations
  readFile: (path: string) => ipcRenderer.invoke('fs:readFile', path),
  writeFile: (path: string, data: string) => ipcRenderer.invoke('fs:writeFile', path, data)
})
```

### Menu and Window Management

```typescript
// main.ts
import { Menu, BrowserWindow, app } from 'electron'

function createMenu() {
  const template: MenuItemConstructorOptions[] = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open XML',
          accelerator: 'CmdOrCtrl+O',
          click: () => {
            mainWindow.webContents.send('menu:open-xml')
          }
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1400,
    height: 850,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      sandbox: false
    }
  })

  return mainWindow
}
```

## 5. Development Workflow

### Hot Reload Setup

**Vite + Electron:**
```javascript
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import electron from 'vite-plugin-electron'

export default defineConfig({
  plugins: [
    react(),
    electron({
      main: {
        entry: 'electron/main.ts',
        onstart(options) {
          options.startup()
        }
      },
      preload: 'electron/preload.ts'
    })
  ]
})
```

### Debugging Configuration

**VS Code Launch Configuration:**
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Launch Renderer",
      "type": "chrome-inspector",
      "request": "launch",
      "url": "http://localhost:5173",
      "port": 5173
    },
    {
      "name": "Launch Electron",
      "type": "node-terminal",
      "request": "launch",
      "command": "npm run electron"
    }
  ]
}
```

### Testing Strategies

**Unit Testing (Vitest):**
```typescript
// tests/accountStore.test.ts
import { useAccountStore } from '../src/stores/accountStore'

test('should create account', async () => {
  const { createAccount } = useAccountStore.getState()

  await createAccount({
    name: 'test-account',
    email: 'test@example.com'
  })

  const accounts = useAccountStore.getState().accounts
  expect(accounts).toHaveLength(1)
  expect(accounts[0].name).toBe('test-account')
})
```

**Integration Tests:**
```typescript
// tests/integration/account-creation.test.ts
import { test, expect } from '@playwright/test'

test.describe('Account Creation Integration', () => {
  test('should create account through UI', async ({ page }) => {
    await page.goto('http://localhost:5173/accounts')

    await page.fill('[data-testid="account-name"]', 'test-account')
    await page.fill('[data-testid="account-email"]', 'test@example.com')
    await page.click('[data-testid="create-account"]')

    await expect(page.locator('[data-testid="account-list"]')).toContainText('test-account')
  })
})
```

### Build and Packaging Processes

**Package Scripts:**
```json
{
  "scripts": {
    "build": "vite build",
    "electron:build": "vite build && electron-builder",
    "electron:dist": "npm run electron:build",
    "electron:pack": "electron-builder --dir",
    "electron:publish": "electron-builder --publish"
  }
}
```

**electron-builder Configuration:**
```json
{
  "appId": "com.suno-account-manager",
  "productName": "Suno Account Manager",
  "directories": {
    "output": "dist"
  },
  "files": [
    "dist/**/*",
    "electron/**/*"
  ],
  "win": {
    "target": "nsis",
    "icon": "build/icon.ico"
  },
  "mac": {
    "target": "dmg",
    "icon": "build/icon.icns"
  },
  "linux": {
    "target": "AppImage",
    "icon": "build/icon.png"
  }
}
```

## Migration Recommendations for Suno Account Manager

### 1. Migration Strategy

**Phase 1: Core Infrastructure**
- Set up TypeScript + React + Electron project structure
- Implement Python backend with stdin/stdout communication
- Create IPC channel definitions and type interfaces
- Build basic authentication system

**Phase 2: Feature Migration**
- Account management (CRUD operations)
- Song creation with queue system
- Download functionality
- History tracking

**Phase 3: Optimization**
- Hot reload for development
- Performance optimization
- Testing integration
- Packaging and distribution

### 2. Architecture Mapping

| Python Component | TypeScript/React Equivalent |
|------------------|-----------------------------|
| `AccountManager` | `useAccountStore` Zustand store |
| `SessionManager` | Backend Python service + IPC calls |
| `BatchSongCreator` | Backend Python service + progress events |
| `QueueManager` | Backend Python service + real-time updates |
| `CustomTkinter UI` | React components + Electron window |

### 3. Key Technical Decisions

**IPC Communication:**
- Use `ipcRenderer.invoke()` + `ipcMain.handle()` for synchronous operations
- Use event-based communication for real-time progress updates
- Implement proper error handling and timeouts

**State Management:**
- Zustand for client-side state (accounts, UI state)
- Backend state managed by Python process
- Real-time synchronization via IPC events

**Performance Considerations:**
- Process-intensive operations (browser automation) in Python backend
- Minimal IPC payload sizes
- Proper cleanup of child processes

### 4. Development Best Practices

**Code Organization:**
- Separate frontend and backend concerns
- Shared TypeScript interfaces across processes
- Proper error boundaries in React components

**Security:**
- Sanitize all IPC communications
- Validate all inputs from renderer process
- Use proper context isolation

**Testing:**
- Unit tests for frontend components and utilities
- Integration tests for IPC communication
- End-to-end tests for complete workflows

## Unresolved Questions

1. **Hot reload integration** - Best way to hot reload Python backend during development
2. **Error handling strategy** - Comprehensive error handling across process boundaries
3. **Performance optimization** - Memory usage with multiple Chrome profiles in backend
4. **Windows-specific requirements** - Handling Windows-specific browser automation