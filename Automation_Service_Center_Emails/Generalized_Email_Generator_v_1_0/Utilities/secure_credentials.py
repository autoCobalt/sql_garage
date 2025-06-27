import ctypes
import sys
from typing import Optional
import random
import string
import gc

try: # importing install_required_libraries()
    from .package_checker import install_required_libraries
except ImportError:
    from package_checker import install_required_libraries
install_required_libraries({'customtkinter'})
import customtkinter as ctk

class SecureCredentialManager:
    """
    Manages credentials more securely by minimizing exposure in memory.
    """
    def __init__(self):
        self._username_widget: Optional[ctk.CTkEntry] = None
        self._password_widget: Optional[ctk.CTkEntry] = None
        self._password_buffer: Optional[bytearray]    = None
        self._widget_cleared: bool = False
        
    def set_widgets(self, username_widget: ctk.CTkEntry, password_widget: ctk.CTkEntry) -> None:
        """Store references to the entry widgets."""
        self._username_widget = username_widget
        self._password_widget = password_widget
        
        # Disable copy/paste for password field
        self._password_widget.bind("<Control-c>", lambda e: "break")
        self._password_widget.bind("<Control-x>", lambda e: "break")
        self._password_widget.bind("<Control-v>", lambda e: "break")
        self._password_widget.bind("<Button-3>",  lambda e: "break")

        self._password_widget.bind("<FocusOut>", self._clear_clipboard)
    
    def _clear_clipboard(self, event=None) -> None:
        try:
            if self._password_widget and self._password_widget.winfo_exists():
                self._password_widget.tk.call('clipboard', 'clear')
        except:
            pass
        
    def get_credentials(self) -> tuple[str, str]:
        """Retrieve credentials only when needed."""
        if not self._username_widget or not self._password_widget:
            return "", ""
            
        username = self._username_widget.get().strip()

        password = self._password_widget.get()
        if password:
            self._password_buffer = bytearray(password.encode('utf-8'))
            self._widget_cleared = False

            return username, password
        
        return username, ""
    
    def get_credentials_safe(self) -> tuple[str, str]:
        username, password = self.get_credentials()
        if password:
            self._overwrite_widget_password()
        return username, password

    def _overwrite_widget_password(self) -> None:
        if self._password_widget and not self._widget_cleared:
            try:
                current_length = len(self._password_widget.get())
                random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=max(current_length, 20)))
                self._password_widget.delete(0, "end")
                self._password_widget.insert(0, random_data)
                self._password_widget.delete(0, "end")
                self._widget_cleared = True
            except Exception:
                pass
    
    def get_password_from_buffer(self) -> str:
        if self._password_buffer:
            try:
                return self._password_buffer.decode('utf-8')
            except Exception:
                return ""
        return ""

    def clear_password(self) -> None:
        """Securely clear password from widget."""
        if self._password_widget and not self._widget_cleared:
            try:
                # Overwrite with random data first
                for _ in range(3):
                    random_data = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
                    self._password_widget.delete(0, "end")
                    self._password_widget.insert(0, random_data)

                self._password_widget.delete(0, "end")
                self._widget_cleared = True
            except Exception:
                pass
        
        self._clear_password_buffer()
    
    def _clear_password_buffer(self) -> None:
        if self._password_buffer:
            for i in range(len(self._password_buffer)):
                self._password_buffer[i] = random.randint(0, 255)
            
            self._password_buffer.clear()
            self._password_buffer = None

            gc.collect()
    
    def clear_all(self) -> None:
        """Clear both username and password."""
        self.clear_password()
        if self._username_widget:
            try:
                random_data = ''.join(random.choices(string.ascii_letters, k=20))
                self._username_widget.delete(0, "end")
                self._username_widget.insert(0, random_data)
                self._username_widget.delete(0, "end")
            except Exception:
                pass
        
        self._clear_clipboard()
    
    def get_username_widget(self) -> Optional[ctk.CTkEntry]:
        return self._username_widget
    
    def get_password_widget(self) -> Optional[ctk.CTkEntry]:
        return self._password_widget

    @staticmethod
    def secure_string_clear(text: str) -> None:
        if not text:
            return
        
        gc.collect()

class SecurePasswordContext:
    def __init__(self, credential_manager: SecureCredentialManager, clear_on_exit: bool = True):
        self.credential_manager = credential_manager
        self.username = ""
        self.password = ""
        self.clear_on_exit = clear_on_exit
    
    def __enter__(self):
        self.username, self.password = self.credential_manager.get_credentials()
        return self.username, self.password
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.clear_on_exit:
            self.credential_manager._overwrite_widget_password()
        
        if self.password:
            SecureCredentialManager.secure_string_clear(self.password)
            self.password = ''.join(random.choices(string.ascii_letters, k=len(self.password)))
            del self.password

        if self.clear_on_exit:
            self.credential_manager._clear_password_buffer()
        gc.collect()