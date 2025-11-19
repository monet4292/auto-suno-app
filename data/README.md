# Data Directory

Thư mục chứa các file dữ liệu runtime của ứng dụng.

## Files

### `suno_accounts.json` - Database tài khoản
**Format:**
```json
{
    "account_name": {
        "email": "user@example.com",
        "created_at": "2025-11-09 01:26:44",
        "last_used": "2025-11-09 03:56:27",
        "status": "active"
    }
}
```

**Mục đích:**
- Lưu danh sách tài khoản Suno
- Mapping account name → metadata
- Liên kết với Chrome profiles trong `profiles/`

**Được quản lý bởi:** `src/core/account_manager.py`

---

### `download_history.json` - Lịch sử downloads
**Format:**
```json
{
    "account_name": {
        "downloaded_ids": ["uuid-1", "uuid-2"],
        "total_downloaded": 2,
        "last_download": "2025-11-09 02:35:10",
        "current_page": 1,
        "last_profile": "@username"
    }
}
```

**Mục đích:**
- Theo dõi bài hát đã tải (tránh duplicate)
- Resume downloads từ trang cuối
- Thống kê số lượng đã tải
- Auto-skip bài đã có

**Được quản lý bởi:** `src/core/download_manager.py`

---

### `settings.json` (future)
Sẽ chứa cấu hình app: theme, download path, etc.

---

## ⚠️ Lưu ý

- **KHÔNG xóa** các file này trừ khi muốn reset app
- File sẽ được tạo tự động nếu không tồn tại
- Nội dung được load khi khởi động app
- Được save mỗi khi có thay đổi

## Git

Các file này **không chứa thông tin nhạy cảm** (không có password/token), 
có thể commit để sync giữa các máy.

Nếu muốn ignore:
```gitignore
data/*.json
!data/README.md
```
