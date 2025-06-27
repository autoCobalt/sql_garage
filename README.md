# SQL Garage 🏥⚙️

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Oracle SQL](https://img.shields.io/badge/Oracle-SQL-red.svg)](https://www.oracle.com/database/)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://python.org)
[![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-green.svg)](https://github.com/TomSchimansky/CustomTkinter)

> **A comprehensive HR automation toolkit for organizations**

SQL Garage is a powerful collection of Oracle SQL scripts and Python applications designed to automate complex HR processes in large organizations. Originally developed for hospital system administration, it provides robust solutions for personnel management, position transfers, bulk processing, and automated communications.

## 🚀 Features

### Core Automation Modules

- **🔄 Bulk Personnel Action Forms (PAF)** - Automated processing of employee position updates and transfers
- **📧 Email Generation System** - GUI-based bulk email automation with template support
- **👥 Employee Transfer Management** - Complex position transfer workflows with validation
- **📊 TCI Compliance Reporting** - Specialized reporting for APRN/CRNA/Physician staff
- **🅿️ Parking Deduction Processing** - Automated payroll deduction management
- **🔍 Fuzzy Name Matching** - Advanced employee search using Levenshtein distance algorithms

### Technical Capabilities

- **Oracle Database Integration** - Native PL/SQL functions and procedures
- **Microsoft Outlook Integration** - Automated draft email creation
- **CSV Data Processing** - Robust file handling with validation
- **GUI Applications** - Modern dark-themed interfaces using CustomTkinter
- **Secure Credential Management** - Built-in password protection and session timeouts
- **Data Transformation** - Field mapping and formatting tools

## 📁 Repository Structure

```
sql_garage/
├── Automation_Bulk_PAF/
│   └── Bulk_PAF_v_5_5/                    # Personnel Action Form bulk processing
├── Automation_Parking_Deduction/
│   └── Parking_Refund_Files_v_1_2/       # Parking deduction management
├── Automation_Service_Center_Emails/
│   └── Generalized_Email_Generator_v_1_0/ # Email automation toolkit
├── Automation_TCI_APRN_CRNA_Phys_Report/
│   └── TCI_APRN_CRNA_Phys_Report_v_1_0/    # Healthcare compliance reporting
├── Automation_Staging_Report/
│   └── TCI_Staging_v_9_3/                # TCI staging and validation
├── Automation_Transfers/
│   └── Transfers_Positions_v_3_5/        # Employee transfer workflows
├── Nearest_Match_Search_By_Name/          # Fuzzy name matching algorithms
└── LICENSE                               # AGPL v3.0 License
```

## 🛠️ Installation

### Prerequisites

- **Oracle Database** (11g or higher)
- **Python 3.7+**
- **Microsoft Outlook** (for email automation)
- **Oracle Client Libraries** (for database connectivity)

### Python Dependencies

The applications will automatically install required packages, including:

```bash
# Core dependencies (auto-installed)
customtkinter>=5.0.0
cx-Oracle>=8.0.0
pandas>=1.3.0
pywin32>=227            # For Outlook integration
openpyxl>=3.0.0        # Excel file support
```

## 🎯 Quick Start

### Email Generator Application

1. **Launch the Application**:
   ```bash
   cd Automation_Service_Center_Emails/Generalized_Email_Generator_v_1_0/
   python email_generator_window.py
   ```

2. **Test Database Connection**:
   - Enter your Oracle credentials
   - Click "Test Connection"
   - Wait for successful connection confirmation

3. **Load Your Data**:
   - Select a CSV file with employee data
   - Choose an email template (.msg file)
   - Configure field mappings

4. **Generate Emails**:
   - Select Employee ID field
   - Choose individual or BCC mode
   - Click "Submit" to create draft emails

### SQL Script Execution

1. **Bulk PAF Processing**:
   ```sql
   -- Connect to Oracle and run:
   @General_Bulk_PAF_v_5_5_ready.sql
   -- Provide required parameters when prompted
   ```

2. **Transfer Processing**:
   ```sql
   -- Set your starting date parameter:
   @Transfer_Positions_v_3_5_ready.sql
   ```

## 💡 Usage Examples

### Bulk Email Generation

```python
# The GUI application handles this, but the workflow is:
# 1. Load employee CSV with required fields (emplid, email, etc.)
# 2. Select Outlook template with placeholder variables
# 3. Map CSV fields to template placeholders
# 4. Generate individual or BCC emails automatically
```

### Position Transfer Workflow

```sql
-- Example: Process transfers for a specific date
EXECUTE :STARTING_DATE := TO_DATE('2025-01-15', 'YYYY-MM-DD');

-- The script will:
-- 1. Identify employees requiring transfers
-- 2. Validate position availability
-- 3. Generate position creation/update instructions
-- 4. Handle FTE/shift changes automatically
```

### Fuzzy Name Matching

```sql
-- Find employees with similar names (handles typos/nicknames)
-- Uses Jaro-Winkler similarity algorithm
-- Returns matches above 90% similarity threshold
```

## ⚡ Key Features Explained

### Bulk PAF Processing
- **Position Updates**: Automated position data modifications
- **Transfer Management**: Cross-departmental employee moves
- **Validation Logic**: Comprehensive business rule checking
- **Error Handling**: Detailed audit trails and exception reporting

### Email Automation
- **Template Support**: Microsoft Outlook .msg files with placeholders
- **Field Mapping**: Intelligent CSV-to-template field matching
- **Data Transformation**: Built-in formatting (currency, names, etc.)
- **Bulk Operations**: Individual emails or BCC distributions
- **Security**: Encrypted credential storage with session timeouts

### Transfer Processing
- **Action Reasoning**: Automatic determination of promotion/lateral/demotion
- **Position Creation**: Generate new positions when needed
- **Complex Validation**: Union rules, FTE categories, manager levels
- **Multi-row Support**: Handle complex benefit/status changes

## 🔧 Configuration

### Environment Variables

Create a `.env` file in each module directory:

```bash
# Database Configuration
ORACLE_HOST=your_oracle_server
ORACLE_PORT=1521
ORACLE_SERVICE=your_service_name
ORACLE_USER=your_username

# File Paths
CONFIDENTIAL_DIR=path/to/confidential/files
TEMPLATE_DIR=path/to/email/templates
OUTPUT_DIR=path/to/output/files

# Application Settings
SESSION_TIMEOUT=300000  # 5 minutes in milliseconds
MAX_EMAIL_RECORDS=1000
DEBUG_MODE=False
```

### Customization

Each module includes configuration files for:
- **Field mappings** between systems
- **Business rule validation** parameters
- **Email template** placeholders
- **Output formatting** options

## 🛡️ Security Considerations

- **Credential Protection**: Passwords are never stored in plaintext
- **Session Management**: Automatic timeouts prevent unauthorized access
- **Data Validation**: Input sanitization prevents SQL injection
- **Audit Logging**: All operations are logged for compliance
- **Access Control**: Database-level permissions required

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10+ (for Outlook integration)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 1GB free space for temporary files
- **Network**: Access to Oracle database server

### Permissions Required
- **Database**: SELECT, INSERT, UPDATE on HR tables
- **File System**: Read/write access to input/output directories
- **Outlook**: Permission to create draft emails
- **Network**: Outbound connections to database server

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Test thoroughly** with sample data before submitting
3. **Document changes** in both code and README
4. **Follow SQL formatting** conventions used in existing scripts
5. **Include error handling** for all new database operations

### Code Style
- **SQL**: Use uppercase keywords, consistent indentation
- **Python**: Follow PEP 8 style guidelines
- **Comments**: Explain business logic, not just code syntax

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

**Key License Points**:
- ✅ **Free to use** for any purpose
- ✅ **Modify and distribute** freely
- ✅ **Commercial use** permitted
- ⚠️ **Network use** triggers copyleft (must share modifications)
- ⚠️ **Source code** must be provided to users
- ⚠️ **Same license** required for derivative works

See the [LICENSE](LICENSE) file for complete terms.

## 👨‍💻 Author

**Walter Alcazar** - *Lead Developer & Hospital Systems Analyst*

## 🆘 Support

### Documentation
- **SQL Comments**: Each script includes detailed inline documentation
- **Version History**: Check file headers for change logs
- **Business Rules**: Refer to comments for HR policy explanations

### Troubleshooting

**Common Issues**:

1. **Database Connection Fails**
   ```
   Error: ORA-12154: TNS:could not resolve the connect identifier
   Solution: Verify Oracle client installation and tnsnames.ora configuration
   ```

2. **Email Generation Fails**
   ```
   Error: Outlook COM object not available
   Solution: Ensure Microsoft Outlook is installed and configured
   ```

3. **CSV Import Errors**
   ```
   Error: Invalid field names detected
   Solution: Check CSV headers match expected format (no special characters)
   ```

### Getting Help

For technical support:
1. **Check the logs** in the application output directory
2. **Review SQL comments** for business rule explanations
3. **Verify permissions** on database tables
4. **Test with sample data** to isolate issues

---

**⚠️ Important Notice**: This toolkit is designed for healthcare HR systems and contains complex business logic specific to hospital operations. Please thoroughly test all scripts in a development environment before production use.

**🏥 Healthcare Compliance**: Ensure all usage complies with HIPAA, state regulations, and your organization's data governance policies.