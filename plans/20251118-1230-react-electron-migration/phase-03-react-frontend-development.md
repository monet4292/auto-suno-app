# Phase 3: React Frontend Development

## Context
**Parent Plan:** [plan.md](plan.md)
**Dependencies:** [Phase 1](phase-01-python-communication-layer.md), [Phase 2](phase-02-electron-typescript-setup.md)
**Duration:** 2-3 weeks
**Priority:** High

## Overview

Develop React frontend with TypeScript, mirroring all CustomTkinter functionality while implementing modern UI patterns, state management with Zustand, and real-time progress updates.

## Key Insights

- Component architecture should directly map to CustomTkinter panels for familiarity
- Zustand provides excellent type-safe state management for desktop applications
- Real-time updates require careful state synchronization between Python backend and React
- Tailwind CSS with Headless UI provides modern, accessible components
- Component reusability is crucial for consistent UI patterns

## Requirements

### Functional Requirements
1. **6 Main Panels:** Account, Create Music, Multiple Songs, Download, History, Song Creation History
2. **Component Architecture:** Atomic design pattern with reusable components
3. **State Management:** Zustand for global state, local state for component-specific data
4. **Real-time Updates:** Live progress tracking for queue and download operations
5. **Form Handling:** Input validation and submission with error handling
6. **File Operations:** XML file upload, download directory selection, file browsing

### Technical Requirements
1. **Type Safety:** Full TypeScript coverage for all components and data
2. **Performance:** Optimized rendering for long-running operations
3. **Accessibility:** Keyboard navigation and screen reader support
4. **Responsive Design:** Adaptable layouts for different window sizes
5. **Error Boundaries:** Graceful error handling and recovery

## Architecture

### Component Hierarchy

```
App (Root)
├── Layout
│   ├── Header (App title, window controls)
│   ├── Sidebar (Navigation)
│   ├── Main Content Area
│   └── Status Bar (Progress indicators)
└── Panels
    ├── AccountPanel
    │   ├── AccountList
    │   ├── AccountForm
    │   └── AccountCard
    ├── CreateMusicPanel
    │   ├── PromptForm
    │   ├── AdvancedOptions
    │   └── PreviewWidget
    ├── MultipleSongsPanel
    │   ├── QueueList
    │   ├── QueueForm
    │   ├── ProgressDisplay
    │   └── BatchControls
    ├── DownloadPanel
    │   ├── DownloadForm
    │   ├── ProgressTable
    │   └── FileSelector
    ├── HistoryPanel
    │   ├── HistoryTable
    │   ├── Filters
    │   └── Statistics
    └── SongCreationHistoryPanel
        ├── CreationTable
        ├── SearchFilters
        └── ExportControls
```

### State Management Architecture

```typescript
// Global State Structure
interface AppState {
  // Navigation and UI state
  activePanel: PanelType;
  sidebarCollapsed: boolean;
  theme: 'dark' | 'light';

  // Application state
  accounts: Account[];
  queues: QueueEntry[];
  downloadProgress: DownloadProgress[];
  creationProgress: CreationProgress[];

  // Real-time state
  isBackendConnected: boolean;
  lastError: string | null;
  notifications: Notification[];
}

// Zustand Store Structure
const useAppStore = create<AppState>((set, get) => ({
  // State implementation
}));

// Specialized stores
const useAccountStore = create<AccountState>((set) => ({
  // Account-specific state
}));

const useQueueStore = create<QueueState>((set) => ({
  // Queue-specific state
}));
```

## Related Code Files

### Files to Create
- `src/App.tsx` - Main application component
- `src/components/Layout/` - Layout components
- `src/components/Panels/` - Panel components
- `src/components/Common/` - Reusable components
- `src/stores/` - Zustand stores
- `src/types/` - TypeScript interfaces
- `src/hooks/` - Custom React hooks
- `src/utils/` - Utility functions

### Files to Modify
- `src/index.css` - Global styles and Tailwind imports
- `index.html` - HTML entry point
- `vite.config.ts` - Development configuration

## Implementation Steps

### Step 1: Foundation Setup (Day 1-2)
1. **Create directory structure**
   ```bash
   mkdir -p src/{components/{Layout,Panels,Common},stores,types,hooks,utils}
   mkdir -p src/components/Layout/{Header,Sidebar,Status}
   mkdir -p src/components/Panels/{Account,Create,Queue,Download,History}
   mkdir -p src/components/Common/{Form,Table,Progress,Modal}
   ```

2. **Setup Tailwind CSS**
   ```css
   /* src/index.css */
   @tailwind base;
   @tailwind components;
   @tailwind utilities;

   :root {
     --color-primary: #3b82f6;
     --color-secondary: #64748b;
     --color-success: #10b981;
     --color-warning: #f59e0b;
     --color-error: #ef4444;
   }

   body {
     @apply bg-gray-900 text-gray-100;
     font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
   }

   /* Custom scrollbar styling */
   ::-webkit-scrollbar {
     @apply w-2 h-2;
   }

   ::-webkit-scrollbar-track {
     @apply bg-gray-800;
   }

   ::-webkit-scrollbar-thumb {
     @apply bg-gray-600 rounded-full;
   }

   ::-webkit-scrollbar-thumb:hover {
     @apply bg-gray-500;
   }
   ```

3. **Create TypeScript types**
   ```typescript
   // src/types/index.ts
   export interface Account {
     name: string;
     email: string;
     created_at: string;
     last_used?: string;
     status: 'active' | 'inactive';
   }

   export interface QueueEntry {
     id: string;
     account_name: string;
     total_songs: number;
     songs_per_batch: number;
     prompts_range: [number, number];
     status: 'pending' | 'in_progress' | 'completed' | 'failed';
     created_at: string;
     completed_count: number;
   }

   export interface SongClip {
     id: string;
     title: string;
     audio_url?: string;
     image_url?: string;
     tags: string;
     created_at?: string;
     duration?: number;
   }

   export interface SunoPrompt {
     title: string;
     lyrics: string;
     style: string;
   }

   export interface AdvancedOptions {
     weirdness: number;
     creativity: number;
     clarity: number;
     model: string;
     vocal_gender: 'auto' | 'male' | 'female';
     lyrics_mode: 'auto' | 'manual';
     style_influence: number;
     persona?: string;
     exclude_styles?: string[];
   }

   export type PanelType = 'account' | 'create' | 'queue' | 'download' | 'history' | 'creation-history';
   ```

### Step 2: State Management Setup (Day 3-4)
1. **Create main app store**
   ```typescript
   // src/stores/appStore.ts
   import { create } from 'zustand';
   import { subscribeWithSelector } from 'zustand/middleware';
   import { PanelType, Account, QueueEntry } from '../types';

   interface AppState {
     // Navigation
     activePanel: PanelType;
     sidebarCollapsed: boolean;

     // Backend connection
     isBackendConnected: boolean;
     lastError: string | null;

     // Data
     accounts: Account[];
     queues: QueueEntry[];

     // Actions
     setActivePanel: (panel: PanelType) => void;
     toggleSidebar: () => void;
     setBackendConnected: (connected: boolean) => void;
     setError: (error: string | null) => void;
     clearError: () => void;
     setAccounts: (accounts: Account[]) => void;
     setQueues: (queues: QueueEntry[]) => void;
   }

   export const useAppStore = create<AppState>()(
     subscribeWithSelector((set, get) => ({
       // Navigation state
       activePanel: 'account' as PanelType,
       sidebarCollapsed: false,

       // Backend connection
       isBackendConnected: false,
       lastError: null,

       // Data
       accounts: [],
       queues: [],

       // Actions
       setActivePanel: (panel) => set({ activePanel: panel }),
       toggleSidebar: () => set((state) => ({
         sidebarCollapsed: !state.sidebarCollapsed
       })),
       setBackendConnected: (connected) => set({
         isBackendConnected: connected,
         lastError: connected ? null : get().lastError
       }),
       setError: (error) => set({ lastError: error }),
       clearError: () => set({ lastError: null }),
       setAccounts: (accounts) => set({ accounts }),
       setQueues: (queues) => set({ queues }),
     }))
   )
   );
   ```

2. **Create account store**
   ```typescript
   // src/stores/accountStore.ts
   import { create } from 'zustand';
   import { Account } from '../types';

   interface AccountStore {
     accounts: Account[];
     loading: boolean;
     error: string | null;

     // Actions
     loadAccounts: () => Promise<void>;
     createAccount: (account: Omit<Account, 'created_at' | 'status'>) => Promise<void>;
     updateAccount: (name: string, updates: Partial<Account>) => Promise<void>;
     deleteAccount: (name: string) => Promise<void>;
   }

   export const useAccountStore = create<AccountStore>((set, get) => ({
     accounts: [],
     loading: false,
     error: null,

     loadAccounts: async () => {
       set({ loading: true, error: null });
       try {
         const accounts = await window.electronAPI.sendCommand({
           type: 'GET_ACCOUNTS',
           payload: {}
         });
         set({ accounts: accounts.data || [], loading: false });
       } catch (error) {
         set({ error: error.message, loading: false });
       }
     },

     createAccount: async (accountData) => {
       set({ loading: true, error: null });
       try {
         const response = await window.electronAPI.sendCommand({
           type: 'CREATE_ACCOUNT',
           payload: accountData
         });

         if (response.success) {
           const newAccount = response.data;
           set((state) => ({
             accounts: [...state.accounts, newAccount],
             loading: false
           }));
         } else {
           set({ error: response.error, loading: false });
         }
       } catch (error) {
         set({ error: error.message, loading: false });
       }
     },

     updateAccount: async (name, updates) => {
       // Implementation for account updates
     },

     deleteAccount: async (name) => {
       // Implementation for account deletion
     }
   }));
   ```

3. **Create queue store with real-time updates**
   ```typescript
   // src/stores/queueStore.ts
   import { create } from 'zustand';
   import { QueueEntry } from '../types';

   interface QueueStore {
     queues: QueueEntry[];
     activeOperations: Map<string, any>;
     progressData: Map<string, any>;

     // Actions
     loadQueues: () => Promise<void>;
     createQueue: (queueData: any) => Promise<void>;
     startQueue: (queueId: string) => Promise<void>;
     updateQueueProgress: (progress: any) => void;
     stopQueue: (queueId: string) => Promise<void>;
   }

   export const useQueueStore = create<QueueStore>((set, get) => ({
     queues: [],
     activeOperations: new Map(),
     progressData: new Map(),

     loadQueues: async () => {
       try {
         const response = await window.electronAPI.sendCommand({
           type: 'GET_QUEUES',
           payload: {}
         });
         set({ queues: response.data || [] });
       } catch (error) {
         console.error('Failed to load queues:', error);
       }
     },

     createQueue: async (queueData) => {
       try {
         const response = await window.electronAPI.sendCommand({
           type: 'CREATE_QUEUE',
           payload: queueData
         });

         if (response.success) {
           set((state) => ({
             queues: [...state.queues, response.data]
           }));
         }
       } catch (error) {
         console.error('Failed to create queue:', error);
       }
     },

     startQueue: async (queueId) => {
       try {
         const response = await window.electronAPI.sendCommand({
           type: 'START_QUEUE',
           payload: { queue_ids: [queueId] }
         });

         if (response.success) {
           set((state) => ({
             activeOperations: new Map(state.activeOperations).set(queueId, response.data),
             queues: state.queues.map(q =>
               q.id === queueId ? { ...q, status: 'in_progress' } : q
             )
           }));
         }
       } catch (error) {
         console.error('Failed to start queue:', error);
       }
     },

     updateQueueProgress: (progress) => {
       const { operation_id, ...progressData } = progress.payload;
       set((state) => {
         const newProgressData = new Map(state.progressData);
         newProgressData.set(operation_id, progressData);
         return { progressData: newProgressData };
       });
     },

     stopQueue: async (queueId) => {
       // Implementation for stopping queue
     }
   }));

   // Set up progress update listener
   if (typeof window !== 'undefined') {
     window.electronAPI.onProgressUpdate((progress) => {
       useQueueStore.getState().updateQueueProgress(progress);
     });
   }
   ```

### Step 3: Layout Components (Day 5-6)
1. **Create main layout component**
   ```typescript
   // src/components/Layout/MainLayout.tsx
   import React from 'react';
   import { Header } from './Header';
   import { Sidebar } from './Sidebar';
   import { StatusBar } from './StatusBar';
   import { useAppStore } from '../../stores/appStore';

   interface MainLayoutProps {
     children: React.ReactNode;
   }

   export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
     const { sidebarCollapsed } = useAppStore();

     return (
       <div className="flex flex-col h-screen bg-gray-900 text-gray-100">
         <Header />

         <div className="flex flex-1 overflow-hidden">
           <Sidebar />

           <main className={`flex-1 overflow-auto transition-all duration-200 ${
             sidebarCollapsed ? 'ml-16' : 'ml-64'
           }`}>
             <div className="p-6">
               {children}
             </div>
           </main>
         </div>

         <StatusBar />
       </div>
     );
   };
   ```

2. **Create sidebar navigation**
   ```typescript
   // src/components/Layout/Sidebar.tsx
   import React from 'react';
   import { useAppStore } from '../../stores/appStore';
   import { PanelType } from '../../types';

   const navigationItems = [
     { id: 'account' as PanelType, label: 'Tài khoản', icon: '👤' },
     { id: 'create' as PanelType, label: 'Tạo nhạc', icon: '🎵' },
     { id: 'queue' as PanelType, label: 'Tạo nhiều bài', icon: '📝' },
     { id: 'download' as PanelType, label: 'Download', icon: '📥' },
     { id: 'history' as PanelType, label: 'Lịch sử', icon: '📜' },
     { id: 'creation-history' as PanelType, label: 'Lịch sử tạo', icon: '🎼' },
   ];

   export const Sidebar: React.FC = () => {
     const { activePanel, setActivePanel, sidebarCollapsed, toggleSidebar } = useAppStore();

     return (
       <div className={`fixed left-0 top-0 h-full bg-gray-800 border-r border-gray-700 transition-all duration-200 z-10 ${
         sidebarCollapsed ? 'w-16' : 'w-64'
       }`}>
         <div className="flex flex-col h-full">
           {/* Logo/Brand */}
           <div className="p-4 border-b border-gray-700">
             <div className="flex items-center">
               <span className="text-2xl">🎵</span>
               {!sidebarCollapsed && (
                 <span className="ml-2 font-bold text-lg">Suno Manager</span>
               )}
             </div>
           </div>

           {/* Navigation */}
           <nav className="flex-1 p-2">
             {navigationItems.map((item) => (
               <button
                 key={item.id}
                 onClick={() => setActivePanel(item.id)}
                 className={`w-full flex items-center px-3 py-2 mb-1 rounded-lg transition-colors ${
                   activePanel === item.id
                     ? 'bg-blue-600 text-white'
                     : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                 }`}
               >
                 <span className="text-xl">{item.icon}</span>
                 {!sidebarCollapsed && (
                   <span className="ml-3 text-sm">{item.label}</span>
                 )}
               </button>
             ))}
           </nav>

           {/* Collapse button */}
           <div className="p-2 border-t border-gray-700">
             <button
               onClick={toggleSidebar}
               className="w-full flex items-center justify-center px-3 py-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-700 transition-colors"
             >
               <span className="text-xl">{sidebarCollapsed ? '→' : '←'}</span>
               {!sidebarCollapsed && (
                 <span className="ml-2 text-sm">Thu gọn</span>
               )}
             </button>
           </div>
         </div>
       </div>
     );
   };
   ```

3. **Create status bar with progress indicators**
   ```typescript
   // src/components/Layout/StatusBar.tsx
   import React from 'react';
   import { useAppStore } from '../../stores/appStore';
   import { useQueueStore } from '../../stores/queueStore';

   export const StatusBar: React.FC = () => {
     const { isBackendConnected, lastError } = useAppStore();
     const { queues } = useQueueStore();

     const activeQueues = queues.filter(q => q.status === 'in_progress');
     const totalProgress = queues.reduce((sum, q) => sum + q.completed_count, 0);
     const totalSongs = queues.reduce((sum, q) => sum + q.total_songs, 0);

     return (
       <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-t border-gray-700 text-sm">
         <div className="flex items-center space-x-4">
           {/* Backend connection status */}
           <div className="flex items-center space-x-2">
             <div className={`w-2 h-2 rounded-full ${
               isBackendConnected ? 'bg-green-500' : 'bg-red-500'
             }`} />
             <span className="text-gray-400">
               {isBackendConnected ? 'Đã kết nối' : 'Mất kết nối'}
             </span>
           </div>

           {/* Queue progress */}
           {activeQueues.length > 0 && (
             <div className="flex items-center space-x-2">
               <span className="text-gray-400">
                 Queue: {totalProgress}/{totalSongs} ({totalSongs > 0 ? Math.round((totalProgress / totalSongs) * 100) : 0}%)
               </span>
             </div>
           )}
         </div>

         {/* Error display */}
         {lastError && (
           <div className="text-red-400">
             Lỗi: {lastError}
           </div>
         )}

         {/* Time */}
         <div className="text-gray-500">
           {new Date().toLocaleTimeString()}
         </div>
       </div>
     );
   };
   ```

### Step 4: Panel Components (Day 7-10)
1. **Create Account Panel**
   ```typescript
   // src/components/Panels/AccountPanel/AccountPanel.tsx
   import React, { useEffect } from 'react';
   import { useAccountStore } from '../../../stores/accountStore';
   import { AccountForm } from './AccountForm';
   import { AccountList } from './AccountList';

   export const AccountPanel: React.FC = () => {
     const { accounts, loading, error, loadAccounts } = useAccountStore();

     useEffect(() => {
       loadAccounts();
     }, [loadAccounts]);

     return (
       <div className="space-y-6">
         {/* Header */}
         <div className="flex justify-between items-center">
           <h1 className="text-2xl font-bold">Quản lý tài khoản</h1>
           <AccountForm mode="create" />
         </div>

         {/* Error display */}
         {error && (
           <div className="bg-red-900/50 border border-red-500 text-red-200 px-4 py-2 rounded">
             {error}
           </div>
         )}

         {/* Loading state */}
         {loading && (
           <div className="text-center py-8 text-gray-400">
             Đang tải tài khoản...
           </div>
         )}

         {/* Account list */}
         {!loading && (
           <AccountList accounts={accounts} />
         )}
       </div>
     );
   };
   ```

2. **Create Multiple Songs Panel (Queue Panel)**
   ```typescript
   // src/components/Panels/QueuePanel/QueuePanel.tsx
   import React, { useEffect } from 'react';
   import { useQueueStore } from '../../../stores/queueStore';
   import { QueueForm } from './QueueForm';
   import { QueueList } from './QueueList';
   import { ProgressDisplay } from './ProgressDisplay';

   export const QueuePanel: React.FC = () => {
     const { queues, activeOperations, loadQueues } = useQueueStore();

     useEffect(() => {
       loadQueues();
     }, [loadQueues]);

     return (
       <div className="space-y-6">
         {/* Header */}
         <div className="flex justify-between items-center">
           <h1 className="text-2xl font-bold">Quản lý hàng đợi</h1>
           <QueueForm />
         </div>

         {/* Active operations progress */}
         {activeOperations.size > 0 && (
           <div className="bg-gray-800 rounded-lg p-4">
             <h2 className="text-lg font-semibold mb-4">Đang thực thi</h2>
             <ProgressDisplay operations={Array.from(activeOperations.values())} />
           </div>
         )}

         {/* Queue list */}
         <QueueList queues={queues} />
       </div>
     );
   };
   ```

### Step 5: Common Components (Day 11-13)
1. **Create form components**
   ```typescript
   // src/components/Common/Form/FormInput.tsx
   import React from 'react';

   interface FormInputProps {
     label: string;
     type?: 'text' | 'email' | 'password' | 'number';
     value: string | number;
     onChange: (value: string | number) => void;
     placeholder?: string;
     error?: string;
     required?: boolean;
     disabled?: boolean;
   }

   export const FormInput: React.FC<FormInputProps> = ({
     label,
     type = 'text',
     value,
     onChange,
     placeholder,
     error,
     required = false,
     disabled = false
   }) => {
     const inputId = `input-${label.replace(/\s+/g, '-').toLowerCase()}`;

     return (
       <div className="space-y-1">
         <label htmlFor={inputId} className="block text-sm font-medium text-gray-300">
           {label}
           {required && <span className="text-red-400 ml-1">*</span>}
         </label>

         <input
           id={inputId}
           type={type}
           value={value}
           onChange={(e) => onChange(type === 'number' ? Number(e.target.value) : e.target.value)}
           placeholder={placeholder}
           disabled={disabled}
           className={`w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-gray-100 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed ${
             error ? 'border-red-500' : ''
           }`}
         />

         {error && (
           <p className="text-sm text-red-400">{error}</p>
         )}
       </div>
     );
   };
   ```

2. **Create table component**
   ```typescript
   // src/components/Common/Table/Table.tsx
   import React from 'react';

   interface TableColumn {
     key: string;
     header: string;
     render?: (value: any, row: any) => React.ReactNode;
   }

   interface TableProps {
     columns: TableColumn[];
     data: any[];
     emptyMessage?: string;
     className?: string;
   }

   export const Table: React.FC<TableProps> = ({
     columns,
     data,
     emptyMessage = 'Không có dữ liệu',
     className = ''
   }) => {
     if (data.length === 0) {
       return (
         <div className={`text-center py-8 text-gray-500 ${className}`}>
           {emptyMessage}
         </div>
       );
     }

     return (
       <div className={`overflow-x-auto ${className}`}>
         <table className="min-w-full divide-y divide-gray-700">
           <thead className="bg-gray-800">
             <tr>
               {columns.map((column) => (
                 <th
                   key={column.key}
                   className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider"
                 >
                   {column.header}
                 </th>
               ))}
             </tr>
           </thead>
           <tbody className="divide-y divide-gray-700">
             {data.map((row, rowIndex) => (
               <tr key={rowIndex} className="hover:bg-gray-800">
                 {columns.map((column) => (
                   <td
                     key={column.key}
                     className="px-6 py-4 whitespace-nowrap text-sm text-gray-300"
                   >
                     {column.render ? column.render(row[column.key], row) : row[column.key]}
                   </td>
                 ))}
               </tr>
             ))}
           </tbody>
         </table>
       </div>
     );
   };
   ```

### Step 6: Integration and Testing (Day 14-15)
1. **Create main app component**
   ```typescript
   // src/App.tsx
   import React, { useEffect } from 'react';
   import { MainLayout } from './components/Layout/MainLayout';
   import { AccountPanel } from './components/Panels/AccountPanel/AccountPanel';
   import { CreateMusicPanel } from './components/Panels/CreateMusicPanel/CreateMusicPanel';
   import { QueuePanel } from './components/Panels/QueuePanel/QueuePanel';
   import { DownloadPanel } from './components/Panels/DownloadPanel/DownloadPanel';
   import { HistoryPanel } from './components/Panels/HistoryPanel/HistoryPanel';
   import { SongCreationHistoryPanel } from './components/Panels/SongCreationHistoryPanel/SongCreationHistoryPanel';
   import { useAppStore } from './stores/appStore';

   const panelComponents = {
     account: AccountPanel,
     create: CreateMusicPanel,
     queue: QueuePanel,
     download: DownloadPanel,
     history: HistoryPanel,
     'creation-history': SongCreationHistoryPanel,
   };

   export const App: React.FC = () => {
     const { activePanel, isBackendConnected, setBackendConnected } = useAppStore();

     useEffect(() => {
       // Test backend connection
       const testConnection = async () => {
         try {
           await window.electronAPI.sendCommand({
             type: 'GET_ACCOUNTS',
             payload: {}
           });
           setBackendConnected(true);
         } catch (error) {
           console.error('Backend connection failed:', error);
           setBackendConnected(false);
         }
       };

       testConnection();

       // Set up backend listeners
       window.electronAPI.onBackendResponse((response) => {
         setBackendConnected(true);
       });

       window.electronAPI.onErrorUpdate((error) => {
         console.error('Backend error:', error);
         setBackendConnected(false);
       });
     }, [setBackendConnected]);

     const ActivePanelComponent = panelComponents[activePanel];

     return (
       <MainLayout>
         <div className="h-full">
           {isBackendConnected ? (
             <ActivePanelComponent />
           ) : (
             <div className="flex items-center justify-center h-full">
               <div className="text-center space-y-4">
                 <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                 <p className="text-gray-400">Đang kết nối với backend...</p>
                 <button
                   onClick={() => window.location.reload()}
                   className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                 >
                   Thử lại
                 </button>
               </div>
             </div>
           )}
         </div>
       </MainLayout>
     );
   };
   ```

2. **Create index entry point**
   ```typescript
   // src/main.tsx
   import React from 'react';
   import ReactDOM from 'react-dom/client';
   import { App } from './App';
   import './index.css';

   const root = ReactDOM.createRoot(
     document.getElementById('root') as HTMLElement
   );

   root.render(
     <React.StrictMode>
       <App />
     </React.StrictMode>
   );
   ```

## Todo List

- [ ] Create component directory structure
- [ ] Setup Tailwind CSS configuration
- [ ] Define TypeScript interfaces and types
- [ ] Implement Zustand stores for state management
- [ ] Create layout components (Header, Sidebar, Status)
- [ ] Implement Account Panel
- [ ] Implement Queue Panel with real-time updates
- [ ] Implement Create Music Panel
- [ ] Implement Download Panel
- [ ] Implement History Panels
- [ ] Create common components (Form, Table, Modal)
- [ ] Set up React app entry point
- [ ] Test component functionality
- [ ] Test real-time progress updates
- [ ] Test error handling and recovery

## Success Criteria

- ✅ All 6 CustomTkinter panels reproduced with React components
- ✅ Real-time progress updates working for queue and download operations
- ✅ State management working correctly with Zustand
- ✅ TypeScript coverage for all components and data
- ✅ Responsive design adapting to window resizing
- ✅ Error boundaries and error handling implemented
- ✅ Component reusability and maintainability
- ✅ Performance optimization for long-running operations

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **State synchronization** | Medium | High | Careful store design and testing |
| **Real-time update performance** | Low | Medium | Efficient event handling and state batching |
| **Component complexity** | Medium | Medium | Atomic design pattern and reusable components |
| **TypeScript compilation issues** | Low | Low | Strict configuration and incremental development |

## Security Considerations

1. **Input Validation:** Validate all form inputs and API responses
2. **XSS Prevention:** Proper sanitization of user-generated content
3. **CSRF Protection:** Implement request validation if needed
4. **Error Information:** Avoid exposing sensitive data in error messages

## Next Steps

1. **Phase 4 Integration:** End-to-end testing and optimization
2. **Performance Testing:** Benchmark against CustomTkinter
3. **User Acceptance Testing:** User feedback and iteration
4. **Migration Tools:** Data migration from JSON files
5. **Production Build:** Optimize build pipeline and package application

---

*This phase creates a modern, maintainable React frontend that fully replicates CustomTkinter functionality while providing enhanced user experience and developer productivity.*