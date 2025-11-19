# Electron + React + TypeScript Architecture Research

## 1. Electron Architecture Patterns

### IPC Communication Best Practices:
- Use `ipcRenderer.invoke()` + `ipcMain.handle()` for two-way communication
- Use `webContents.send()` for main-to-renderer communication
- Secure preload scripts with `contextBridge.exposeInMainWorld()`
- Namespace channel naming: `account:create`, `songs:create-batch`

### Security Considerations:
- Don't expose entire Electron APIs
- Limit renderer process permissions
- Avoid synchronous methods for performance

## 2. TypeScript Integration

### Configuration Setup:
- TypeScript strict mode for type safety
- Shared types between main and renderer processes
- Interface definitions for Account, SongPrompt, AdvancedOptions

### Build System:
- Vite for React hot reload and optimization
- TypeScript compiler for Electron main process
- Shared type definitions package

## 3. Python Backend Communication

### stdin/stdout JSON Protocol:
```typescript
interface Command<T = any> {
  id: string
  type: string
  payload?: T
  timestamp: number
}

interface Response<T = any> {
  id: string
  type: string
  success: boolean
  data?: T
  error?: string
  timestamp: number
}
```

### Real-time Progress Callbacks:
- Event-based progress updates from Python backend
- Operation ID tracking for async operations
- Timeout and retry mechanism

## 4. React + Electron Integration

### Component Architecture:
- React components with Zustand state management
- File system access via IPC channels
- Menu and window management with Electron APIs

### Development Workflow:
- Vite for hot reload and build optimization
- VS Code debugging configuration
- Testing strategy: unit + integration + e2e tests

## 5. Migration Recommendations

### Component Mapping:
| Python Component | TypeScript/React Equivalent |
|------------------|-----------------------------|
| AccountManager | useAccountStore Zustand |
| SessionManager | Python backend service + IPC |
| BatchSongCreator | Python backend service + progress events |
| QueueManager | Python backend service + real-time updates |
| CustomTkinter UI | React components + Electron |

### Migration Strategy:
1. **Phase 1**: Core infrastructure (IPC, Python backend, type interfaces)
2. **Phase 2**: Feature migration (account, creation, download, history)
3. **Phase 3**: Optimization (hot reload, testing, packaging)

## Key Technical Decisions:
- Keep browser automation in Python backend
- Zustand for frontend state, Python for backend state
- Process-intensive operations in Python
- TypeScript strict mode for type safety