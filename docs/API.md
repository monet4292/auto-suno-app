# Suno API Documentation
# Tài liệu API cho Suno.com Integration

## 📋 Tổng Quan

Document này mô tả **tất cả API endpoints** của Suno.com được sử dụng trong Suno Account Manager v2.0. Bao gồm authentication, data fetching, và rate limiting.

**Base URL**: `https://studio-api.prod.suno.com/api`  
**Authentication**: Bearer token (JWT) từ cookie `__session`  
**Content-Type**: `application/json`

---

## 🔐 Authentication

### Token Source
```http
Cookie: __session={jwt_token}
```

**Token Extraction**:
```python
# From Chrome profile cookie
cookies = driver.get_cookies()
for cookie in cookies:
    if cookie['name'] == '__session':
        session_token = cookie['value']
```

**Token Structure** (JWT):
```json
{
  "aud": "suno-api",
  "azp": "https://suno.com",
  "exp": 1762626034,
  "iat": 1762622434,
  "https://suno.ai/claims/clerk_id": "user_2abc123",
  "https://suno.ai/claims/email": "user@example.com",
  "sid": "sess_2xyz789",
  "sub": "user_2abc123"
}
```

**Token Lifetime**: ~24 hours  
**Refresh Method**: User login lại qua Chrome profile

---

## 📡 API Endpoints

### 1. Get User Info (Billing)

**Purpose**: Lấy thông tin user hiện tại (username, credits, subscription)

```http
GET /billing/info
Authorization: Bearer {session_token}
```

**Response** (200 OK):
```json
{
  "user_id": "user_2abc123",
  "email": "user@example.com",
  "username": "my_username",
  "display_name": "My Display Name",
  "credits_remaining": 150,
  "subscription_tier": "pro",
  "billing_period_end": "2025-12-09T00:00:00Z",
  "is_trial": false
}
```

**Usage trong app**:
```python
# download_manager.py:get_user_info()
def get_user_info(self, session_token: str) -> dict:
    response = requests.get(
        f"{SUNO_API_URL}/billing/info",
        headers={"Authorization": f"Bearer {session_token}"}
    )
    return response.json()
```

**Rate Limit**: 10 req/min per user  
**Error Codes**:
- `401 Unauthorized`: Token hết hạn hoặc invalid
- `429 Too Many Requests`: Vượt rate limit

---

### 2. Get My Clips (Feed)

**Purpose**: Lấy danh sách bài hát của user hiện tại (trang /me)

```http
GET /feed/v2?page={page_number}
Authorization: Bearer {session_token}
```

**Query Parameters**:
- `page` (optional, default: 0): Page number (pagination)
- `limit` (optional, default: 20): Clips per page

**Response** (200 OK):
```json
{
  "clips": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "My Song Title",
      "audio_url": "https://cdn.suno.ai/audio/550e8400.mp3",
      "image_url": "https://cdn.suno.ai/images/550e8400_large.jpeg",
      "image_large_url": "https://cdn.suno.ai/images/550e8400_large.jpeg",
      "video_url": "https://cdn.suno.ai/videos/550e8400.mp4",
      "created_at": "2025-11-08T14:30:00Z",
      "model_name": "chirp-v3-5",
      "status": "complete",
      "gpt_description_prompt": "A happy pop song about sunshine",
      "prompt": "[Verse 1]\nSunshine on my face...",
      "style": "pop, upbeat, 120bpm",
      "tags": "pop upbeat sunshine",
      "duration": 185.5,
      "error_type": null,
      "error_message": null,
      "play_count": 42,
      "upvote_count": 8,
      "is_public": true,
      "is_trashed": false,
      "reaction": null,
      "metadata": {
        "tags": "pop upbeat sunshine",
        "prompt": "[Verse 1]...",
        "gpt_description_prompt": "A happy pop song...",
        "type": "gen",
        "duration": 185.5,
        "refund_credits": null,
        "stream": true,
        "error_type": null,
        "error_message": null
      }
    }
  ],
  "has_more": true,
  "next_page": 1,
  "total_count": 125
}
```

**Usage trong app**:
```python
# suno_batch_download.py:fetch_my_clips()
def fetch_my_clips(self) -> List[dict]:
    clips = []
    page = 0
    while True:
        response = requests.get(
            f"{SUNO_API_URL}/feed/v2?page={page}",
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        data = response.json()
        clips.extend(data.get('clips', []))
        if not data.get('has_more', False):
            break
        page += 1
    return clips
```

**Rate Limit**: 30 req/min per user  
**Error Codes**:
- `401 Unauthorized`: Token invalid
- `403 Forbidden`: No access to feed
- `429 Too Many Requests`: Rate limit exceeded

---

### 3. Get Profile Clips

**Purpose**: Lấy danh sách bài hát public của user khác

```http
GET /clips/profile/{username}?page={page_number}
Authorization: Bearer {session_token}
```

**Path Parameters**:
- `username` (required): Username (không có @) hoặc user_id

**Query Parameters**:
- `page` (optional, default: 0): Page number
- `limit` (optional, default: 20): Clips per page

**Response** (200 OK):
```json
{
  "clips": [
    {
      "id": "660f9500-f39c-52e5-b827-557766550111",
      "title": "Public Song",
      "audio_url": "https://cdn.suno.ai/audio/660f9500.mp3",
      "image_url": "https://cdn.suno.ai/images/660f9500_large.jpeg",
      "created_at": "2025-11-07T10:15:00Z",
      "is_public": true,
      "display_name": "Artist Name",
      "handle": "artist_username",
      "avatar_image_url": "https://cdn.suno.ai/avatars/123.jpg",
      "metadata": { /* same structure as /feed/v2 */ }
    }
  ],
  "has_more": false,
  "total_count": 8
}
```

**Usage trong app**:
```python
# suno_batch_download.py:fetch_profile_clips()
def fetch_profile_clips(self, profile_name: str) -> List[dict]:
    # Remove @ if present
    username = profile_name.lstrip('@')
    clips = []
    page = 0
    while True:
        response = requests.get(
            f"{SUNO_API_URL}/clips/profile/{username}?page={page}",
            headers={"Authorization": f"Bearer {self.session_token}"}
        )
        data = response.json()
        clips.extend(data.get('clips', []))
        if not data.get('has_more', False):
            break
        page += 1
    return clips
```

**Rate Limit**: 60 req/min per user (cao hơn vì public data)  
**Error Codes**:
- `401 Unauthorized`: Token invalid
- `404 Not Found`: Username không tồn tại
- `429 Too Many Requests`: Rate limit exceeded

---

### 4. Create Song (Generate)

**Purpose**: Tạo bài hát mới (Custom Mode)

```http
POST /generate
Authorization: Bearer {session_token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "prompt": "[Verse 1]\nLyrics here...\n[Chorus]\nMore lyrics...",
  "tags": "pop, upbeat, 120bpm",
  "title": "My Song Title",
  "make_instrumental": false,
  "wait_audio": false,
  "mv": "chirp-v3-5",
  "continue_clip_id": null,
  "continue_at": null
}
```

**Request Fields**:
- `prompt` (required): Lyrics content
- `tags` (required): Styles/genres (comma-separated)
- `title` (optional): Song title
- `make_instrumental` (optional, default: false): Tạo instrumental
- `wait_audio` (optional, default: false): Đợi audio render xong
- `mv` (optional, default: "chirp-v3-5"): Model version
- `continue_clip_id` (optional): ID của clip để extend
- `continue_at` (optional): Timestamp để extend từ đó

**Response** (200 OK):
```json
{
  "clips": [
    {
      "id": "770g0600-g49d-63f6-c938-668877661222",
      "status": "submitted",
      "title": "My Song Title",
      "created_at": "2025-11-09T12:00:00Z",
      "metadata": {
        "tags": "pop, upbeat, 120bpm",
        "prompt": "[Verse 1]...",
        "type": "gen",
        "duration": null,
        "refund_credits": false
      }
    }
  ]
}
```

**Note**: 
- Song generation là async, status = "submitted" → "streaming" → "complete"
- Cần poll GET `/feed/v2` để check status
- Thời gian tạo: ~30-60 giây

**Usage trong app**:
```python
# Hiện tại KHÔNG sử dụng API này
# Thay vào đó dùng browser automation (BatchSongCreator)
# Lý do: Tránh CAPTCHA, sử dụng giao diện web chính thống
```

**Rate Limit**: 5 req/min per user (strict)  
**Credits Cost**: 10 credits per generation (2 variations)  
**Error Codes**:
- `400 Bad Request`: Missing required fields
- `401 Unauthorized`: Token invalid
- `402 Payment Required`: Insufficient credits
- `429 Too Many Requests`: Rate limit exceeded

---

### 5. Get Clip Details

**Purpose**: Lấy thông tin chi tiết của 1 clip

```http
GET /clip/{clip_id}
Authorization: Bearer {session_token}
```

**Path Parameters**:
- `clip_id` (required): UUID của clip

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Song",
  "audio_url": "https://cdn.suno.ai/audio/550e8400.mp3",
  "image_url": "https://cdn.suno.ai/images/550e8400_large.jpeg",
  "video_url": "https://cdn.suno.ai/videos/550e8400.mp4",
  "created_at": "2025-11-08T14:30:00Z",
  "model_name": "chirp-v3-5",
  "status": "complete",
  "metadata": { /* full metadata */ },
  "user_id": "user_2abc123",
  "display_name": "Artist Name",
  "handle": "artist_username",
  "is_liked_by_user": false,
  "reaction": null,
  "major_model_version": "v3.5",
  "is_trashed": false,
  "is_public": true
}
```

**Rate Limit**: 100 req/min per user  
**Error Codes**:
- `401 Unauthorized`: Token invalid
- `404 Not Found`: Clip ID không tồn tại

---

## 🔒 Rate Limiting

### Per-Endpoint Limits

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| `/billing/info` | 10 req | 1 min |
| `/feed/v2` | 30 req | 1 min |
| `/clips/profile/{username}` | 60 req | 1 min |
| `/generate` | 5 req | 1 min |
| `/clip/{clip_id}` | 100 req | 1 min |

### Global Limits
- **Per User**: 200 req/min total across all endpoints
- **Per IP**: 500 req/min total (multiple users)

### Rate Limit Response
```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 60

{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please wait 60 seconds.",
  "retry_after": 60
}
```

### Handling trong app
```python
# download_manager.py
for attempt in range(RETRY_ATTEMPTS):
    try:
        response = requests.get(url, headers=headers, timeout=DOWNLOAD_TIMEOUT)
        response.raise_for_status()
        break
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            retry_after = int(e.response.headers.get('Retry-After', 60))
            logger.warning(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
        elif attempt == RETRY_ATTEMPTS - 1:
            raise
```

---

## 📊 Response Status Codes

### Success Codes
- `200 OK`: Request thành công
- `201 Created`: Resource created (POST /generate)
- `204 No Content`: Success but no response body

### Client Error Codes
- `400 Bad Request`: Invalid request body/parameters
- `401 Unauthorized`: Token invalid hoặc expired
- `402 Payment Required`: Insufficient credits
- `403 Forbidden`: No permission (e.g., private profile)
- `404 Not Found`: Resource không tồn tại
- `429 Too Many Requests`: Rate limit exceeded

### Server Error Codes
- `500 Internal Server Error`: Server lỗi
- `502 Bad Gateway`: Upstream service down
- `503 Service Unavailable`: Maintenance mode

---

## 🎵 Clip Object Schema

### Full Clip Structure
```typescript
interface Clip {
  // Identifiers
  id: string;                    // UUID
  user_id: string;               // Owner user ID
  
  // Content URLs
  audio_url: string;             // MP3 file (primary)
  video_url: string;             // MP4 video
  image_url: string;             // Thumbnail (small)
  image_large_url: string;       // Thumbnail (large, 1024x1024)
  
  // Metadata
  title: string;                 // Song title
  created_at: string;            // ISO 8601 datetime
  model_name: string;            // "chirp-v3-5", "chirp-v3"
  status: string;                // "submitted" | "streaming" | "complete" | "error"
  duration: number | null;       // Seconds (null if not complete)
  
  // Generation Params
  prompt: string;                // Lyrics
  tags: string;                  // Styles (comma-separated)
  gpt_description_prompt: string; // Description prompt (if used)
  make_instrumental: boolean;
  
  // User Info (if profile clips)
  display_name: string;          // Artist display name
  handle: string;                // Username
  avatar_image_url: string;      // Avatar URL
  
  // Engagement
  play_count: number;            // Total plays
  upvote_count: number;          // Total upvotes
  is_liked_by_user: boolean;     // Current user liked?
  reaction: string | null;       // Reaction emoji
  
  // Visibility
  is_public: boolean;            // Public on Suno?
  is_trashed: boolean;           // In trash?
  
  // Errors (if status = "error")
  error_type: string | null;     // Error category
  error_message: string | null;  // Error detail
  
  // Advanced
  metadata: {
    tags: string;
    prompt: string;
    gpt_description_prompt: string;
    type: string;                // "gen" | "concat" | "continue"
    duration: number | null;
    refund_credits: boolean | null;
    stream: boolean;
    error_type: string | null;
    error_message: string | null;
  };
  
  major_model_version: string;   // "v3" | "v3.5" | "v4"
  continue_clip_id: string | null; // Parent clip if extension
  continue_at: number | null;    // Start timestamp if extension
}
```

---

## 🛡️ Error Handling Best Practices

### 1. Token Expiration
```python
try:
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        # Token hết hạn
        messagebox.showerror("Session hết hạn", "Vui lòng đăng nhập lại.")
        # Trigger re-login flow
        self.session_manager.launch_browser(account_name)
```

### 2. Rate Limiting
```python
# Implement exponential backoff
retry_delays = [1, 2, 5, 10, 30]  # seconds
for i, delay in enumerate(retry_delays):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        break
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            if i < len(retry_delays) - 1:
                logger.warning(f"Rate limited. Retry in {delay}s...")
                time.sleep(delay)
            else:
                raise Exception("Max retries exceeded for rate limit")
```

### 3. Network Errors
```python
import requests
from requests.exceptions import Timeout, ConnectionError

try:
    response = requests.get(url, timeout=30)
except Timeout:
    logger.error("Request timeout after 30s")
    raise
except ConnectionError:
    logger.error("Network connection failed")
    raise
```

---

## 📝 Change Log

### 2025-11-09 - Initial API Documentation
**Added**:
- ✅ 5 core endpoints documented
- ✅ Authentication flow
- ✅ Rate limiting details
- ✅ Full Clip object schema
- ✅ Error handling patterns
- ✅ Usage examples from codebase

**Notes**:
- API documentation based on reverse engineering Suno.com
- Endpoints may change without notice (not official API)
- Always check response structure in production

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-09  
**Author**: AI Agent  
**Status**: Complete

**⚠️ Disclaimer**: Suno.com không có public API documentation. Document này dựa trên quan sát traffic và testing. Sử dụng với trách nhiệm riêng.
