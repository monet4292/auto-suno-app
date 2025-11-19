// Backend communication types
export interface BackendCommand {
  id: string;
  type: string;
  payload?: any;
  timestamp?: number;
}

export interface BackendResponse {
  id: string;
  type: string;
  success: boolean;
  data?: any;
  error?: string;
  error_code?: string;
  timestamp?: number;
}

export interface ProgressEvent {
  id: string;
  type: string;
  payload: {
    operation_id?: string;
    message: string;
    progress?: number;
    song_id?: string;
    status?: string;
    title?: string;
    queue_id?: string;
    completed?: number;
    total?: number;
    current_song?: string;
    file_name?: string;
    downloaded?: number;
    total_bytes?: number;
    speed?: number;
  };
  timestamp: number;
}

// Account types
export interface Account {
  name: string;
  email?: string;
  created_at: string;
  last_used?: string;
  status: 'active' | 'inactive';
}

// Queue types
export interface QueueEntry {
  id: string;
  account_name: string;
  total_songs: number;
  songs_per_batch: number;
  prompts_range: [number, number];
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  completed_count: number;
  created_at: string;
  updated_at?: string;
}

export interface SunoPrompt {
  title: string;
  lyrics: string;
  style: string;
}

// Song types
export interface SongClip {
  id: string;
  title: string;
  audio_url: string;
  metadata?: {
    duration?: number;
    created_at?: string;
    tags?: string[];
  };
}

export interface DownloadHistory {
  account_name: string;
  downloaded_ids: string[];
  total_downloaded: number;
  last_download?: string;
}

// Session types
export interface SessionInfo {
  token: string;
  expires_at?: number;
  profile_path?: string;
}

// Advanced options for song creation
export interface AdvancedOptions {
  weirdness?: number;
  creativity?: number;
  clarity?: number;
  model?: 'v4' | 'v3.5' | 'v3';
  vocal_gender?: 'auto' | 'male' | 'female';
  lyrics_mode?: 'auto' | 'manual';
  style_influence?: number;
}

// History types
export interface SongCreationRecord {
  song_id: string;
  title: string;
  prompt_xml: string;
  prompt_index: number;
  account_name: string;
  status: 'completed' | 'failed' | 'in_progress';
  created_at: string;
  urls?: {
    audio_url?: string;
    video_url?: string;
    share_url?: string;
  };
}

// Command types (matching backend)
export type CommandType =
  // Account Management
  | 'GET_ACCOUNTS'
  | 'CREATE_ACCOUNT'
  | 'UPDATE_ACCOUNT'
  | 'RENAME_ACCOUNT'
  | 'DELETE_ACCOUNT'
  | 'GET_ACCOUNT_PROFILE_PATH'

  // Queue Management
  | 'GET_QUEUES'
  | 'CREATE_QUEUE'
  | 'REMOVE_QUEUE'
  | 'UPDATE_QUEUE_PROGRESS'
  | 'VALIDATE_PROMPTS'
  | 'CLEAR_QUEUES'

  // Session Management
  | 'LAUNCH_BROWSER'
  | 'GET_SESSION_TOKEN'
  | 'VERIFY_SESSION'

  // Download Management
  | 'GET_DOWNLOAD_HISTORY'
  | 'FETCH_CLIPS'
  | 'GET_NEW_CLIPS'
  | 'DOWNLOAD_CLIP'
  | 'BATCH_DOWNLOAD'
  | 'CLEAR_DOWNLOAD_HISTORY'

  // Song Creation
  | 'CREATE_SONGS_BATCH'
  | 'START_QUEUE_EXECUTION'

  // History Management
  | 'GET_CREATION_HISTORY'
  | 'ADD_CREATION_RECORD'
  | 'EXPORT_HISTORY_TO_CSV'
  | 'SEARCH_HISTORY';

// Response types (matching backend)
export type ResponseType = string; // Dynamic based on command + _RESPONSE

// Progress event types
export type ProgressEventType =
  | 'QUEUE_PROGRESS'
  | 'BATCH_PROGRESS'
  | 'SONG_PROGRESS'
  | 'DOWNLOAD_PROGRESS'
  | 'BATCH_DOWNLOAD_PROGRESS'
  | 'SONG_CREATION_PROGRESS'
  | 'ERROR_UPDATE'
  | 'WARNING_UPDATE';

// Error types
export interface AppError extends Error {
  code?: string;
  details?: any;
}