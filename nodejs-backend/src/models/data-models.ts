/**
 * Data Models - TypeScript implementation of Python data models
 * Compatible with existing Python data structures
 */

export interface AccountData {
  name: string;
  email: string;
  created_at: string;
  last_used?: string;
  status: string;
}

export class Account {
  name: string;
  email: string;
  created_at: string;
  last_used?: string;
  status: string;

  constructor(data: AccountData) {
    this.name = data.name;
    this.email = data.email;
    this.created_at = data.created_at;
    this.last_used = data.last_used;
    this.status = data.status || "active";
  }

  toDict(): Record<string, any> {
    return {
      name: this.name,
      email: this.email,
      created_at: this.created_at,
      last_used: this.last_used,
      status: this.status
    };
  }

  static fromDict(data: Record<string, any>): Account {
    return new Account({
      name: data.name,
      email: data.email,
      created_at: data.created_at,
      last_used: data.last_used,
      status: data.status || "active"
    });
  }

  updateLastUsed(): void {
    this.last_used = new Date().toISOString();
  }
}

export interface DownloadHistoryData {
  account_name: string;
  downloaded_ids: string[];
  total_downloaded: number;
  last_download?: string;
  current_page: number;
  last_profile: string;
}

export class DownloadHistory {
  account_name: string;
  downloadedIds: string[];
  totalDownloaded: number;
  lastDownload?: string;
  currentPage: number;
  lastProfile: string;

  constructor(data: DownloadHistoryData) {
    this.account_name = data.account_name;
    this.downloadedIds = data.downloaded_ids || [];
    this.totalDownloaded = data.total_downloaded || 0;
    this.lastDownload = data.last_download;
    this.currentPage = data.current_page || 1;
    this.lastProfile = data.last_profile || "";
  }

  addDownload(clipId: string): void {
    if (!this.downloadedIds.includes(clipId)) {
      this.downloadedIds.push(clipId);
      this.totalDownloaded = this.downloadedIds.length;
      this.lastDownload = new Date().toISOString();
    }
  }

  isDownloaded(clipId: string): boolean {
    return this.downloadedIds.includes(clipId);
  }

  clear(): void {
    this.downloadedIds = [];
    this.totalDownloaded = 0;
    this.lastDownload = undefined;
  }

  toDict(): Record<string, any> {
    return {
      account_name: this.account_name,
      downloaded_ids: this.downloadedIds,
      total_downloaded: this.totalDownloaded,
      last_download: this.lastDownload,
      current_page: this.currentPage,
      last_profile: this.lastProfile
    };
  }

  static fromDict(data: Record<string, any>): DownloadHistory {
    return new DownloadHistory({
      account_name: data.account_name,
      downloaded_ids: data.downloaded_ids || [],
      total_downloaded: data.total_downloaded || 0,
      last_download: data.last_download,
      current_page: data.current_page || 1,
      last_profile: data.last_profile || ""
    });
  }
}

export interface SongClipData {
  id: string;
  title: string;
  audio_url?: string;
  image_url?: string;
  tags: string;
  created_at?: string;
  duration?: number | string;
  display_name?: string;
  metadata?: {
    tags?: string;
    duration_formatted?: string;
    [key: string]: any;
  };
}

export class SongClip {
  id: string;
  title: string;
  audioUrl?: string;
  imageUrl?: string;
  tags: string;
  createdAt?: string;
  duration?: number | string;
  displayName?: string;
  metadata?: Record<string, any>;

  constructor(data: SongClipData) {
    this.id = data.id;
    this.title = data.title;
    this.audioUrl = data.audio_url;
    this.imageUrl = data.image_url;
    this.tags = data.tags || "";
    this.createdAt = data.created_at;
    this.duration = data.duration;
    this.displayName = data.display_name;
    this.metadata = data.metadata;
  }

  static fromApiResponse(data: Record<string, any>): SongClip {
    const metadata = data.metadata || {};

    return new SongClip({
      id: data.id || '',
      title: data.title || 'Unknown',
      audio_url: data.audio_url,
      image_url: data.image_url || data.image_large_url,
      tags: metadata.tags || '',
      created_at: data.created_at,
      duration: metadata.duration_formatted || data.duration,
      display_name: data.display_name,
      metadata: metadata
    });
  }

  toPythonDict(): Record<string, any> {
    return {
      id: this.id,
      title: this.title,
      audio_url: this.audioUrl,
      image_url: this.imageUrl,
      tags: this.tags,
      created_at: this.createdAt,
      duration: this.duration,
      display_name: this.displayName,
      metadata: this.metadata
    };
  }

  getFileName(): string {
    const sanitizedTitle = this.title.replace(/[^\w\s-]/g, '').replace(/\s+/g, '-').toLowerCase();
    return `${sanitizedTitle}-${this.id}`;
  }

  toDict(): Record<string, any> {
    return {
      id: this.id,
      title: this.title,
      audio_url: this.audioUrl,
      image_url: this.imageUrl,
      tags: this.tags,
      created_at: this.createdAt,
      duration: this.duration,
      display_name: this.displayName,
      metadata: this.metadata
    };
  }
}

export interface DownloadTaskData {
  clip: SongClipData;
  output_dir: string;
  with_thumbnail: boolean;
  append_uuid: boolean;
  status: "pending" | "downloading" | "completed" | "failed";
  progress: number;
  error_message?: string;
}

export class DownloadTask {
  clip: SongClip;
  outputDir: string;
  withThumbnail: boolean;
  appendUuid: boolean;
  status: "pending" | "downloading" | "completed" | "failed";
  progress: number;
  errorMessage?: string;

  constructor(data: DownloadTaskData) {
    this.clip = new SongClip(data.clip);
    this.outputDir = data.output_dir;
    this.withThumbnail = data.with_thumbnail;
    this.appendUuid = data.append_uuid;
    this.status = data.status || "pending";
    this.progress = data.progress || 0;
    this.errorMessage = data.error_message;
  }

  updateProgress(progress: number): void {
    this.progress = Math.min(100, Math.max(0, progress));
    if (this.progress > 0 && this.progress < 100) {
      this.status = "downloading";
    } else if (this.progress >= 100) {
      this.status = "completed";
    }
  }

  setError(error: string): void {
    this.errorMessage = error;
    this.status = "failed";
  }

  toDict(): Record<string, any> {
    return {
      clip: this.clip.toDict(),
      output_dir: this.outputDir,
      with_thumbnail: this.withThumbnail,
      append_uuid: this.appendUuid,
      status: this.status,
      progress: this.progress,
      error_message: this.errorMessage
    };
  }

  static fromDict(data: Record<string, any>): DownloadTask {
    return new DownloadTask({
      clip: data.clip,
      output_dir: data.output_dir,
      with_thumbnail: data.with_thumbnail,
      append_uuid: data.append_uuid,
      status: data.status || "pending",
      progress: data.progress || 0,
      error_message: data.error_message
    });
  }
}

export interface QueueEntryData {
  id: string;
  account_name: string;
  total_songs: number;
  songs_per_batch: number;
  prompts_range: [number, number];
  status: "pending" | "running" | "completed" | "failed" | "paused";
  created_at: string;
  completed_count: number;
}

export class QueueEntry {
  id: string;
  accountName: string;
  totalSongs: number;
  songsPerBatch: number;
  promptsRange: [number, number];
  status: "pending" | "running" | "completed" | "failed" | "paused";
  createdAt: string;
  completedCount: number;

  constructor(data: QueueEntryData) {
    this.id = data.id;
    this.accountName = data.account_name;
    this.totalSongs = data.total_songs;
    this.songsPerBatch = data.songs_per_batch;
    this.promptsRange = data.prompts_range || [0, 0];
    this.status = data.status || "pending";
    this.createdAt = data.created_at || new Date().toISOString();
    this.completedCount = data.completed_count || 0;
  }

  get progress(): number {
    if (this.totalSongs === 0) return 0;
    return Math.round((this.completedCount / this.totalSongs) * 100);
  }

  get remainingCount(): number {
    return this.totalSongs - this.completedCount;
  }

  updateCompleted(count: number): void {
    this.completedCount = Math.min(this.totalSongs, Math.max(0, count));
    if (this.completedCount >= this.totalSongs) {
      this.status = "completed";
    }
  }

  toDict(): Record<string, any> {
    return {
      id: this.id,
      account_name: this.accountName,
      total_songs: this.totalSongs,
      songs_per_batch: this.songsPerBatch,
      prompts_range: [...this.promptsRange],
      status: this.status,
      created_at: this.createdAt,
      completed_count: this.completedCount
    };
  }

  static fromDict(data: Record<string, any>): QueueEntry {
    const promptsRange = Array.isArray(data.prompts_range)
      ? [data.prompts_range[0], data.prompts_range[1]] as [number, number]
      : [0, 0];

    return new QueueEntry({
      id: data.id,
      account_name: data.account_name,
      total_songs: data.total_songs,
      songs_per_batch: data.songs_per_batch,
      prompts_range: promptsRange,
      status: data.status || "pending",
      created_at: data.created_at || new Date().toISOString(),
      completed_count: data.completed_count || 0
    });
  }
}

export interface SongCreationRecordData {
  song_id: string;
  title: string;
  prompt_index: number;
  account_name: string;
  status: "pending" | "creating" | "completed" | "failed";
  created_at: string;
  error_message?: string;
}

export class SongCreationRecord {
  songId: string;
  title: string;
  promptIndex: number;
  accountName: string;
  status: "pending" | "creating" | "completed" | "failed";
  createdAt: string;
  errorMessage?: string;

  constructor(data: SongCreationRecordData) {
    this.songId = data.song_id;
    this.title = data.title;
    this.promptIndex = data.prompt_index;
    this.accountName = data.account_name;
    this.status = data.status || "pending";
    this.createdAt = data.created_at || new Date().toISOString();
    this.errorMessage = data.error_message;
  }

  toDict(): Record<string, any> {
    return {
      song_id: this.songId,
      title: this.title,
      prompt_index: this.promptIndex,
      account_name: this.accountName,
      status: this.status,
      created_at: this.createdAt,
      error_message: this.errorMessage
    };
  }

  static fromDict(data: Record<string, any>): SongCreationRecord {
    return new SongCreationRecord({
      song_id: data.song_id,
      title: data.title,
      prompt_index: data.prompt_index,
      account_name: data.account_name,
      status: data.status || "pending",
      created_at: data.created_at || new Date().toISOString(),
      error_message: data.error_message
    });
  }
}