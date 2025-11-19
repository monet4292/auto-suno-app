"""
Download Panel - Tải bài hát
"""
import threading
from pathlib import Path
from urllib.parse import urlparse

import customtkinter as ctk
from tkinter import filedialog, messagebox

from config.settings import DOWNLOADS_DIR
from src.core import AccountManager, DownloadManager, SessionManager
from src.utils import logger, validate_profile_name


class DownloadPanel(ctk.CTkFrame):
    """Panel download bài hát"""

    def __init__(
        self,
        parent,
        account_manager: AccountManager,
        session_manager: SessionManager,
        download_manager: DownloadManager,
    ):
        super().__init__(parent)

        self.account_manager = account_manager
        self.session_manager = session_manager
        self.download_manager = download_manager

        self.selected_account = None
        self.downloading = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_ui()

    def create_ui(self):
        """Create UI components"""

        # Header
        header = ctk.CTkLabel(
            self,
            text="Download bài hát",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Main content
        content = ctk.CTkFrame(self)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)

        # Account selection
        account_frame = ctk.CTkFrame(content)
        account_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=10)
        account_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            account_frame,
            text="Tài khoản:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")

        self.account_menu = ctk.CTkOptionMenu(
            account_frame,
            values=["Chọn tài khoản..."],
            command=self.on_account_selected,
            width=300,
        )
        self.account_menu.grid(row=0, column=1, padx=20, pady=15, sticky="w")

        # Profile input
        profile_frame = ctk.CTkFrame(content)
        profile_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        profile_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            profile_frame,
            text="Download từ:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # Checkbox để chọn download từ /create
        self.use_my_songs = ctk.BooleanVar(value=True)
        my_songs_check = ctk.CTkCheckBox(
            profile_frame,
            text="Bài hát của tôi (/create)",
            variable=self.use_my_songs,
            command=self.toggle_profile_input,
        )
        my_songs_check.grid(row=0, column=1, padx=20, pady=15, sticky="w")

        # Profile entry (disabled khi dùng /create)
        self.profile_entry = ctk.CTkEntry(
            profile_frame,
            placeholder_text="@username hoặc link profile",
            width=300,
            state="disabled",
        )
        self.profile_entry.grid(row=0, column=2, padx=20, pady=15, sticky="w")

        # Download options
        options_frame = ctk.CTkFrame(content)
        options_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkLabel(
            options_frame,
            text="Tùy chọn:",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Limit
        limit_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        limit_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)

        ctk.CTkLabel(limit_frame, text="Số bài tải:").grid(
            row=0, column=0, sticky="w"
        )
        self.limit_entry = ctk.CTkEntry(limit_frame, width=100, placeholder_text="Tất cả")
        self.limit_entry.grid(row=0, column=1, padx=10)

        # Thumbnail
        self.thumbnail_var = ctk.BooleanVar(value=True)
        thumbnail_check = ctk.CTkCheckBox(
            options_frame,
            text="Tải thumbnail & metadata",
            variable=self.thumbnail_var,
        )
        thumbnail_check.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        # UUID
        self.uuid_var = ctk.BooleanVar(value=True)
        uuid_check = ctk.CTkCheckBox(
            options_frame,
            text="Thêm UUID vào tên file",
            variable=self.uuid_var,
        )
        uuid_check.grid(row=3, column=0, padx=20, pady=5, sticky="w")

        # Resume download
        self.resume_var = ctk.BooleanVar(value=True)
        resume_check = ctk.CTkCheckBox(
            options_frame,
            text="Tiếp tục tải từ trang đã lưu",
            variable=self.resume_var,
        )
        resume_check.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        # Output directory
        dir_frame = ctk.CTkFrame(options_frame, fg_color="transparent")
        dir_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(5, 15))
        dir_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dir_frame, text="Thư mục:").grid(row=0, column=0, sticky="w")

        self.dir_entry = ctk.CTkEntry(dir_frame, placeholder_text="Mặc định")
        self.dir_entry.grid(row=0, column=1, padx=10, sticky="ew")

        browse_btn = ctk.CTkButton(
            dir_frame,
            text="Chọn",
            command=self.browse_directory,
            width=40,
        )
        browse_btn.grid(row=0, column=2)

        # Download button
        self.download_btn = ctk.CTkButton(
            content,
            text="Bắt đầu tải",
            command=self.start_download,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        self.download_btn.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        # Progress
        self.progress_frame = ctk.CTkFrame(content)
        self.progress_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=ctk.CTkFont(size=12),
        )
        self.progress_label.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
        self.progress_bar.set(0)

        self.progress_frame.grid_remove()

    def toggle_profile_input(self):
        """Toggle profile input based on checkbox"""
        if self.use_my_songs.get():
            self.profile_entry.configure(state="disabled")
        else:
            self.profile_entry.configure(state="normal")

    def refresh(self):
        """Refresh account list"""
        accounts = self.account_manager.get_all_accounts()

        if accounts:
            account_names = [acc.name for acc in accounts]
            self.account_menu.configure(values=account_names)
            if account_names:
                self.account_menu.set(account_names[0])
                self.selected_account = account_names[0]
        else:
            self.account_menu.configure(values=["Chưa có tài khoản"])
            self.account_menu.set("Chưa có tài khoản")
            self.selected_account = None

    def on_account_selected(self, account_name: str):
        """Handle account selection"""
        self.selected_account = account_name

        # Auto-fill profile if email available
        account = self.account_manager.get_account(account_name)
        if account and account.email:
            username = account.email.split("@")[0]
            self.profile_entry.delete(0, "end")
            self.profile_entry.insert(0, f"@{username}")

    def browse_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)

    def start_download(self):
        """Start download process"""

        if self.downloading:
            messagebox.showwarning("Cảnh báo", "Đang tải, vui lòng đợi!")
            return

        if not self.selected_account:
            messagebox.showerror("Lỗi", "Vui lòng chọn tài khoản!")
            return

        # Determine source
        use_my_songs = self.use_my_songs.get()
        profile_name: str | None = None

        if not use_my_songs:
            raw_profile = self.profile_entry.get().strip()
            if not raw_profile:
                messagebox.showerror(
                    "Lỗi",
                    "Vui lòng nhập tên profile hoặc chọn 'Bài hát của tôi'!",
                )
                return

            profile_name = self._normalize_profile_input(raw_profile)
            if not profile_name or not validate_profile_name(profile_name):
                messagebox.showerror(
                    "Lỗi",
                    "Tên profile không hợp lệ!\nVD: @username hoặc https://suno.com/@username",
                )
                return

        # Get limit
        limit_str = self.limit_entry.get().strip()
        limit: int | None = None
        if limit_str:
            try:
                limit = int(limit_str)
                if limit <= 0:
                    messagebox.showerror("Lỗi", "Số bài phải > 0!")
                    return
            except ValueError:
                messagebox.showerror("Lỗi", "Số bài không hợp lệ!")
                return

        # Output directory
        output_dir = self.dir_entry.get().strip()
        if not output_dir:
            output_dir = str(DOWNLOADS_DIR / self.selected_account)

        output_path = Path(output_dir)
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            messagebox.showerror("Lỗi", f"Không tạo được thư mục:\n{exc}")
            return

        source_text = "Bài hát của tôi (/create)" if use_my_songs else profile_name
        if not messagebox.askyesno(
            "Xác nhận",
            f"Tải bài hát từ: {source_text}\n"
            f"Tài khoản: {self.selected_account}\n"
            f"Số bài: {limit if limit else 'Tất cả'}\n"
            f"Thư mục: {output_path}\n\n"
            "Tiếp tục?",
        ):
            return

        thread = threading.Thread(
            target=self.download_thread,
            args=(use_my_songs, profile_name, limit, output_path),
            daemon=True,
        )
        thread.start()

    def download_thread(
        self,
        use_my_songs: bool,
        profile_name: str | None,
        limit: int | None,
        output_path: Path,
    ):
        """Download in background thread"""

        self.downloading = True
        self.download_btn.configure(state="disabled", text="Đang tải...")
        self.progress_frame.grid()

        driver = None

        try:
            self.update_progress("Đang mở trình duyệt...", 0)

            if use_my_songs:
                session_token, driver = self.session_manager.get_session_token_from_me_page(
                    self.selected_account
                )

                if not session_token:
                    messagebox.showerror(
                        "Lỗi",
                        "Không lấy được session token!\n\n"
                        "Nguyên nhân có thể:\n"
                        "1. Profile đang được sử dụng - đóng tất cả cửa sổ Chrome\n"
                        "2. Chưa đăng nhập - dùng 'Sử dụng tài khoản' để đăng nhập\n"
                        "3. Session hết hạn - đăng nhập lại",
                    )
                    return
            else:
                session_token = self.session_manager.get_session_token(self.selected_account)

                if not session_token:
                    messagebox.showerror(
                        "Lỗi",
                        "Không lấy được session token!\n"
                        "Hãy đăng nhập lại tài khoản.",
                    )
                    return

            output_path.mkdir(parents=True, exist_ok=True)

            # Use paginated streaming download to save memory
            self.update_progress("Đang chuẩn bị tải...", 10)

            start_page = 0
            if self.resume_var.get():
                # History loader ensures skipped clips are tracked properly
                self.download_manager.get_history(self.selected_account)

            stats = self.download_manager.batch_download_paginated(
                account_name=self.selected_account,
                session_token=session_token,
                output_dir=output_path,
                profile_name=profile_name,
                use_create_page=use_my_songs,
                start_page=start_page,
                max_pages=None,
                max_clips=limit,
                with_thumbnail=self.thumbnail_var.get(),
                append_uuid=self.uuid_var.get(),
                progress_callback=self.update_progress,
                delay=2,
            )

            message = (
                f"✅ Thành công: {stats.get('success', 0)}\n"
                f"❌ Thất bại: {stats.get('failed', 0)}\n"
                f"⏭️  Đã bỏ qua: {stats.get('skipped', 0)}\n"
                f"📄 Tổng số trang: {stats.get('total_pages', 0)}\n"
                f"📊 Tổng đã tải: {stats.get('success', 0) + stats.get('skipped', 0)} bài\n\n"
                f"📁 Thư mục: {output_path}"
            )
            messagebox.showinfo("Hoàn thành!", message)

        except Exception as exc:
            logger.error(f"Download error: {exc}")
            messagebox.showerror("Lỗi", f"Lỗi khi tải:\n{exc}")

        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Browser closed after download")
                except Exception:
                    pass

            self.downloading = False
            self.download_btn.configure(state="normal", text="Bắt đầu tải")
            self.progress_frame.grid_remove()
            self.update_progress("", 0)

    def _normalize_profile_input(self, text: str) -> str | None:
        """
        Normalize user input into @username form.
        Supports raw usernames, @user, and full Suno profile links.
        """
        if not text:
            return None

        cleaned = text.strip()
        if not cleaned:
            return None

        if cleaned.startswith("@"):
            return cleaned

        if cleaned.startswith("http"):
            parsed = urlparse(cleaned)
            path = (parsed.path or "").strip("/")
            if not path:
                return None

            if "@" in path:
                username = path[path.find("@") :]
                username = username.split("/")[0]
                if not username.startswith("@"):
                    username = f"@{username}"
                return username

            last_segment = path.split("/")[-1]
            if last_segment:
                return f"@{last_segment}"
            return None

        cleaned = cleaned.lstrip("@")
        return f"@{cleaned}" if cleaned else None

    def update_progress(self, message: str, progress: int):
        """Update progress UI"""
        self.progress_label.configure(text=message)
        self.progress_bar.set(progress / 100)
