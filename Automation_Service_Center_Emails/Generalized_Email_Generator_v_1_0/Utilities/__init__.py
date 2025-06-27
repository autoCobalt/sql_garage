# install_required_libraries(modules: Set[str]) -> None: installs any necessary libraries
# is_package_installed(package_identifier: str) -> bool: checks if a specific package is installed
from .package_checker import install_required_libraries, is_package_installed

# get_confidential_csv_file() -> List[Dict[str, str]]: retrieves a list of all csv files in a specified directory key=filename value=full_path
# get_confidential_email_templates() -> List[Dict[str, str]]: retrieves email templates from a specified directory key=filename value=full_path
# read_csv_file(filename: Optional[str]) -> List[Dict[str, str]]: reads a CSV file and returns its content in a listed key-value format
# select_csv_file() -> str: allows the user to select a CSV file from a dialog
# select_email_file() -> str: allows the user to select an email template file from a dialog
from .file_loader import get_confidential_csv_files, get_confidential_email_templates, read_csv_file, select_csv_file, select_email_file, normalize_field_for_matching

# env_values: Final[Dict[str, str]] is a dictionary containing environment variables
# color_scheme: Final[Dict[str, str]] is a dictionary containing color codes from the tech_future scheme for the application
from .constants import env_values, color_scheme

from .color_constants import create_hover_color, ModernColors, ColorPalettes

# query_db_for_busn_emails_from_emplid(employees: List[Dict[str, str]]) -> List[Dict[str, str]] retrieves business emails from the key 'emplid' in a list of dictionaries
# query_db(sql_query: str, username: Optional[str] = None, password: Optional[str] = None): queries the database and returns all results as a list of dictionaries
# test_connection(username: Optional[str] = None, password: Optional[str] = None) -> bool: tests the database connection with optional credentials
from .db_utilities import query_db_for_busn_emails_from_emplid, query_db, test_connection

# create_draft_email_individual_to(template_msg_path: str, replacements: Dict[str, str]) -> bool: creates a draft email in Outlook to an individual recipient and returns True if successful
from .outlook_utilities import create_draft_email_individual_to, create_draft_email_bcc_all, get_template_placeholders

# SecurecredentialManager - class to manage credentials more securely
from .secure_credentials import SecureCredentialManager, SecurePasswordContext