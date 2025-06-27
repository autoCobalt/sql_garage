import csv
import os
import codecs
import re
from pathlib import Path
from typing import List, Dict, Final, Optional, Callable
import tkinter as tk
from tkinter import filedialog

#-- CONSTANTS ------------------------------------------------------------------------------------------------------
base_confidential_data_folder:  Final[str] = "Confidential_Data"
base_email_folder:              Final[str] = "Confidential_Data/Email_Templates"
main_path:                      Final[str] = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)),"../"))
confidential_data_path:         Final[str] = os.path.normpath(os.path.join(main_path,base_confidential_data_folder))
confidential_email_path:        Final[str] = os.path.normpath(os.path.join(main_path,base_email_folder))
#-------------------------------------------------------------------------------------------------------------------

# Validates file path by verifying that it is safe to open.
def validate_file_path(file_path: str, allowed_extensions: set[str], max_file_size_mb: int = 50) -> tuple[bool, str]:
    try:
        path = Path(file_path)

        # Check if file exists
        if not path.exists():
            return False, "File does not exist"
        
        # Check if it's actually a file
        if not path.is_file():
            return False, "Path is not a file"
        
        # Validate extension
        if path.suffix.lower() not in allowed_extensions:
            return False, f"Invalid file extension. Allowed: {allowed_extensions}"
        
        # Check file size to prevent resource exhaustion
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > max_file_size_mb:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {max_file_size_mb}MB)"
        
        # Ensure file is within expected directories
        try:
            # Resolve to absolute path and check if it's within base paths
            resolved_path = path.resolve()
            base_path = Path(main_path).resolve()
            resolved_path.relative_to(base_path)
        except ValueError:
            # If we can't make it relative to base_path, it may be from open file dialog. This is ok.
            pass

        return True, ""
    except Exception as e:
        return False, f"Validation error: {str(e)}"

# Normalizes field names and removes any dangerous characters
def normalize_field_for_matching(field_name: str) -> str:
    if not field_name or not isinstance(field_name, str):
        return ""

    normalized = re.sub(r'[^\w\s-]', '', str(field_name))

    normalized = normalized.lower()

    normalized = re.sub(r'[\s-]+', '_', normalized)

    normalized = re.sub(r'_+', '_', normalized).strip('_')

    return normalized

# Returns selected CSV file's normalized path.
def select_csv_file() -> Optional[str]:
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    try:
        
        filename: str = filedialog.askopenfilename(
            title       = "Select CSV File",
            filetypes   = [("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir  = confidential_data_path,
            multiple    = False # type: ignore
        )
    
        if not filename or not filename.strip():
            return None

        normalized_path: str = os.path.normpath(filename)

        if not os.path.exists(normalized_path):
            print(f"Error: Selected file does not exist: {normalized_path}")
            quit()
        if not normalized_path.lower().endswith('.csv'):
            print(f"Warning: Selected file is not a CSV file: {normalized_path}")
            quit()

        return normalized_path

    except Exception as e:
        print(f"Error selecting file: {e}")
        quit()
    finally:
        try:
            root.destroy()
        except:
            pass

# Returns selected msg file's normalized path.
def select_email_file() -> Optional[str]:
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    try:
        
        filename: str = filedialog.askopenfilename(
            title       = "Select Outlook msg File",
            filetypes   = [("msg files", "*.msg")],
            initialdir  = confidential_email_path,
            multiple    = False # type: ignore
        )
    
        if not filename or not filename.strip():
            return None

        normalized_path: str = os.path.normpath(filename)

        if not os.path.exists(normalized_path):
            print(f"Error: Selected msg file does not exist: {normalized_path}")
            quit()
        if not normalized_path.lower().endswith('.msg'):
            print(f"Warning: Selected file is not a msg file: {normalized_path}")
            quit()

        return normalized_path

    except Exception as e:
        print(f"Error selecting file: {e}")
        quit()
    finally:
        try:
            root.destroy()
        except:
            pass

# Returns a list of csv files found inside the confidential_data_path folder
def get_confidential_csv_files() -> List[Dict[str, str]]:
    csv_files: List[Dict[str, str]] = []

    if not os.path.exists(confidential_data_path):
        print(f"Warning: Confidential directory does not exist: {confidential_data_path}")
        return csv_files
    elif not os.path.isdir(confidential_data_path):
        print(f"Warning: Confidential path is not a directory: {confidential_data_path}")
        return csv_files

    try:
        all_files: List[str] = os.listdir(confidential_data_path)

        for filename in all_files:
            if filename.lower().endswith('.csv'):
                full_path: str = os.path.normpath(os.path.join(confidential_data_path, filename))

                #Verify it's actually a file (not a subdirectory)
                if os.path.isfile(full_path):
                    file_dict: Dict[str, str] = {f"{base_confidential_data_folder}/{filename}": full_path}
                    csv_files.append(file_dict)
        
    except PermissionError:
        print(f"Error: Permission denied accessing directory: {confidential_data_path}")
    except OSError as e:
        print(f"Error accessing directory {confidential_data_path}: {e}")

    return csv_files

# Returns a list of msg files found inside the confidential_email_path folder
def get_confidential_email_templates() -> List[Dict[str, str]]:
    email_templates: List[Dict[str, str]] = []

    if not os.path.exists(confidential_email_path):
        print(f"Warning: Confidential directory does not exist: {confidential_email_path}")
        return email_templates
    elif not os.path.isdir(confidential_email_path):
        print(f"Warning: Confidential path is not a directory: {confidential_email_path}")
        return email_templates

    try:
        all_files: List[str] = os.listdir(confidential_email_path)

        for filename in all_files:
            if filename.lower().endswith('.msg'):
                full_path: str = os.path.normpath(os.path.join(confidential_email_path, filename))

                #Verify it's actually a file (not a subdirectory)
                if os.path.isfile(full_path):
                    file_dict: Dict[str, str] = {f"{base_email_folder}/{filename}": full_path}
                    email_templates.append(file_dict)
        
    except PermissionError:
        print(f"Error: Permission denied accessing directory: {confidential_email_path}")
    except OSError as e:
        print(f"Error accessing directory {confidential_email_path}: {e}")

    return email_templates

# Reads all contents of a csv file and returns the data as a List[Dict[str, str]]
def read_csv_file(printer_function, filename: Optional[str] = None, # -> List[Dict[str, str]]
                  transform_headers: bool = True,
                  custom_transformers: Optional[Dict[str, Callable[[str], str]]] = None) -> List[Dict[str, str]]:

    if not filename:
        filename = select_csv_file()
    if not filename:
        return []

    is_valid, error_msg = validate_file_path(filename, {'.csv'}, max_file_size_mb=100)
    if not is_valid:
        printer_function(f"Error: {error_msg}")
        return []

    data_records: List[Dict[str, str]] = []
    processed_headers: Dict[str, str] = {}

    max_rows: int = 10000 # Limit rows to prevent resource exhaustion
    try:
        encoding = 'utf-8'  # Default encoding

        # Fix any BOM issues by reading the file with utf-8 encoding
        with open(filename, 'rb') as file:
            raw_data = file.read(4) # Read the first 4 bytes

            if raw_data.startswith(codecs.BOM_UTF8):
                # If BOM is detected, read the file with utf-8 encoding
                printer_function("Detected UTF-8 BOM, using utf-8-sig encoding to handle it.")
                encoding = 'utf-8-sig'
            elif raw_data.startswith(codecs.BOM_UTF16):
                # If UTF-16 BOM is detected, read the file with utf-16 encoding
                printer_function("Detected UTF-16 BOM, using utf-16 encoding to handle it.")
                encoding = 'utf-16'
        
        
        with open(filename, 'r', encoding=encoding, newline='') as file:
            csv_reader: csv.DictReader  = csv.DictReader(file)

            # Get and process headers
            original_headers: List[str] = list(csv_reader.fieldnames or [])            
            if not original_headers:
                printer_function("Error: CSV file appears to have no headers.")
                return[]
            
            # Limit column header number to 100 to prevent resource exhaustion
            if len(original_headers) > 100:
                printer_function(f"Warning: CSV has {len(original_headers)} columns. Processing only first 100.")
                original_headers = original_headers[:100]

            cleaned_headers: List[str] = []
            for header in original_headers:
                clean_header = header.strip('\ufeff\ufffe\x00').strip()
                cleaned_headers.append(clean_header)

            printer_function(f"Original headers: {original_headers}")
            if original_headers != cleaned_headers:
                printer_function(f"Cleaned headers: {cleaned_headers}")


            # Create header mapping if transformation is enabled
            if transform_headers:
                for original_header, clean_header in zip(original_headers, cleaned_headers):
                    processed_header: str = normalize_field_for_matching(clean_header)
                    processed_headers[original_header] = processed_header
            else:
                for original_header, clean_header in zip(original_headers, cleaned_headers):
                    processed_headers[original_header] = clean_header.strip()

            printer_function(f"Found columns:    {list(processed_headers.values())}\n")

            row_count: int = 0
            
            for row in csv_reader:
                row_count += 1

                if row_count > max_rows:
                    printer_function(f"Warning: CSV has more than {max_rows} rows. Processing stopped at row {max_rows}.")
                    break

                record: Dict[str, str] = {}

                for original_header, processed_header in processed_headers.items():
                    raw_value: str = row.get(original_header, '').strip()
                    processed_value: str = ""

                    if custom_transformers and processed_header in custom_transformers:
                        try:
                            transformer = custom_transformers[processed_header]

                            if not callable(transformer):
                                printer_function(f"Warning: Transformer for {processed_header} is not callable")
                                processed_value = str(raw_value).strip()
                            else:
                                processed_value: str = transformer(raw_value)

                        except Exception as e:
                            printer_function(f"Warning: Transformation failed for {processed_header} in row {row_count} with raw_value = {raw_value}: {e}")
                            processed_value = raw_value
                    else:
                        processed_value = str(raw_value).strip()

                    record[processed_header] = processed_value

                # Only add non-empty records
                if any(value.strip() for value in record.values()):
                    data_records.append(record)

        plural_rows_check: str = "s" if row_count > 1 else ""
        printer_function(f"Successfully loaded {len(data_records)} record{plural_rows_check} from {row_count} row{plural_rows_check}.")

    except UnicodeDecodeError as e:
        for alt_encoding in ['latin1', 'cp1252', 'iso-8859-1']:
            try:
                print(f"trying alternative encoding: {alt_encoding}")
                with open(filename, 'r', encoding=alt_encoding, newline='') as file:
                    csv_reader = csv.DictReader(file)
                    original_headers = list(csv_reader.fieldnames or [])

                    cleaned_headers = [header.strip('\ufeff\ufffe\x00').strip() for header in original_headers]

                    data_records = []
                    row_count = 0
                    for row in csv_reader:
                        row_count += 1
                        if row_count > max_rows:
                            break
                        record = {normalize_field_for_matching(header): str(value).strip() for header, value in row.items() if header}
                        if any(value.strip() for value in record.values()):
                            data_records.append(record)
                    print(f"Successfully read file with alternative encoding: {alt_encoding}")
                    print(f"Loaded {len(data_records)} records.")
                    return data_records
            except Exception:
                continue
        
        print(f"Unable to decode file {filename} with utf-8 or alternative encodings. Please check the file encoding.")
        quit()
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        quit()
    except PermissionError:
        print(f"Error: Permission denied accessing file: {filename}")
        quit()
    except csv.Error as e:
        print(f"Error: Invalid CSV format in file {filename}: {e}")
        quit()
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        quit()

    if not data_records:
        print(f"No data found in file. File may be empty or contain only headers. Exiting...")
        quit()
    
    return data_records