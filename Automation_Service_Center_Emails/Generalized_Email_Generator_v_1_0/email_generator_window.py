import os
import sys
from io import StringIO
import tkinter as tk
import re
import queue
import threading
import csv
import codecs
import signal
from typing import Dict, List, Optional, Final, Any, Callable

from Utilities import (
    #from package_checker
    install_required_libraries, 
    
    #from file_loader
    get_confidential_csv_files, get_confidential_email_templates, read_csv_file, select_csv_file, select_email_file, normalize_field_for_matching,

    #from constants
    color_scheme,

    #from db_utilities
    query_db_for_busn_emails_from_emplid, test_connection,

    #from outlook_utilities
    create_draft_email_individual_to, create_draft_email_bcc_all, get_template_placeholders,

    # SecureCredentialManager class to manage username and password
    # SecurePasswordContext to manage password security
    SecureCredentialManager, SecurePasswordContext
)

install_required_libraries({'customtkinter'})
import customtkinter as ctk
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class UIConstants:
    WINDOW_WIDTH:   Final[int] = 1200
    WINDOW_HEIGHT:  Final[int] = 1300
    PADDING_LARGE:  Final[int] = 20
    PADDING_MEDIUM: Final[int] = 15
    PADDING_SMALL:  Final[int] = 8

    # font tuple (font_style, font_size, font_weight)
    TITLE_FONT: Final[tuple] = ("Consolas", 22, "bold")
    INPUT_FONT: Final[tuple] = ("Consolas", 11)
    BUTTON_FONT:Final[tuple] = ("Consolas", 11, "bold")

class MainApplicationWindow:
    def __init__(self) -> None:
        self.window: ctk.CTk = ctk.CTk()
        self.connection_tested: bool = False
        self.csv_files: List[Dict[str, str]] = []
        self.email_templates: List[Dict[str, str]] = []

        # UI Elements
        self.connection_button: Optional[ctk.CTkButton]   = None
        self.csv_dropdown:      Optional[ctk.CTkComboBox] = None
        self.email_dropdown:    Optional[ctk.CTkComboBox] = None
        self.output_textbox:    Optional[ctk.CTkTextbox]  = None
        self.connection_status: Optional[ctk.CTkLabel]    = None

        # Credential manager
        self.credential_manager = SecureCredentialManager()

        # Session timeout variables
        self._session_timer: Optional[str] = None
        self._session_timeout_ms: int = 300000

        # Field transformation attributes
        self.field_transform_frame: Optional[ctk.CTkFrame] = None
        self.field_widgets: Dict[str, Any] = {}
        self.current_csv_fields: List[str] = []
        self.emplid_field_var: Optional[tk.StringVar] = None
        self.bcc_mode_var: Optional[tk.BooleanVar] = None
        self.bcc_checkbox: Optional[ctk.CTkCheckBox] = None
        self._updating_field_config = False

        # Track currently loaded file paths to prevent unnecessary reloading
        self._current_csv_path: Optional[str] = None
        self._current_email_path: Optional[str] = None

        # Placeholder matching section
        self.outlook_placeholders: List[str] = []
        self.placeholder_mapping: Dict[str, Optional[str]] = {}
        self.unmatched_placeholders: List[str] = []
        self._extracting_placeholders: bool = False
        self._updating_field_mapping: bool = False
        self._updating_field_config: bool = False

        # Initialize the window
        self._setup_window()
        self._create_ui_elements()
        self._load_file_lists()
        self._setup_print_redirection()

        self.window.after(500, self._scroll_console_to_bottom)

    def _scroll_console_to_bottom(self) -> None:
        try:
            if self.output_textbox:
                self.output_textbox.configure(state="normal")
                self.output_textbox.see("end")
                self.output_textbox.configure(state="disabled")
        except Exception:
            pass

    @staticmethod
    def validate_db_credentials(username: str, password: str) -> tuple[bool, str]:
        if not username or not password:
            return False, "Username and password are required"
        
        if len(username) > 50:
            return False, "Username too long (max 50 characters)"
        
        dangerous_patterns = ["'", '"', "--", "/*", "*/", ";", "\\", "\x00"]
        for pattern in dangerous_patterns:
            if pattern in username:
                return False, f"Invalid character in username: {pattern}"
            
        if len(password) > 100:
            return False, "Password too long (max 100 characters)"
        
        return True, ""

    # Sanitize output text
    @staticmethod
    def sanitize_output_text(text: str) -> str:
        if not isinstance(text, str):
            text = str(text)
        
        # Remove control characters that could affect display
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        if len(text) > 10000:
            text = text[:10000] + "... (truncated)"
        return text

    def _start_session_timeout(self) -> None:
        if self._session_timer:
            self.window.after_cancel(self._session_timer)
        
        def session_timeout_expired() -> None:
            self._write_to_output("\u23F1 Session timed out. Please test connection again.\n")
            self._clear_credentials()
            
        self._session_timer = self.window.after(self._session_timeout_ms, session_timeout_expired)

    def _debug_placeholder_state(self) -> None:
        self._write_to_output("=== PLACEHOLDER DEBUG STATE ===")
        self._write_to_output(f"Outlook placeholders: {self.outlook_placeholders}")
        self._write_to_output(f"Placeholder mapping: {self.placeholder_mapping}")
        self._write_to_output(f"Unmatched placeholders: {self.unmatched_placeholders}")
        self._write_to_output(f"Extracting flag: {self._extracting_placeholders}")
        self._write_to_output(f"Updating mapping flag: {self._updating_field_mapping}")
        self._write_to_output(f"Updating config flag: {self._updating_field_config}")
        self._write_to_output("=== END DEBUG STATE ===")

    def _setup_window(self) -> None:
        self.window.title("Custom Email Generator")
        
        self.window.minsize(1000, 700)
        self.window.resizable(True, True)
        self.window.configure(fg_color=color_scheme["background"])

        width = max(1200, UIConstants.WINDOW_WIDTH)
        height = max(1000, UIConstants.WINDOW_HEIGHT)
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        self.window.update_idletasks()

    def _create_ui_elements(self) -> None:
        self.window.grid_columnconfigure(0, weight=0, minsize=400) # Left column for connection section
        self.window.grid_columnconfigure(1, weight=1, minsize=600) # Right column for file section
        self.window.grid_rowconfigure(4, weight=1)

        self._create_connection_section()
        self._create_file_selection_section()
        self._create_output_section()

    def _create_connection_section(self) -> None:
        conn_frame = ctk.CTkFrame(
            self.window, 
            fg_color=color_scheme["surface"],
            corner_radius=12,
            border_width=1,
            border_color=color_scheme["secondary"]
        )
        conn_frame.grid(row=1, column=0, padx=(20, 10), pady=(15, 10), sticky="nsew")
        conn_frame.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(conn_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=(10, 10), pady=(10,5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)

        conn_title = ctk.CTkLabel(
            header_frame,
            text="\U0001F517 Database Connection",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=color_scheme["text"]
        )
        conn_title.grid(row=0, column=0, padx=(5, 0), sticky="w")

        spacer_frame = ctk.CTkFrame(header_frame, fg_color="transparent", height=1)
        spacer_frame.grid(row=0, column=1, sticky="ew")

        clear_creds_button = ctk.CTkButton(
            header_frame,
            text="Clear",
            command=self._clear_credentials,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=color_scheme["secondary"],
            hover_color=color_scheme["primary_hover"],
            text_color=color_scheme["text"],
            corner_radius=6
        )
        clear_creds_button.grid(row=0, column=2, padx=(10, 10), sticky="e")

        self._create_credential_inputs(conn_frame)
        self._create_connection_status(conn_frame)

    def _clear_credentials(self) -> None:
        try:
            username_widget = self.credential_manager.get_username_widget()
            password_widget = self.credential_manager.get_password_widget()

            if username_widget:
                username_widget.delete(0, "end")
            if password_widget:
                password_widget.delete(0, "end")
                password_widget.configure(show="*")

            self.credential_manager.clear_all()

            self.connection_tested = False

            if self._session_timer:
                self.window.after_cancel(self._session_timer)
                self._session_timer = None

            self._reset_connection_ui()

            self._write_to_output("\U0001F9F9 Credentials cleared and connection reset")

            if username_widget:
                username_widget.focus()

        except Exception as e:
            self._write_to_output(f"\u274C Error clearing credentials: {e}")
    
    def _create_credential_inputs(self, parent: ctk.CTkFrame) -> None:
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.grid(row=1, column=0, columnspan=2, padx=(10,10), pady=5, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        username_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Username",
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color=color_scheme["background"],
            text_color=color_scheme["text"],
            border_color=color_scheme["secondary"],
            corner_radius=8
        )
        username_entry.grid(row=0, column=0, padx=(10,10), pady=(0, 5), sticky="ew")

        password_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Password",
            show="*",
            font=ctk.CTkFont(size=12),
            height=35,
            fg_color=color_scheme["background"],
            text_color=color_scheme["text"],
            border_color=color_scheme["secondary"],
            corner_radius=8
        )
        password_entry.grid(row=1, column=0, padx=(10,10), sticky="ew")

        self.credential_manager.set_widgets(username_entry, password_entry)

        def clear_clipboard_on_focus(event):
            try:
                self.window.clipboard_clear()
            except:
                pass

        password_widget = self.credential_manager.get_password_widget()
        username_widget = self.credential_manager.get_username_widget()

        # Keyboard shortcuts
        if password_widget:
            password_widget.bind("<FocusIn>", clear_clipboard_on_focus)
            password_widget.bind("<Return>", lambda e: self._test_connection_async())
            password_widget.bind("<Control-Return>", lambda e: self._test_connection_async())
            password_widget.bind("<KeyRelease>", self._on_credential_change)

        if username_widget:
            username_widget.bind("<Tab>", lambda e: password_widget.focus() if password_widget else None) # type: ignore
            username_widget.bind("<KeyRelease>", self._on_credential_change)
        
    def _create_connection_status(self, parent_frame: ctk.CTkFrame) -> None:
        status_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        status_frame.grid(row=2, column=0, columnspan=2, padx=(20,20), pady=(2, 12), sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        self.connection_status = ctk.CTkLabel(
            status_frame,
            text="\u26AA Not connected",
            font=ctk.CTkFont(size=11),
            text_color=color_scheme["disabled"]
        )
        self.connection_status.grid(row=0, column=0, pady=(2, 5), sticky="w")

        self.connection_button = ctk.CTkButton(
            status_frame,
            text="Test Connection",
            command=self._test_connection_async,
            font=ctk.CTkFont(size=12, weight="bold"),
            height=35,
            corner_radius=8,
            fg_color=color_scheme["primary"],
            hover_color=color_scheme["primary_hover"],
            text_color_disabled=color_scheme["disabled"],
            text_color=color_scheme["text"]
        )
        self.connection_button.grid(row=1, column=0, sticky="ew")

    def _create_file_selection_section(self) -> None:
        file_frame = ctk.CTkFrame(
            self.window, 
            fg_color=color_scheme["surface"],
            corner_radius=12,
            border_width=1,
            border_color=color_scheme["secondary"]
        )
        file_frame.grid(row=1, column=1, padx=(10,20), pady=(15, 10), sticky="nsew")
        file_frame.grid_columnconfigure(0, weight=1)

        file_title = ctk.CTkLabel(
            file_frame,
            text="\U0001F4C1 File Selection",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=color_scheme["text"]
        )
        file_title.grid(row=0, column=0, padx=(15,10), pady=(8, 3), sticky="w")

        self._create_file_selector(
            file_frame,
            row=1,
            label="\U0001F4CA CSV Data File",
            dropdown_var="csv_dropdown",
            open_command=self._open_csv_file,
            values=["No files found"]
        )

        self._create_file_selector(
            file_frame,
            row=2,
            label="\U0001F4E7 Email Template",
            dropdown_var="email_dropdown",
            open_command=self._open_email_file,
            values=["No templates found"]
        )
    
    def _create_file_selector(self, parent: ctk.CTkFrame, row: int, label: str, dropdown_var: str, open_command: Callable[[], None], values: List[str]) -> None:
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.grid(row=row, column=0, padx=20, pady=3, sticky="ew")
        container.grid_columnconfigure(0, weight=1)

        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color_scheme["text"]
        )
        label_widget.grid(row=0, column=0, pady=(0, 3), sticky="w")

        selector_frame = ctk.CTkFrame(container, fg_color="transparent")
        selector_frame.grid(row=1, column=0, sticky="ew")
        selector_frame.grid_columnconfigure(0, weight=1)

        command_callback = None
        if dropdown_var == "csv_dropdown":
            command_callback = self._on_csv_dropdown_change
        elif dropdown_var == "email_dropdown":
            command_callback = self._on_email_dropdown_change

        dropdown = ctk.CTkComboBox(
            selector_frame,
            values=values,
            state="readonly",
            font=ctk.CTkFont(size=11),
            height=32,
            fg_color=color_scheme["background"],
            text_color=color_scheme["text"],
            border_color=color_scheme["secondary"],
            button_color=color_scheme["primary"],
            button_hover_color=color_scheme["primary_hover"],
            corner_radius=8,
            command=command_callback
        )
        dropdown.grid(row=0, column=0, padx=(0,10), sticky="ew")
        setattr(self, dropdown_var, dropdown)

        open_button = ctk.CTkButton(
            selector_frame,
            text="Browse",
            command=open_command,
            width=80,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color=color_scheme["accent"],
            hover_color=color_scheme["secondary"],
            text_color=color_scheme["background"],
            corner_radius=8
        )
        open_button.grid(row=0, column=1)

    def _create_output_section(self) -> None:
        console_frame = ctk.CTkFrame(
            self.window,
            fg_color=color_scheme["surface"],
            corner_radius=12,
            border_width=1,
            border_color=color_scheme["secondary"]
        )
        console_frame.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")
        console_frame.grid_columnconfigure(0, weight=1)
        console_frame.grid_rowconfigure(1, weight=1)

        header_frame = ctk.CTkFrame(console_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=0)
        header_frame.grid_columnconfigure(1, weight=1)
        header_frame.grid_columnconfigure(2, weight=0)

        console_title = ctk.CTkLabel(
            header_frame,
            text="\U0001F4CB Console Output",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=color_scheme["text"]
        )
        console_title.grid(row=0, column=0, sticky="w")

        spacer_frame = ctk.CTkFrame(header_frame, fg_color="transparent", height=1)
        spacer_frame.grid(row=0, column=1, sticky="ew")

        clear_button = ctk.CTkButton(
            header_frame,
            text="Clear",
            command=self._clear_output,
            width=60,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=color_scheme["secondary"],
            hover_color=color_scheme["primary_hover"],
            text_color=color_scheme["text"],
            corner_radius=6
        )
        clear_button.grid(row=0, column=2, pady=(0, 5), sticky="e")

        self.output_textbox = ctk.CTkTextbox(
            console_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color=color_scheme["background"],
            text_color=color_scheme["text"],
            border_color=color_scheme["secondary"],
            corner_radius=8,
            border_width=1
        )
        self.output_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.output_textbox.configure(state="disabled")
    
    def _clear_output(self) -> None:
        try:
            self.output_textbox.configure(state="normal") # type: ignore
            self.output_textbox.delete("1.0", "end") # type: ignore
            self.output_textbox.configure(state="disabled") # type: ignore
        except Exception as e:
            self._write_to_output(f"\u274C Error clearing output: {e}")

    def _load_file_lists(self) -> None:

        self._write_to_output("\U0001F4C2 Loading available files...")

        try:
            
            self.csv_files = get_confidential_csv_files()
            if self.csv_files:
                csv_names = [list(file_dict.keys())[0] for file_dict in self.csv_files]
                self.csv_dropdown.configure(values=csv_names) # type: ignore
                self.csv_dropdown.set(csv_names[0]) # type: ignore

                default_csv_path = list(self.csv_files[0].values())[0]
                self._current_csv_path = default_csv_path
                self._write_to_output("Loading CSV fields first...")
                self._load_csv_fields(default_csv_path)
            else:
                self.csv_dropdown.configure(values=["No CSV files found"]) # type: ignore
                self.csv_dropdown.set("No CSV files found") # type: ignore

            # Load email templates AFTER CSV fields are loaded
            self.email_templates = get_confidential_email_templates()
            if self.email_templates:
                email_names = [list(template_dict.keys())[0] for template_dict in self.email_templates]
                self.email_dropdown.configure(values=email_names) # type: ignore
                self.email_dropdown.set(email_names[0]) # type: ignore

                default_template_path = list(self.email_templates[0].values())[0]
                self._current_email_path = default_template_path
                self._write_to_output("Loading email template placeholders...")
                self._extract_template_placeholders(default_template_path)
            else:
                self.email_dropdown.configure(values=["No email templates found"]) # type: ignore
                self.email_dropdown.set("No email templates found") # type: ignore

            self._app_fully_initialized = True

        except FileNotFoundError:
            self._write_to_output("\U0001F4C1 Confidential directory not found.")
        except PermissionError:
            self._write_to_output("\U0001F512 Permission denied accessing confidential files.")
        except Exception as e:
            self._write_to_output(f"\u274C Error loading file lists: {e}")

    @staticmethod
    def validate_csv_field_names(field_names: List[str]) -> tuple[bool, str]:
        if not field_names:
            return False, "No field names found"
        
        if len(field_names) != len(set(field_names)):
            return False, "Duplicate field names detected"
        
        for field in field_names:
            if not field or not field.strip():
                return False, "Empty field name found"
            if len(field) > 100:
                return False, f"Field name too long: {field[:50]}..."
        
        return True, ""

    def _extract_template_placeholders(self, template_path: str) -> None:
        try:
            if hasattr(self, '_extracting_placeholders') and self._extracting_placeholders:
                self._write_to_output("\u26A0 Skipping recursive placeholder extraction")
                return

            self._extracting_placeholders = True

            try:
                self.outlook_placeholders = get_template_placeholders(self._write_to_output, template_path)

                if self.outlook_placeholders:
                    plural_check = "s" if len(self.outlook_placeholders) > 1 else ""
                    self._write_to_output(f"Found {len(self.outlook_placeholders)} placeholder{plural_check} in email msg template: {', '.join(self.outlook_placeholders)}")

                    if hasattr(self, 'current_csv_fields') and self.current_csv_fields:
                        self._update_field_mapping()
                else:
                    self._write_to_output("No variable placeholders found in the email template - template will be used as-is")
                    self.placeholder_mapping = {}
                    self.unmatched_placeholders = []

                    if hasattr(self, 'current_csv_fields') and self.current_csv_fields:
                        self._update_field_mapping()
            except Exception as inner_e:
                self._write_to_output(f"\u26A0 Error extracting placeholders: {inner_e}")
                self.outlook_placeholders = []
                self.placeholder_mapping = {}
                self.unmatched_placeholders = []

        finally:
            self._extracting_placeholders = False
            self._write_to_output("\u2705 Placeholder extraction completed")

    def _update_field_mapping(self) -> None:
        if hasattr(self, '_updating_field_mapping') and self._updating_field_mapping:
            self._write_to_output("\U0001F504 Preventing recursive field mapping update")
            return
        
        if not hasattr(self, 'current_csv_fields') or not self.current_csv_fields:
            self._write_to_output("CSV fields not loaded yet - skipping field mapping update")
            return

        self._updating_field_mapping = True

        try:
        
            self.placeholder_mapping = {}
            self.unmatched_placeholders = []

            if not hasattr(self, 'outlook_placeholders') or not self.outlook_placeholders:
                self._write_to_output("No email placeholders to map - using direct CSV field mapping")

            else:
                self._write_to_output(f"\U0001F517 Mapping {len(self.outlook_placeholders)} placeholders to CSV fields")

                for placeholder in self.outlook_placeholders:
                    if placeholder.lower() == 'email':
                        continue
            
                    normalized_placeholder = normalize_field_for_matching(placeholder)

                    matched = False
                    for csv_field in self.current_csv_fields:
                        if normalized_placeholder == csv_field:
                            self.placeholder_mapping[placeholder] = csv_field
                            matched = True
                            break
                    
                    if not matched:
                        self.placeholder_mapping[placeholder] = None
                        self.unmatched_placeholders.append(placeholder)

                if self.unmatched_placeholders:
                    self._write_to_output(f"\nAvailable CSV fields: {', '.join(self.current_csv_fields)}")
                    
            should_recreate_ui = (
                self.field_transform_frame and
                hasattr(self, 'current_original_fields') and
                hasattr(self, 'current_csv_fields') and
                not (hasattr(self, '_updating_field_config') and self._updating_field_config) and
                not (hasattr(self, '_initial_ui_creation') and self._initial_ui_creation)
            )

            if should_recreate_ui:
                self._write_to_output("\U0001F3A8 Recreating field configuration UI")
                self._create_field_transform_section(self.current_original_fields, self.current_csv_fields)
            else:
                self._write_to_output("\u23F8 Skipping UI recreation (already updating or missing data)")
        except Exception as e:
            self._write_to_output(f"\u274C Error in field mapping: {e}")
        finally:
            self._updating_field_mapping = False
            self._write_to_output("\u2705 Field mapping update completed")

    def _on_csv_dropdown_change(self, selected_name: str) -> None:
        self._write_to_output("\n")
        try:
            if selected_name in ["No files found", "No CSV files found"]:
                if self.field_transform_frame:
                    self.field_transform_frame.destroy()
                    self.field_widgets.clear()
                self._current_csv_path = None
                return

            if hasattr(self, '_debug_info_printed'):
                self._debug_info_printed = False
            if hasattr(self, '_auto_select_message_printed'):
                self._auto_select_message_printed = False
            
            csv_path = None
            for file_dict in self.csv_files:
                if selected_name in file_dict:
                    csv_path = file_dict[selected_name]
                    break

            if csv_path and csv_path == self._current_csv_path:
                self._write_to_output(f"\U0001F4C4 CSV file '{selected_name}' is already loaded")
                self.window.after(100, self._scroll_console_to_bottom)
                return

            if hasattr(self, '_debug_info_printed'):
                self._debug_info_printed = False
            if hasattr(self, '_auto_select_message_printed'):
                self._auto_select_message_printed = False
            
            if csv_path and os.path.exists(csv_path):
                self._write_to_output(f"Loading fields from: {selected_name}")
                self._current_csv_path = csv_path
                self._load_csv_fields(csv_path)
                self.window.after(100, self._scroll_console_to_bottom)
            else:
                self._write_to_output(f"\u274C CSV file not found: {csv_path if csv_path else selected_name}")

        except Exception as e:
            self._write_to_output(f"\u274C Error loading CSV fields: {e}")

    def _on_email_dropdown_change(self, selected_name: str) -> None:
        try:
            if selected_name in ["No templates found", "No email templates found"]:
                self.outlook_placeholders = []
                self.placeholder_mapping = {}
                self.unmatched_placeholders = []
                if self.field_transform_frame and hasattr(self, 'current_csv_fields'):
                    self._create_field_transform_section(self.current_original_fields, self.current_csv_fields)
                self._current_email_path = None
                return
            
            email_path = None
            for template_dict in self.email_templates:
                if selected_name in template_dict:
                    email_path = template_dict[selected_name]
                    break

            if email_path and email_path == self._current_email_path:
                self._write_to_output(f"\U0001F4E7 Email template '{selected_name}' is already loaded")
                self.window.after(100, self._scroll_console_to_bottom)
                return
            
            if email_path and os.path.exists(email_path):
                self._write_to_output(f"Loading template: {email_path}")
                self._current_email_path = email_path
                self._extract_template_placeholders(email_path)
                self.window.after(100, self._scroll_console_to_bottom)
            else:
                self._write_to_output(f"\u274C Email template not found: {email_path if email_path else selected_name}")
        except Exception as e:
            self._write_to_output(f"\u274C Error loading email template: {e}")

    def _setup_print_redirection(self) -> None:
        self.original_stdout = sys.stdout

        class TextboxWriter:
            def __init__(self, textbox, original_stdout):
                self.textbox = textbox
                self.original_stdout = original_stdout

            def write(self, text: str) -> None:
                if text.strip():
                    self.textbox.after(0, lambda t=text: self._safe_write(t))
                self.original_stdout.write(text)

            def _safe_write(self, text: str) -> None:
                try:
                    self.textbox.configure(state="normal")
                    self.textbox.insert("end", text)
                    if not text.endswith('\n'):
                        self.textbox.insert("end", '\n')
                    self.textbox.see("end")
                    self.textbox.configure(state="disabled")
                except:
                    pass

            def flush(self) -> None:
                self.original_stdout.flush()

        sys.stdout = TextboxWriter(self.output_textbox, self.original_stdout)

    def _write_to_output(self, text: str) -> None:
        safe_text = text
        try:
            safe_text = self.sanitize_output_text(text)
            self.output_textbox.configure(state="normal") # type: ignore
            self.output_textbox.insert("end", f"{safe_text}\n") # type: ignore
            self.output_textbox.see("end") # type: ignore
            self.output_textbox.configure(state="disabled") # type: ignore
        except Exception as e:
            print(f"Error writing to output: {e}")

    def _on_credential_change(self, event) -> None:
        if self.connection_tested:
            self.connection_tested = False

            if self._session_timer:
                self.window.after_cancel(self._session_timer)
                self._session_timer = None
            
        self._reset_connection_ui()

    def _update_connection_ui(self, success: bool) -> None:
        username_widget = self.credential_manager.get_username_widget()
        password_widget = self.credential_manager.get_password_widget()

        if success:
            self.connection_button.configure( # type: ignore
                text="\u2713 Submit",
                text_color=color_scheme["secondary"],
                fg_color=color_scheme["success"],
                hover_color=color_scheme["success_hover"]
            )

            self.connection_status.configure( # type: ignore
                text="\U0001F7E2 Connected",
                text_color=color_scheme["success"]
            )

            if username_widget:
                username_widget.configure(border_color=color_scheme["success"]) # type: ignore
            if password_widget:
                password_widget.configure(border_color=color_scheme["success"]) # type: ignore

        else:
            self.connection_button.configure( # type: ignore
                text="Test Connection",
                text_color=color_scheme["text"],
                fg_color=color_scheme["primary"],
                hover_color=color_scheme["primary_hover"]
            )

            self.connection_status.configure( # type: ignore
                text="\U0001F534 Failed",
                text_color=color_scheme["error"]
            )

            if username_widget:
                username_widget.configure(border_color=color_scheme["error"]) # type: ignore
            if password_widget:
                password_widget.configure(border_color=color_scheme["error"]) # type: ignore

    def _test_connection_with_timeout(self, username: str, password: str, timeout_seconds: int = 30) -> tuple[bool, str]:
        result_queue = queue.Queue()

        def test_worker():
            try:
                result = test_connection(username, password)
                result_queue.put((result, None))
            except Exception as e:
                result_queue.put((False, str(e)))
        
        worker_thread = threading.Thread(target=test_worker, daemon=True)
        worker_thread.start()

        try:
            # Wait for result with timeout
            success, error = result_queue.get(timeout=timeout_seconds)
            return success, error if error else ""
        except queue.Empty:
            return False, f"Connection test timed out after {timeout_seconds} seconds"

    def _test_connection_async(self) -> None:
        if self.connection_tested:
            self._on_submit()
            return


        with SecurePasswordContext(self.credential_manager, clear_on_exit=False) as (username, password):
            is_valid, error_msg = self.validate_db_credentials(username, password)
            if not is_valid:
                self._write_to_output(f"Invalid credentials: {error_msg}")
                return

            self.connection_button.configure(state="disabled", text="Testing...") # type: ignore

            captured_username: str = str(username) if username else ""
            captured_password: str = str(password) if password else ""

            def test_in_thread():
                try:
                    success, error_msg = self._test_connection_with_timeout(
                        username=captured_username, 
                        password=captured_password, 
                        timeout_seconds=30
                    )

                    if error_msg:
                        self.window.after(0, lambda: self._on_test_error(error_msg))
                    else:
                        self.window.after(0, lambda: self._on_test_result(success))

                except Exception as e:
                    self.window.after(0, lambda: self._on_test_error(str(e)))

            threading.Thread(target=test_in_thread, daemon=True).start()

    def _reset_connection_ui(self) -> None:
        username_widget = self.credential_manager.get_username_widget()
        password_widget = self.credential_manager.get_password_widget()

        self.connection_button.configure( # type: ignore
            text="Test Connection",
            text_color=color_scheme["text"],
            fg_color=color_scheme["primary"],
            hover_color=color_scheme["primary_hover"]
        )

        self.connection_status.configure( # type: ignore
            text="\u26AA Not connected",
            text_color=color_scheme["disabled"]
        )

        if username_widget:
            username_widget.configure(border_color=color_scheme["secondary"]) # type: ignore
        if password_widget:
            password_widget.configure(border_color=color_scheme["secondary"]) # type: ignore

    def _on_test_result(self, success: bool) -> None:
        self.connection_button.configure(state="normal") # type: ignore

        if success:
            self.connection_tested = True
            self._update_connection_ui(True)
            self._write_to_output("\u2713 Database connection successful!")

            self._start_session_timeout()
        else:
            self.connection_tested = False
            self._update_connection_ui(False)
            self._write_to_output("\u2717 Database connection failed!")

    def _on_test_error(self, error_msg: str) -> None:

        self.connection_button.configure(state="normal") # type: ignore
        self.connection_tested = False
        self._update_connection_ui(False)
        self._write_to_output(f"\u2717 Connection test error: {error_msg}")

    def _on_submit(self) -> None:
        self._write_to_output("=== Starting Email Generation ===")

        if not self.connection_tested:
            self._write_to_output("\u274C Please test and confirm the database connection first.")
            return
        
        self._start_session_timeout()

       
        with SecurePasswordContext(self.credential_manager, clear_on_exit=False) as (username, password):
            try:
                is_valid, error_msg = self.validate_db_credentials(username, password)
                if not is_valid:
                    self._write_to_output(f"\u274C Invalid credentials: {error_msg}")
                    return
                
                emplid_field = self._get_selected_emplid_field()
                if not emplid_field:
                    self._write_to_output("\u274C Please select the Employee ID field from the dropdown.")
                    return

                csv_file_path = self._get_selected_csv_path()
                email_template_path = self._get_selected_email_path()

                if not csv_file_path or self.csv_dropdown.get() in ["No files found", "No CSV files found"]: # type: ignore
                    self._write_to_output("\u274C Please select a valid CSV file")
                    return
                
                if not email_template_path or self.email_dropdown.get() in ["No templates found", "No email templates found"]: # type: ignore
                    self._write_to_output("\u274C Please select an email template")
                    return
                
                if not os.path.exists(csv_file_path):
                    self._write_to_output(f"\u274C CSV file not found: {csv_file_path}")
                    return
                
                if not os.path.exists(email_template_path):
                    self._write_to_output(f"\u274C Email template not found: {email_template_path}")
                    return

                self._write_to_output(f"\n\U0001F4C4 CSV File: {csv_file_path}")
                self._write_to_output(f"\n\U0001F4E7 Email Template: {email_template_path}\n")
                self._write_to_output(f"\n\U0001F194 Employee ID Field: {emplid_field}\n")

                transformers = self._get_selected_transformers()
                if transformers:
                    self._write_to_output(f"\n\U0001F4DD Applied Transformations:")
                    for field, transformer in transformers.items():
                        transform_name = transformer.__name__.replace("_", " ").title()
                        self._write_to_output(f"  - {field}: {transform_name}")
                    self._write_to_output("")

                employee_data = read_csv_file(
                    printer_function=self._write_to_output,
                    filename=csv_file_path,
                    custom_transformers=transformers
                )

                if not employee_data:
                    self._write_to_output("\u274C No valid employee data found in the CSV file.")
                    return
                
                max_emails = 1000
                if len(employee_data) > max_emails:
                    self._write_to_output(f"\u26A0 Warning: CSV contains {len(employee_data)} records. Processing only first {max_emails}")
                    employee_data = employee_data[:max_emails]

                if emplid_field not in employee_data[0]:
                    self._write_to_output(f"\u274C Employee ID field '{emplid_field}' not found in the CSV data.")
                    available_fields = list(employee_data[0].keys())
                    self._write_to_output(f"Available fields: {', '.join(available_fields)}")

                    self._write_to_output(f"Selected original field from dropdown: {self.emplid_field_var.get() if self.emplid_field_var else 'None'}")
                    self._write_to_output(f"Mapped to cleaned field: {emplid_field}")
                    self._write_to_output("Field mapping debug:")
                    if hasattr(self, 'emplid_field_mapping'):
                        for orig, cleaned in self.emplid_field_mapping.items():
                            self._write_to_output(f" '{orig}' -> '{cleaned}'")
                    return
                

                employee_data = query_db_for_busn_emails_from_emplid(
                    printer_function=self._write_to_output,
                    employees=employee_data, 
                    emplid_field=emplid_field,
                    username=username,
                    password=password
                )
            
            except Exception as e:
                self._write_to_output(f"\u274C Error during email generation: {e}")
                return

        if not employee_data:
            self._write_to_output("\u274C No valid employee data found after querying the database.")
            return
        
        bcc_mode = self.bcc_mode_var.get() if self.bcc_mode_var else False

        if bcc_mode:
            self._create_bcc_email(email_template_path, employee_data)
        else:
            self._create_individual_emails(email_template_path, employee_data)

    def _get_selected_csv_path(self) -> Optional[str]:

        selected_name = self.csv_dropdown.get() # type: ignore
        for file_dict in self.csv_files:
            if selected_name in file_dict:
                return file_dict[selected_name]
            
        return None

    def _get_selected_email_path(self) -> Optional[str]:

        selected_name = self.email_dropdown.get() # type: ignore
        for template_dict in self.email_templates:
            if selected_name in template_dict:
                return template_dict[selected_name]

        return None

    def _open_csv_file(self) -> None:

        try:
            selected_file = select_csv_file()
            if selected_file:
                # Check if this exact file path already exists in the dropdown
                file_already_exists = any(
                    selected_file in file_dict.values() for file_dict in self.csv_files
                )

                if file_already_exists:
                    for file_dict in self.csv_files:
                        if selected_file in file_dict.values():
                            existing_display_name = list(file_dict.keys())[0]
                            self.csv_dropdown.set(existing_display_name) # type: ignore
                            self._write_to_output(f"File already loaded: {existing_display_name}")
                            self._current_csv_path = selected_file
                            self._load_csv_fields(selected_file)
                            self.window.after(200, self._scroll_console_to_bottom)
                            return

                base_filename = os.path.basename(selected_file)
                # Create a display name for the dropdown
                display_name = self._create_unique_display_name(base_filename, selected_file, self.csv_files)

                current_values = list(self.csv_dropdown.cget("values")) # type: ignore
                current_values.append(display_name)
                self.csv_dropdown.configure(values=current_values) # type: ignore

                self.csv_files.append({display_name: selected_file})
                self.csv_dropdown.set(display_name) # type: ignore
                self._write_to_output(f"\nSelected CSV file: {display_name}")

                self._current_csv_path = selected_file
                self._load_csv_fields(selected_file)
                self.window.after(200, self._scroll_console_to_bottom)


        except Exception as e:
            self._write_to_output(f"Error selecting CSV file: {e}")

    def _open_email_file(self) -> None:

        try:
            selected_file = select_email_file()
            if selected_file:
                file_already_exists = any(
                    selected_file in file_dict.values() for file_dict in self.email_templates
                )

                if file_already_exists:
                    for template_dict in self.email_templates:
                        if selected_file in template_dict.values():
                            existing_display_name = list(template_dict.keys())[0]
                            self.email_dropdown.set(existing_display_name) # type: ignore
                            self._write_to_output(f"Template already loaded: {existing_display_name}")
                            self._current_email_path = selected_file
                            self._extract_template_placeholders(selected_file)
                            self.window.after(200, self._scroll_console_to_bottom)
                            return
                base_filename = os.path.basename(selected_file)
                # Create a display name for the dropdown
                display_name = self._create_unique_display_name(base_filename, selected_file, self.email_templates)

                # Create a unique filename for the dropdown
                current_values = list(self.email_dropdown.cget("values")) # type: ignore
                current_values.append(display_name)
                self.email_dropdown.configure(values=current_values) # type: ignore

                self.email_templates.append({display_name: selected_file})
                self.email_dropdown.set(display_name) # type: ignore
                self._write_to_output(f"Selected email template: {display_name}")

                self._current_email_path = selected_file
                self._extract_template_placeholders(selected_file)
                self.window.after(200, self._scroll_console_to_bottom)

        except Exception as e:
            self._write_to_output(f"Error selecting email template: {e}")

    def _create_unique_display_name(self, base_filename: str, file_path: str, existing_files: List[Dict[str, str]]) -> str:

        existing_display_names = [list(file_dict.keys())[0] for file_dict in existing_files]

        if base_filename not in existing_display_names:
            return base_filename
        
        parent_dir = os.path.basename(os.path.dirname(file_path))
        display_name_with_dir = f"{parent_dir} - {base_filename}"

        if display_name_with_dir in existing_display_names:
            path_parts = file_path.split(os.sep)

            if len(path_parts) >= 3:
                parent_dirs = os.sep.join(path_parts[-3:-1])
                display_name_with_dir = f"{base_filename} ({parent_dirs})"
            else:
                display_name_with_dir = f"{base_filename} ({file_path})"

        return display_name_with_dir

    def _create_transformer_functions(self) -> Dict[str, Callable[[str], str]]:

        def capitalize_name(value: str) -> str:
            if not value or not value.strip():
                return value
            
            if len(value) > 500:
                value = value[:500]
            
            value = re.sub(r'[^\w\s-]', '', value)
            return ' '.join(word.capitalize() for word in value.split())
        
        def currency_format(value: str) -> str:
            if not value or not value.strip():
                return "0.00"
            
            if len(value) > 50:
                value = value[:50]

            cleaned = re.sub(r'[^\d.-]', '', value.strip())

            try:
                number = float(cleaned) if cleaned else 0.0
                if number > 999999999.99:
                    number = 999999999.99
                elif number < -999999999.99:
                    number = -999999999.99
                return f"{number:.2f}"
            except ValueError:
                self._write_to_output(f"\u26A0 Warning: Could not convert '{value}' to a number. Returning '0.00'.")
                return "0.00"

        def currency_format_with_symbol(value: str) -> str:
            if not value or not value.strip():
                return "$0.00"

            if len(value) > 50:
                value = value[:50]

            cleaned = re.sub(r'[^\d.-]', '', value.strip())

            try:
                number = float(cleaned) if cleaned else 0.0
                if number > 999999999.99:
                    number = 999999999.99
                elif number < -999999999.99:
                    number = -999999999.99
                return f"${number:.2f}"
            except:
                self._write_to_output(f"\u26A0 Warning: Could not convert '{value}' to a number. Returning '$0.00'")
                return "$0.00"
            
        
        return {
            "capitalize": capitalize_name,
            "currency": currency_format,
            "currency_with_symbol": currency_format_with_symbol
        }

    def _get_selected_transformers(self) -> Dict[str, Callable[[str], str]]:
        transformers = {}
        available_transformers = self._create_transformer_functions()

        for field_name, widgets in self.field_widgets.items():
            transform_type = widgets["transform_var"].get()
            available_transformers = self._create_transformer_functions()

            if transform_type == "Capitalize":
                transformers[field_name] = available_transformers["capitalize"]
            elif transform_type == "Currency (with 2 decimals showing)":
                currency_prefix_var = widgets.get("currency_prefix_var")
                if currency_prefix_var and currency_prefix_var.get():
                    transformers[field_name] = available_transformers["currency_with_symbol"]
                else:
                    transformers[field_name] = available_transformers["currency"]

        return transformers

    def _get_selected_emplid_field(self) -> Optional[str]:
        if self.emplid_field_var:
            selected_original = self.emplid_field_var.get()
            if selected_original != "Select emplid field..." and hasattr(self, 'emplid_field_mapping'):
                return self.emplid_field_mapping.get(selected_original)
        return None

    def _load_csv_fields(self, csv_file_path: str) -> None:
        try:
            encoding = 'utf-8'

            with open(csv_file_path, 'rb') as file:
                raw_data = file.read(4)
                if raw_data.startswith(codecs.BOM_UTF8):
                    encoding = 'utf-8-sig'
                elif raw_data.startswith(codecs.BOM_UTF16):
                    encoding = 'utf-16'
            
            with open(csv_file_path, 'r', encoding=encoding, newline='') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader, [])

                if headers:
                    original_headers = []
                    cleaned_headers = []
                    
                    for header in headers:
                        original_header = header.strip('\ufeff\ufffe\x00').strip()
                        original_headers.append(original_header)

                        processed_header = normalize_field_for_matching(original_header)
                        cleaned_headers.append(processed_header)
                    
                    is_valid, error_msg = self.validate_csv_field_names(cleaned_headers)
                    if not is_valid:
                        self._write_to_output(f"\u274C Invalid CSV headers: {error_msg}")
                        return

                    plural_check = "s" if len(cleaned_headers) > 1 else ""
                    self._write_to_output(f"Found {len(cleaned_headers)} CSV field{plural_check}: {', '.join(cleaned_headers)}")

                    self._create_field_transform_section(original_headers, cleaned_headers)
                else:
                    self._write_to_output("\u26A0 No headers found in the CSV file.")
        except Exception as e:
            self._write_to_output(f"\u274C Error reading CSV fields: {e}")

    def _create_field_transform_section(self, original_csv_fields: List[str], cleaned_csv_fields: List[str]) -> None:
        if hasattr(self, '_updating_field_config') and self._updating_field_config:
            return
        
        self._updating_field_config = True
        is_initial_load = not hasattr(self, '_app_fully_initialized')

        if not hasattr(self, '_initial_ui_creation'):
            self._initial_ui_creation = True
        
        try:
            if self.field_transform_frame:
                self.field_transform_frame.destroy()
                self.field_widgets.clear()

            if not original_csv_fields or not cleaned_csv_fields:
                self._write_to_output("No CSV fields to configure")
                return

            self.current_original_fields = original_csv_fields
            self.current_csv_fields = cleaned_csv_fields

            should_print_debug = (
                not hasattr(self, '_debug_info_printed') or
                not self._debug_info_printed or
                not is_initial_load
            )

            if should_print_debug:
                max_orig_length  = max(len(f"'{orig}'") for orig in original_csv_fields)
                max_clean_length = max(len(f"'{cleaned}'") for cleaned in cleaned_csv_fields)

                self._write_to_output("Field normalization debug:")
                for orig, cleaned in zip(original_csv_fields, cleaned_csv_fields):
                    orig_padded = f"'{orig}'".ljust(max_orig_length)
                    clean_padded = f"'{cleaned}'".ljust(max_clean_length)
                    
                    self._write_to_output(f" {orig_padded} -> {clean_padded} (used in CSV data & matching)")

                if is_initial_load:
                    self._debug_info_printed = True

            self.field_transform_frame = ctk.CTkFrame(
                self.window,
                fg_color=color_scheme["surface"],
                corner_radius=12,
                border_width=1,
                border_color=color_scheme["secondary"]
            )
            self.field_transform_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")
            self.field_transform_frame.grid_columnconfigure(0, weight=1)

            header_frame = ctk.CTkFrame(self.field_transform_frame, fg_color="transparent")
            header_frame.grid(row=0, column=0, padx=(10, 10), pady=(10, 5), sticky="ew")
            header_frame.grid_columnconfigure(0, weight=0)
            header_frame.grid_columnconfigure(1, weight=1)
            header_frame.grid_columnconfigure(2, weight=0)

            title_text = "\U0001F6E0 Field Configuration"
            if not hasattr(self, 'outlook_placeholders') or not self.outlook_placeholders:
                title_text += " (No Email Placeholders - Direct Field Mapping)"

            title_label = ctk.CTkLabel(
                header_frame,
                text=title_text,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=color_scheme["text"]
            )
            title_label.grid(row=0, column=0, padx=(5, 0), sticky="w")

            spacer_frame = ctk.CTkFrame(header_frame, fg_color="transparent", height=1)
            spacer_frame.grid(row=0, column=1, sticky="ew")

            reset_button = ctk.CTkButton(
                header_frame,
                text="Reset to Defaults",
                command=self._reset_field_configuration,
                width=130,
                height=28,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=color_scheme["secondary"],
                hover_color=color_scheme["primary_hover"],
                text_color=color_scheme["text"],
                corner_radius=8
            )
            reset_button.grid(row=0, column=2, padx=(10, 10), pady=(5, 5))

            self._create_field_config_content()
        except Exception as e:
            self._write_to_output(f"\u274C Error creating field transform section: {e}")
        finally:
            self._updating_field_config = False

            if hasattr(self, '_initial_ui_creation'):
                self._initial_ui_creation = False

    def _update_transform_example(self, field_name: str, selected_transform: str) -> None:
        if field_name not in self.field_widgets:
            return

        widgets = self.field_widgets[field_name]
        example_label = widgets.get("example_label")
        currency_checkbox = widgets.get("currency_checkbox")

        if selected_transform == "Currency (with 2 decimals showing)":
            currency_checkbox.grid()
            self._update_currency_example(field_name)
        else:
            currency_checkbox.grid_remove()

            examples = {
                "Capitalize": "Examples:     'john doe' -> 'John Doe',     'walter' -> 'Walter',     'WALTER' -> 'Walter'",
                "Currency (with 2 decimals showing)": "Examples:     '$3,218' -> '3218.00',     '500' -> '500.00'",
                "Do nothing": ""
            }

            example_text = examples.get(selected_transform, "")
            example_label.configure(
                text=example_text,
                text_color=color_scheme["disabled"]
            )

    def _update_currency_example(self, field_name: str) -> None:
        if field_name not in self.field_widgets:
            return

        widgets = self.field_widgets[field_name]
        example_label = widgets.get("example_label")
        currency_prefix_var = widgets.get("currency_prefix_var")

        if currency_prefix_var.get():
            example_text = "Examples:   '$3,218' -> '$3218.00',   '500' -> '$500.00'"
        else:
            example_text = "Examples:   '$3,218' -> '3218.00',   '500' -> '500.00'"

        example_label.configure(text=example_text, text_color=color_scheme["disabled"])
        
    def _on_emplid_field_change(self, selected_original_field: str) -> None:
        highlight_color = "#E9DC92"
        normal_border = color_scheme["secondary"]

        # Reset all field highlights
        if hasattr(self, '_emplid_dropdown_ref') and self._emplid_dropdown_ref is not None:
            if selected_original_field == "Select emplid field...":
                self._emplid_dropdown_ref.configure(border_color=normal_border, border_width=1)
            else:
                self._emplid_dropdown_ref.configure(border_color=highlight_color, border_width=2)

        if hasattr(self, '_emplid_label_frame_ref') and self._emplid_label_frame_ref is not None:
            if selected_original_field == "Select emplid field...":
                self._emplid_label_frame_ref.configure(border_color=normal_border, border_width=0)
            else:
                self._emplid_label_frame_ref.configure(border_color=highlight_color, border_width=2)

        selected_cleaned_field = None
        if selected_original_field != "Select emplid field..." and  hasattr(self, 'emplid_field_mapping'):
            selected_cleaned_field = self.emplid_field_mapping.get(selected_original_field)

        for field_name, widgets in self.field_widgets.items():
            if field_name == selected_cleaned_field:
                widgets["dropdown"].configure(state="disabled")
                widgets["transform_var"].set("Do nothing")
                widgets["label_frame"].configure(border_color=highlight_color, border_width=2)
                widgets["example_label"].configure(
                    text="(Employee ID field - no transformation applied)",
                    text_color=color_scheme["accent"]
                )
            else:
                widgets["dropdown"].configure(state="readonly")  # type: ignore
                widgets["label_frame"].configure(border_color=normal_border, border_width=0)  # type: ignore
                current_transform = widgets["transform_var"].get()
                self._update_transform_example(field_name, current_transform)

        if hasattr(self, '_unused_field_refs') and self._unused_field_refs:
            for field_name, refs in self._unused_field_refs.items():
                if field_name == selected_cleaned_field:
                    frame_vals = refs['frame_grid_values']
                    refs['frame'].grid_forget()
                    refs['frame'].grid(row=frame_vals['row'], column=frame_vals['column'], padx=frame_vals['padx'], pady=frame_vals['pady'], sticky="w")

                    refs['frame'].configure(border_color=highlight_color, border_width=2)
                    refs['label'].configure(
                        text=refs['original_name'],
                        font=ctk.CTkFont(size=11, slant="roman"),
                        text_color=color_scheme["text"]
                    )
                else:
                    frame_vals = refs['frame_grid_values']
                    refs['frame'].grid_forget()
                    refs['frame'].grid(row=frame_vals['row'], column=frame_vals['column'], padx=frame_vals['padx'], pady=frame_vals['pady'], sticky="e")
                    refs['frame'].configure(border_color=normal_border, border_width=0)
                    refs['label'].configure(
                        text=f"{refs['original_name']} (unused)",
                        font=ctk.CTkFont(size=11, slant="italic"),
                        text_color=color_scheme["disabled"]
                    )
        
    def _get_default_emplid_field(self) -> Optional[str]:
        if not hasattr(self, 'current_original_fields') or not hasattr(self, 'current_csv_fields'):
            return None

        emplid_patterns = ['emplid', 'employee id', 'employeeid', 'emp id', 'empid', 'employee number', 'emp number']
        is_initial_load = not hasattr(self, '_app_fully_initialized')

        normalized_patterns = [normalize_field_for_matching(pattern) for pattern in emplid_patterns]

        for orig, cleaned in zip(self.current_original_fields, self.current_csv_fields):
            normalized_field = normalize_field_for_matching(cleaned)
            
            if any(pattern == normalized_field for pattern in normalized_patterns):

                should_print_message = (
                    not hasattr(self, '_auto_select_message_printed') or
                    not self._auto_select_message_printed or
                    not is_initial_load
                )
                
                if should_print_message:
                    self._write_to_output(f"Auto-selected Employee ID field: '{orig}' (maps to '{cleaned}', normalized: '{normalized_field}')")
                    if is_initial_load:
                        self._auto_select_message_printed = True
                return orig
            
        if self.current_original_fields:

            should_print_message = (
                not hasattr(self, '_auto_select_message_printed') or
                not self._auto_select_message_printed or
                not is_initial_load
            )
            
            if should_print_message:
                self._write_to_output(f"No Employee ID field auto-detected. Please manually select from dropdown.")
                if is_initial_load:
                    self._auto_select_message_printed = True
            return None

        return None

    def _create_field_config_content(self) -> None:
        scrollable_frame = ctk.CTkScrollableFrame(
            self.field_transform_frame,
            height=420,
            fg_color=color_scheme["background"],
        )
        scrollable_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        scrollable_frame.grid_columnconfigure(0, weight=0, minsize=180)
        scrollable_frame.grid_columnconfigure(1, weight=0, minsize=160)
        scrollable_frame.grid_columnconfigure(2, weight=0, minsize=210)
        scrollable_frame.grid_columnconfigure(3, weight=1, minsize=300)

        scrollable_frame.grid_rowconfigure(0, weight=0)
        scrollable_frame.grid_rowconfigure(1, weight=0)
        scrollable_frame.grid_rowconfigure(2, weight=0)
        scrollable_frame.grid_rowconfigure(3, weight=0)
        
        self._scrollable_frame_ref = scrollable_frame

        def _on_mouse_wheel(event):
            scrollable_frame._parent_canvas.yview_scroll(int(-1 * (event.delta / 12)), "units")

        scrollable_frame.bind("<MouseWheel>", _on_mouse_wheel)

        def bind_to_canvas():
            try:
                canvas = scrollable_frame._parent_canvas
                canvas.bind("<MouseWheel>", _on_mouse_wheel)
            except AttributeError:
                scrollable_frame.after(100, bind_to_canvas)

        scrollable_frame.after(100, bind_to_canvas)
        scrollable_frame.focus_set()

        current_row = 0

        # Employee ID Field Section
        emplid_label_frame = ctk.CTkFrame(
            scrollable_frame,
            fg_color="transparent",
            corner_radius=6,
            border_width=0,
            border_color=color_scheme["secondary"]
        )
        emplid_label_frame.grid(row=current_row, column=0, padx=(10, 5), pady=(5,1), sticky="w")

        emplid_label = ctk.CTkLabel(
            emplid_label_frame,
            text="\U0001F194 Employee ID Field:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=color_scheme["text"]
        )
        emplid_label.grid(row=0, column=0, padx=5, pady=2)

        self._emplid_label_frame_ref = emplid_label_frame

        field_mapping = {}
        emplid_dropdown_values = ["Select emplid field..."]

        if hasattr(self, 'current_original_fields') and hasattr(self, 'current_csv_fields'):
            for orig, cleaned in zip(self.current_original_fields, self.current_csv_fields):
                field_mapping[orig] = cleaned
                emplid_dropdown_values.append(orig)

        self.emplid_field_mapping = field_mapping
        self.emplid_field_var = ctk.StringVar(value="Select emplid field...")
        emplid_dropdown = ctk.CTkComboBox(
            scrollable_frame,
            variable=self.emplid_field_var,
            values=emplid_dropdown_values,
            state="readonly",
            font=ctk.CTkFont(size=11),
            fg_color=color_scheme["background"],
            text_color=color_scheme["text"],
            border_color=color_scheme["secondary"],
            button_color=color_scheme["accent"],
            button_hover_color=color_scheme["secondary"],
            command=self._on_emplid_field_change
        )
        emplid_dropdown.grid(row=current_row, column=1, columnspan=3, padx=(5, 10), pady=(5, 2), sticky="w")
        self._emplid_dropdown_ref = emplid_dropdown

        current_row += 1

        separator = ctk.CTkLabel(
            scrollable_frame,
            text="Field Transformations",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=color_scheme["text"]
        )
        separator.grid(row=current_row, column=0, columnspan=4, padx=(10, 10), pady=(5, 2), sticky="ew")

        current_row += 1

        headers = [
            ("Outlook Fields", 0),
            ("CSV Fields", 1),
            ("Formatting Options", 2),
            ("Examples", 3)
        ]

        for header_text, col in headers:
            header_label = ctk.CTkLabel(
                scrollable_frame,
                text=header_text,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=color_scheme["text"]
            )
            header_label.grid(row=current_row, column=col, padx=((123 if header_text == "Examples" else 10), 5), pady=(2, 2), sticky="w" if header_text == "Examples" else "")
        
        current_row += 1

        transform_options = ["Do nothing", "Capitalize", "Currency (with 2 decimals showing)"]

        # Get selected employee ID field
        selected_emplid_original = self.emplid_field_var.get() if self.emplid_field_var else None

        selected_emplid_cleaned = None
        if selected_emplid_original and selected_emplid_original != "Select emplid field..." and hasattr(self, 'emplid_field_mapping'):
            selected_emplid_cleaned = self.emplid_field_mapping.get(selected_emplid_original)

        # Display unmatched Outlook fields first
        if hasattr(self, 'unmatched_placeholders') and self.unmatched_placeholders:
            placeholder_plural_check = "s" if len(self.unmatched_placeholders) > 1 else ""
            self._write_to_output(f"Unmatched {len(self.unmatched_placeholders)} email placeholder{placeholder_plural_check}: {self.unmatched_placeholders}")
            for placeholder in self.unmatched_placeholders:
                outlook_frame = ctk.CTkFrame(
                    scrollable_frame,
                    fg_color=color_scheme["warning_bg"],
                    corner_radius=6,
                    border_width=2,
                    border_color=color_scheme["warning"]
                )
                outlook_frame.grid(row=current_row, column=0, padx=(10, 5), pady=2, sticky="ew")

                outlook_label = ctk.CTkLabel(
                    outlook_frame,
                    text=f"\u26A0 {{{{{placeholder}}}}}",
                    font=ctk.CTkFont(size=11),
                    text_color=color_scheme["warning_text"]
                )
                outlook_label.grid(row=0, column=0, padx=8, pady=4)

                unmatched_label = ctk.CTkLabel(
                    scrollable_frame,
                    text="(No match found)",
                    font=ctk.CTkFont(size=11, slant="italic"),
                    text_color=color_scheme["warning"]
                )
                unmatched_label.grid(row=current_row, column=1, padx=(5, 5), pady=2, sticky="ew")

                current_row += 1

        displayed_csv_fields = set()

        # Display matched fields
        if hasattr(self, 'placeholder_mapping') and self.placeholder_mapping:
            for placeholder, csv_field in self.placeholder_mapping.items():
                if csv_field is not None:
                    displayed_csv_fields.add(csv_field)
                    
                    original_field_name = None
                    if hasattr(self, 'current_original_fields') and hasattr(self, 'current_csv_fields'):
                        for orig, cleaned in zip(self.current_original_fields, self.current_csv_fields):
                            if cleaned == csv_field:
                                original_field_name = orig
                                break
                    
                    if not original_field_name:
                        continue

                    is_emplid_field = (csv_field == selected_emplid_cleaned)

                    outlook_label = ctk.CTkLabel(
                        scrollable_frame,
                        text=f"{{{{{placeholder}}}}}",
                        font=ctk.CTkFont(size=11),
                        text_color=color_scheme["success"]
                    )
                    outlook_label.grid(row=current_row, column=0, padx=(10,5), pady=2, sticky="e")

                    csv_frame = ctk.CTkFrame(
                        scrollable_frame,
                        fg_color="transparent",
                        corner_radius=6,
                        border_width=2 if is_emplid_field else 0,
                        border_color= "#E9DC92" if is_emplid_field else color_scheme["secondary"]
                    )
                    csv_frame.grid(row=current_row, column=1, padx=(5, 5), pady=2, sticky="ew")

                    csv_label = ctk.CTkLabel(
                        csv_frame,
                        text=original_field_name,
                        font=ctk.CTkFont(size=11),
                        text_color=color_scheme["text"]
                    )
                    csv_label.grid(row=0, column=0, padx=5, pady=2)

                    transform_var = ctk.StringVar(value="Do nothing")

                    transform_dropdown = ctk.CTkComboBox(
                        scrollable_frame,
                        variable=transform_var,
                        values=transform_options,
                        state="disabled" if is_emplid_field else "readonly",
                        font=ctk.CTkFont(size=10),
                        width=200,
                        height=28,
                        fg_color=color_scheme["background"],
                        text_color=color_scheme["text"],
                        border_color=color_scheme["secondary"],
                        border_width=1,
                        button_color=color_scheme["primary"],
                        button_hover_color=color_scheme["primary_hover"],
                        command=lambda value, field=csv_field: self._update_transform_example(field, value)
                    )
                    transform_dropdown.grid(row=current_row, column=2, padx=(5, 5), pady=2, sticky="w")

                    example_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
                    example_container.grid(row=current_row, column=3, padx=(5, 10), pady=2, sticky="w")
                    example_container.grid_columnconfigure(0,weight=0, minsize=120)
                    example_container.grid_columnconfigure(1, weight=1)

                    currency_prefix_var = tk.BooleanVar(value=False)
                    currency_checkbox = ctk.CTkCheckBox(
                        example_container,
                        text="Include $ symbol",
                        variable=currency_prefix_var,
                        font=ctk.CTkFont(size=10),
                        text_color=color_scheme["text"],
                        fg_color=color_scheme["primary"],
                        hover_color=color_scheme["primary_hover"],
                        border_color=color_scheme["secondary"],
                        command=lambda field=csv_field: self._update_currency_example(field)
                    )
                    currency_checkbox.grid(row=0, column=0, padx=(0,10), sticky="w")
                    currency_checkbox.grid_remove()
                    
                    example_label = ctk.CTkLabel(
                        example_container,
                        text="(Employee ID field - no transformation applied)" if is_emplid_field else "",
                        font=ctk.CTkFont(size=10),
                        text_color=color_scheme["accent"] if is_emplid_field else color_scheme["disabled"],
                        wraplength=350,
                        anchor="w",
                        justify="left"
                    )
                    example_label.grid(row=0, column=1, sticky="w")

                    self.field_widgets[csv_field] = {
                        "label": csv_label,
                        "label_frame": csv_frame,
                        "dropdown": transform_dropdown,
                        "transform_var": transform_var,
                        "example_label": example_label,
                        "example_container": example_container,
                        "currency_checkbox": currency_checkbox,
                        "currency_prefix_var": currency_prefix_var,
                        "original_name": original_field_name
                    }

                    current_row += 1

        # Always display the selected employee ID field if it's not already displayed
        if selected_emplid_cleaned and selected_emplid_cleaned not in displayed_csv_fields:
            matching_placeholder = None
            if hasattr(self, 'placeholder_mapping') and self.placeholder_mapping:
                for placeholder, csv_field in self.placeholder_mapping.items() if hasattr(self, 'placeholder_mapping') else []:
                    if csv_field == selected_emplid_cleaned:
                        matching_placeholder = placeholder
                        break

            original_field_name = None
            if hasattr(self, 'current_original_fields') and hasattr(self, 'current_csv_fields'):
                for orig, cleaned in zip(self.current_original_fields, self.current_csv_fields):
                    if cleaned == selected_emplid_cleaned:
                        original_field_name = orig
                        break

            if original_field_name:
                outlook_text = f"{{{{{matching_placeholder}}}}}" if matching_placeholder else "(Employee ID field)"
                outlook_label = ctk.CTkLabel(
                    scrollable_frame,
                    text=outlook_text,
                    font=ctk.CTkFont(size=11, slant="italic" if not matching_placeholder else "roman"),
                    text_color=color_scheme["success"] if matching_placeholder else color_scheme["accent"]
                )
                outlook_label.grid(row=current_row, column=0, padx=(10, 5), pady=2, sticky="w")

                csv_frame = ctk.CTkFrame(
                    scrollable_frame,
                    fg_color="transparent",
                    corner_radius=6,
                    border_width=2,
                    border_color="#E9DC92"
                )
                csv_frame.grid(row=current_row, column=1, padx=(5, 5), pady=2, sticky="ew")

                csv_label = ctk.CTkLabel(
                    csv_frame,
                    text=original_field_name,
                    font=ctk.CTkFont(size=11),
                    text_color=color_scheme["text"]
                )
                csv_label.grid(row=0, column=0, padx=5, pady=1)

                
                transform_var = ctk.StringVar(value="Do nothing")
                transform_dropdown = ctk.CTkComboBox(
                    scrollable_frame,
                    variable=transform_var,
                    values=transform_options,
                    state="disabled",
                    font=ctk.CTkFont(size=10),
                    width=200,
                    height=28,
                    fg_color=color_scheme["background"],
                    text_color=color_scheme["text"],
                    border_color="#E9DC92",
                    border_width=2,
                    button_color=color_scheme["primary"],
                    button_hover_color=color_scheme["primary_hover"]
                )
                transform_dropdown.grid(row=current_row, column=2, padx=5, pady=2, sticky="w")

                example_label = ctk.CTkLabel(
                    scrollable_frame,
                    text="(Employee ID field - no transformation applied)",
                    font=ctk.CTkFont(size=10),
                    text_color=color_scheme["accent"],
                    wraplength=400
                )
                example_label.grid(row=current_row, column=3, padx=(10, 20), pady=2, sticky="w")
                
                displayed_csv_fields.add(selected_emplid_cleaned)
                current_row += 1

        self._unused_field_refs = {}

        # Display unmatched CSV fields at the bottom
        if hasattr(self, 'current_original_fields') and hasattr(self, 'current_csv_fields'):            
            for orig, cleaned in zip(self.current_original_fields, self.current_csv_fields):
                if cleaned not in displayed_csv_fields:
                    is_emplid_field = (cleaned == selected_emplid_cleaned)

                    empty_label = ctk.CTkLabel(
                        scrollable_frame,
                        text="",
                        font=ctk.CTkFont(size=11),
                        text_color=color_scheme["disabled"]
                    )
                    empty_label.grid(row=current_row, column=0, padx=(10, 5), pady=2)


                    csv_frame = ctk.CTkFrame(
                        scrollable_frame,
                        fg_color="transparent",
                        corner_radius=6,
                        border_width=2 if is_emplid_field else 0,
                        border_color= "#E9DC92" if is_emplid_field else color_scheme["secondary"]
                    )
                    csv_frame.grid(row=current_row, column=1, padx=(5,5), pady=2, sticky="e")

                    csv_text   = orig                   if is_emplid_field else f"{orig} (unused)"
                    font_slant = "roman"                if is_emplid_field else "italic"
                    text_color = color_scheme["text"]   if is_emplid_field else color_scheme["disabled"]

                    csv_label = ctk.CTkLabel(
                        csv_frame,
                        text=csv_text,
                        font=ctk.CTkFont(size=11, slant=font_slant),
                        text_color=text_color
                    )
                    csv_label.grid(row=0, column=0, padx=5, pady=2)

                    self._unused_field_refs[cleaned] = {
                        'frame': csv_frame,
                        'frame_grid_values': {"row": current_row, "column": 1, "padx":(5,5), "pady": 2},
                        'label': csv_label,
                        'original_name': orig
                    }

                    current_row += 1

        default_field = self._get_default_emplid_field()
        if default_field:
            self.emplid_field_var.set(default_field)
            self._on_emplid_field_change(default_field)

        self._create_bcc_mode_section()

    def _reset_field_configuration(self) -> None:
        try:
            default_emplid_field = self._get_default_emplid_field()
            current_emplid_field = self.emplid_field_var.get() if self.emplid_field_var else None
            emplid_reset_made = False

            if default_emplid_field and self.emplid_field_var:
                if current_emplid_field != default_emplid_field:
                    self.emplid_field_var.set(default_emplid_field)
                    self._write_to_output(f"\U0001F504 Reset Employee ID field to: {default_emplid_field}")
                    emplid_reset_made = True
            else:
                if self.emplid_field_var and current_emplid_field != "Select emplid field...":
                    self.emplid_field_var.set("Select emplid field...")
                    self._write_to_output(f"\U0001F504 Reset Employee ID field to selection prompt (no default field found)")
                    emplid_reset_made = True
            
            reset_count = 0
            currency_reset_count = 0

            for field_name, widgets in self.field_widgets.items():
                transform_var = widgets.get("transform_var")
                currency_prefix_var = widgets.get("currency_prefix_var")

                if transform_var and "Do nothing" != transform_var.get():
                    transform_var.set("Do nothing")
                    reset_count += 1
                
                if currency_prefix_var and currency_prefix_var.get():
                    currency_prefix_var.set(False)
                    currency_reset_count += 1
                
                self._update_transform_example(field_name, "Do nothing")

            if default_emplid_field and self.emplid_field_var:
                self._on_emplid_field_change(default_emplid_field)
            elif self.emplid_field_var:
                self._on_emplid_field_change("Select emplid field...")
            
            if reset_count > 0:
                plural_transformations = "s" if reset_count != 1 else ""
                self._write_to_output(f"\U0001F504 Reset {reset_count} field transformation{plural_transformations} to 'Do nothing'")

            if currency_reset_count >0:
                plural_currency = "s" if currency_reset_count != 1 else ""
                self._write_to_output(f"\U0001F504 Unchecked {currency_reset_count} currency checkbox{plural_currency}")

            no_changes_msg = ": No changes were made. All fields are already default values." if not (emplid_reset_made or reset_count > 0 or currency_reset_count > 0) else ""
            self._write_to_output(f"\u2705 Field configuration reset completed{no_changes_msg}\n")
        
        except Exception as e:
            self._write_to_output(f"\u274C Error resetting field configuration: {e}")

    def _create_bcc_mode_section(self) -> None:
        bcc_frame = ctk.CTkFrame(
            self.field_transform_frame,
            fg_color="transparent"
        )
        bcc_frame.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")

        self.bcc_mode_var = tk.BooleanVar(value=False)
        self.bcc_checkbox = ctk.CTkCheckBox(
            bcc_frame,
            text="\U0001F4E7 BCC Mode: Create a single email with all recipients in BCC. Note: Only the first record in the CSV file will be used for any placeholder fields in the outlook file.",
            variable=self.bcc_mode_var,
            font=ctk.CTkFont(size=12),
            text_color=color_scheme["text"],
            fg_color=color_scheme["primary"],
            hover_color=color_scheme["primary_hover"],
            border_color=color_scheme["secondary"]
        )
        self.bcc_checkbox.grid(row=0, column=0, sticky="w")

    def _create_individual_emails(self, email_template_path: str, employee_data: List[Dict[str, str]]) -> None:
        email_count = len(employee_data)
        plural_check = "s" if email_count > 1 else ""

        self._write_to_output(f"\n\U0001F4E7 Generating {email_count} individual email{plural_check}:\n")

        emplid_field = self._get_selected_emplid_field()
        if not emplid_field:
            emplid_field = 'emplid'

        field_display_name = emplid_field.replace("_", " ").title()

        successful_emails = 0
        failed_emails=0
        emails_with_unreplaced_vars = 0
        
        for index, employee in enumerate(employee_data):
            emplid = employee.get(emplid_field, 'Unknown')
            email_address = employee.get('email', '').strip()

            if not email_address or '@' not in email_address:
                failed_emails += 1
                self._write_to_output(f"{str(index+1).rjust(3)}. {field_display_name}: {emplid}   \u26A0 WARNING: No business email found - skipping email creation")
            else:
                try:
                    old_stdout = sys.stdout
                    captured_output = StringIO()
                    sys.stdout = captured_output
                    
                    subject = create_draft_email_individual_to(self._write_to_output, email_template_path, employee)

                    sys.stdout = old_stdout
                    warning_output = captured_output.getvalue()
                    
                    if subject:
                        successful_emails += 1
                        output_line = f"{str(index+1).rjust(3)}. {field_display_name}: {emplid}   Subject: {subject}"

                        if "Unreplaced variables" in warning_output and "WARNING" in warning_output:
                            emails_with_unreplaced_vars += 1

                            warning_lines = [line.strip() for line in warning_output.split('\n') if line.strip() and 'WARNING' in line]
                            if warning_lines:
                                clean_warning = warning_lines[0].replace('⚠ WARNING: ', '').replace('\u26A0 WARNING: ', '')
                                output_line += f"   \u26A0 {clean_warning}" # type: ignore

                        self._write_to_output(output_line)
                    else:
                        failed_emails += 1
                        self._write_to_output(f"{str(index+1).rjust(3)}. {field_display_name}: {emplid}   \u274C ERROR: Failed to create email")
                except Exception as e:
                    failed_emails += 1
                    self._write_to_output(f"{str(index+1).rjust(3)}. {field_display_name}: {emplid}   \u274C ERROR: Email creation failed - {str(e)}")

        self._write_to_output(f"\n\U0001F4CA Summary:")
        self._write_to_output(f"  \u2705 Successfully created: {successful_emails} email{'s' if successful_emails != 1 else ''}")
        if failed_emails > 0:
            self._write_to_output(f"  \u26A0 Failed/Skipped: {failed_emails} email{('s' if failed_emails != 1 else '')}")
        if emails_with_unreplaced_vars > 0:
            self._write_to_output(f"   \U0001F4DD Emails with unreplaced variables: {emails_with_unreplaced_vars}")
        self._write_to_output("")

    def _create_bcc_email(self, email_template_path: str, employee_data: List[Dict[str, str]]) -> None:
        email_addresses = [employee.get('email', 'Unknown') for employee in employee_data if employee.get('email') and employee['email'].strip() and '@' in employee['email']]

        if not email_addresses:
            self._write_to_output("\u274C No valid email addresses found in the employee data.")
            return
        
        self._write_to_output(f"\n\U0001F4E7 Creating BCC email with {len(email_addresses)} recipients:\n")

        template_data = employee_data[0].copy()  # Use the first employee's data for the template

        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        subject = create_draft_email_bcc_all(self._write_to_output, email_template_path, template_data, email_addresses)

        sys.stdout = old_stdout
        warning_output = captured_output.getvalue()

        if subject:
            output_line = f"\u2705 BCC Email Created - Subject: {subject}"

            if "Unreplaced variables" in warning_output and "WARNING" in warning_output:
                warning_lines = [line.strip() for line in warning_output.split('\n') if line.strip() and 'WARNING' in line]
                if warning_lines:
                    clean_warning = warning_lines[0].replace('⚠ WARNING: ', '').replace('\u26A0 WARNING: ', '')
                output_line += f"\n\u26A0 {clean_warning}" # type: ignore

            self._write_to_output(output_line)
            plural_check = "s" if len(email_addresses) > 1 else ""
            self._write_to_output(f" {len(email_addresses)} Recipient{plural_check}: {', '.join(email_addresses)}")
        else:
            self._write_to_output("\u274C Failed to create BCC email. Please check the template and employee data.")

    def show(self) -> None:
        self._write_to_output("Application started\n")
        self.window.mainloop()

    def close(self) -> None:

        if self._session_timer:
            self.window.after_cancel(self._session_timer)
            self._session_timer = None

        self.credential_manager.clear_all()

        sys.stdout = self.original_stdout
        self.window.destroy()
        
def main():
    
    try:
        app: MainApplicationWindow = MainApplicationWindow()
        app.show()
    except KeyboardInterrupt:
        print("Application interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
    finally:
        try:
            app.close() # type: ignore
        except:
            pass

if __name__ == "__main__":
    main()