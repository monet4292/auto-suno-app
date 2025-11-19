"""
Multiple Songs Panel - UI tạo nhiều bài hát (refactored)

ĐÃ TÁCH toàn bộ Selenium & batching logic sang core: `BatchSongCreator`.
UI chỉ còn nhiệm vụ:
 - Thu thập input
 - Gọi BatchSongCreator với callback progress
 - Hiển thị kết quả

Ưu điểm:
 - Dễ test đơn vị cho `BatchSongCreator`
 - UI mỏng, tránh thao tác trực tiếp WebDriver
 - Có thể thay đổi engine (Selenium → API) mà không sửa UI
"""
import customtkinter as ctk
import threading
import math
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Set, Optional

from src.core import AccountManager, QueueManager, SongCreationHistoryManager
from src.core.batch_song_creator import BatchSongCreator
from src.core.queue_manager import QueueValidationError
from src.core.session_manager import SessionManager
from src.core.suno_api_client import SunoApiClient
from src.utils.prompt_parser import SunoPromptParser, SunoPrompt
from config.settings import PROFILES_DIR
from src.utils import logger
from src.models import QueueEntry


class MultipleSongsPanel(ctk.CTkFrame):
    """Panel tạo nhiều bài hát từ file XML sử dụng core BatchSongCreator"""

    STATUS_ICONS = {
        "waiting": "⏳",
        "pending": "⏳",
        "success": "✅",
        "failed": "❌"
    }

    def __init__(
        self,
        parent,
        account_manager: AccountManager,
        queue_manager: QueueManager,
        session_manager: SessionManager,
        history_manager: SongCreationHistoryManager
    ):
        super().__init__(parent)
        self.account_manager = account_manager
        self.queue_manager = queue_manager
        self.session_manager = session_manager
        self.history_manager = history_manager
        self.prompts: List[SunoPrompt] = []
        self.results: List[Dict[str, Any]] = []
        self.creator: BatchSongCreator | None = None
        self.queue_checkvars: Dict[str, ctk.BooleanVar] = {}
        self.queue_selection_state: Dict[str, bool] = {}
        self.selected_queue_ids: Set[str] = set()
        self.pending_songs: List[Dict[str, Any]] = []
        self.matched_song_ids: Set[str] = set()
        self.preview_entries: List[Dict[str, Any]] = []
        self._stop_requested = False
        self._build_ui()

    # ================== UI BUILD ==================
    def _build_ui(self):
        # 2-column layout: Settings (left) | Results (right)
        self.grid_columnconfigure(0, weight=1)  # Left: settings
        self.grid_columnconfigure(1, weight=2)  # Right: results (wider)
        self.grid_rowconfigure(0, weight=0)     # Title row
        self.grid_rowconfigure(1, weight=1)     # Content row

        title_label = ctk.CTkLabel(
            self,
            text="Tạo Nhiều Bài Hát Cùng Lúc",
            font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        # LEFT COLUMN: Settings
        left_container = ctk.CTkScrollableFrame(self, width=450)
        left_container.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")

        input_frame = ctk.CTkFrame(left_container)
        input_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(input_frame, text="Account:", font=("Arial", 14, "bold")).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.account_var = ctk.StringVar()
        self.account_dropdown = ctk.CTkComboBox(
            input_frame,
            variable=self.account_var,
            values=self._get_account_list(),
            width=300
        )
        self.account_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(input_frame, text="XML File:", font=("Arial", 14, "bold")).grid(
            row=1, column=0, padx=10, pady=10, sticky="w"
        )
        file_frame = ctk.CTkFrame(input_frame)
        file_frame.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.file_path_var = ctk.StringVar(value="src/prompt/multiple-suno-prompt.xml")
        self.file_entry = ctk.CTkEntry(file_frame, textvariable=self.file_path_var, width=250)
        self.file_entry.pack(side="left", padx=5)
        self.browse_button = ctk.CTkButton(file_frame, text="📁", command=self._browse_file, width=40)
        self.browse_button.pack(side="left", padx=2)
        self.parse_button = ctk.CTkButton(file_frame, text="Parse", command=self._parse_xml, width=70)
        self.parse_button.pack(side="left", padx=2)
        self.clear_prompts_button = ctk.CTkButton(file_frame, text="Clear", width=60, command=self._clear_parsed_data)
        self.clear_prompts_button.pack(side="left", padx=2)

        # Advanced options toggle
        advanced_header = ctk.CTkFrame(left_container)
        advanced_header.pack(fill="x", padx=10, pady=(5, 0))
        self.use_advanced_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            advanced_header,
            text="Sử dụng Advanced Options",
            variable=self.use_advanced_var,
            command=self._toggle_advanced
        ).pack(side="left", padx=10, pady=5)

        # Advanced container
        self.advanced_container = ctk.CTkFrame(left_container)
        self.advanced_container.pack(fill="x", padx=10, pady=5)
        self._build_advanced_options()
        self._toggle_advanced()

        # Queue controls
        queue_section = ctk.CTkFrame(left_container)
        queue_section.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(
            queue_section,
            text="Hàng chờ tạo bài hát",
            font=("Arial", 16, "bold")
        ).pack(anchor="w", padx=5, pady=(0, 5))

        queue_input_frame = ctk.CTkFrame(queue_section)
        queue_input_frame.pack(fill="x", padx=5, pady=(0, 5))

        ctk.CTkLabel(queue_input_frame, text="Tổng số bài:", font=("Arial", 13)).grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.total_songs_entry = ctk.CTkEntry(queue_input_frame, width=100)
        self.total_songs_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.add_queue_button = ctk.CTkButton(
            queue_input_frame,
            text="Thêm vào hàng chờ",
            command=self._on_add_queue_click
        )
        self.add_queue_button.grid(row=2, column=0, columnspan=2, padx=5, pady=(5, 10))

        self.queue_status_label = ctk.CTkLabel(
            queue_section,
            text="Chưa có hàng chờ nào",
            font=("Arial", 12),
            text_color="gray"
        )
        self.queue_status_label.pack(anchor="w", padx=5, pady=(0, 5))

        self.queue_list_container = ctk.CTkScrollableFrame(
            queue_section,
            height=180
        )
        self.queue_list_container.pack(fill="both", padx=5, pady=(0, 5))
        self._render_queue_list()

        self.status_log = ctk.CTkTextbox(
            queue_section,
            height=120,
            state="disabled"
        )
        self.status_log.pack(fill="both", padx=5, pady=(5, 0))

        self.refresh_status_button = ctk.CTkButton(
            queue_section,
            text="Cập nhật trạng thái",
            command=self._refresh_pending_status
        )
        self.refresh_status_button.pack(fill="x", padx=5, pady=(5, 10))

        # Buttons (at bottom of left column)
        button_frame = ctk.CTkFrame(left_container)
        button_frame.pack(fill="x", padx=10, pady=15)
        self.start_button = ctk.CTkButton(
            button_frame,
            text="Bắt Đầu",
            command=self._on_start_click,
            width=200,
            height=45,
            font=("Arial", 16, "bold"),
            fg_color="green",
            state="disabled"
        )
        self.start_button.pack(side="left", padx=5)
        self.stop_button = ctk.CTkButton(
            button_frame,
            text="Dừng",
            command=self._on_stop_click,
            width=100,
            height=45,
            font=("Arial", 14),
            fg_color="red",
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=5)

        # RIGHT COLUMN: Results
        right_container = ctk.CTkFrame(self)
        right_container.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        right_container.grid_rowconfigure(1, weight=1)  # Preview area
        right_container.grid_rowconfigure(3, weight=1)  # Result area
        right_container.grid_columnconfigure(0, weight=1)

        # Preview section
        ctk.CTkLabel(
            right_container, 
            text="Danh Sách Bài Hát", 
            font=("Arial", 16, "bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.preview_text = ctk.CTkTextbox(right_container, height=250)
        self.preview_text.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.preview_text.insert("1.0", "Chưa parse file nào. Click 'Parse' để bắt đầu.")

        # Progress section
        progress_frame = ctk.CTkFrame(right_container)
        progress_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        
        self.progress_label = ctk.CTkLabel(
            progress_frame, 
            text="Sẵn sàng tạo bài hát", 
            font=("Arial", 12)
        )
        self.progress_label.pack(pady=(5, 2))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=(2, 5))
        self.progress_bar.set(0)

        # Results section
        ctk.CTkLabel(
            right_container, 
            text="Kết Quả", 
            font=("Arial", 16, "bold")
        ).grid(row=3, column=0, padx=10, pady=(10, 5), sticky="nw")
        
        self.result_text = ctk.CTkTextbox(right_container, height=200)
        self.result_text.grid(row=4, column=0, padx=10, pady=5, sticky="nsew")
        right_container.grid_rowconfigure(4, weight=1)  # Make results expandable

    def _build_advanced_options(self):
        """Tạo các control cho Advanced Options"""
        self.advanced_container.grid_columnconfigure(1, weight=1)
        # Exclude Styles
        ctk.CTkLabel(self.advanced_container, text="Exclude Styles:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.exclude_styles_var = ctk.StringVar()
        ctk.CTkEntry(self.advanced_container, textvariable=self.exclude_styles_var, width=300, placeholder_text="rock, metal...").grid(row=0, column=1, padx=10, pady=5, sticky="w")
        # Vocal Gender
        ctk.CTkLabel(self.advanced_container, text="Vocal Gender:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.vocal_gender_var = ctk.StringVar(value="")
        gender_frame = ctk.CTkFrame(self.advanced_container)
        gender_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        for v in ["Male", "Female", ""]:
            ctk.CTkRadioButton(gender_frame, text=v or "None", variable=self.vocal_gender_var, value=v).pack(side="left", padx=5)
        # Lyrics Mode
        ctk.CTkLabel(self.advanced_container, text="Lyrics Mode:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.lyrics_mode_var = ctk.StringVar(value="")
        lyrics_frame = ctk.CTkFrame(self.advanced_container)
        lyrics_frame.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        for v in ["Manual", "Auto", ""]:
            ctk.CTkRadioButton(lyrics_frame, text=v or "None", variable=self.lyrics_mode_var, value=v).pack(side="left", padx=5)
        # Weirdness
        ctk.CTkLabel(self.advanced_container, text="Weirdness:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.weirdness_var = ctk.IntVar(value=50)
        weird_frame = ctk.CTkFrame(self.advanced_container)
        weird_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.weirdness_slider = ctk.CTkSlider(weird_frame, from_=0, to=100, variable=self.weirdness_var, width=250, command=lambda v: self.weirdness_label.configure(text=f"{int(float(v))}%"))
        self.weirdness_slider.pack(side="left")
        self.weirdness_label = ctk.CTkLabel(weird_frame, text="50%")
        self.weirdness_label.pack(side="left", padx=5)
        # Style Influence
        ctk.CTkLabel(self.advanced_container, text="Style Influence:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.style_influence_var = ctk.IntVar(value=50)
        style_frame = ctk.CTkFrame(self.advanced_container)
        style_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.style_influence_slider = ctk.CTkSlider(style_frame, from_=0, to=100, variable=self.style_influence_var, width=250, command=lambda v: self.style_influence_label.configure(text=f"{int(float(v))}%"))
        self.style_influence_slider.pack(side="left")
        self.style_influence_label = ctk.CTkLabel(style_frame, text="50%")
        self.style_influence_label.pack(side="left", padx=5)
        # Persona
        ctk.CTkLabel(self.advanced_container, text="Persona:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.persona_name_var = ctk.StringVar()
        ctk.CTkEntry(self.advanced_container, textvariable=self.persona_name_var, width=300, placeholder_text="Tên persona...").grid(row=5, column=1, padx=10, pady=5, sticky="w")

    def _toggle_advanced(self):
        state = "normal" if self.use_advanced_var.get() else "disabled"
        for w in self.advanced_container.winfo_children():
            try:
                w.configure(state=state)
            except Exception:
                pass

    # ================== HELPERS ==================
    def _get_account_list(self):
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            return ["Chưa có account nào"]
        return [acc.name for acc in accounts]

    def _set_result_message(self, message: str) -> None:
        """Show a brief message in the results box."""
        self.result_text.delete("1.0", "end")
        self.result_text.insert("1.0", message)

    def _on_add_queue_click(self):
        account_name = self.account_var.get()
        if not account_name or account_name == "Chưa có account nào":
            self._set_result_message("❌ Vui lòng chọn account trước khi thêm hàng chờ")
            return
        if not self.prompts:
            self._set_result_message("❌ Chưa parse prompts! Click 'Parse' trước.")
            return

        total_value = self.total_songs_entry.get().strip()
        try:
            total_songs = int(total_value)
        except ValueError:
            self._set_result_message("❌ Tổng số bài phải là số nguyên")
            return
        if total_songs <= 0:
            self._set_result_message("❌ Tổng số bài phải lớn hơn 0")
            return

        per_batch = self._default_songs_per_session(total_songs)

        try:
            entry = self.queue_manager.add_queue_entry(
                account_name,
                total_songs,
                per_batch,
                self.prompts
            )
        except QueueValidationError as exc:
            self._set_result_message(f"❌ {exc}")
            return

        self.queue_selection_state[entry.id] = False
        self.queue_checkvars.pop(entry.id, None)
        self.selected_queue_ids.discard(entry.id)
        self._render_queue_list()
        self._set_result_message(
            f"✅ Đã thêm {entry.total_songs} bài cho account {entry.account_name}"
        )

    def _render_queue_list(self):
        for child in self.queue_list_container.winfo_children():
            child.destroy()

        entries = self.queue_manager.get_all_queues()
        if not entries:
            placeholder = ctk.CTkLabel(
                self.queue_list_container,
                text="Hàng chờ trống. Thêm queue lên để bắt đầu.",
                font=("Arial", 12),
                text_color="gray"
            )
            placeholder.pack(padx=10, pady=30)
            self.selected_queue_ids.clear()
            self.queue_checkvars.clear()
        else:
            valid_ids = set()
            for entry in entries:
                valid_ids.add(entry.id)
                row = ctk.CTkFrame(self.queue_list_container)
                row.pack(fill="x", padx=5, pady=3)

                var = ctk.BooleanVar(value=self.queue_selection_state.get(entry.id, False))
                self.queue_checkvars[entry.id] = var
                checkbox = ctk.CTkCheckBox(
                    row,
                    text=self._format_queue_label(entry),
                    variable=var,
                    command=lambda qid=entry.id: self._on_queue_checkbox_changed(qid)
                )
                checkbox.pack(side="left", padx=5, pady=5, anchor="w")

                delete_btn = ctk.CTkButton(
                    row,
                    text="Xóa",
                    width=50,
                    command=lambda qid=entry.id: self._on_queue_remove(qid),
                    fg_color="transparent",
                    hover_color="#444"
                )
                delete_btn.pack(side="right", padx=5)

                status_text = f"{entry.status.title()} · {entry.completed_count}/{entry.total_songs}"
                status_label = ctk.CTkLabel(
                    row,
                    text=status_text,
                    font=("Arial", 12),
                    text_color="gray"
                )
                status_label.pack(side="right", padx=5)

                if var.get():
                    self.selected_queue_ids.add(entry.id)

            self.selected_queue_ids &= valid_ids

        self._update_queue_status_text()
        self._refresh_start_button_state()

    def _on_queue_checkbox_changed(self, queue_id: str):
        var = self.queue_checkvars.get(queue_id)
        if var is None:
            return
        selected = var.get()
        self.queue_selection_state[queue_id] = selected
        if selected:
            self.selected_queue_ids.add(queue_id)
        else:
            self.selected_queue_ids.discard(queue_id)
        self._refresh_start_button_state()

    def _refresh_start_button_state(self):
        if not hasattr(self, "start_button"):
            return
        state = "normal" if self.selected_queue_ids else "disabled"
        self.start_button.configure(state=state)

    def _refresh_pending_status(self):
        if not self.pending_songs:
            self._set_result_message("Không có bài nào đang chờ ID.")
            return

        grouped = defaultdict(list)
        for pending in self.pending_songs:
            grouped[pending["account_name"]].append(pending)

        updated = 0
        for account_name, items in grouped.items():
            token = self.session_manager.get_session_token(account_name)
            if not token:
                logger.warning(f"Không lấy được session token cho {account_name}")
                continue
            client = SunoApiClient(session_token=token)
            clips = client.fetch_my_clips()
            if not clips:
                continue
            for pending_entry in items:
                clip = self._find_clip_for_pending(pending_entry, clips)
                if clip:
                    updated += 1
                    pending_entry["completed"] = True
                    song_id = clip.get("id")
                    self._mark_pending_complete(pending_entry, song_id)

        self.pending_songs = [p for p in self.pending_songs if not p.get("completed")]

        if updated:
            self._set_result_message(f"✅ Đã cập nhật {updated} bài chờ ID")
        else:
            self._set_result_message("⏳ Chưa tìm thấy ID mới, thử lại sau")

    def _find_clip_for_pending(self, pending_entry: Dict[str, Any], clips: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        title = pending_entry["title"]
        for clip in clips:
            clip_id = clip.get("id")
            clip_title = clip.get("title")
            if not clip_id or clip_id in self.matched_song_ids:
                continue
            if clip_title and clip_title.strip().lower() == title.strip().lower():
                return clip
        return None

    def _mark_pending_complete(self, pending_entry: Dict[str, Any], song_id: str | None):
        title = pending_entry["title"]
        icon = self.STATUS_ICONS["success"]
        msg = f"{icon} Cập nhật: {title}"
        if song_id:
            msg += f" → {song_id}"
            self.matched_song_ids.add(song_id)
        self.status_log.configure(state="normal")
        self.status_log.insert("1.0", msg + "\n")
        self.status_log.configure(state="disabled")
        self._update_preview_entry(title, "success", song_id)

    def _calculate_session_count(self, total_prompts: int) -> int:
        if total_prompts > 30:
            return 4
        if total_prompts > 20:
            return 3
        if total_prompts > 10:
            return 2
        return 1

    def _default_songs_per_session(self, total_songs: int) -> int:
        sessions = self._calculate_session_count(total_songs)
        return math.ceil(total_songs / sessions)

    @staticmethod
    def _format_queue_label(entry: QueueEntry) -> str:
        start, end = entry.prompts_range
        return (
            f"{entry.account_name}: {entry.total_songs} bài "
            f"(~{entry.songs_per_batch}/lần) · Prompt {start + 1}-{end}"
        )

    def _update_queue_status_text(self):
        total = len(self.prompts)
        if total == 0:
            text = "Chưa parse prompt nào"
        else:
            if self.queue_manager.prompts:
                available = self.queue_manager.available_prompt_slots
            else:
                available = total
            text = f"Parsed {total} prompts · {available} còn lại trong hàng chờ"
        self.queue_status_label.configure(text=text)

    def _browse_file(self):
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Chọn XML file",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self._parse_xml()

    def _parse_xml(self):
        file_path = self.file_path_var.get()
        if not file_path:
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", "❌ Chưa chọn file!")
            return
        self.prompts = SunoPromptParser.parse_all_from_file(file_path)
        self.pending_songs.clear()
        self.matched_song_ids.clear()
        self.preview_entries = []
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        if not self.prompts:
            self.preview_text.insert("1.0", "❌ Không parse được prompt nào từ file!")
            self.preview_text.configure(state="disabled")
            return

        self.preview_entries = [
            {"title": prompt.title, "status": "waiting", "text": f"⏳ {prompt.title}"}
            for prompt in self.prompts
        ]
        self._refresh_preview_text()
        logger.info(f"Parsed {len(self.prompts)} prompts from {file_path}")
        self._update_queue_status_text()

    def _clear_parsed_data(self):
        self.prompts = []
        self.preview_entries = []
        self.pending_songs.clear()
        self.matched_song_ids.clear()
        self.queue_manager.clear()
        self._render_queue_list()
        self.selected_queue_ids.clear()
        self.queue_selection_state.clear()
        self.status_log.configure(state="normal")
        self.status_log.delete("1.0", "end")
        self.status_log.configure(state="disabled")
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "Đã xóa danh sách prompt. Parse lại file để tiếp tục.")
        self.preview_text.configure(state="disabled")
        self.result_text.delete("1.0", "end")
        self._update_queue_status_text()
        self._set_result_message("Đã xóa log & danh sách prompt")

    # ================== ACTIONS ==================
    def _on_start_click(self):
        if not self.selected_queue_ids:
            self._set_result_message("❌ Chưa chọn hàng chờ nào để bắt đầu")
            return
        if not self.prompts:
            self._set_result_message("❌ Chưa parse prompts! Click 'Parse' trước.")
            return

        self._stop_requested = False
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.result_text.delete("1.0", "end")
        thread = threading.Thread(target=self._run_queue_thread, daemon=True)
        thread.start()

    def _on_stop_click(self):
        self._stop_requested = True
        if self.creator:
            self.creator.stop()
        self.stop_button.configure(state="disabled")
        self._set_progress("❌ Đã dừng", 0)
        self._refresh_start_button_state()

    def _run_queue_thread(self):
        aggregated_results: List[Dict[str, Any]] = []
        advanced = self._collect_advanced_options()
        auto_submit = True
        queue_ids = list(self.selected_queue_ids)

        for queue_id in queue_ids:
            if self._stop_requested:
                break

            entry = self.queue_manager.get_queue(queue_id)
            if not entry:
                continue

            start, end = entry.prompts_range
            queue_prompts = self.queue_manager.prompts[start:end]
            if not queue_prompts:
                self._set_result_message(f"❌ Queue {entry.account_name} không có prompt nào")
                self.queue_manager.update_queue_progress(queue_id, status="failed")
                continue

            profile_path = PROFILES_DIR / entry.account_name
            if not profile_path.exists():
                self._set_result_message(f"❌ Profile không tồn tại: {profile_path}")
                self.queue_manager.update_queue_progress(queue_id, status="failed")
                continue

            self.queue_manager.update_queue_progress(queue_id, status="in_progress")
            self._render_queue_list()
            self._set_progress(
                f"Queue {entry.account_name}: {entry.total_songs} bài",
                0
            )

            self.creator = BatchSongCreator(profile_path=profile_path)
            session_count = self._calculate_session_count(len(queue_prompts))
            songs_per_session = math.ceil(len(queue_prompts) / session_count)
            def progress_adapter(msg, prog, song_id, status_label, prompt_title):
                self._handle_prompt_progress(
                    queue_id=queue_id,
                    account_name=entry.account_name,
                    prompt_title=prompt_title,
                    message=msg,
                    progress=prog,
                    song_id=song_id,
                    status=status_label
                )
            try:
                batch_results = self.creator.create_songs_batch(
                    prompts=queue_prompts,
                    songs_per_session=songs_per_session,
                    advanced_options=advanced,
                    auto_submit=auto_submit,
                    progress_callback=progress_adapter,
                    account_name=entry.account_name,
                    history_manager=self.history_manager
                )
            except Exception as exc:
                logger.error(f"Queue run error: {exc}")
                batch_results = [{'title': 'ERROR', 'success': False, 'error': str(exc)}]

            aggregated_results.extend(batch_results)
            successful = sum(1 for r in batch_results if r.get('success'))
            status = "completed" if successful >= entry.total_songs else "failed"
            self.queue_manager.update_queue_progress(
                queue_id,
                completed_count=successful,
                status=status
            )
            self.queue_selection_state[queue_id] = False
            self.selected_queue_ids.discard(queue_id)
            self._render_queue_list()

        if aggregated_results:
            self._show_results(aggregated_results)
        elif not self._stop_requested:
            self._set_result_message("❌ Không có kết quả nào được tạo ra")

        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self._stop_requested = False
        self._refresh_start_button_state()

    def _on_queue_remove(self, queue_id: str) -> None:
        removed = self.queue_manager.remove_queue_entry(queue_id)
        self.queue_selection_state.pop(queue_id, None)
        self.selected_queue_ids.discard(queue_id)
        if removed:
            self._set_result_message("Đã xóa queue")
        self.pending_songs = [p for p in self.pending_songs if p["queue_id"] != queue_id]
        self.after(10, self._render_queue_list)
    # ================== ADVANCED OPTIONS ==================
    def _collect_advanced_options(self) -> Dict[str, Any]:
        return {
            'enabled': self.use_advanced_var.get(),
            'exclude_styles': self.exclude_styles_var.get().strip(),
            'vocal_gender': self.vocal_gender_var.get() or None,
            'lyrics_mode': self.lyrics_mode_var.get() or None,
            'weirdness': self.weirdness_var.get(),
            'style_influence': self.style_influence_var.get(),
            'persona_name': self.persona_name_var.get().strip() or None
        }

    # ================== UI CALLBACKS ==================
    def _set_progress(self, message: str, progress: int = 0):
        self.progress_label.configure(text=message)
        self.progress_bar.set(progress / 100 if progress <= 100 else 1)

    def _handle_prompt_progress(
        self,
        queue_id: str,
        account_name: str,
        prompt_title: str,
        message: str,
        progress: int,
        song_id: str | None,
        status: str
    ):
        self._set_progress(message, progress)
        self._update_song_status(queue_id, account_name, prompt_title, message, song_id, status)

    def _refresh_preview_text(self):
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", "end")
        if not self.preview_entries:
            self.preview_text.insert("1.0", "Chưa parse file nào. Click 'Parse' để bắt đầu.")
        else:
            lines = [entry["text"] for entry in self.preview_entries]
            self.preview_text.insert("1.0", "\n".join(lines))
        self.preview_text.configure(state="disabled")

    def _update_song_status(
        self,
        queue_id: str,
        account_name: str,
        prompt_title: str,
        message: str,
        song_id: str | None,
        status: str
    ):
        icon = self.STATUS_ICONS.get(status, "❌")
        line = f"{icon} {message}"
        if song_id:
            line += f" → {song_id}"
        elif status == "pending":
            line += " (đang chờ ID)"
        self.status_log.configure(state="normal")
        self.status_log.insert("1.0", line + "\n")
        self.status_log.configure(state="disabled")

        self._update_preview_entry(prompt_title, status, song_id)

        if status == "pending":
            self.pending_songs.append({
                "queue_id": queue_id,
                "account_name": account_name,
                "title": prompt_title,
                "created_at": datetime.now()
            })
        elif status == "success" and song_id:
            self.matched_song_ids.add(song_id)

    def _update_preview_entry(self, title: str, status: str, song_id: str | None):
        icon = self.STATUS_ICONS.get(status, "❌")
        updated = False
        for entry in self.preview_entries:
            if entry["title"] == title and entry["status"] in {"waiting", "pending"}:
                entry["status"] = status
                if song_id:
                    entry["text"] = f"{icon} {title} → {song_id}"
                elif status == "pending":
                    entry["text"] = f"{icon} {title} (đang chờ ID)"
                else:
                    entry["text"] = f"{icon} {title} (không thành công)"
                updated = True
                break
        if not updated:
            # fallback: append new line if not found
            note = f"{icon} {title}"
            if song_id:
                note += f" → {song_id}"
            self.preview_entries.append({"title": title, "status": status, "text": note})
        self._refresh_preview_text()

    def _show_results(self, results: List[Dict[str, Any]]):
        self.result_text.delete("1.0", "end")
        successful = [r for r in results if r['success'] and not r.get('pending')]
        output = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        output += f"KẾT QUẢ: {len(successful)}/{len(results)} bài thành công\n"
        output += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for r in results:
            if r.get('pending'):
                status = "⏳"
            else:
                status = "✅" if r['success'] else "❌"
            output += f"{status} {r['title']}\n"
            if r.get('error'):
                output += f"   ↳ Lỗi: {r['error']}\n"
        self.result_text.insert("1.0", output)

    def refresh(self):
        accounts = self._get_account_list()
        self.account_dropdown.configure(values=accounts)
        if accounts and accounts[0] != "Chưa có account nào":
            self.account_var.set(accounts[0])
        self._render_queue_list()
