import os
from typing import Final
from email_generator_window import MainApplicationWindow

main_path: Final[str] = os.path.normpath(os.path.dirname(os.path.realpath(__file__)))

"""
def deprecated_main() -> None:
    try:
        
        emp_file           = default_emp_file     if os.path.exists(default_emp_file)     else None
        tuition_email_file = default_tuition_file if os.path.exists(default_tuition_file) else select_email_file( default_req_dir if os.path.exists(default_req_dir) else dir_path)
        
        employee_data: List[Dict[str, str]] = read_tuition_file(filename=emp_file, dir_path=dir_path)
        query_db_for_busn_emails_from_emplid(employee_data)

        max_email_length:   int = max((len(d.get('email', '')) for d in employee_data), default=0)
        max_amt_length:     int = max((len(d.get('payment_amount', '')) for d in employee_data), default=0)
        email_count:        int = len(employee_data)
        
        print(f"Generating {email_count} Email{"s" if email_count > 1 else ""}:\n")
        for index, employee in enumerate(employee_data):
            print((f"{index+1}").rjust(3) + ".", create_draft_email_individual_to(tuition_email_file, employee, max_email_length, max_amt_length))
        print()
        #window.keep_open()
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
    finally:
        sys.stdout = 5 #original_stdout
"""
def main():
    try:
        app = MainApplicationWindow()
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