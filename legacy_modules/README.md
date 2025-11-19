# Legacy Modules

Thư mục chứa các module core từ v1.0 vẫn đang được sử dụng bởi main app.

## Modules

### `suno_batch_download.py`
- **Mục đích:** Download hàng loạt bài hát từ Suno
- **Được sử dụng bởi:**
  - `src/core/download_manager.py`
  - `src/ui/download_panel.py`
- **Tính năng:**
  - Fetch clips từ Suno API
  - Download MP3 với metadata
  - Pagination support
  - Auto-resume downloads

### `suno_auto_create.py`
- **Mục đích:** Tự động tạo bài hát trên Suno
- **Được sử dụng bởi:**
  - `src/ui/create_music_panel.py`
- **Tính năng:**
  - Điền form tạo nhạc tự động
  - Hỗ trợ Custom Mode
  - Batch creation với nhiều tabs

## Import Pattern

```python
from legacy_modules import SunoBatchDownloader
from legacy_modules import SunoMusicCreator, SunoCreateConfig
```

## Tương lai

Các module này sẽ được refactor dần vào `src/core/` theo Clean Architecture.
Hiện tại giữ nguyên để đảm bảo tính tương thích.
