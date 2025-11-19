"""
Song Creation History Panel
"""
import math
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from config.settings import DOWNLOADS_DIR
from src.core import AccountManager
from src.core.song_creation_history_manager import SongCreationHistoryManager
from src.utils import format_datetime, logger


class SongCreationHistoryPanel(ctk.CTkFrame):
    """Panel hiển thị lịch sử tạo bài hát."""

    PAGE_SIZE = 20
    STATUS_ICONS = {
        "success": "✅",
        "pending": "⏳",
        "failed": "❌"
    }

    def __init__(
        self,
        parent,
        account_manager: AccountManager,
        history_manager: SongCreationHistoryManager,
    ):
        super().__init__(parent)
        self.account_manager = account_manager
        self.history_manager = history_manager
        self.filtered_records = []
        self.current_page = 1
        self._copy_feedback_id = None

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        header_frame = ctk.CTkFrame(self)
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header_frame,
            text="Lịch sử Tạo Bài Hát",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w")

        refresh_btn = ctk.CTkButton(
            header_frame,
            text="Làm mới",
            command=self.refresh,
            width=120
        )
        refresh_btn.grid(row=0, column=2, sticky="e")

        filter_frame = ctk.CTkFrame(self)
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 5))
        filter_frame.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(filter_frame, text="Account:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.account_var = ctk.StringVar(value="Tất cả")
        self.account_menu = ctk.CTkOptionMenu(
            filter_frame,
            values=["Tất cả"],
            variable=self.account_var,
            command=self._on_filter_change,
            width=150
        )
        self.account_menu.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ctk.CTkLabel(filter_frame, text="Tìm kiếm:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(filter_frame, textvariable=self.search_var, placeholder_text="Tên bài hoặc ID")
        search_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        search_entry.bind("<Return>", lambda _: self._apply_filters(reset_page=True))

        search_btn = ctk.CTkButton(
            filter_frame,
            text="Tìm",
            command=lambda: self._apply_filters(reset_page=True),
            width=70
        )
        search_btn.grid(row=0, column=4, padx=5, pady=5)

        export_btn = ctk.CTkButton(
            filter_frame,
            text="Export CSV",
            command=self._export_csv,
            width=120
        )
        export_btn.grid(row=0, column=5, padx=5, pady=5, sticky="e")

        self.copy_feedback_label = ctk.CTkLabel(
            filter_frame,
            text="",
            text_color="gray"
        )
        self.copy_feedback_label.grid(row=1, column=0, columnspan=6, sticky="w", padx=5, pady=(0, 5))

        table_frame = ctk.CTkFrame(self)
        table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 10))
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(1, weight=1)

        header_labels = ["Thời Gian", "Account", "Tên Bài", "Song ID", "Trạng Thái"]
        header_row = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        for idx, text in enumerate(header_labels):
            ctk.CTkLabel(
                header_row,
                text=text,
                font=ctk.CTkFont(size=12, weight="bold")
            ).grid(row=0, column=idx, padx=10, sticky="w")

        self.table_body = ctk.CTkScrollableFrame(table_frame, corner_radius=10)
        self.table_body.grid(row=1, column=0, sticky="nsew")
        self.table_body.grid_columnconfigure(0, weight=1)

        pagination_frame = ctk.CTkFrame(self)
        pagination_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        pagination_frame.grid_columnconfigure(1, weight=1)

        self.prev_btn = ctk.CTkButton(
            pagination_frame,
            text="‹ Trước",
            command=self._prev_page,
            width=120
        )
        self.prev_btn.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.page_label = ctk.CTkLabel(pagination_frame, text="")
        self.page_label.grid(row=0, column=1, padx=5, pady=5)

        self.next_btn = ctk.CTkButton(
            pagination_frame,
            text="Tiếp ›",
            command=self._next_page,
            width=120
        )
        self.next_btn.grid(row=0, column=2, padx=5, pady=5, sticky="e")

    def refresh(self):
        """Reload data and reapply filters."""
        self.history_manager.load_records()
        self._update_account_menu()
        self._apply_filters(reset_page=True)

    def _update_account_menu(self):
        accounts = self.account_manager.get_all_accounts()
        options = ["Tất cả"] + [account.name for account in accounts]
        self.account_menu.configure(values=options)
        if self.account_var.get() not in options:
            self.account_var.set("Tất cả")

    def _on_filter_change(self, _=None):
        self._apply_filters(reset_page=True)

    def _apply_filters(self, reset_page: bool = False):
        if reset_page:
            self.current_page = 1
        records = self.history_manager.get_all_records()

        account_filter = self.account_var.get()
        if account_filter and account_filter != "Tất cả":
            records = [rec for rec in records if rec.account_name == account_filter]

        query = self.search_var.get().strip()
        if query:
            lower = query.lower()
            records = [
                rec for rec in records
                if lower in rec.title.lower() or lower in rec.song_id.lower()
                or lower in rec.status.lower()
            ]

        self.filtered_records = records
        self._render_table()

    def _render_table(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        total = len(self.filtered_records)
        total_pages = max(1, math.ceil(total / self.PAGE_SIZE))
        self.current_page = min(self.current_page, total_pages)
        self.current_page = max(1, self.current_page)
        start = (self.current_page - 1) * self.PAGE_SIZE
        end = start + self.PAGE_SIZE
        page_records = self.filtered_records[start:end]

        if not page_records:
            empty_label = ctk.CTkLabel(
                self.table_body,
                text="Chưa có bản ghi nào.",
                text_color="gray"
            )
            empty_label.grid(row=0, column=0, pady=20)
        else:
            for row_idx, record in enumerate(page_records):
                row_frame = ctk.CTkFrame(self.table_body, corner_radius=10, fg_color="#1f1f1f")
                row_frame.grid(row=row_idx, column=0, sticky="ew", pady=2, padx=2)
                row_frame.grid_columnconfigure(4, weight=1)
                row_frame.bind("<Button-1>", lambda event, rec=record: self._copy_song_id(rec.song_id))

                formatted_time = format_datetime(record.created_at)
                values = [
                    formatted_time,
                    record.account_name,
                    record.title,
                    record.song_id,
                    f"{self.STATUS_ICONS.get(record.status, '')} {record.status.capitalize()}"
                ]

                for col_idx, value in enumerate(values):
                    label = ctk.CTkLabel(row_frame, text=value, wraplength=180 if col_idx == 2 else None)
                    label.grid(row=0, column=col_idx, padx=8, pady=10, sticky="w")
                    label.bind("<Button-1>", lambda event, rec=record: self._copy_song_id(rec.song_id))

        self.page_label.configure(text=f"Trang {self.current_page}/{total_pages}")
        self.prev_btn.configure(state="disabled" if self.current_page <= 1 else "normal")
        self.next_btn.configure(state="disabled" if self.current_page >= total_pages else "normal")

    def _prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._render_table()

    def _next_page(self):
        total = len(self.filtered_records)
        total_pages = max(1, math.ceil(total / self.PAGE_SIZE))
        if self.current_page < total_pages:
            self.current_page += 1
            self._render_table()

    def _copy_song_id(self, song_id: str):
        if not song_id:
            return

        self.clipboard_clear()
        self.clipboard_append(song_id)
        self.copy_feedback_label.configure(text=f"Đã copy: {song_id}")
        if self._copy_feedback_id:
            self.after_cancel(self._copy_feedback_id)
        self._copy_feedback_id = self.after(2500, lambda: self.copy_feedback_label.configure(text=""))

    def _export_csv(self):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"song-creation-history-{now}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=default_name,
            initialdir=DOWNLOADS_DIR
        )
        if not path:
            return

        try:
            output_path = Path(path)
            self.history_manager.export_to_csv(output_path)
            messagebox.showinfo("Export CSV", f"Đã xuất {output_path}")
        except Exception as exc:
            logger.error(f"CSV export failed: {exc}")
            messagebox.showerror("Lỗi", "Không thể xuất lịch sử sang CSV.")
