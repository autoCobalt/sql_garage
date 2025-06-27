import os
from typing import List, Dict, Final, Optional

try: # importing env_values
    from .constants import env_values, ConnectionState
except ImportError:
    from constants import env_values, ConnectionState # type: ignore
    
try: # importing install_required_libraries()
    from .package_checker import install_required_libraries
except ImportError:
    from package_checker import install_required_libraries
    
install_required_libraries({'oracledb'})
import oracledb

# Returns Connection successful True/False
def test_connection(username, password) -> bool:
    try:
        connection = oracledb.connect(user=username, password=password, dsn=env_values['ds'])
        connection.close()
        return True
    except oracledb.Error as error:
        return False

# Returns all rows from a query run of a given SQL statement
def query_db(printer_function,sql_query, username: Optional[str] = None, password: Optional[str] = None):
    if not test_connection(username=username, password=password):
        printer_function("Login cancelled or invalid credentials provided")
        return []
        
    try:
        with oracledb.connect(user=username, password=password, dsn=env_values['ds']) as connection:
            printer_function("Successfully connected to the database")

            with connection.cursor() as cursor:
                cursor.execute(sql_query)
                results = cursor.fetchall()

        return results
    
    except oracledb.Error as error:
        printer_function(f"Error connecting to the database: {error}")
        quit()

# Customized query run to pull business emails from a list of emplid's and stores them in the list with the key 'email'
def query_db_for_busn_emails_from_emplid(printer_function, # -> List[Dict[str, str]]
                                         employees: List[Dict[str, str]], 
                                         emplid_field: str,
                                         username: Optional[str] = None, 
                                         password: Optional[str] = None) -> List[Dict[str,str]]:
    sql_query = \
    '''
        select
              a.emplid
            , a.email_addr
        from
            ps_email_addresses a
        where
                a.emplid in (:emplids)
            and a.e_addr_type = 'BUSN'
    '''

    try:
        emplids = [employee[emplid_field] for employee in employees if emplid_field in employee]

        if not emplids:
            printer_function(f"\u26A0 Warning: No emplids found in field '{emplid_field}'")
            return employees
        
        printer_function(f"Found {len(emplids)} emplids in field '{emplid_field}'")
        
    except KeyError as e:
        printer_function(f"\u274C Error: Field '{emplid_field}' not found in employee records")
        return employees

    if not emplids:
        printer_function("\u26A0 Warning: No emplids provided to query")
        return employees
    
    str_delimited_emplids = ", ".join("'" + str(emplid) + "'" for emplid in emplids)
    sql_query = sql_query.replace(":emplids", str_delimited_emplids)

    printer_function(f"\U0001F50D Querying database for {len(emplids)} employee email addresses...")

    results = dict(query_db(printer_function=printer_function,sql_query=sql_query,username=username,password=password)) # type: ignore

    emails_found = 0
    for employee in employees:
        if emplid_field in employee:
            employee_id = employee[emplid_field]
            email = results.get(employee_id, '')
            employee['email'] = email
            if email:
                emails_found += 1
        else:
            employee['email'] = ''

    printer_function(f"\U0001F4E7 Found {emails_found} email addresses for {len(employees)} employees")

    return employees