"""
Advanced Options Widget - Reusable component cho Suno Advanced Settings
"""
import customtkinter as ctk
from typing import Dict, Any


class AdvancedOptionsWidget(ctk.CTkFrame):
    """
    Reusable widget cho Advanced Options
    
    Features:
    - Exclude Styles
    - Vocal Gender (Male/Female)
    - Lyrics Mode (Manual/Auto)
    - Weirdness Slider (0-100%)
    - Style Influence Slider (0-100%)
    - Persona Name
    """
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # Variables
        self.use_advanced_var = ctk.BooleanVar(value=False)
        self.exclude_styles_var = ctk.StringVar(value="")
        self.vocal_gender_var = ctk.StringVar(value="")
        self.lyrics_mode_var = ctk.StringVar(value="")
        self.weirdness_var = ctk.IntVar(value=50)
        self.style_influence_var = ctk.IntVar(value=50)
        self.persona_name_var = ctk.StringVar(value="")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Header with checkbox
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=5)
        
        use_advanced_check = ctk.CTkCheckBox(
            header_frame,
            text="Sử dụng Advanced Options",
            variable=self.use_advanced_var,
            font=("Arial", 13, "bold"),
            command=self._toggle_advanced_options
        )
        use_advanced_check.pack(side="left", padx=10)
        
        # Options container
        self.options_container = ctk.CTkFrame(self)
        self.options_container.pack(fill="x", padx=10, pady=5)
        
        # Row 1: Exclude Styles
        ctk.CTkLabel(
            self.options_container,
            text="Exclude Styles:",
            font=("Arial", 11)
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        
        self.exclude_styles_entry = ctk.CTkEntry(
            self.options_container,
            textvariable=self.exclude_styles_var,
            width=300,
            placeholder_text="rock, metal, edm..."
        )
        self.exclude_styles_entry.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Row 2: Vocal Gender
        ctk.CTkLabel(
            self.options_container,
            text="Vocal Gender:",
            font=("Arial", 11)
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        
        gender_frame = ctk.CTkFrame(self.options_container)
        gender_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkRadioButton(
            gender_frame,
            text="Male",
            variable=self.vocal_gender_var,
            value="Male"
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            gender_frame,
            text="Female",
            variable=self.vocal_gender_var,
            value="Female"
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            gender_frame,
            text="None",
            variable=self.vocal_gender_var,
            value=""
        ).pack(side="left", padx=5)
        
        # Row 3: Lyrics Mode
        ctk.CTkLabel(
            self.options_container,
            text="Lyrics Mode:",
            font=("Arial", 11)
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        lyrics_mode_frame = ctk.CTkFrame(self.options_container)
        lyrics_mode_frame.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ctk.CTkRadioButton(
            lyrics_mode_frame,
            text="Manual",
            variable=self.lyrics_mode_var,
            value="Manual"
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            lyrics_mode_frame,
            text="Auto",
            variable=self.lyrics_mode_var,
            value="Auto"
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            lyrics_mode_frame,
            text="None",
            variable=self.lyrics_mode_var,
            value=""
        ).pack(side="left", padx=5)
        
        # Row 4: Weirdness Slider
        ctk.CTkLabel(
            self.options_container,
            text="Weirdness:",
            font=("Arial", 11)
        ).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        weirdness_frame = ctk.CTkFrame(self.options_container)
        weirdness_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        self.weirdness_slider = ctk.CTkSlider(
            weirdness_frame,
            from_=0,
            to=100,
            variable=self.weirdness_var,
            width=250
        )
        self.weirdness_slider.pack(side="left", padx=5)
        
        self.weirdness_label = ctk.CTkLabel(
            weirdness_frame,
            text="50%",
            font=("Arial", 11, "bold"),
            width=50
        )
        self.weirdness_label.pack(side="left", padx=5)
        
        self.weirdness_slider.configure(
            command=lambda v: self.weirdness_label.configure(text=f"{int(v)}%")
        )
        
        # Row 5: Style Influence Slider
        ctk.CTkLabel(
            self.options_container,
            text="Style Influence:",
            font=("Arial", 11)
        ).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        style_influence_frame = ctk.CTkFrame(self.options_container)
        style_influence_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        self.style_influence_slider = ctk.CTkSlider(
            style_influence_frame,
            from_=0,
            to=100,
            variable=self.style_influence_var,
            width=250
        )
        self.style_influence_slider.pack(side="left", padx=5)
        
        self.style_influence_label = ctk.CTkLabel(
            style_influence_frame,
            text="50%",
            font=("Arial", 11, "bold"),
            width=50
        )
        self.style_influence_label.pack(side="left", padx=5)
        
        self.style_influence_slider.configure(
            command=lambda v: self.style_influence_label.configure(text=f"{int(v)}%")
        )
        
        # Row 6: Persona Name
        ctk.CTkLabel(
            self.options_container,
            text="Persona:",
            font=("Arial", 11)
        ).grid(row=5, column=0, padx=10, pady=5, sticky="w")
        
        persona_frame = ctk.CTkFrame(self.options_container)
        persona_frame.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        
        self.persona_entry = ctk.CTkEntry(
            persona_frame,
            textvariable=self.persona_name_var,
            width=250,
            placeholder_text="Minh Chien, John Doe..."
        )
        self.persona_entry.pack(side="left", padx=5)
        
        ctk.CTkLabel(
            persona_frame,
            text="Tìm và chọn persona theo tên",
            font=("Arial", 9),
            text_color="gray"
        ).pack(side="left", padx=5)
        
        # Disable by default
        self._toggle_advanced_options()
    
    def _toggle_advanced_options(self):
        """Enable/disable advanced options controls"""
        state = "normal" if self.use_advanced_var.get() else "disabled"
        
        # Disable/enable all widgets
        for widget in self.options_container.winfo_children():
            if isinstance(widget, (ctk.CTkEntry, ctk.CTkSlider)):
                widget.configure(state=state)
            elif isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, (ctk.CTkRadioButton, ctk.CTkSlider)):
                        child.configure(state=state)
    
    def get_settings(self) -> Dict[str, Any]:
        """
        Lấy tất cả settings
        
        Returns:
            Dict chứa tất cả settings
        """
        return {
            'enabled': self.use_advanced_var.get(),
            'exclude_styles': self.exclude_styles_var.get().strip(),
            'vocal_gender': self.vocal_gender_var.get(),
            'lyrics_mode': self.lyrics_mode_var.get(),
            'weirdness': self.weirdness_var.get(),
            'style_influence': self.style_influence_var.get(),
            'persona_name': self.persona_name_var.get().strip()
        }
    
    def reset(self):
        """Reset về giá trị mặc định"""
        self.use_advanced_var.set(False)
        self.exclude_styles_var.set("")
        self.vocal_gender_var.set("")
        self.lyrics_mode_var.set("")
        self.weirdness_var.set(50)
        self.style_influence_var.set(50)
        self.persona_name_var.set("")
        self._toggle_advanced_options()
