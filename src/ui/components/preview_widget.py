"""
Preview Widget - Hiển thị danh sách bài hát từ XML
"""
import customtkinter as ctk
from typing import List
from src.utils.prompt_parser import SunoPrompt


class PreviewWidget(ctk.CTkFrame):
    """
    Widget hiển thị preview danh sách bài hát
    
    Features:
    - Hiển thị số lượng bài
    - Preview title, style, lyrics của từng bài
    - Tự động scroll
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Title
        ctk.CTkLabel(
            self,
            text="📋 Danh Sách Bài Hát:",
            font=("Arial", 14, "bold")
        ).pack(padx=10, pady=5, anchor="w")
        
        # Textbox
        self.preview_text = ctk.CTkTextbox(self, width=650, height=200)
        self.preview_text.pack(padx=10, pady=5)
        self.preview_text.insert("1.0", "Chưa parse file nào. Click 'Parse' để bắt đầu.")
    
    def display_prompts(self, prompts: List[SunoPrompt]):
        """
        Hiển thị danh sách prompts
        
        Args:
            prompts: List of SunoPrompt objects
        """
        self.preview_text.delete("1.0", "end")
        
        if not prompts:
            self.preview_text.insert("1.0", "❌ Không parse được prompt nào từ file!")
            return
        
        output = f"✅ Tìm thấy {len(prompts)} bài hát:\n\n"
        
        for i, prompt in enumerate(prompts, 1):
            output += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            output += f"Bài {i}: {prompt.title}\n"
            output += f"Style: {prompt.style[:60]}...\n"
            output += f"Lyrics: {len(prompt.lyrics)} ký tự\n"
            output += f"Preview: {prompt.lyrics[:80].replace(chr(10), ' ')}...\n\n"
        
        self.preview_text.insert("1.0", output)
    
    def show_error(self, message: str):
        """Hiển thị lỗi"""
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", f"❌ {message}")
    
    def clear(self):
        """Xóa nội dung"""
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "Chưa parse file nào. Click 'Parse' để bắt đầu.")
