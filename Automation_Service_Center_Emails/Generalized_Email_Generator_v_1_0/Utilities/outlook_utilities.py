import re
import time
import gc
from typing import Optional, List
from pathlib import Path

try: # importing install_required_libraries()
    from .package_checker import install_required_libraries
except ImportError:
    from package_checker import install_required_libraries
install_required_libraries({'pywin32', 'pypiwin32'})
import win32com.client

# Validate email template path
def validate_template_path(template_path: str) -> tuple[bool, str]:
    try:
        path = Path(template_path)
        if not path.exists():
            return False, "Template file does not exist"
        if not path.is_file():
            return False, "Template path is not a file"
        if path.suffix.lower() != '.msg':
            return False, "Template must be a .msg file"
        
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > 10:
            return False, f"Template file too large: {file_size_mb:.1f}MB"
        return True, ""
    except Exception as e:
        return False, f"Validation error: {str(e)}"

# Sanitize replacement values
def sanitize_replacement_value(value: str) -> str:
    if not isinstance(value, str):
        value = str(value)
    
    # Limit length to prevent DoS
    if len(value) > 1000:
        value = value[:1000] + "..."
    
    # Remove null bytes and other control characters
    value = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', value)
    return value

def get_template_placeholders(printer_function,template_msg_path, create_draft: bool = False) -> List[str]:
    outlook = None
    template_msg = None

    is_valid, error_msg = validate_template_path(template_msg_path)
    if not is_valid:
        printer_function(f"Error: {error_msg}")
        return []

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        template_msg = outlook.CreateItemFromTemplate(template_msg_path)

        if not create_draft:
            try:
                template_msg.UnRead = False
                template_msg.Saved = True
            except:
                pass

        full_text = f"{template_msg.Subject} {template_msg.HTMLBody}"

        if len(full_text) > 1000000: # 1MB limit
            printer_function("Warning: Template text too large, truncating...")
            full_text = full_text[:1000000]

        placeholders = re.findall(r'\{\{([^{}]+)\}\}', full_text)

        cleaned_placeholders = []
        for placeholder in placeholders:
            clean_var = re.sub(r'<[^>]+>', '', placeholder).strip()

            if clean_var and len(clean_var) < 100 and clean_var not in cleaned_placeholders:
                cleaned_placeholders.append(clean_var)

        template_msg.Close(0)

        return cleaned_placeholders
    except Exception as e:
        printer_function(f"Error extracting placeholders: {e}")
        return []
    finally:
        if template_msg is not None:
            try:
                template_msg.Close(0)
                template_msg.Delete() if hasattr(template_msg, 'Delete') else None
                del template_msg
            except:
                pass
        
        if outlook is not None:
            try:
                del outlook
            except:
                pass
        
        gc.collect()
        time.sleep(0.1)

def _find_unreplaced_variables(text):
    if not text:
        return []
    
    unreplaced = re.findall(r'\{\{([^{}]+)\}\}', text)

    cleaned_variables = []
    for var in unreplaced:
        clean_var = re.sub(r'<[^>]+>', '', var).strip()
        if clean_var:
            cleaned_variables.append(clean_var)
    
    return list(set(cleaned_variables))

def _replace_template_variables(text, replacements):
    """Replace template variables in text"""
    if not text or not replacements:
        return text
    
    # Sanitize all replacement values
    safe_replacements = {}
    for key, value in replacements.items():
        safe_replacements[key] = sanitize_replacement_value(value)

    for key, value in safe_replacements.items():
        pattern =  r'\{\{[^{}]*' + re.escape(str(key)) + r'[^{}]*\}\}'
        text = re.sub(pattern, value, text)

    return text

def _generate_email(printer_function, template_msg_path, replacements, create_draft: bool = True):
    outlook = None
    draft_msg = None

    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        draft_msg = outlook.CreateItemFromTemplate(template_msg_path)

        if not create_draft:
            try:
                draft_msg.UnRead = False
                draft_msg.Saved = True
            except:
                pass
        
        draft_msg.HTMLBody = _replace_template_variables(draft_msg.HTMLBody, replacements)
        draft_msg.Subject = _replace_template_variables(draft_msg.Subject, replacements)

        return draft_msg

    except Exception as e:
        printer_function(f"Error: {e}")
        if draft_msg is not None:
            try:
                draft_msg.Close(0)
                draft_msg.Delete() if hasattr(draft_msg, 'Delete') else None
                del draft_msg
            except:
                pass
        if outlook is not None:
            try:
                del outlook
            except:
                pass

    return None

# Validate email address format
def validate_email_format(email: str) -> bool:
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))

# Creates individualized draft email and returns True/False on success state
def create_draft_email_individual_to(printer_function, template_msg_path, replacements) -> Optional[str]:
    """Create a draft email from template with variable replacements"""

    is_valid, error_msg = validate_template_path(template_path=template_msg_path)
    if not is_valid:
        printer_function(f"Error: {error_msg}")
        return None
    
    if 'email' in replacements:
        email = replacements.get('email', '').strip()
        if not validate_email_format(email):
            printer_function(f"Error: Invalid email format: {email}")
            return None

    draft_msg = _generate_email(printer_function, template_msg_path=template_msg_path, replacements=replacements, create_draft=True)
    if not draft_msg:
        return None
    
    try:
        email_addresses = replacements.get('email', '').strip()
        if email_addresses and validate_email_format(email_addresses):
            draft_msg.To = email_addresses
        else:
            printer_function(f"Warning: No valid email addresses provided")
            
        subject_msg = draft_msg.Subject

        unreplaced_in_subject = _find_unreplaced_variables(draft_msg.Subject)
        unreplaced_in_body = _find_unreplaced_variables(draft_msg.HTMLBody)

        all_unreplaced = list(set(unreplaced_in_subject + unreplaced_in_body))

        if all_unreplaced:
            formatted_vars = [f'{{{{{var}}}}}' for var in all_unreplaced]
            printer_function(f"\u26A0 WARNING: Unreplaced variables found {', '.join(formatted_vars)}")
        
        draft_msg.Save()
        draft_msg.Close(0)

        return subject_msg 
    except Exception as e:
        printer_function(f"Error: {e}")
        return ""
    finally:
        if draft_msg is not None:
            try:
                draft_msg.Close(0)
                del draft_msg
            except:
                pass
        
        gc.collect()

def create_draft_email_bcc_all(printer_function, template_msg_path, template_data, email_addresses) -> Optional[str]:
    """Create a single draft email from template with variable replacements and BCC all recipients"""
    outlook = None
    draft_msg = None
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        draft_msg = outlook.CreateItemFromTemplate(template_msg_path)

        draft_msg.HTMLBody = _replace_template_variables(draft_msg.HTMLBody, template_data)
        draft_msg.Subject = _replace_template_variables(draft_msg.Subject, template_data)

        unreplaced_in_subject = _find_unreplaced_variables(draft_msg.Subject)
        unreplaced_in_body = _find_unreplaced_variables(draft_msg.HTMLBody)

        all_unreplaced = list(set(unreplaced_in_subject + unreplaced_in_body))

        if all_unreplaced:
            printer_function(f"\u26A0 WARNING: Unreplaced variables found {', '.join([f'{{{{{var}}}}}' for var in all_unreplaced])}")

            
        bcc_list = ";".join(email_addresses)
        draft_msg.BCC = bcc_list
        draft_msg.To = ""

        subject_msg = draft_msg.Subject

        draft_msg.Save()
        time.sleep(0.1)
        draft_msg.Close(0)

        return subject_msg
    except Exception as e:
        printer_function(f"Error creating BCC email: {e}")
        return None
    finally:
        if draft_msg is not None:
            try:
                draft_msg.Close(0)
                del draft_msg
            except:
                pass
        
        if outlook is not None:
            try:
                del outlook
            except:
                pass
        
        gc.collect()
    
