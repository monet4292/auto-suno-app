"""
Account Panel - Quản lý tài khoản
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
import time

from selenium.common.exceptions import WebDriverException

from src.core import AccountManager, SessionManager
from src.utils import format_datetime, logger


class AccountPanel(ctk.CTkFrame):
    """Panel quản lý tài khoản"""
    
    def __init__(self, parent, account_manager: AccountManager, session_manager: SessionManager):
        super().__init__(parent)
        
        self.account_manager = account_manager
        self.session_manager = session_manager
        
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
            text="Quản lý tài khoản",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        
        # Buttons
        btn_frame = ctk.CTkFrame(header_frame)
        btn_frame.grid(row=0, column=1, padx=20, pady=20)
        
        add_btn = ctk.CTkButton(
            btn_frame,
            text="Thêm tài khoản",
            command=self.add_account,
            width=150
        )
        add_btn.grid(row=0, column=0, padx=5)
        
        refresh_btn = ctk.CTkButton(
            btn_frame,
            text="Làm mới",
            command=self.refresh,
            width=120
        )
        refresh_btn.grid(row=0, column=1, padx=5)
        
        # Account list
        list_frame = ctk.CTkFrame(self)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        list_frame.grid_columnconfigure(0, weight=1)
        list_frame.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame
        self.scrollable = ctk.CTkScrollableFrame(list_frame)
        self.scrollable.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.scrollable.grid_columnconfigure(0, weight=1)
    
    def refresh(self):
        """Refresh account list"""
        
        # Clear current list
        for widget in self.scrollable.winfo_children():
            widget.destroy()
        
        # Load accounts
        self.account_manager.load_accounts()
        accounts = self.account_manager.get_all_accounts()
        
        if not accounts:
            no_account_label = ctk.CTkLabel(
                self.scrollable,
                text="Chưa có tài khoản nào\nHãy thêm tài khoản mới!",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            no_account_label.grid(row=0, column=0, pady=100)
            return
        
        # Display accounts
        for idx, account in enumerate(accounts):
            self.create_account_card(account, idx)
    
    def create_account_card(self, account, row):
        """Create account card"""
        
        card = ctk.CTkFrame(self.scrollable, corner_radius=10)
        card.grid(row=row, column=0, sticky="ew", pady=6, padx=10)
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
        
        created_label = ctk.CTkLabel(
            card,
            text=f"Tạo: {format_datetime(account.created_at)}",
            text_color="gray"
        )
        created_label.grid(row=2, column=0, sticky="w", padx=20, pady=2)
        
        if account.last_used:
            used_label = ctk.CTkLabel(
                card,
                text=f"Dùng: {format_datetime(account.last_used)}",
                text_color="gray"
            )
            used_label.grid(row=3, column=0, sticky="w", padx=20, pady=(2, 15))
        else:
            ctk.CTkLabel(card, text="").grid(row=3, column=0, pady=(2, 15))
        
        # Action buttons
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=4, padx=20, pady=10)
        
        use_btn = ctk.CTkButton(
            btn_frame,
            text="🌐 Đăng nhập",
            command=lambda: self.use_account(account.name),
            width=100
        )
        use_btn.grid(row=0, column=0, padx=5, pady=5)
        
        rename_btn = ctk.CTkButton(
            btn_frame,
            text="Đổi tên",
            command=lambda: self.rename_account(account.name),
            width=100
        )
        rename_btn.grid(row=0, column=1, padx=5, pady=5)
        
        delete_btn = ctk.CTkButton(
            btn_frame,
            text="Xóa",
            command=lambda: self.delete_account(account.name),
            width=100,
            fg_color="red",
            hover_color="darkred"
        )
        delete_btn.grid(row=0, column=2, padx=5, pady=5)
    
    def add_account(self):
        """Add new account"""
        
        dialog = ctk.CTkInputDialog(
            text="Nhập tên tài khoản:",
            title="Thêm tài khoản mới"
        )
        account_name = dialog.get_input()
        
        if not account_name:
            return
        
        dialog = ctk.CTkInputDialog(
            text="Nhập email:",
            title="Thêm tài khoản mới"
        )
        email = dialog.get_input()
        
        if not email:
            return
        
        # Add account
        if self.account_manager.add_account(account_name, email):
            messagebox.showinfo("Thành công", f"Đã thêm tài khoản: {account_name}")
            
            # Launch browser for login
            if messagebox.askyesno("Đăng nhập", "Mở trình duyệt để đăng nhập ngay?"):
                self.use_account(account_name)
            
            self.refresh()
        else:
            messagebox.showerror("Lỗi", "Không thể thêm tài khoản. Tên đã tồn tại!")
    
    def use_account(self, account_name: str):
        """Use account - launch browser"""
        
        def launch():
            driver = self.session_manager.launch_browser(account_name)
            if driver:
                self.account_manager.update_last_used(account_name)
                self.after(0, self.refresh)
                self.after(0, lambda: self._monitor_browser_session(driver, account_name))
            else:
                self.after(0, lambda: messagebox.showerror("Lỗi", "Không thể mở trình duyệt!"))
        
        # Launch in thread to avoid blocking UI
        thread = threading.Thread(target=launch, daemon=True)
        thread.start()

    def _monitor_browser_session(self, driver, account_name: str):
        """Show success toast once the browser closes."""
        def wait_for_exit():
            while True:
                try:
                    _ = driver.title
                except WebDriverException:
                    break
                except Exception:
                    break
                time.sleep(1)

            try:
                driver.quit()
            except Exception:
                pass

            self.after(0, lambda: messagebox.showinfo(
                "Thành công",
                "Đã lưu thông tin tài khoản thành công."
            ))

        monitor = threading.Thread(target=wait_for_exit, daemon=True)
        monitor.start()
    
    def rename_account(self, old_name: str):
        """Rename account"""
        
        dialog = ctk.CTkInputDialog(
            text=f"Nhập tên mới cho '{old_name}':",
            title="Đổi tên tài khoản"
        )
        new_name = dialog.get_input()
        
        if not new_name or new_name == old_name:
            return
        
        if self.account_manager.rename_account(old_name, new_name):
            messagebox.showinfo("Thành công", f"Đã đổi tên: {old_name} → {new_name}")
            self.refresh()
        else:
            messagebox.showerror("Lỗi", "Không thể đổi tên tài khoản!")
    
    def delete_account(self, account_name: str):
        """Delete account"""
        
        if not messagebox.askyesno(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa tài khoản '{account_name}'?"
        ):
            return
        
        delete_profile = messagebox.askyesno(
            "Xóa dữ liệu",
            "Xóa cả dữ liệu profile (session, cookies)?"
        )
        
        if self.account_manager.delete_account(account_name, delete_profile):
            messagebox.showinfo("Thành công", f"Đã xóa tài khoản: {account_name}")
            self.refresh()
        else:
            messagebox.showerror("Lỗi", "Không thể xóa tài khoản!")
