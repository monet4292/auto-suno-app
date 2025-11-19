# UI Components Guide

## Overview

This guide provides comprehensive documentation for the UI components of the Suno Account Manager application, built with CustomTkinter.

## Architecture

The UI follows a modular architecture with separate panels for different functionalities:
- **MainWindow**: Main application container
- **Account Panel**: Account management interface
- **Create Panel**: Song creation interface
- **Download Panel**: Song download management
- **History Panel**: Creation history tracking
- **Multiple Songs Panel**: Batch song creation

---

## MainWindow

### Overview
Main application window that orchestrates all UI components and manages the application lifecycle.

### Key Features
- Tab-based interface for different functionalities
- Menu bar with file operations and help
- Status bar with application state information
- Responsive layout management

### Methods
```python
def run_app():
    """Entry point for the application"""

def __init__(self):
    """Initialize main window with all panels"""

def setup_ui(self):
    """Setup UI components and layout"""
```

---

## AccountPanel

### Overview
Manages Suno account credentials and authentication state.

### Components
- Account list display
- Add/Edit/Delete account functionality
- Login status indicators
- Account switching interface

### Key Methods
```python
def add_account(self, username: str, password: str):
    """Add new Suno account"""

def edit_account(self, account_id: str, username: str, password: str):
    """Edit existing account credentials"""

def delete_account(self, account_id: str):
    """Remove account from the system"""

def login_account(self, account_id: str):
    """Authenticate with Suno using stored credentials"""
```

### Usage Pattern
```python
# Access account panel
account_panel = main_window.account_panel

# Add new account
account_panel.add_account("username", "password")

# Check login status
is_logged_in = account_panel.is_account_logged_in(account_id)
```

---

## CreateMusicPanel

### Overview
Interface for creating individual songs with Suno AI.

### Features
- Title and lyrics input fields
- Style selection dropdown
- Instrumental toggle
- Generation parameters configuration
- Real-time preview of generated content

### Key Methods
```python
def create_song(self, title: str, lyrics: str, style: str, instrumental: bool):
    """Create a single song with specified parameters"""

def preview_generation(self):
    """Preview song generation settings"""

def reset_form(self):
    """Clear all input fields"""
```

### UI Elements
- **Title Entry**: Text input for song title
- **Lyrics Text**: Multi-line text input for song lyrics
- **Style Dropdown**: Selection for musical style
- **Instrumental Switch**: Toggle for instrumental-only generation
- **Generate Button**: Triggers song creation

### Configuration Options
- `max_lyrics_length`: Maximum allowed lyrics characters
- `style_options`: Available musical styles
- `generation_timeout`: Timeout for song creation

---

## MultipleSongsPanel

### Overview
Advanced interface for batch song creation with queue management.

### Features
- Multiple prompt input (file upload or manual entry)
- Batch size configuration
- Account assignment for batches
- Progress tracking for batch operations
- Queue management integration

### Key Methods
```python
def load_prompts_from_file(self, file_path: str):
    """Load song prompts from CSV/JSON file"""

def create_batch(self, prompts: List[SunoPrompt], account_name: str, batch_size: int):
    """Create batch of songs with specified parameters"""

def monitor_progress(self, queue_id: str):
    """Monitor progress of batch creation"""
```

### File Formats Supported

#### CSV Format
```csv
title,lyrics,style
Song Title 1,"Lyrics for song 1","Pop"
Song Title 2,"Lyrics for song 2","Rock"
```

#### JSON Format
```json
[
  {
    "title": "Song Title 1",
    "lyrics": "Lyrics for song 1",
    "style": "Pop"
  },
  {
    "title": "Song Title 2",
    "lyrics": "Lyrics for song 2",
    "style": "Rock"
  }
]
```

### Batch Configuration
- `max_batch_size`: Maximum songs per batch (default: 10)
- `concurrent_batches`: Number of simultaneous batches
- `retry_attempts`: Number of retry attempts on failure

---

## DownloadPanel

### Overview
Manages downloading of generated songs to local storage.

### Features
- Download queue display
- Download progress tracking
- File format selection (MP3, WAV)
- Download location configuration
- Pause/Resume download functionality

### Key Methods
```python
def download_song(self, song_id: str, format: str, output_path: str):
    """Download specific song in specified format"""

def pause_download(self, download_id: str):
    """Pause active download"""

def resume_download(self, download_id: str):
    """Resume paused download"""

def cancel_download(self, download_id: str):
    """Cancel and remove download"""
```

### Download Options
- **Format Selection**: MP3, WAV, FLAC
- **Quality Settings**: Standard, High, Lossless
- **Metadata**: Include song metadata in downloaded files
- **Folder Organization**: Automatic folder creation by artist/album

---

## HistoryPanel

### Overview
Tracks and displays song creation history with filtering and search capabilities.

### Features
- Chronological song creation history
- Search by title, style, or date
- Status tracking (pending, completed, failed)
- Export functionality
- Detailed song information display

### Key Methods
```python
def load_history(self):
    """Load song creation history from database"""

def search_history(self, query: str, filters: dict):
    """Search history with specified criteria"""

def export_history(self, format: str, output_path: str):
    """Export history to CSV, JSON, or Excel"""
```

### Display Options
- **List View**: Compact list with key information
- **Detail View**: Expanded view with full song details
- **Status Filters**: Show only specific statuses
- **Date Range**: Filter by creation date range

---

## SongCreationHistoryPanel

### Overview
Specialized panel for detailed tracking of song creation processes.

### Features
- Real-time creation progress
- Step-by-step process tracking
- Error reporting and debugging information
- Performance metrics

### Tracking Information
- Creation start/end times
- Processing duration
- API response times
- Error messages and stack traces
- Resource usage statistics

---

## UI Components Library

### AdvancedOptionsWidget

Advanced configuration widget for song generation parameters.

```python
class AdvancedOptionsWidget:
    def __init__(self, parent):
        self.parent = parent
        self.setup_ui()

    def setup_ui(self):
        # Temperature slider
        # Duration control
        # Vocals/instrumental balance
        # Custom model parameters
```

### PreviewWidget

Widget for previewing song generation settings and metadata.

```python
class PreviewWidget:
    def update_preview(self, title: str, lyrics: str, style: str):
        """Update preview with current settings"""

    def show_metadata(self, metadata: dict):
        """Display song metadata preview"""
```

### SunoSelectors

UI selector components for Suno-specific options.

```python
class SunoSelectors:
    def get_style_selector(self):
        """Return style selection dropdown"""

    def get_instrumental_selector(self):
        """Return instrumental/vocal options"""

    def get_quality_selector(self):
        """Return quality settings selector"""
```

---

## Styling and Theming

### Theme Configuration
Application supports light and dark themes with customizable colors:

```python
# Light theme colors
LIGHT_THEME = {
    "bg_color": "#FFFFFF",
    "fg_color": "#000000",
    "button_color": "#007BFF",
    "success_color": "#28A745",
    "error_color": "#DC3545"
}

# Dark theme colors
DARK_THEME = {
    "bg_color": "#2B2B2B",
    "fg_color": "#FFFFFF",
    "button_color": "#0D6EFD",
    "success_color": "#198754",
    "error_color": "#DC3545"
}
```

### Custom Styling
Components can be customized through the style configuration system:

```python
def apply_custom_style(self, component_type: str, style_dict: dict):
    """Apply custom styling to component type"""
```

---

## Event Handling

### Event Types
- **Button Clicks**: User interactions with buttons
- **Form Submissions**: Data entry form submissions
- **Selection Changes**: Dropdown/selection changes
- **Progress Updates**: Background task progress updates
- **Status Changes**: Application state changes

### Event Handler Pattern
```python
def on_button_click(self, event):
    """Handle button click events"""

def on_form_submit(self, form_data: dict):
    """Handle form submission with validation"""

def on_progress_update(self, progress_data: dict):
    """Handle progress update from background tasks"""
```

---

## Accessibility

### Keyboard Navigation
- Tab navigation between components
- Enter key for form submission
- Escape key for dialog cancellation
- Shortcut keys for common operations

### Screen Reader Support
- Proper ARIA labels and descriptions
- Semantic HTML structure
- Focus management
- Status announcements

### Visual Accessibility
- High contrast themes
- Adjustable font sizes
- Color blind friendly palettes
- Clear visual indicators

---

## Performance Optimization

### UI Responsiveness
- Asynchronous operations for long-running tasks
- Progress indicators for user feedback
- Lazy loading of large data sets
- Efficient redrawing and layout updates

### Memory Management
- Proper widget cleanup on panel switching
- Limited history retention with pagination
- Efficient data structures for large datasets
- Memory monitoring and cleanup

---

## Testing

### Unit Tests
UI component testing with simulated user interactions:

```python
def test_account_panel_add_account():
    """Test adding account through UI"""

def test_create_panel_form_validation():
    """Test form validation in create panel"""

def test_download_panel_progress_tracking():
    """Test download progress display"""
```

### Integration Tests
End-to-end UI workflow testing:

```python
def test_complete_song_creation_workflow():
    """Test full song creation from UI"""

def test_batch_creation_and_download():
    """Test batch creation and download workflow"""
```

---

## Future Enhancements

### Planned UI Features
- Drag and drop file upload
- Real-time collaboration features
- Advanced filtering and search
- Custom dashboard layouts
- Mobile-responsive design

### Performance Improvements
- Virtual scrolling for large lists
- Component lazy loading
- Optimized rendering pipelines
- GPU-accelerated graphics