"""
History Panel - Lịch sử download
"""
import customtkinter as ctk
from tkinter import messagebox

from src.core import AccountManager, DownloadManager
from src.utils import format_datetime


class HistoryPanel(ctk.CTkFrame):
    """Panel lịch sử download"""
    
    def __init__(self, parent, account_manager: AccountManager, download_manager: DownloadManager):
        super().__init__(parent)
        
        self.account_manager = account_manager
        self.download_manager = download_manager
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.create_ui()
    
    def create_ui(self):
        """Create UI components"""
        
        # Header
        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            header_frame,
            text="Lịch sử Download",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="Làm mới",
            command=self.refresh,
            width=120
        )
        refresh_btn.grid(row=0, column=1, padx=20, pady=20)
        
        # History list
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, sticky="nsew")
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        self.scrollable = ctk.CTkScrollableFrame(list_frame)
        self.scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable.grid_columnconfigure(0, weight=1)
    
    def refresh(self):
        """Refresh history list"""
        
        # Clear current list
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        
        # Load accounts and histories
        self.download_manager.load_histories()
        accounts = self.account_manager.get_all_accounts()
        
        if not accounts:
            no_data_label = ctk.CTkLabel(
                self.scrollable,
                text="Chưa có dữ liệu",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_data_label.grid(row=0, column=0, pady=100)
            return
        
        # Calculate total
        total_downloads = 0
        
        # Display histories
        for idx, account in enumerate(accounts):
            history = self.download_manager.get_history(account.name)
            total_downloads += history.total_downloaded
            self.create_history_card(account, history, idx)
        
        # Summary at top
        summary = ctk.CTkFrame(self.scrollable, corner_radius=10, fg_color="#1f538d")
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 20), padx=5)
        
        summary_label = ctk.CTkLabel(
            summary,
            text=f"Tổng cộng: {total_downloads} bài đã tải từ {len(accounts)} tài khoản",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        summary_label.pack(pady=15, padx=20)
        
        # Move summary to top
        summary.tkraise()
    
    def create_history_card(self, account, history, row):
        """Create history card for account"""
        
        card = ctk.CTkFrame(self.scrollable, corner_radius=10)
        card.grid(row=row+1, column=0, sticky="ew", pady=5, padx=5)
        card.grid_columnconfigure(1, weight=1)
        
        # Account info
        name_label = ctk.CTkLabel(
            card,
            text=f"📧 {account.name}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        name_label.grid(row=0, column=0, sticky="w", padx=20, pady=(15, 5))
        
        email_label = ctk.CTkLabel(
            card,
            text=f"Email: {account.email}",
            text_color="gray"
        )
        email_label.grid(row=1, column=0, sticky="w", padx=20, pady=2)
        
        # Download stats
        stats_frame = ctk.CTkFrame(card, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="w", padx=20, pady=5)
        
        downloaded_label = ctk.CTkLabel(
            stats_frame,
            text=f"Đã tải: {history.total_downloaded} bài",
            font=ctk.CTkFont(weight="bold")
        )
        downloaded_label.grid(row=0, column=0, sticky="w", pady=2)
        
        if history.last_download:
            last_label = ctk.CTkLabel(
                stats_frame,
                text=f"🕐 Lần cuối: {format_datetime(history.last_download)}",
                text_color="gray"
            )
            last_label.grid(row=1, column=0, sticky="w", pady=2)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            card,
            text="Xóa lịch sử",
            command=lambda: self.clear_history(account.name),
            width=120,
            fg_color="red",
            hover_color="darkred"
        )
        clear_btn.grid(row=0, column=1, rowspan=3, padx=20, pady=10)
        
        # Spacing
        ctk.CTkLabel(card, text="").grid(row=3, column=0, pady=(0, 10))
    
    def clear_history(self, account_name: str):
        """Clear history for account"""
        
        if not messagebox.askyesno(
            "Xác nhận",
            f"Xóa lịch sử download của '{account_name}'?\n\n"
            "Các bài đã tải sẽ có thể tải lại."
        ):
            return
        
        if self.download_manager.clear_history(account_name):
            messagebox.showinfo("Thành công", f"Đã xóa lịch sử của {account_name}")
            self.refresh()
        else:
            messagebox.showerror("Lỗi", "Không thể xóa lịch sử!")
