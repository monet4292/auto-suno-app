"""
Main Application Window
"""
import customtkinter as ctk
from typing import Optional

from config.settings import APP_NAME, APP_VERSION, APP_WIDTH, APP_HEIGHT, THEME, APPEARANCE_MODE
from src.core import (
    AccountManager,
    QueueManager,
    SessionManager,
    DownloadManager,
    SongCreationHistoryManager
)
from src.ui.account_panel import AccountPanel
from src.ui.download_panel import DownloadPanel
from src.ui.history_panel import HistoryPanel
from src.ui.create_music_panel import CreateMusicPanel
from src.ui.multiple_songs_panel import MultipleSongsPanel
from src.ui.song_creation_history_panel import SongCreationHistoryPanel
from src.utils import logger


class MainWindow(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Set theme
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(THEME)
        
        # Window configuration
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.window_width = APP_WIDTH
        self.window_height = 750
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.minsize(APP_WIDTH, self.window_height)  # Minimum size
        
        # Center window
        self.center_window()
        
        # Initialize managers
        self.account_manager = AccountManager()
        self.session_manager = SessionManager()
        self.download_manager = DownloadManager()
        self.queue_manager = QueueManager()
        self.song_creation_history_manager = SongCreationHistoryManager()
        
        # Create UI
        self.create_ui()
        
        logger.info("Application started")
    
    def center_window(self):
        """Center window on screen"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.window_width // 2)
        y = (self.winfo_screenheight() // 2) - (self.window_height // 2)
        self.geometry(f'{self.window_width}x{self.window_height}+{x}+{y}')
    
    def create_ui(self):
        """Create main UI"""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.create_tabbar()
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.panels = {}
        self.active_tab = "accounts"
        self.create_panels()
        self.tab_buttons.set(self.key_to_label[self.active_tab])
        self._show_current_tab()
    
    def create_tabbar(self):
        self.tab_map = [
            ("accounts", "Tài khoản"),
            ("create_music", "Tạo nhạc"),
            ("multiple_songs", "Tạo nhiều bài"),
            ("download", "Download"),
            ("history", "Lịch sử Download"),
            ("song_creation_history", "Lịch sử Tạo bài hát"),
        ]
        self.key_to_label = {key: label for key, label in self.tab_map}
        self.label_to_key = {label: key for key, label in self.tab_map}
        labels = [label for _, label in self.tab_map]

        self.tab_buttons = ctk.CTkSegmentedButton(
            self,
            values=labels,
            command=self._on_tab_click,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.tab_buttons.grid(row=0, column=0, sticky="ew", padx=20, pady=(10, 5))

    def create_panels(self):
        """Create all content panels"""

        self.panels["accounts"] = AccountPanel(
            self.content_frame,
            self.account_manager,
            self.session_manager
        )

        self.panels["create_music"] = CreateMusicPanel(
            self.content_frame,
            self.account_manager,
            self.session_manager
        )

        self.panels["multiple_songs"] = MultipleSongsPanel(
            self.content_frame,
            self.account_manager,
            self.queue_manager,
            self.session_manager,
            self.song_creation_history_manager
        )

        self.panels["download"] = DownloadPanel(
            self.content_frame,
            self.account_manager,
            self.session_manager,
            self.download_manager
        )

        self.panels["history"] = HistoryPanel(
            self.content_frame,
            self.account_manager,
            self.download_manager
        )
        self.panels["song_creation_history"] = SongCreationHistoryPanel(
            self.content_frame,
            self.account_manager,
            self.song_creation_history_manager
        )

    def _show_current_tab(self):
        for panel in self.panels.values():
            panel.grid_remove()
        current = self.active_tab
        if current in self.panels:
            self.panels[current].grid(row=0, column=0, sticky="nsew", padx=20, pady=(0, 20))
            self.panels[current].refresh()

    def _on_tab_click(self, label: str):
        key = self.label_to_key.get(label)
        if not key or key == self.active_tab:
            return
        self.active_tab = key
        self._show_current_tab()
    
    def change_appearance_mode(self, mode: str):
        """Change appearance mode"""
        ctk.set_appearance_mode(mode.lower())
        logger.info(f"Appearance mode changed to: {mode}")


def run_app():
    """Run the application"""
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    run_app()
