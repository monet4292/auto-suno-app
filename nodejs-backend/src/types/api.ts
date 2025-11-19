/**
 * API related type definitions
 */

export interface RequestWithAuth extends Request {
  sessionToken?: string;
  user?: UserInfo;
}

export interface AccountData {
  name: string;
  email?: string;
  created_at?: string;
  last_used?: string;
  status?: string;
}

export interface DownloadRequest {
  accountName: string;
  profileName?: string;
  useMySongs?: boolean;
  useCreatePage?: boolean;
  outputPath?: string;
  options?: DownloadOptions;
}

export interface DownloadOptions {
  withThumbnail?: boolean;
  appendUuid?: boolean;
  delay?: number;
  maxClips?: number;
  startPage?: number;
  maxPages?: number;
}

export interface DownloadStatus {
  id: string;
  accountName: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  totalClips: number;
  processedClips: number;
  successCount: number;
  failedCount: number;
  skippedCount: number;
  startTime: string;
  endTime?: string;
  error?: string;
}

export interface BridgeRequest {
  action: string;
  data: Record<string, any>;
}

export interface BridgeResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export interface HealthCheckResponse {
  status: 'ok' | 'error';
  timestamp: string;
  uptime: number;
  version?: string;
  memory?: NodeJS.MemoryUsage;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  resetTime: number;
  retryAfter?: number;
}