# AGENTS.md

**Audience:** AI coding agents, frontend developers  
**Applies to:** `src/ui/**/*.py`  
**Scope:** Panel patterns, component structure, threading model, CustomTkinter conventions  
**Last reviewed:** 2025-11-10  
**Owners:** UI team, frontend developers

---

## Component Structure

### Panel Hierarchy

```
MainWindow (CTk root)
├── Title Bar
├── Navigation (CTkSegmentedButton)
└── Content Frame (switches panels)
    ├── AccountPanel
    ├── MultipleSongsPanel (Queue)
    ├── CreateMusicPanel (Simple)
    ├── DownloadPanel
    ├── HistoryPanel
    └── SongCreationHistoryPanel
```

See `memory-bank/FLOW_DIAGRAMS.md#ui-component-hierarchy` for full diagram.

### Panel Pattern

All panels inherit from `ctk.CTkFrame`:

```python
class YourPanel(ctk.CTkFrame):
    def __init__(
        self,
        parent: ctk.CTkFrame,
        # Inject managers (never create inside panel!)
        account_manager: AccountManager,
        session_manager: SessionManager,
        **kwargs
    ):
        super().__init__(parent, **kwargs)
        
        # Store manager references
        self.account_manager = account_manager
        self.session_manager = session_manager
        
        # Build UI
        self._create_widgets()
        self._layout_widgets()
        
        # Load initial state
        self._refresh_data()
    
    def _create_widgets(self):
        """Create all widgets (buttons, labels, etc)"""
        self.button = ctk.CTkButton(self, text="Click", command=self.on_click)
    
    def _layout_widgets(self):
        """Arrange widgets with grid/pack"""
        self.button.pack(pady=10)
    
    def _refresh_data(self):
        """Load data from managers and update UI"""
        accounts = self.account_manager.get_all_accounts()
        # Update dropdown, labels, etc.
```

**Why this pattern?**
- Clear separation: creation → layout → data
- Testable: mock managers in constructor
- Maintainable: easy to find where widgets are created/placed

---

## Panel Patterns

### Dependency Injection

**✅ CORRECT:**
```python
# main_window.py
class MainWindow(ctk.CTk):
    def __init__(self):
        # Create managers ONCE
        self.account_manager = AccountManager()
        self.session_manager = SessionManager()
        self.queue_manager = QueueManager()
        
        # Inject into panels
        self.account_panel = AccountPanel(
            parent=self.content_frame,
            account_manager=self.account_manager,
            session_manager=self.session_manager
        )
```

**❌ WRONG:**
```python
class AccountPanel(ctk.CTkFrame):
    def __init__(self, parent):
        # Creates duplicate manager instance!
        self.account_manager = AccountManager()
```

### Progress Callbacks

Long operations (download, batch create) run in background threads and update UI via callbacks:

```python
class DownloadPanel(ctk.CTkFrame):
    def start_download(self):
        """Spawn background thread for download"""
        thread = threading.Thread(
            target=self.download_thread,
            args=(account, limit, output_path),
            daemon=True  # CRITICAL: Dies with main thread
        )
        thread.start()
    
    def download_thread(self, account: str, limit: int, output_path: Path):
        """Worker thread - does NOT touch UI directly"""
        try:
            # Do work...
            self.download_manager.batch_download(
                clips=clips,
                progress_callback=self.update_progress  # Pass callback
            )
        except Exception as e:
            # Update UI from thread (CustomTkinter allows this)
            self.show_error(str(e))
    
    def update_progress(self, message: str, percentage: int):
        """
        Called from worker thread.
        CustomTkinter widgets are thread-safe for configure().
        """
        self.progress_label.configure(text=message)
        self.progress_bar.set(percentage / 100)
```

**Why daemon=True?**
- Background threads die when main thread exits
- Prevents app hanging on close
- No zombie processes

---

## Threading Model

### Main Thread vs Background Threads

```
Main Thread (UI Event Loop)
├── Render UI
├── Handle clicks
├── Spawn background threads
└── Receive callbacks from workers

Background Thread 1 (Download)
├── Open Chrome
├── Extract token
├── Call API
├── Download files
└── Call UI callback ──┐
                       │
Background Thread 2    │
(Batch Create)         │
├── Open Chrome        │
├── Fill forms         │
├── Wait for creation  │
└── Call UI callback ──┴─→ Main Thread updates UI
```

**Rules:**
1. **Never block main thread** with long operations (I/O, browser launch)
2. **Always use `daemon=True`** for background threads
3. **CustomTkinter is thread-safe** for `configure()` calls
4. **Never create widgets** from background threads (only update existing ones)

### Example: Download Panel Threading

```python
def start_download(self):
    # Validate on main thread
    if not self.account_var.get():
        messagebox.showerror("Lỗi", "Vui lòng chọn tài khoản")
        return
    
    # Disable button (prevent double-click)
    self.download_button.configure(state="disabled")
    
    # Spawn worker
    thread = threading.Thread(
        target=self.download_thread,
        args=(self.account_var.get(), int(self.limit_var.get())),
        daemon=True
    )
    thread.start()

def download_thread(self, account: str, limit: int):
    try:
        # Long operation in background
        clips = self.download_manager.fetch_clips(account, limit)
        
        for i, clip in enumerate(clips):
            # Download work...
            
            # Update UI from worker (thread-safe)
            self.update_progress(f"Downloading {i+1}/{len(clips)}", (i+1)/len(clips)*100)
    
    except Exception as e:
        logger.error(f"Download failed: {e}", exc_info=True)
        self.show_error(str(e))
    
    finally:
        # Re-enable button
        self.download_button.configure(state="normal")
```

---

## CustomTkinter Conventions

### Widget Naming

```python
# Suffix by widget type
self.account_dropdown = ctk.CTkOptionMenu(...)
self.limit_entry = ctk.CTkEntry(...)
self.download_button = ctk.CTkButton(...)
self.progress_label = ctk.CTkLabel(...)
self.progress_bar = ctk.CTkProgressBar(...)

# StringVar/IntVar for input binding
self.account_var = ctk.StringVar()
self.limit_var = ctk.StringVar(value="10")
```

### Layout Patterns

**Grid Layout** (structured forms):
```python
def _layout_widgets(self):
    # Label-input pairs in 2 columns
    self.account_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
    self.account_dropdown.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
    
    self.limit_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
    self.limit_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)
    
    # Configure column weights for resize
    self.columnconfigure(1, weight=1)
```

**Pack Layout** (vertical stacks):
```python
def _layout_widgets(self):
    # Stack vertically with padding
    self.title_label.pack(pady=10, padx=20, anchor="w")
    self.description_label.pack(pady=5, padx=20, anchor="w")
    self.button_frame.pack(pady=10, padx=20, fill="x")
```

**Frames for Grouping**:
```python
# Create logical sections
self.config_frame = ctk.CTkFrame(self)
self.config_frame.pack(pady=10, padx=20, fill="x")

# Widgets inside frame
self.option1_checkbox = ctk.CTkCheckBox(self.config_frame, text="Option 1")
self.option1_checkbox.pack(pady=5, anchor="w")
```

### Colors & Styling

Use centralized style config:

```python
from config.style_config import COLORS, FONTS

# Buttons
self.primary_button = ctk.CTkButton(
    self,
    text="Bắt đầu",
    fg_color=COLORS["primary"],
    hover_color=COLORS["primary_hover"],
    font=FONTS["button"]
)

# Success/Warning/Danger states
self.status_label.configure(
    text="✅ Thành công",
    text_color=COLORS["success"]
)
```

### ScrollableFrame Pattern

For long content (lists, logs):

```python
class HistoryPanel(ctk.CTkFrame):
    def _create_widgets(self):
        # Scrollable area
        self.scrollable_frame = ctk.CTkScrollableFrame(
            self,
            width=600,
            height=400
        )
        self.scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add items dynamically
        for item in self.history:
            item_frame = self._create_history_item(item)
            item_frame.pack(fill="x", pady=5)
    
    def _create_history_item(self, item: dict) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.scrollable_frame)
        
        title_label = ctk.CTkLabel(frame, text=item["title"], font=("Arial", 14, "bold"))
        title_label.pack(anchor="w", padx=10, pady=5)
        
        date_label = ctk.CTkLabel(frame, text=item["date"], font=("Arial", 10))
        date_label.pack(anchor="w", padx=10, pady=2)
        
        return frame
```

---

## Reusable Components

Components in `src/ui/components/`:

### AdvancedOptionsWidget

Collapsible advanced options for song creation:

```python
from src.ui.components.advanced_options_widget import AdvancedOptionsWidget

class CreateMusicPanel(ctk.CTkFrame):
    def _create_widgets(self):
        self.advanced_options = AdvancedOptionsWidget(
            parent=self,
            on_change_callback=self.on_options_changed
        )
        self.advanced_options.pack(fill="x", pady=10)
    
    def on_options_changed(self, options: dict):
        """Called when any option changes"""
        self.current_options = options
        print(f"Options updated: {options}")
```

### PreviewWidget

Display generated XML prompts:

```python
from src.ui.components.preview_widget import PreviewWidget

class CreateMusicPanel(ctk.CTkFrame):
    def _create_widgets(self):
        self.preview = PreviewWidget(parent=self)
        self.preview.pack(fill="both", expand=True, pady=10)
    
    def show_preview(self, xml_content: str):
        self.preview.set_content(xml_content)
```

### SunoSelectors

CSS selectors for Suno.com automation:

```python
from src.ui.components.suno_selectors import SunoSelectors

# Use in form automation
lyrics_input = driver.find_element(By.CSS_SELECTOR, SunoSelectors.LYRICS_TEXTAREA)
```

---

## Panel-Specific Patterns

### AccountPanel

**Responsibility**: Account CRUD, profile management

```python
class AccountPanel(ctk.CTkFrame):
    def add_account(self):
        """
        Flow:
        1. Show dialog for name input
        2. Validate (no duplicates)
        3. Spawn background thread
        4. Launch Chrome for manual login
        5. Wait for user to close browser
        6. Save account to JSON
        7. Refresh dropdown
        """
        name = simpledialog.askstring("Thêm tài khoản", "Nhập tên:")
        if not name:
            return
        
        if self.account_manager.account_exists(name):
            messagebox.showerror("Lỗi", "Tên tài khoản đã tồn tại")
            return
        
        thread = threading.Thread(
            target=self.add_account_thread,
            args=(name,),
            daemon=True
        )
        thread.start()
```

### MultipleSongsPanel (Queue)

**Responsibility**: Queue management, batch creation

```python
class MultipleSongsPanel(ctk.CTkFrame):
    def upload_prompts(self):
        """
        1. Open file dialog (.xml)
        2. Parse with SunoPromptParser
        3. Display count in UI
        4. Enable "Add Queue" button
        """
        filepath = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not filepath:
            return
        
        parser = SunoPromptParser()
        self.prompts = parser.parse_file(filepath)
        self.prompts_label.configure(text=f"Đã load {len(self.prompts)} prompts")
        self.add_queue_button.configure(state="normal")
    
    def add_queue(self):
        """
        1. Validate inputs
        2. Call queue_manager.add_queue_entry()
        3. Refresh queue list
        4. Show success message
        """
        try:
            queue_id = self.queue_manager.add_queue_entry(
                account_name=self.account_var.get(),
                song_count=int(self.song_count_var.get()),
                batch_size=int(self.batch_size_var.get()),
                prompts=self.prompts
            )
            self.refresh_queue_list()
            messagebox.showinfo("Thành công", f"Đã thêm queue: {queue_id[:8]}")
        except QueueValidationError as e:
            messagebox.showerror("Lỗi", str(e))
```

### CreateMusicPanel (Simple)

**Responsibility**: Single song creation with preview

```python
class CreateMusicPanel(ctk.CTkFrame):
    def __init__(self, parent, **managers):
        super().__init__(parent)
        # 2-column layout
        self.left_column = ctk.CTkScrollableFrame(self, width=500)
        self.left_column.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        self.right_column = ctk.CTkFrame(self, width=400)
        self.right_column.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Left: Input form
        # Right: Preview + actions
```

### DownloadPanel

**Responsibility**: Download orchestration with progress

```python
class DownloadPanel(ctk.CTkFrame):
    def start_download(self):
        """
        Threading pattern:
        1. Validate inputs on main thread
        2. Disable button
        3. Spawn download_thread
        4. Thread calls progress_callback
        5. Finally: re-enable button
        """
        # See Threading Model section above
```

---

## Error Handling

### User-Facing Errors

Use `messagebox` for errors:

```python
from tkinter import messagebox

# Error
messagebox.showerror("Lỗi", "Vui lòng chọn tài khoản")

# Warning
messagebox.showwarning("Cảnh báo", "Profile đang được sử dụng")

# Info
messagebox.showinfo("Thành công", "Tải xuống hoàn tất")

# Question
result = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?")
if result:
    # User clicked Yes
```

### Status Messages

Use labels with color coding:

```python
def show_status(self, message: str, status_type: str = "info"):
    """
    status_type: "info" | "success" | "warning" | "error"
    """
    colors = {
        "info": COLORS["info"],
        "success": COLORS["success"],
        "warning": COLORS["warning"],
        "error": COLORS["danger"]
    }
    
    self.status_label.configure(
        text=message,
        text_color=colors.get(status_type, COLORS["info"])
    )
```

---

## Tab Navigation

Implemented in `MainWindow`:

```python
class MainWindow(ctk.CTk):
    def __init__(self):
        # Segmented button for tab switching
        self.nav_bar = ctk.CTkSegmentedButton(
            self,
            values=["🎵 Tài khoản", "🎼 Tạo Nhiều", "🎵 Tạo Nhạc", "📥 Download", "📜 Lịch sử"],
            command=self.on_tab_change
        )
        self.nav_bar.set("🎵 Tài khoản")  # Default tab
    
    def on_tab_change(self, value: str):
        """Hide all panels, show selected one"""
        panels = {
            "🎵 Tài khoản": self.account_panel,
            "🎼 Tạo Nhiều": self.multiple_songs_panel,
            "🎵 Tạo Nhạc": self.create_music_panel,
            "📥 Download": self.download_panel,
            "📜 Lịch sử": self.history_panel
        }
        
        # Hide all
        for panel in panels.values():
            panel.pack_forget()
        
        # Show selected
        panels[value].pack(fill="both", expand=True)
```

---

## Testing UI Components

Mock managers and test logic without launching GUI:

```python
from unittest.mock import MagicMock
import pytest

def test_account_panel_add_validation():
    # Mock managers
    mock_account_manager = MagicMock()
    mock_account_manager.account_exists.return_value = True
    
    # Create panel (won't render in test)
    panel = AccountPanel(
        parent=MagicMock(),  # Mock parent
        account_manager=mock_account_manager,
        session_manager=MagicMock()
    )
    
    # Test validation logic
    # (avoid testing actual GUI rendering)
    assert panel.account_manager.account_exists("test")
```

For full UI testing, see `tests/AGENTS.md#ui-testing`.

---

## Entry Points

| File | Panel Class | Responsibility |
|------|------------|----------------|
| `main_window.py` | `MainWindow` | Root window, manager init, tab navigation |
| `account_panel.py` | `AccountPanel` | Account CRUD, profile management |
| `multiple_songs_panel.py` | `MultipleSongsPanel` | Queue management, batch creation |
| `create_music_panel.py` | `CreateMusicPanel` | Single song creation with preview |
| `download_panel.py` | `DownloadPanel` | Download orchestration |
| `history_panel.py` | `HistoryPanel` | Download history display |
| `song_creation_history_panel.py` | `SongCreationHistoryPanel` | Creation history, CSV export |

---

## Cross-References

- **Manager patterns**: See `src/core/AGENTS.md#manager-lifecycle`
- **Configuration**: See `config/AGENTS.md#path-constants`
- **Architecture**: See `memory-bank/FLOW_DIAGRAMS.md#ui-component-hierarchy`
- **Threading**: See this file's [Threading Model](#threading-model) section

---

**Questions?** Check root `AGENTS.md` for general guidelines.
