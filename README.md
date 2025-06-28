# SQL Garage 🏥⚙️
**Warning**: Highly customized queries. Any personal use must be altered for your own systems.
A comprehensive collection of SQL automation tools designed for PeopleSoft HR management at large healthcare organizations. These tools transform complex, time-intensive HR processes from manual tasks taking days or weeks into automated workflows completed in hours.

## 🎯 Project Overview

**SQL Garage** is a production-ready suite of Oracle SQL scripts and Python applications that automate critical HR operations including employee transfers, bulk position changes, hiring workflows, and payroll deductions. Originally developed for a large corporate hospital system, these tools have proven to dramatically improve operational efficiency while reducing human error.

### Key Benefits
- **Time Reduction**: Complex employee transfers reduced from ~1 week to ~1 hour
- **Accuracy**: Automated validation and error checking
- **Scalability**: Handles bulk operations for hundreds of employees
- **Integration**: Seamless PeopleSoft integration with Excel template workflows

## 🛠️ Core Automation Tools

### 1. **Bulk Position Action Forms (PAF)** 📋
**Location**: `Automation_Bulk_PAF/Bulk_PAF_v_5_5/`

Intelligently handles mass employee moves by determining whether to:
- Update position data tables for field changes (dept, hours, shift, reports_to, jobcode)
- Transfer employees to existing positions
- Create new positions when no suitable match exists

**Business Logic**: Analyzes employee groupings and field matching to optimize position management strategy.

### 2. **Employee Transfers & Promotions** 🔄
**Location**: `Automation_Transfers/Transfers_Positions_v_3_5/`

Processes complex employee transfers with automatic classification:
- **Promotions (PRO)**: Grade/salary increases
- **Demotions (DEM)**: Grade/salary decreases  
- **Lateral Moves (LTM)**: Department/jobcode changes
- **Shift Changes (SFT)**: Schedule modifications
- **Hours Changes (HRS)**: FTE adjustments

**Impact**: Reduces transfer processing time from nearly a week to approximately one hour.

### 3. **TCI Staging Reports** 📊
**Location**: `Automation_TCI_Staging_Report/TCI_Staging_v_9_3/`

Comprehensive hiring/rehire processing with automatic employee history analysis:
- Candidate eligibility verification
- Historical employment record matching
- Rehire status determination
- Data validation and error flagging

### 4. **APRN/CRNA/Physician Reports** 👩‍⚕️
**Location**: `Automation_TCI_APRN_CRNA_Phys_Report/TCI_APRN_CRNA_Phys_Report_v_1_0/`

Specialized hiring workflow for clinical staff (Advanced Practice Registered Nurses, Certified Registered Nurse Anesthetists, and Physicians) with profession-specific validation rules.

### 5. **Parking Deduction Management** 🚗
**Location**: `Automation_Parking_Deduction/Parking_Refund_Files_v_1_2/`

Automated processing of parking refund requests:
- Processes parking department refund data
- Generates payroll-ready refund files
- Separates active vs. terminated employee handling
- Excel template integration for seamless workflow

### 6. **Email Service Center** 📧
**Location**: `Automation_Service_Center_Emails/Generalized_Email_Generator_v_1_0/`

Python-based email automation system for employee notifications:
- Individualized tuition payment notifications
- Tax liability alerts for imputed income
- Template-based email generation with field substitution
- Outlook integration for draft creation

**Key Features**:
- Database integration for employee data retrieval
- CSV file processing with field transformation
- Secure credential management
- BCC mode for bulk communications

### 7. **Name Matching System** 🔍
**Location**: `Nearest_Match_Search_By_Name/`

Advanced fuzzy matching using Levenshtein Distance algorithm:
- Handles name variations (nicknames, typos, married names)
- Historical name change tracking
- Probabilistic matching with confidence scores
- Supports legal name changes and aliases

## 🏗️ Technical Architecture

### Technologies Used
- **Database**: Oracle SQL with PeopleSoft integration
- **Scripting**: Python 3.8+ with modern libraries
- **UI**: CustomTkinter for desktop applications
- **Email**: Outlook COM integration
- **Data Processing**: Pandas, CSV, Excel template workflows

### Key Technical Features
- **Parameterized Queries**: Secure, reusable SQL with bind variables
- **Error Handling**: Comprehensive validation and rollback capabilities
- **Performance Optimization**: Efficient query design for large datasets
- **Security**: Credential encryption and secure password handling
- **Logging**: Detailed audit trails and process monitoring

## 📁 Repository Structure

```
sql_garage/
├── Automation_Bulk_PAF/
│   └── Bulk_PAF_v_5_5/           # Mass employee position changes
├── Automation_Parking_Deduction/
│   └── Parking_Refund_Files_v_1_2/  # Parking refund processing
├── Automation_Service_Center_Emails/
│   └── Generalized_Email_Generator_v_1_0/  # Email automation system
├── Automation_TCI_APRN_CRNA_Phys_Report/
│   └── TCI_APRN_CRNA_Phys_Report_v_1_0/  # Clinical staff hiring
├── Automation_TCI_Staging_Report/
│   └── TCI_Staging_v_9_3/        # General hiring/rehire processing
├── Automation_Transfers/
│   └── Transfers_Positions_v_3_5/  # Employee transfer automation
├── Nearest_Match_Search_By_Name/  # Fuzzy name matching
└── LICENSE                       # AGPL License
```

## 🚀 Getting Started

### Prerequisites
- Oracle Database with PeopleSoft tables access
- Python 3.8+ (for email automation)
- Microsoft Outlook (for email features)
- Excel (for template workflows)

### Basic Usage
1. **Identify the automation tool** needed for your HR process
2. **Review the SQL file** in the appropriate subfolder
3. **Prepare input data** using provided Excel templates
4. **Execute the query** with appropriate parameters
5. **Review output** and process results

### Python Email Tool Setup
```bash
# Install required dependencies
pip install customtkinter pandas openpyxl pywin32

# Run the email generator
python email_generator_window.py
```

## 📊 Performance Metrics

| Process | Manual Time | Automated Time | Improvement |
|---------|-------------|----------------|-------------|
| Employee Transfers | ~1 week | ~1 hour | 40x faster |
| Bulk PAF Processing | ~2-3 days | ~2-3 hours | 10x faster |
| Hiring Reports | ~4-6 hours | ~30 minutes | 8x faster |
| Email Notifications | ~1-2 hours | ~10 minutes | ~15x faster |

## 🔒 Security & Compliance

- **Data Privacy**: Handles sensitive employee information securely
- **Audit Trails**: Comprehensive logging for compliance tracking
- **Access Control**: Database-level security integration
- **Encryption**: Secure credential storage and transmission
- **HIPAA Considerations**: Healthcare-appropriate data handling

## 🤝 Contributing

This project represents production-ready tools developed for enterprise HR operations. Contributions should maintain:

- **Code Quality**: Comprehensive error handling and validation
- **Documentation**: Clear comments and process documentation
- **Testing**: Thorough validation with realistic data scenarios
- **Security**: Secure coding practices for sensitive HR data

## 📋 Version History

- **v5.5** - Bulk PAF automation with enhanced position matching
- **v9.3** - TCI Staging with improved historical record analysis
- **v3.5** - Transfer automation with comprehensive action classification
- **v1.2** - Parking deduction processing with payroll integration
- **v1.0** - Email automation with template-based generation

## 📄 License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

See [LICENSE](LICENSE) file for full license terms.

## 👨‍💻 Author

**Walter Alcazar**  
*Senior Database Developer & HR Systems Analyst*

Developed for large-scale healthcare HR operations with focus on automation, efficiency, and data integrity.

---

## 📞 Support

For technical questions or implementation guidance:
- Review the comprehensive SQL comments in each automation tool
- Check the detailed process documentation in individual subfolders
- Ensure proper PeopleSoft table access and permissions

**Note**: These tools are designed for enterprise PeopleSoft environments and require appropriate database access and HR domain knowledge for effective implementation.

---

*Transform your HR operations from manual processes to automated workflows with SQL Garage.* ⚙️✨
