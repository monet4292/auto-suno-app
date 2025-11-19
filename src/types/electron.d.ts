import { BackendCommand, BackendResponse, ProgressEvent } from './backend';

// Window API types
export interface ElectronAPI {
  // Backend communication
  sendCommand: (command: BackendCommand) => Promise<BackendResponse>;

  // Event listeners
  onBackendResponse: (callback: (response: BackendResponse) => void) => void;
  onProgressUpdate: (callback: (progress: ProgressEvent) => void) => void;
  onErrorUpdate: (callback: (error: ProgressEvent) => void) => void;
  onWarningUpdate: (callback: (warning: ProgressEvent) => void) => void;

  // Remove listeners
  removeListener: (channel: string, callback: (...args: any[]) => void) => void;
  removeAllListeners: (channel?: string) => void;

  // Window management
  minimizeWindow: () => Promise<{ success: boolean }>;
  maximizeWindow: () => Promise<{ success: boolean; isMaximized: boolean }>;
  closeWindow: () => Promise<{ success: boolean }>;

  // App information
  getAppVersion: () => Promise<string>;
  platform: () => Promise<string>;

  // File operations
  selectDirectory: () => Promise<string | null>;
  selectFile: (filters?: { name: string; extensions: string[] }[]) => Promise<string | null>;
  openExternal: (url: string) => Promise<{ success: boolean }>;

  // Development tools
  openDevTools: () => void;
  reload: () => void;
}

// Window state types
export interface WindowState {
  isMaximized: boolean;
  isMinimized: boolean;
  isFocused: boolean;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

// Menu action types
export type MenuAction =
  | 'NEW_ACCOUNT'
  | 'IMPORT_ACCOUNTS'
  | 'EXPORT_ACCOUNTS'
  | 'PREFERENCES'
  | 'ABOUT'
  | 'RELOAD'
  | 'DEV_TOOLS'
  | 'QUIT';

// Application info
export interface AppInfo {
  name: string;
  version: string;
  platform: string;
  arch: string;
  electronVersion: string;
  nodeVersion: string;
  chromeVersion: string;
}

// IPC Channels
export const IPC_CHANNELS = {
  // Main communication
  SEND_COMMAND: 'SEND_COMMAND',
  BACKEND_RESPONSE: 'BACKEND_RESPONSE',

  // Progress events
  PROGRESS_UPDATE: 'PROGRESS_UPDATE',
  ERROR_UPDATE: 'ERROR_UPDATE',
  WARNING_UPDATE: 'WARNING_UPDATE',

  // Window management
  WINDOW_MINIMIZE: 'WINDOW_MINIMIZE',
  WINDOW_MAXIMIZE: 'WINDOW_MAXIMIZE',
  WINDOW_CLOSE: 'WINDOW_CLOSE',
  WINDOW_STATE_CHANGED: 'WINDOW_STATE_CHANGED',

  // Menu actions
  MENU_ACTION: 'MENU_ACTION',

  // App info
  GET_APP_VERSION: 'GET_APP_VERSION',
  GET_PLATFORM: 'GET_PLATFORM',

  // File operations
  SELECT_DIRECTORY: 'SELECT_DIRECTORY',
  SELECT_FILE: 'SELECT_FILE',
  OPEN_EXTERNAL: 'OPEN_EXTERNAL',

  // Development
  OPEN_DEV_TOOLS: 'OPEN_DEV_TOOLS',
  RELOAD_APP: 'RELOAD_APP'
} as const;

// Error types
export interface AppError {
  type: 'PYTHON_ERROR' | 'IPC_ERROR' | 'VALIDATION_ERROR' | 'UNKNOWN_ERROR';
  message: string;
  details?: any;
  timestamp: number;
}

// Validation types
export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings?: string[];
}

// Global window interface extension
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}