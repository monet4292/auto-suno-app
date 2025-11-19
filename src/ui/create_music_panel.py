"""
Create Music Panel - UI để tạo nhạc tự động trên Suno
"""
import customtkinter as ctk
import threading
from typing import Optional
from pathlib import Path

# Import từ core
from src.core.account_manager import AccountManager
from src.core.session_manager import SessionManager
from legacy_modules import SunoMusicCreator, SunoCreateConfig
from config.style_config import FONT_LABEL, FONT_TITLE, FONT_SUBTITLE


class CreateMusicPanel(ctk.CTkFrame):
    """
    Panel tạo nhạc tự động với Suno Custom Mode
    
    Features:
    - Chọn account đã lưu
    - Nhập Persona, Lyrics, Styles, Title
    - Cấu hình Advanced Options
    - Progress bar hiển thị tiến trình
    - Hiển thị kết quả (URLs bài hát)
    """
    
    def __init__(self, parent, account_manager: AccountManager, session_manager: SessionManager):
        super().__init__(parent)
        
        self.account_manager = account_manager
        self.session_manager = session_manager
        self.music_creator = SunoMusicCreator(
            session_manager=session_manager,
            progress_callback=self._update_progress
        )
        
        # Storage cho created songs
        self.created_songs = []  # List of {title, prompt_xml, urls}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Thiết lập giao diện 2 cột: Form (trái) và Kết quả (phải)"""
        
        # Configure grid weights để 2 cột co giãn
        self.grid_columnconfigure(0, weight=1)  # Cột trái
        self.grid_columnconfigure(1, weight=1)  # Cột phải
        self.grid_rowconfigure(1, weight=1)     # Cho phép row 1 expand
        
        # Title (full width)
        title_label = ctk.CTkLabel(
            self, 
            text="Tạo Nhạc Tự Động",
            font=FONT_TITLE
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # ============================================
        # CỘT TRÁI: FORM INPUT
        # ============================================
        left_container = ctk.CTkScrollableFrame(self, width=700, height=650)
        left_container.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        left_container.grid_columnconfigure(0, weight=1)
        
        # 1️⃣ PHẦN 1: CHỌN ACCOUNT
        account_frame = ctk.CTkFrame(left_container)
        account_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        account_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(account_frame, text="Account:", font=FONT_LABEL).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        
        self.account_var = ctk.StringVar()
        self.account_dropdown = ctk.CTkComboBox(
            account_frame,
            variable=self.account_var,
            values=self._get_account_list(),
            width=250
        )
        self.account_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # 2️⃣ PHẦN 2: PERSONA (Optional)
        persona_frame = ctk.CTkFrame(left_container)
        persona_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        persona_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(persona_frame, text="Persona (optional):", font=FONT_LABEL).grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        
        self.persona_var = ctk.StringVar()
        self.persona_entry = ctk.CTkEntry(
            persona_frame,
            textvariable=self.persona_var,
            placeholder_text="Nhập tên Persona hoặc để trống"
        )
        self.persona_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # 3️⃣ PHẦN 3: NỘI DUNG CHÍNH
        content_frame = ctk.CTkFrame(left_container)
        content_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Lyrics
        ctk.CTkLabel(content_frame, text="Lyrics:", font=FONT_LABEL).grid(
            row=0, column=0, padx=10, pady=5, sticky="nw"
        )
        
        self.lyrics_text = ctk.CTkTextbox(content_frame, height=150)
        self.lyrics_text.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.lyrics_text.insert("1.0", "[Verse 1]\nLời bài hát...\n\n[Chorus]\n...")
        
        # Styles
        ctk.CTkLabel(content_frame, text="Styles:", font=FONT_LABEL).grid(
            row=1, column=0, padx=10, pady=5, sticky="w"
        )
        
        self.styles_var = ctk.StringVar()
        self.styles_entry = ctk.CTkEntry(
            content_frame,
            textvariable=self.styles_var,
            placeholder_text="Pop, upbeat, 120bpm, piano, guitar..."
        )
        self.styles_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        # Title
        ctk.CTkLabel(content_frame, text="Title (optional):", font=FONT_LABEL).grid(
            row=2, column=0, padx=10, pady=5, sticky="w"
        )
        
        self.title_var = ctk.StringVar()
        self.title_entry = ctk.CTkEntry(
            content_frame,
            textvariable=self.title_var,
            placeholder_text="Tên bài hát (để trống để AI tự đặt)"
        )
        self.title_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # 4️⃣ PHẦN 4: ADVANCED OPTIONS
        advanced_frame = ctk.CTkFrame(left_container)
        advanced_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        advanced_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(advanced_frame, text="Advanced Options", font=FONT_LABEL).grid(
            row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w"
        )
        
        # Vocal Gender
        ctk.CTkLabel(advanced_frame, text="Vocal Gender:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.vocal_gender_var = ctk.StringVar(value="Auto")
        vocal_gender_dropdown = ctk.CTkComboBox(
            advanced_frame,
            variable=self.vocal_gender_var,
            values=["Auto", "Male", "Female"],
            width=200
        )
        vocal_gender_dropdown.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Lyrics Mode
        ctk.CTkLabel(advanced_frame, text="Lyrics Mode:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.lyrics_mode_var = ctk.StringVar(value="Auto")
        lyrics_mode_dropdown = ctk.CTkComboBox(
            advanced_frame,
            variable=self.lyrics_mode_var,
            values=["Auto", "Manual"],
            width=200
        )
        lyrics_mode_dropdown.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Weirdness
        ctk.CTkLabel(advanced_frame, text="Weirdness:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.weirdness_var = ctk.IntVar(value=50)
        self.weirdness_slider = ctk.CTkSlider(
            advanced_frame,
            from_=0,
            to=100,
            variable=self.weirdness_var,
            width=200
        )
        self.weirdness_slider.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.weirdness_label = ctk.CTkLabel(advanced_frame, text="50%")
        self.weirdness_label.grid(row=3, column=2, padx=5, pady=5)
        self.weirdness_slider.configure(command=self._update_weirdness_label)
        
        # Style Influence
        ctk.CTkLabel(advanced_frame, text="Style Influence:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.style_influence_var = ctk.IntVar(value=50)
        self.style_influence_slider = ctk.CTkSlider(
            advanced_frame,
            from_=0,
            to=100,
            variable=self.style_influence_var,
            width=200
        )
        self.style_influence_slider.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.style_influence_label = ctk.CTkLabel(advanced_frame, text="50%")
        self.style_influence_label.grid(row=4, column=2, padx=5, pady=5)
        self.style_influence_slider.configure(command=self._update_style_influence_label)
        
        # 5️⃣ PHẦN 5: PROGRESS & ACTIONS
        progress_frame = ctk.CTkFrame(left_container)
        progress_frame.grid(row=4, column=0, sticky="ew", padx=10, pady=5)
        progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(progress_frame, text="Chưa bắt đầu")
        self.progress_label.grid(row=1, column=0, padx=10, pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(progress_frame)
        button_frame.grid(row=2, column=0, pady=10)
        
        self.create_button = ctk.CTkButton(
            button_frame,
            text="Tạo Bài Hát",
            command=self._on_create_click,
            width=200,
            height=40,
            font=("Arial", 14, "bold")
        )
        self.create_button.grid(row=0, column=0, padx=10)
        
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="Xóa Form",
            command=self._clear_form,
            width=150,
            height=40
        )
        self.clear_button.grid(row=0, column=1, padx=10)
        
        # ============================================
        # CỘT PHẢI: KẾT QUẢ BÀI HÁT ĐÃ TẠO
        # ============================================
        right_container = ctk.CTkFrame(self, width=600)
        right_container.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # Title cột phải
        ctk.CTkLabel(
            right_container,
            text="🎤 Bài Hát Đã Tạo",
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        # Scrollable frame cho danh sách bài hát
        self.songs_list_frame = ctk.CTkScrollableFrame(right_container, width=550, height=650)
        self.songs_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Message khi chưa có bài nào
        self.empty_label = ctk.CTkLabel(
            self.songs_list_frame,
            text="Chưa có bài hát nào.\nNhấn 'Tạo Bài Hát' để bắt đầu!",
            font=("Arial", 12),
            text_color="gray"
        )
        self.empty_label.pack(pady=50)
        
    def _get_account_list(self):
        """Lấy danh sách accounts từ AccountManager"""
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            return ["Chưa có account nào"]
        return [acc.name for acc in accounts]
    
    def _update_weirdness_label(self, value):
        """Cập nhật label Weirdness slider"""
        self.weirdness_label.configure(text=f"{int(float(value))}%")
    
    def _update_style_influence_label(self, value):
        """Cập nhật label Style Influence slider"""
        self.style_influence_label.configure(text=f"{int(float(value))}%")
    
    def _clear_form(self):
        """Xóa toàn bộ form"""
        self.persona_var.set("")
        self.lyrics_text.delete("1.0", "end")
        self.styles_var.set("")
        self.title_var.set("")
        self.vocal_gender_var.set("Auto")
        self.lyrics_mode_var.set("Auto")
        self.weirdness_var.set(50)
        self.style_influence_var.set(50)
        self.progress_bar.set(0)
        self.progress_label.configure(text="Chưa bắt đầu")
    
    def _update_progress(self, message: str, progress: int):
        """
        Callback từ SunoMusicCreator để cập nhật progress
        
        Args:
            message: Thông điệp hiển thị
            progress: % hoàn thành (0-100)
        """
        self.progress_label.configure(text=message)
        self.progress_bar.set(progress / 100)
    
    def _on_create_click(self):
        """Xử lý khi click nút Tạo Bài Hát"""
        # Validate
        account_name = self.account_var.get()
        if not account_name or account_name == "Chưa có account nào":
            self._update_progress("❌ Vui lòng chọn account!", 0)
            return
        
        styles = self.styles_var.get().strip()
        if not styles:
            self._update_progress("❌ Vui lòng nhập Styles!", 0)
            return
        
        # Disable button
        self.create_button.configure(state="disabled", text="Đang tạo...")
        
        # Chạy trong thread riêng để không block UI
        thread = threading.Thread(
            target=self._create_music_thread,
            args=(account_name,),
            daemon=True
        )
        thread.start()
    
    def _create_music_thread(self, account_name: str):
        """Thread worker để tạo nhạc"""
        try:
            # Tạo config
            config = SunoCreateConfig(
                persona_name=self.persona_var.get().strip() or None,
                lyrics=self.lyrics_text.get("1.0", "end").strip(),
                styles=self.styles_var.get().strip(),
                title=self.title_var.get().strip() or None,
                vocal_gender=None if self.vocal_gender_var.get() == "Auto" else self.vocal_gender_var.get(),
                lyrics_mode=None if self.lyrics_mode_var.get() == "Auto" else self.lyrics_mode_var.get(),
                weirdness=self.weirdness_var.get(),
                style_influence=self.style_influence_var.get(),
                wait_for_generation=True,
                timeout=120
            )
            
            # Tạo nhạc
            result = self.music_creator.create_song(account_name, config)
            
            # Hiển thị kết quả
            if result["success"]:
                # Tạo XML prompt
                prompt_xml = self._generate_prompt_xml(config)
                
                # Thêm vào danh sách
                song_title = config.title or "Untitled Song"
                for url in result["song_urls"]:
                    self._add_song_to_list(song_title, prompt_xml, url)
                
                self._update_progress(f"✅ Đã tạo {len(result['song_urls'])} bài hát!", 100)
            else:
                self._update_progress(f"❌ Lỗi: {result['error']}", 0)
                
        except Exception as e:
            self._update_progress(f"❌ Exception: {str(e)}", 0)
        finally:
            # Re-enable button
            self.create_button.configure(state="normal", text="Tạo Bài Hát")
    
    def refresh(self):
        """Refresh panel - gọi khi panel được hiển thị"""
        # Cập nhật danh sách accounts
        accounts = self._get_account_list()
        self.account_dropdown.configure(values=accounts)
        if accounts and accounts[0] != "Chưa có account nào":
            self.account_var.set(accounts[0])
    
    def _generate_prompt_xml(self, config: SunoCreateConfig) -> str:
        """Tạo XML prompt từ config"""
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        root = ET.Element("suno_prompt")
        
        if config.persona_name:
            ET.SubElement(root, "persona").text = config.persona_name
        
        ET.SubElement(root, "lyrics").text = config.lyrics or ""
        ET.SubElement(root, "styles").text = config.styles or ""
        
        if config.title:
            ET.SubElement(root, "title").text = config.title
        
        # Advanced options
        if config.vocal_gender:
            ET.SubElement(root, "vocal_gender").text = config.vocal_gender
        if config.lyrics_mode:
            ET.SubElement(root, "lyrics_mode").text = config.lyrics_mode
        if config.weirdness and config.weirdness != 50:
            ET.SubElement(root, "weirdness").text = str(config.weirdness)
        if config.style_influence and config.style_influence != 50:
            ET.SubElement(root, "style_influence").text = str(config.style_influence)
        
        # Pretty print XML
        xml_str = ET.tostring(root, encoding='unicode')
        dom = minidom.parseString(xml_str)
        return dom.toprettyxml(indent="  ")
    
    def _add_song_to_list(self, title: str, prompt_xml: str, url: str):
        """Thêm bài hát vào danh sách kết quả"""
        # Ẩn empty label nếu đây là bài đầu tiên
        if len(self.created_songs) == 0:
            self.empty_label.pack_forget()
        
        # Thêm vào storage
        song_data = {
            "title": title,
            "prompt_xml": prompt_xml,
            "url": url
        }
        self.created_songs.append(song_data)
        
        # Tạo song card
        song_card = ctk.CTkFrame(self.songs_list_frame)
        song_card.pack(fill="x", padx=5, pady=5)
        
        # Title
        title_label = ctk.CTkLabel(
            song_card,
            text=f"{title}",
            font=("Arial", 13, "bold"),
            anchor="w"
        )
        title_label.pack(fill="x", padx=10, pady=(10, 5))
        
        # URL (clickable)
        url_label = ctk.CTkLabel(
            song_card,
            text=f"🔗 {url[:60]}...",
            font=("Arial", 10),
            text_color="blue",
            anchor="w",
            cursor="hand2"
        )
        url_label.pack(fill="x", padx=10, pady=5)
        
        # Bind click để copy URL
        url_label.bind("<Button-1>", lambda e: self._copy_to_clipboard(url))
        
        # Button frame
        btn_frame = ctk.CTkFrame(song_card)
        btn_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # Copy XML button
        copy_btn = ctk.CTkButton(
            btn_frame,
            text="📋 Copy XML Prompt",
            command=lambda: self._copy_to_clipboard(prompt_xml),
            width=150,
            height=30,
            font=("Arial", 11)
        )
        copy_btn.pack(side="left", padx=5)
        
        # Copy URL button
        copy_url_btn = ctk.CTkButton(
            btn_frame,
            text="🔗 Copy URL",
            command=lambda: self._copy_to_clipboard(url),
            width=120,
            height=30,
            font=("Arial", 11),
            fg_color="gray40"
        )
        copy_url_btn.pack(side="left", padx=5)
    
    def _copy_to_clipboard(self, text: str):
        """Copy text vào clipboard"""
        import pyperclip
        try:
            pyperclip.copy(text)
            # Show temporary notification
            self._update_progress("✅ Đã copy vào clipboard!", 100)
        except:
            self._update_progress("❌ Không thể copy", 0)
