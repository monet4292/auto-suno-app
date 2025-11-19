/**
 * Suno API related type definitions
 */

export interface SongClip {
  id: string;
  title: string;
  audio_url?: string;
  image_url?: string;
  tags: string;
  created_at?: string;
  duration?: string;
  display_name?: string;
  metadata?: {
    tags?: string;
    duration_formatted?: string;
  };

  // Helper methods
  toPythonDict(): Record<string, any>;
  getFileName(): string;
}

export interface UserInfo {
  username: string;
  email: string;
  credits: number;
  display_name?: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface PaginatedResponse<T> {
  clips: T[];
  lastPage: number;
  hasMore: boolean;
  totalCount?: number;
}

export interface ClipMetadata {
  id: string;
  title: string;
  prompt?: string;
  style?: string;
  duration?: number;
  created_at: string;
  is_public?: boolean;
  user_id?: string;
  display_name?: string;
}

export interface CreateClipRequest {
  prompt?: string;
  style?: string;
  title?: string;
  tags?: string[];
  is_public?: boolean;
  continue_at?: string;
}

export interface SearchFilters {
  tags?: string[];
  duration_min?: number;
  duration_max?: number;
  created_after?: string;
  created_before?: string;
}