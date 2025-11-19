# Phase 2: React Frontend Integration

**Phase ID:** 251119-1021-P2
**Duration:** 5 days
**Priority:** Critical
**Dependencies:** Phase 1 - Foundation Setup (Complete)

## Overview

Implement React frontend with TypeScript, state management using Zustand, and integration with the Electron main process and Python backend. This phase focuses on creating a modern, responsive UI that communicates securely with the backend through IPC.

## Objectives

1. **React Application Structure**: Set up component-based architecture following Clean Architecture principles
2. **State Management**: Implement Zustand stores for application state
3. **Type Safety**: Create comprehensive TypeScript interfaces
4. **UI Components**: Build reusable components following design system
5. **Backend Integration**: Establish robust communication with Python backend
6. **Real-time Updates**: Implement progress tracking and live updates

## Architecture Overview

```
React Frontend Architecture
┌─────────────────────────────────────────────────────────┐
│                    App.tsx (Root)                         │
├─────────────────────────────────────────────────────────┤
│                Global State (Zustand)                     │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  useAccountStore     │  useSongStore                │  │
│  │  useDownloadStore   │  useUIStore                   │  │
│  │  useSettingsStore   │  useProgressStore             │  │
│  └─────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                   Component Layers                        │
│  ┌─────────────────────────────────────────────────────┐  │
│  │             Layout Components                         │  │
│  │  • MainLayout, Sidebar, Header, Footer             │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │            Feature Components                        │  │
│  │  • AccountManager, SongCreator, DownloadManager    │  │
│  │  • HistoryView, SettingsView                       │  │
│  └─────────────────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │             UI Components                            │  │
│  │  • Button, Input, Modal, Progress, Table          │  │
│  └─────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│                  Integration Layer                       │
│  ┌─────────────────────────────────────────────────────┐  │
│  │              Hooks and Utilities                      │  │
│  │  • useElectronAPI, useBackendCommand,              │  │
│  │  • useRealtimeUpdates, useErrorHandler              │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Daily Breakdown

### Day 1: Application Structure and Type Definitions

#### Morning (4 hours)
**Task: Create comprehensive TypeScript type definitions**

```typescript
// src/types/shared/account.ts
export interface Account {
  id: string;
  name: string;
  email: string;
  created_at: string;
  last_used?: string;
  status: 'active' | 'inactive' | 'expired';
  profile_path?: string;
}

export interface AccountFormData {
  name: string;
  email: string;
}

export interface AccountValidationResult {
  isValid: boolean;
  errors: string[];
}

// src/types/shared/song.ts
export interface SongPrompt {
  title: string;
  lyrics: string;
  style: string;
  advanced_options?: AdvancedOptions;
}

export interface AdvancedOptions {
  weirdness: number;
  creativity: number;
  clarity: number;
  model: 'v4' | 'v3.5' | 'v3';
  vocal_gender: 'auto' | 'male' | 'female';
  lyrics_mode: 'auto' | 'manual';
  style_influence: number;
  persona_name?: string;
}

export interface SongClip {
  id: string;
  title: string;
  audio_url?: string;
  image_url?: string;
  created_at?: string;
  duration?: string;
  tags: string;
  metadata?: {
    [key: string]: any;
  };
}

export interface SongCreationRequest {
  prompts: SongPrompt[];
  account_name: string;
  batch_size: number;
  options: {
    auto_submit: boolean;
    human_delays: boolean;
    keep_browser_open: boolean;
  };
}

// src/types/shared/download.ts
export interface DownloadTask {
  id: string;
  account_name: string;
  clip_ids: string[];
  output_dir: string;
  options: DownloadOptions;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

export interface DownloadOptions {
  include_metadata: boolean;
  include_thumbnails: boolean;
  overwrite_existing: boolean;
  parallel_downloads: number;
}

// src/types/shared/queue.ts
export interface QueueEntry {
  id: string;
  account_name: string;
  total_songs: number;
  songs_per_batch: number;
  prompts_range: [number, number];
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  completed_count: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface QueueExecution {
  id: string;
  selected_queues: string[];
  status: 'preparing' | 'running' | 'completed' | 'failed';
  current_queue?: string;
  progress: {
    total_songs: number;
    completed_songs: number;
    current_queue_progress: number;
  };
  started_at: string;
  completed_at?: string;
}
```

```typescript
// src/types/api/commands.ts
export type CommandType =
  | 'ACCOUNT_LIST'
  | 'ACCOUNT_CREATE'
  | 'ACCOUNT_UPDATE'
  | 'ACCOUNT_DELETE'
  | 'SESSION_GET_TOKEN'
  | 'SESSION_REFRESH'
  | 'SONGS_CREATE_BATCH'
  | 'DOWNLOAD_START'
  | 'DOWNLOAD_PAUSE'
  | 'DOWNLOAD_RESUME'
  | 'QUEUE_LIST'
  | 'QUEUE_CREATE'
  | 'QUEUE_START'
  | 'QUEUE_PAUSE'
  | 'QUEUE_DELETE'
  | 'HISTORY_GET_SONGS'
  | 'HISTORY_GET_DOWNLOADS'
  | 'SETTINGS_GET'
  | 'SETTINGS_UPDATE'
  | 'SYSTEM_PING';

export interface Command<T = any> {
  id: string;
  type: CommandType;
  payload?: T;
  timestamp: number;
}

// src/types/api/responses.ts
export interface Response<T = any> {
  id: string;
  type: CommandType;
  success: boolean;
  data?: T;
  error?: string;
  timestamp: number;
}

export interface ProgressEvent {
  type: 'progress';
  operation_id: string;
  operation_type: string;
  progress: number;
  message: string;
  data?: any;
  timestamp: number;
}

export interface ErrorEvent {
  type: 'error';
  error_type: string;
  message: string;
  details?: any;
  timestamp: number;
}
```

#### Afternoon (4 hours)
**Task: Set up Zustand stores for state management**

```typescript
// src/stores/accountStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { Account, AccountFormData } from '@/types/shared/account';
import { electronAPI } from '@/types/electron';

interface AccountState {
  accounts: Account[];
  currentAccount: Account | null;
  isLoading: boolean;
  error: string | null;

  actions: {
    loadAccounts: () => Promise<void>;
    createAccount: (data: AccountFormData) => Promise<Account>;
    updateAccount: (id: string, data: Partial<Account>) => Promise<boolean>;
    deleteAccount: (id: string) => Promise<boolean>;
    selectAccount: (account: Account | null) => void;
    refreshSession: (accountId: string) => Promise<boolean>;
    clearError: () => void;
  };
}

export const useAccountStore = create<AccountState>()(
  devtools(
    (set, get) => ({
      accounts: [],
      currentAccount: null,
      isLoading: false,
      error: null,

      actions: {
        loadAccounts: async () => {
          set({ isLoading: true, error: null });

          try {
            const response = await electronAPI.sendCommand({
              id: `load-accounts-${Date.now()}`,
              type: 'ACCOUNT_LIST',
              timestamp: Date.now()
            });

            if (response.success) {
              set({ accounts: response.data || [], isLoading: false });
            } else {
              set({ error: response.error || 'Failed to load accounts', isLoading: false });
            }
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Unknown error',
              isLoading: false
            });
          }
        },

        createAccount: async (data: AccountFormData) => {
          try {
            const response = await electronAPI.sendCommand({
              id: `create-account-${Date.now()}`,
              type: 'ACCOUNT_CREATE',
              payload: data,
              timestamp: Date.now()
            });

            if (response.success) {
              const newAccount = response.data as Account;
              set(state => ({
                accounts: [...state.accounts, newAccount]
              }));
              return newAccount;
            } else {
              throw new Error(response.error || 'Failed to create account');
            }
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Unknown error'
            });
            throw error;
          }
        },

        updateAccount: async (id: string, data: Partial<Account>) => {
          try {
            const response = await electronAPI.sendCommand({
              id: `update-account-${Date.now()}`,
              type: 'ACCOUNT_UPDATE',
              payload: { id, ...data },
              timestamp: Date.now()
            });

            if (response.success) {
              set(state => ({
                accounts: state.accounts.map(account =>
                  account.id === id ? { ...account, ...data } : account
                )
              }));
              return true;
            } else {
              throw new Error(response.error || 'Failed to update account');
            }
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Unknown error'
            });
            return false;
          }
        },

        deleteAccount: async (id: string) => {
          try {
            const response = await electronAPI.sendCommand({
              id: `delete-account-${Date.now()}`,
              type: 'ACCOUNT_DELETE',
              payload: { id },
              timestamp: Date.now()
            });

            if (response.success) {
              set(state => ({
                accounts: state.accounts.filter(account => account.id !== id),
                currentAccount: state.currentAccount?.id === id ? null : state.currentAccount
              }));
              return true;
            } else {
              throw new Error(response.error || 'Failed to delete account');
            }
          } catch (error) {
            set({
              error: error instanceof Error ? error.message : 'Unknown error'
            });
            return false;
          }
        },

        selectAccount: (account: Account | null) => {
          set({ currentAccount: account });
        },

        refreshSession: async (accountId: string) => {
          try {
            const response = await electronAPI.sendCommand({
              id: `refresh-session-${Date.now()}`,
              type: 'SESSION_REFRESH',
              payload: { account_id: accountId },
              timestamp: Date.now()
            });

            return response.success;
          } catch (error) {
            console.error('Failed to refresh session:', error);
            return false;
          }
        },

        clearError: () => {
          set({ error: null });
        }
      }
    }),
    {
      name: 'account-store'
    }
  )
);

// Export hook for convenience
export const useAccountActions = () => useAccountStore(state => state.actions);
export const useCurrentAccount = () => useAccountStore(state => state.currentAccount);
```

```typescript
// src/stores/songStore.ts
import { create } from 'zustand';
import { devtools, subscribeWithSelector } from 'zustand/middleware';
import { SongPrompt, SongClip, SongCreationRequest, QueueEntry } from '@/types/shared';
import { electronAPI } from '@/types/electron';

interface SongState {
  // Song creation
  prompts: SongPrompt[];
  queues: QueueEntry[];
  currentCreation: QueueExecution | null;
  createdSongs: SongClip[];

  // Loading and error states
  isLoading: boolean;
  isCreating: boolean;
  error: string | null;
  creationProgress: any;

  actions: {
    // Prompt management
    loadPromptsFromFile: (filePath: string) => Promise<SongPrompt[]>;
    setPrompts: (prompts: SongPrompt[]) => void;
    clearPrompts: () => void;

    // Queue management
    createQueue: (data: {
      account_name: string;
      total_songs: number;
      songs_per_batch: number;
    }) => Promise<QueueEntry>;
    startQueue: (queueId: string) => Promise<boolean>;
    pauseQueue: (queueId: string) => Promise<boolean>;
    deleteQueue: (queueId: string) => Promise<boolean>;

    // Batch operations
    startSelectedQueues: (queueIds: string[]) => Promise<void>;

    // History
    loadCreatedSongs: (accountId?: string) => Promise<void>;
    clearCreatedSongs: () => void;

    // Utility
    clearError: () => void;
  };
}

export const useSongStore = create<SongState>()(
  devtools(
    subscribeWithSelector((set, get) => ({
      // Initial state
      prompts: [],
      queues: [],
      currentCreation: null,
      createdSongs: [],
      isLoading: false,
      isCreating: false,
      error: null,
      creationProgress: null,

      actions: {
        loadPromptsFromFile: async (filePath: string) => {
          set({ isLoading: true, error: null });

          try {
            const response = await electronAPI.sendCommand({
              id: `load-prompts-${Date.now()}`,
              type: 'PROMPTS_LOAD_FILE',
              payload: { file_path: filePath },
              timestamp: Date.now()
            });

            if (response.success) {
              const prompts = response.data as SongPrompt[];
              set({ prompts, isLoading: false });
              return prompts;
            } else {
              throw new Error(response.error || 'Failed to load prompts');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            set({ error: errorMessage, isLoading: false });
            throw error;
          }
        },

        setPrompts: (prompts: SongPrompt[]) => {
          set({ prompts });
        },

        clearPrompts: () => {
          set({ prompts: [] });
        },

        createQueue: async (data) => {
          const state = get();
          const availablePrompts = state.prompts.length;
          const usedPrompts = state.queues.reduce(
            (total, queue) => total + queue.total_songs, 0
          );

          if (usedPrompts + data.total_songs > availablePrompts) {
            throw new Error(
              `Insufficient prompts. Available: ${availablePrompts - usedPrompts}, Required: ${data.total_songs}`
            );
          }

          try {
            const response = await electronAPI.sendCommand({
              id: `create-queue-${Date.now()}`,
              type: 'QUEUE_CREATE',
              payload: data,
              timestamp: Date.now()
            });

            if (response.success) {
              const newQueue = response.data as QueueEntry;
              set(state => ({
                queues: [...state.queues, newQueue]
              }));
              return newQueue;
            } else {
              throw new Error(response.error || 'Failed to create queue');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            set({ error: errorMessage });
            throw error;
          }
        },

        startQueue: async (queueId: string) => {
          try {
            const response = await electronAPI.sendCommand({
              id: `start-queue-${Date.now()}`,
              type: 'QUEUE_START',
              payload: { queue_id: queueId },
              timestamp: Date.now()
            });

            if (response.success) {
              set(state => ({
                queues: state.queues.map(queue =>
                  queue.id === queueId ? { ...queue, status: 'running' } : queue
                )
              }));
              return true;
            } else {
              throw new Error(response.error || 'Failed to start queue');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            set({ error: errorMessage });
            return false;
          }
        },

        pauseQueue: async (queueId: string) => {
          try {
            const response = await electronAPI.sendCommand({
              id: `pause-queue-${Date.now()}`,
              type: 'QUEUE_PAUSE',
              payload: { queue_id: queueId },
              timestamp: Date.now()
            });

            if (response.success) {
              set(state => ({
                queues: state.queues.map(queue =>
                  queue.id === queueId ? { ...queue, status: 'paused' } : queue
                )
              }));
              return true;
            } else {
              throw new Error(response.error || 'Failed to pause queue');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            set({ error: errorMessage });
            return false;
          }
        },

        deleteQueue: async (queueId: string) => {
          try {
            const response = await electronAPI.sendCommand({
              id: `delete-queue-${Date.now()}`,
              type: 'QUEUE_DELETE',
              payload: { queue_id: queueId },
              timestamp: Date.now()
            });

            if (response.success) {
              set(state => ({
                queues: state.queues.filter(queue => queue.id !== queueId)
              }));
              return true;
            } else {
              throw new Error(response.error || 'Failed to delete queue');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            set({ error: errorMessage });
            return false;
          }
        },

        startSelectedQueues: async (queueIds: string[]) => {
          set({ isCreating: true, error: null });

          try {
            const response = await electronAPI.sendCommand({
              id: `start-queues-${Date.now()}`,
              type: 'QUEUE_START_BATCH',
              payload: { queue_ids: queueIds },
              timestamp: Date.now()
            });

            if (response.success) {
              const execution = response.data as QueueExecution;
              set({
                currentCreation: execution,
                isCreating: true
              });
            } else {
              throw new Error(response.error || 'Failed to start queues');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            set({ error: errorMessage, isCreating: false });
            throw error;
          }
        },

        loadCreatedSongs: async (accountId?: string) => {
          set({ isLoading: true, error: null });

          try {
            const response = await electronAPI.sendCommand({
              id: `load-songs-${Date.now()}`,
              type: 'HISTORY_GET_SONGS',
              payload: { account_id: accountId },
              timestamp: Date.now()
            });

            if (response.success) {
              const songs = response.data as SongClip[];
              set({ createdSongs: songs, isLoading: false });
            } else {
              throw new Error(response.error || 'Failed to load songs');
            }
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            set({ error: errorMessage, isLoading: false });
          }
        },

        clearCreatedSongs: () => {
          set({ createdSongs: [] });
        },

        clearError: () => {
          set({ error: null });
        }
      }
    })),
    {
      name: 'song-store'
    }
  )
);

// Export hooks for convenience
export const useSongActions = () => useSongStore(state => state.actions);
export const usePrompts = () => useSongStore(state => state.prompts);
export const useQueues = () => useSongStore(state => state.queues);
export const useCreationProgress = () => useSongStore(state => ({
  currentCreation: state.currentCreation,
  isCreating: state.isCreating,
  creationProgress: state.creationProgress
}));
```

### Day 2: Layout Components and Navigation

#### Morning (4 hours)
**Task: Create main layout and navigation structure**

```typescript
// src/components/layout/MainLayout.tsx
import React, { useEffect } from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { StatusBar } from './StatusBar';
import { useAccountStore } from '@/stores/accountStore';
import { useUIStore } from '@/stores/uiStore';
import { electronAPI } from '@/types/electron';

interface MainLayoutProps {
  children: React.ReactNode;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const { actions: accountActions, error: accountError } = useAccountStore();
  const { activeView, setActiveView, isSidebarCollapsed, setSidebarCollapsed } = useUIStore();

  useEffect(() => {
    // Initialize accounts on mount
    accountActions.loadAccounts();

    // Listen for backend events
    electronAPI.onBackendReady(() => {
      console.log('Backend is ready');
    });

    electronAPI.onProgressUpdate((progress) => {
      console.log('Progress update:', progress);
    });

    electronAPI.onErrorUpdate((error) => {
      console.error('Backend error:', error);
    });

    // Listen for menu actions
    electronAPI.onMenuAction((action) => {
      switch (action) {
        case 'NEW_ACCOUNT':
          setActiveView('accounts');
          break;
        default:
          console.log('Unknown menu action:', action);
      }
    });

    // Cleanup listeners
    return () => {
      electronAPI.removeAllListeners('BACKEND_READY');
      electronAPI.removeAllListeners('PROGRESS_UPDATE');
      electronAPI.removeAllListeners('ERROR_UPDATE');
      electronAPI.removeAllListeners('MENU_NEW_ACCOUNT');
    };
  }, [accountActions, setActiveView]);

  const handleSidebarToggle = () => {
    setSidebarCollapsed(!isSidebarCollapsed);
  };

  return (
    <div className="main-layout">
      <Header
        onSidebarToggle={handleSidebarToggle}
        isSidebarCollapsed={isSidebarCollapsed}
      />

      <div className="main-content">
        <Sidebar
          activeView={activeView}
          onViewChange={setActiveView}
          isCollapsed={isSidebarCollapsed}
        />

        <main className={`content-area ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
          {accountError && (
            <div className="error-banner">
              <span className="error-message">{accountError}</span>
              <button
                onClick={accountActions.clearError}
                className="error-dismiss"
              >
                ×
              </button>
            </div>
          )}

          {children}
        </main>
      </div>

      <StatusBar />
    </div>
  );
};
```

```typescript
// src/components/layout/Sidebar.tsx
import React from 'react';
import { useUIStore } from '@/stores/uiStore';
import { useAccountStore } from '@/stores/accountStore';
import { useSongStore } from '@/stores/songStore';
import {
  UsersIcon,
  MusicNoteIcon,
  QueueListIcon,
  ArrowDownTrayIcon,
  ClockIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  activeView: string;
  onViewChange: (view: string) => void;
  isCollapsed: boolean;
}

const navigationItems = [
  { id: 'accounts', label: 'Tài khoản', icon: UsersIcon },
  { id: 'create', label: 'Tạo nhạc', icon: MusicNoteIcon },
  { id: 'queue', label: 'Hàng đợi', icon: QueueListIcon },
  { id: 'download', label: 'Download', icon: ArrowDownTrayIcon },
  { id: 'history', label: 'Lịch sử', icon: ClockIcon },
  { id: 'settings', label: 'Cài đặt', icon: Cog6ToothIcon },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeView,
  onViewChange,
  isCollapsed
}) => {
  const { currentAccount } = useAccountStore();
  const { queues } = useSongStore();
  const { badgeCount } = useUIStore();

  // Calculate badge counts
  const runningQueues = queues.filter(q => q.status === 'running').length;
  const pendingQueues = queues.filter(q => q.status === 'pending').length;

  const getBadgeCount = (viewId: string) => {
    switch (viewId) {
      case 'queue':
        return runningQueues > 0 ? runningQueues : (pendingQueues > 0 ? pendingQueues : null);
      default:
        return null;
    }
  };

  return (
    <nav className={`sidebar ${isCollapsed ? 'collapsed' : ''}`}>
      <div className="sidebar-header">
        {!isCollapsed && (
          <div className="app-info">
            <h2>Suno Manager</h2>
            <span className="version">v3.0</span>
          </div>
        )}
      </div>

      <div className="sidebar-content">
        {currentAccount && !isCollapsed && (
          <div className="current-account">
            <div className="account-avatar">
              <UsersIcon className="w-6 h-6" />
            </div>
            <div className="account-details">
              <div className="account-name">{currentAccount.name}</div>
              <div className="account-email">{currentAccount.email}</div>
            </div>
          </div>
        )}

        <ul className="navigation-list">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const badgeCount = getBadgeCount(item.id);
            const isActive = activeView === item.id;

            return (
              <li key={item.id}>
                <button
                  className={`nav-item ${isActive ? 'active' : ''}`}
                  onClick={() => onViewChange(item.id)}
                  title={isCollapsed ? item.label : undefined}
                >
                  <Icon className="nav-icon" />
                  {!isCollapsed && (
                    <>
                      <span className="nav-label">{item.label}</span>
                      {badgeCount !== null && badgeCount > 0 && (
                        <span className="nav-badge">{badgeCount}</span>
                      )}
                    </>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </div>

      {!isCollapsed && currentAccount && (
        <div className="sidebar-footer">
          <div className="account-status">
            <div className="status-indicator active" />
            <span>Đã kết nối</span>
          </div>
        </div>
      )}
    </nav>
  );
};
```

```typescript
// src/stores/uiStore.ts
import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

interface UIState {
  // Navigation
  activeView: string;
  previousView: string | null;
  navigationHistory: string[];

  // Layout
  isSidebarCollapsed: boolean;
  isDarkMode: boolean;
  windowSize: { width: number; height: number };

  // Notifications
  notifications: Notification[];
  badgeCount: Record<string, number>;

  // Loading states
  globalLoading: boolean;

  actions: {
    setActiveView: (view: string) => void;
    goBack: () => void;
    toggleSidebar: () => void;
    setSidebarCollapsed: (collapsed: boolean) => void;
    toggleDarkMode: () => void;
    setWindowSize: (size: { width: number; height: number }) => void;

    // Notifications
    addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
    removeNotification: (id: string) => void;
    clearNotifications: () => void;

    // Badges
    setBadgeCount: (key: string, count: number) => void;

    // Loading
    setGlobalLoading: (loading: boolean) => void;
  };
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  timestamp: number;
  autoClose?: boolean;
  duration?: number;
}

export const useUIStore = create<UIState>()(
  devtools(
    (set, get) => ({
      // Initial state
      activeView: 'accounts',
      previousView: null,
      navigationHistory: ['accounts'],
      isSidebarCollapsed: false,
      isDarkMode: true,
      windowSize: { width: 1400, height: 850 },
      notifications: [],
      badgeCount: {},
      globalLoading: false,

      actions: {
        setActiveView: (view: string) => {
          set(state => {
            const newHistory = [...state.navigationHistory];
            if (state.activeView !== view) {
              newHistory.push(view);
            }

            return {
              activeView: view,
              previousView: state.activeView,
              navigationHistory: newHistory
            };
          });
        },

        goBack: () => {
          set(state => {
            const history = [...state.navigationHistory];
            if (history.length > 1) {
              history.pop(); // Remove current
              const previousView = history[history.length - 1];

              return {
                activeView: previousView,
                previousView: state.activeView,
                navigationHistory: history
              };
            }
            return state;
          });
        },

        toggleSidebar: () => {
          set(state => ({ isSidebarCollapsed: !state.isSidebarCollapsed }));
        },

        setSidebarCollapsed: (collapsed: boolean) => {
          set({ isSidebarCollapsed: collapsed });
        },

        toggleDarkMode: () => {
          set(state => {
            const newMode = !state.isDarkMode;
            // Apply theme to document
            document.documentElement.classList.toggle('dark', newMode);
            return { isDarkMode: newMode };
          });
        },

        setWindowSize: (size: { width: number; height: number }) => {
          set({ windowSize: size });
        },

        addNotification: (notification) => {
          const id = `notif-${Date.now()}-${Math.random()}`;
          const fullNotification: Notification = {
            id,
            timestamp: Date.now(),
            autoClose: notification.type !== 'error',
            duration: notification.type === 'error' ? 0 : 5000,
            ...notification
          };

          set(state => ({
            notifications: [...state.notifications, fullNotification]
          }));

          // Auto close notification
          if (fullNotification.autoClose && fullNotification.duration) {
            setTimeout(() => {
              get().actions.removeNotification(id);
            }, fullNotification.duration);
          }
        },

        removeNotification: (id: string) => {
          set(state => ({
            notifications: state.notifications.filter(n => n.id !== id)
          }));
        },

        clearNotifications: () => {
          set({ notifications: [] });
        },

        setBadgeCount: (key: string, count: number) => {
          set(state => ({
            badgeCount: { ...state.badgeCount, [key]: count }
          }));
        },

        setGlobalLoading: (loading: boolean) => {
          set({ globalLoading: loading });
        }
      }
    }),
    {
      name: 'ui-store'
    }
  )
);

// Export hooks for convenience
export const useUIActions = () => useUIStore(state => state.actions);
export const useActiveView = () => useUIStore(state => state.activeView);
export const useNotifications = () => useUIStore(state => state.notifications);
```

#### Afternoon (4 hours)
**Task: Create Header and StatusBar components**

```typescript
// src/components/layout/Header.tsx
import React from 'react';
import {
  Bars3Icon,
  MinusIcon,
  Square2StackIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { electronAPI } from '@/types/electron';

interface HeaderProps {
  onSidebarToggle: () => void;
  isSidebarCollapsed: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onSidebarToggle,
  isSidebarCollapsed
}) => {
  const handleMinimize = async () => {
    await electronAPI.minimizeWindow();
  };

  const handleMaximize = async () => {
    await electronAPI.maximizeWindow();
  };

  const handleClose = async () => {
    await electronAPI.closeWindow();
  };

  return (
    <header className="app-header">
      <div className="header-left">
        <button
          className="sidebar-toggle"
          onClick={onSidebarToggle}
          title={isSidebarCollapsed ? 'Mở sidebar' : 'Đóng sidebar'}
        >
          <Bars3Icon className="w-5 h-5" />
        </button>

        <div className="app-title">
          <h1>Suno Account Manager</h1>
        </div>
      </div>

      <div className="header-center">
        {/* Future: Search bar or breadcrumbs */}
      </div>

      <div className="header-right">
        <div className="window-controls">
          <button
            className="window-control minimize"
            onClick={handleMinimize}
            title="Thu nhỏ"
          >
            <MinusIcon className="w-4 h-4" />
          </button>

          <button
            className="window-control maximize"
            onClick={handleMaximize}
            title="Phóng to/Thu nhỏ"
          >
            <Square2StackIcon className="w-4 h-4" />
          </button>

          <button
            className="window-control close"
            onClick={handleClose}
            title="Đóng"
          >
            <XMarkIcon className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
```

```typescript
// src/components/layout/StatusBar.tsx
import React, { useEffect, useState } from 'react';
import { useUIStore } from '@/stores/uiStore';
import { useSongStore } from '@/stores/songStore';
import { electronAPI } from '@/types/electron';

export const StatusBar: React.FC = () => {
  const { windowSize } = useUIStore();
  const { currentCreation, isCreating } = useSongStore();
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'error'>('disconnected');
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    // Update time every second
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    // Monitor backend status
    let isBackendReady = false;

    electronAPI.onBackendReady(() => {
      setBackendStatus('connected');
      isBackendReady = true;
    });

    electronAPI.onErrorUpdate(() => {
      setBackendStatus('error');
    });

    // Check backend status periodically
    const statusCheck = setInterval(async () => {
      if (!isBackendReady) {
        try {
          await electronAPI.sendCommand({
            id: `status-check-${Date.now()}`,
            type: 'SYSTEM_PING',
            timestamp: Date.now()
          });
          setBackendStatus('connected');
          isBackendReady = true;
        } catch (error) {
          setBackendStatus('disconnected');
        }
      }
    }, 5000);

    return () => {
      clearInterval(statusCheck);
      electronAPI.removeAllListeners('BACKEND_READY');
      electronAPI.removeAllListeners('ERROR_UPDATE');
    };
  }, []);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getStatusIndicator = () => {
    const statusConfig = {
      connected: { color: 'bg-green-500', label: 'Đã kết nối' },
      disconnected: { color: 'bg-gray-500', label: 'Mất kết nối' },
      error: { color: 'bg-red-500', label: 'Lỗi' }
    };

    const config = statusConfig[backendStatus];

    return (
      <div className="status-indicator">
        <div className={`status-dot ${config.color}`} />
        <span className="status-text">{config.label}</span>
      </div>
    );
  };

  return (
    <div className="status-bar">
      <div className="status-left">
        {getStatusIndicator()}

        {isCreating && currentCreation && (
          <div className="creation-status">
            <span>Đang tạo nhạc:</span>
            <div className="progress-mini">
              <div
                className="progress-bar"
                style={{ width: `${currentCreation.progress.completed_songs / currentCreation.progress.total_songs * 100}%` }}
              />
            </div>
            <span>{currentCreation.progress.completed_songs}/{currentCreation.progress.total_songs}</span>
          </div>
        )}
      </div>

      <div className="status-center">
        {/* Future: Add status messages or tooltips */}
      </div>

      <div className="status-right">
        <span className="window-size">
          {windowSize.width} × {windowSize.height}
        </span>
        <span className="separator">|</span>
        <span className="current-time">
          {formatTime(currentTime)}
        </span>
      </div>
    </div>
  );
};
```

### Day 3: Core UI Components

#### Morning (4 hours)
**Task: Create reusable UI components**

```typescript
// src/components/ui/Button.tsx
import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({
    children,
    className,
    variant = 'primary',
    size = 'md',
    loading = false,
    icon,
    iconPosition = 'left',
    fullWidth = false,
    disabled,
    ...props
  }, ref) => {
    const baseClasses = 'btn';

    const variantClasses = {
      primary: 'btn-primary',
      secondary: 'btn-secondary',
      danger: 'btn-danger',
      ghost: 'btn-ghost'
    };

    const sizeClasses = {
      sm: 'btn-sm',
      md: 'btn-md',
      lg: 'btn-lg'
    };

    const classes = clsx(
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      {
        'btn-loading': loading,
        'btn-full-width': fullWidth,
        'btn-icon-only': icon && !children
      },
      className
    );

    const renderIcon = () => {
      if (!icon) return null;

      return (
        <span className={clsx('btn-icon', `btn-icon-${iconPosition}`)}>
          {icon}
        </span>
      );
    };

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || loading}
        {...props}
      >
        {loading && (
          <span className="btn-spinner">
            <div className="spinner" />
          </span>
        )}

        {iconPosition === 'left' && renderIcon()}

        {children && <span className="btn-text">{children}</span>}

        {iconPosition === 'right' && renderIcon()}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

```typescript
// src/components/ui/Input.tsx
import React, { InputHTMLAttributes, forwardRef } from 'react';
import { clsx } from 'clsx';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({
    className,
    label,
    error,
    helperText,
    leftIcon,
    rightIcon,
    fullWidth = false,
    ...props
  }, ref) => {
    const inputId = props.id || `input-${Math.random().toString(36).substr(2, 9)}`;

    const classes = clsx(
      'input-wrapper',
      {
        'input-wrapper-full-width': fullWidth,
        'input-wrapper-error': error,
        'input-wrapper-disabled': props.disabled
      },
      className
    );

    const inputClasses = clsx(
      'input',
      {
        'input-with-left-icon': leftIcon,
        'input-with-right-icon': rightIcon
      }
    );

    return (
      <div className={classes}>
        {label && (
          <label htmlFor={inputId} className="input-label">
            {label}
            {props.required && <span className="input-required">*</span>}
          </label>
        )}

        <div className="input-container">
          {leftIcon && (
            <div className="input-icon input-icon-left">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={inputClasses}
            {...props}
          />

          {rightIcon && (
            <div className="input-icon input-icon-right">
              {rightIcon}
            </div>
          )}
        </div>

        {error && (
          <div className="input-error">
            {error}
          </div>
        )}

        {helperText && !error && (
          <div className="input-helper">
            {helperText}
          </div>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';
```

```typescript
// src/components/ui/Modal.tsx
import React, { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';
import { clsx } from 'clsx';
import { XMarkIcon } from '@heroicons/react/24/outline';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
  showCloseButton?: boolean;
  closeOnOverlayClick?: boolean;
  preventBodyScroll?: boolean;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'md',
  children,
  showCloseButton = true,
  closeOnOverlayClick = true,
  preventBodyScroll = true
}) => {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      // Store previous focus
      previousFocusRef.current = document.activeElement as HTMLElement;

      // Prevent body scroll
      if (preventBodyScroll) {
        document.body.style.overflow = 'hidden';
      }

      // Focus modal
      setTimeout(() => {
        modalRef.current?.focus();
      }, 100);

      // Add ESC key handler
      const handleEscape = (event: KeyboardEvent) => {
        if (event.key === 'Escape') {
          onClose();
        }
      };

      document.addEventListener('keydown', handleEscape);

      return () => {
        document.removeEventListener('keydown', handleEscape);

        // Restore body scroll
        if (preventBodyScroll) {
          document.body.style.overflow = '';
        }

        // Restore focus
        if (previousFocusRef.current) {
          previousFocusRef.current.focus();
        }
      };
    }
  }, [isOpen, onClose, preventBodyScroll]);

  if (!isOpen) return null;

  const sizeClasses = {
    sm: 'modal-sm',
    md: 'modal-md',
    lg: 'modal-lg',
    xl: 'modal-xl'
  };

  const handleOverlayClick = (event: React.MouseEvent) => {
    if (event.target === event.currentTarget && closeOnOverlayClick) {
      onClose();
    }
  };

  const modalContent = (
    <div className="modal-overlay" onClick={handleOverlayClick}>
      <div
        ref={modalRef}
        className={clsx('modal', sizeClasses[size])}
        tabIndex={-1}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        {(title || showCloseButton) && (
          <div className="modal-header">
            {title && (
              <h2 id="modal-title" className="modal-title">
                {title}
              </h2>
            )}

            {showCloseButton && (
              <button
                className="modal-close"
                onClick={onClose}
                aria-label="Đóng"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            )}
          </div>
        )}

        <div className="modal-content">
          {children}
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};
```

#### Afternoon (4 hours)
**Task: Create Progress and Table components**

```typescript
// src/components/ui/Progress.tsx
import React from 'react';
import { clsx } from 'clsx';

interface ProgressProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'success' | 'warning' | 'error';
  showLabel?: boolean;
  label?: string;
  animated?: boolean;
  striped?: boolean;
}

export const Progress: React.FC<ProgressProps> = ({
  value,
  max = 100,
  size = 'md',
  variant = 'default',
  showLabel = false,
  label,
  animated = false,
  striped = false
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizeClasses = {
    sm: 'progress-sm',
    md: 'progress-md',
    lg: 'progress-lg'
  };

  const variantClasses = {
    default: 'progress-default',
    success: 'progress-success',
    warning: 'progress-warning',
    error: 'progress-error'
  };

  const progressClasses = clsx(
    'progress',
    sizeClasses[size],
    variantClasses[variant],
    {
      'progress-striped': striped,
      'progress-animated': animated && striped
    }
  );

  return (
    <div className="progress-wrapper">
      {(label || showLabel) && (
        <div className="progress-label">
          <span>{label || `${Math.round(percentage)}%`}</span>
        </div>
      )}

      <div className={progressClasses}>
        <div
          className="progress-bar"
          style={{ width: `${percentage}%` }}
          role="progressbar"
          aria-valuenow={value}
          aria-valuemin={0}
          aria-valuemax={max}
        />
      </div>
    </div>
  );
};

// Circular Progress Component
interface CircularProgressProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  showLabel?: boolean;
  label?: string;
  variant?: 'default' | 'success' | 'warning' | 'error';
}

export const CircularProgress: React.FC<CircularProgressProps> = ({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  showLabel = true,
  label,
  variant = 'default'
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  const variantColors = {
    default: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444'
  };

  const color = variantColors[variant];

  return (
    <div className="circular-progress" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        className="progress-ring"
      >
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          className="progress-ring-circle"
        />
      </svg>

      {showLabel && (
        <div className="circular-progress-label">
          <span className="progress-value">
            {label || `${Math.round(percentage)}%`}
          </span>
        </div>
      )}
    </div>
  );
};
```

```typescript
// src/components/ui/Table.tsx
import React from 'react';
import { clsx } from 'clsx';

interface Column<T> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (value: any, row: T, index: number) => React.ReactNode;
}

interface TableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  emptyMessage?: string;
  striped?: boolean;
  hoverable?: boolean;
  compact?: boolean;
  selectable?: boolean;
  selectedRows?: Set<number>;
  onRowSelect?: (index: number, selected: boolean) => void;
  onRowClick?: (row: T, index: number) => void;
  onSort?: (column: keyof T, direction: 'asc' | 'desc') => void;
  sortColumn?: keyof T;
  sortDirection?: 'asc' | 'desc';
}

export function Table<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  emptyMessage = 'Không có dữ liệu',
  striped = true,
  hoverable = true,
  compact = false,
  selectable = false,
  selectedRows = new Set(),
  onRowSelect,
  onRowClick,
  onSort,
  sortColumn,
  sortDirection
}: TableProps<T>) {
  const handleSort = (column: Column<T>) => {
    if (!column.sortable || !onSort) return;

    const newDirection =
      sortColumn === column.key && sortDirection === 'asc' ? 'desc' : 'asc';

    onSort(column.key, newDirection);
  };

  const handleRowSelect = (index: number, checked: boolean) => {
    onRowSelect?.(index, checked);
  };

  const getSortIcon = (column: Column<T>) => {
    if (!column.sortable || sortColumn !== column.key) {
      return <div className="sort-icon sort-icon-none" />;
    }

    return (
      <div className={clsx('sort-icon', `sort-icon-${sortDirection}`)} />
    );
  };

  const tableClasses = clsx(
    'table',
    {
      'table-striped': striped,
      'table-hoverable': hoverable,
      'table-compact': compact,
      'table-selectable': selectable
    }
  );

  if (loading) {
    return (
      <div className="table-loading">
        <div className="spinner" />
        <span>Đang tải...</span>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="table-empty">
        <span>{emptyMessage}</span>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className={tableClasses}>
        <thead>
          <tr>
            {selectable && (
              <th className="table-header-select">
                <input
                  type="checkbox"
                  checked={selectedRows.size === data.length && data.length > 0}
                  onChange={(e) => {
                    const checked = e.target.checked;
                    for (let i = 0; i < data.length; i++) {
                      handleRowSelect(i, checked);
                    }
                  }}
                />
              </th>
            )}

            {columns.map((column) => (
              <th
                key={String(column.key)}
                className={clsx('table-header', `table-header-align-${column.align || 'left'}`)}
                style={{ width: column.width }}
              >
                <div className="table-header-content">
                  {column.sortable ? (
                    <button
                      className="table-sort-button"
                      onClick={() => handleSort(column)}
                    >
                      <span>{column.label}</span>
                      {getSortIcon(column)}
                    </button>
                  ) : (
                    <span>{column.label}</span>
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((row, index) => {
            const isSelected = selectedRows.has(index);

            return (
              <tr
                key={index}
                className={clsx('table-row', {
                  'table-row-selected': isSelected
                })}
                onClick={() => onRowClick?.(row, index)}
              >
                {selectable && (
                  <td className="table-cell-select">
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={(e) => handleRowSelect(index, e.target.checked)}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </td>
                )}

                {columns.map((column) => {
                  const value = row[column.key];
                  const content = column.render
                    ? column.render(value, row, index)
                    : String(value || '');

                  return (
                    <td
                      key={String(column.key)}
                      className={clsx('table-cell', `table-cell-align-${column.align || 'left'}`)}
                    >
                      {content}
                    </td>
                  );
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
```

### Day 4-5: Feature Components and Integration

*(Continue with creating feature-specific components like AccountManager, SongCreator, etc.)*

## CSS Styles Framework

```css
/* src/styles/main.css */
:root {
  /* Color Palette */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-secondary: #6b7280;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;

  /* Dark theme colors */
  --color-bg-primary: #111827;
  --color-bg-secondary: #1f2937;
  --color-bg-tertiary: #374151;
  --color-text-primary: #f9fafb;
  --color-text-secondary: #d1d5db;
  --color-text-tertiary: #9ca3af;

  /* Spacing */
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;

  /* Border radius */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-xl: 0.75rem;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  line-height: 1.6;
}

.app {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Layout Components */
.main-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  height: 48px;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-md);
  user-select: none;
  -webkit-app-region: drag;
}

.app-header .header-left,
.app-header .header-right {
  -webkit-app-region: no-drag;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 250px;
  background-color: var(--color-bg-secondary);
  border-right: 1px solid var(--color-bg-tertiary);
  display: flex;
  flex-direction: column;
  transition: width 0.2s ease;
}

.sidebar.collapsed {
  width: 60px;
}

.content-area {
  flex: 1;
  overflow: auto;
  padding: var(--spacing-lg);
  transition: margin-left 0.2s ease;
}

.status-bar {
  height: 24px;
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-md);
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

/* Component styles will continue... */
```

## Testing Strategy

```typescript
// tests/components/ui/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '@/components/ui/Button';

describe('Button', () => {
  it('renders correctly with default props', () => {
    render(<Button>Click me</Button>);

    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('Click me');
    expect(button).toHaveClass('btn-primary', 'btn-md');
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(button).toHaveClass('btn-loading');
    expect(button.querySelector('.spinner')).toBeInTheDocument();
  });
});
```

## Success Criteria

### Functional Requirements
- ✅ React application loads in Electron window
- ✅ State management works with Zustand
- ✅ Components render correctly with TypeScript
- ✅ Navigation between views works
- ✅ Layout responsive to window resizing

### Technical Requirements
- ✅ TypeScript compilation successful
- ✅ No runtime type errors
- ✅ Component reusability and consistency
- ✅ Performance under 100ms for UI updates
- ✅ Memory usage under 50MB for basic components

### User Experience Requirements
- ✅ Intuitive navigation
- ✅ Responsive design
- ✅ Loading states and error handling
- ✅ Accessibility compliance
- ✅ Consistent visual design

---

*This phase establishes the React frontend foundation with modern component architecture, state management, and type safety while maintaining clean code principles and user experience standards.*