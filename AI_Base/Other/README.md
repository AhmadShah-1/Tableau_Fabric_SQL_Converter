# Tableau to Fabric SQL Converter

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Python application that automatically converts Tableau SQL queries to Microsoft Fabric SQL syntax, streamlining the migration process from Tableau to Power BI (Microsoft Fabric).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Supported Functions](#supported-functions)
- [Architecture](#architecture)
- [Testing](#testing)
- [Examples](#examples)
- [Known Limitations](#known-limitations)
- [Contributing](#contributing)
- [Authors](#authors)

## 🎯 Overview

As organizations migrate analytics dashboards from Tableau to Power BI (Microsoft Fabric), manually converting SQL queries is time-consuming and error-prone. This application automates the conversion process, reducing migration time and minimizing errors.

### Problem Statement

Manual SQL conversion during Tableau to Fabric migration:
- Consumes significant time and resources
- Is repetitive and error-prone
- Diverts valuable resources from higher-impact work

### Solution

An automated Python application that:
- Converts Tableau SQL to Fabric-compatible SQL
- Uses sqlparse for reliable SQL parsing with regex fallback
- Provides an intuitive GUI for easy operation
- Generates visualizations of conversion metrics
- Flags complex patterns for manual review

## ✨ Features

- **Automatic SQL Conversion**: Converts common Tableau SQL functions to Fabric equivalents
- **User-Friendly GUI**: Intuitive Tkinter-based interface with split-pane preview
- **Comprehensive Function Support**: 
  - Date functions (NOW, TODAY, MAKEDATE, etc.)
  - String functions (LENGTH, SUBSTR, CONTAINS, etc.)
  - Aggregate functions (SUM, AVG, MEDIAN, etc.)
  - Logical functions (IF, IFNULL, etc.)
- **Intelligent Flagging**: Identifies syntax requiring manual review
- **Visual Analytics**: Matplotlib-based conversion metrics and statistics
- **Memory Efficient**: Generator functions for processing large files
- **Modular Design**: Clean, maintainable architecture with separate components

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- tkinter (usually included with Python)

### Step 1: Clone or Download the Repository

```bash
git clone <repository-url>
cd Tableau_Fabric_SQL_Converter
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
python main/main.py
```

The application window should open successfully.

## 💻 Usage

### Running the Application

#### Option 1: Python Script

```bash
python main/main.py
```

#### Option 2: Compiled Executable (Windows)

After packaging with PyInstaller:
```bash
Tableau_Fabric_SQL_Converter.exe
```

### Using the GUI

1. **Load SQL File**
   - Click "Browse..." to select a Tableau SQL file (`.sql` or `.txt`)
   - Click "Load & Convert" to process the file

2. **Review Conversion**
   - View original Tableau SQL in the left pane
   - View converted Fabric SQL in the right pane
   - Check "Flagged Items" section for items needing manual review

3. **Save Results**
   - Click "💾 Save Converted SQL" to save the converted query
   - Choose destination and filename

4. **Generate Visualization**
   - Click "📊 Generate Visualization" to see conversion metrics
   - View success rates, function breakdowns, and flagged items
   - Visualization is saved to `assets/` directory

5. **Get Help**
   - Click "❓ Help" for usage instructions and supported functions

### Keyboard Shortcuts

- The text areas support standard copy/paste operations
- Use mouse scroll or scrollbars to navigate long SQL queries

## 📊 Supported Functions

### Date Functions

| Tableau Function | Fabric Equivalent | Notes |
|-----------------|-------------------|-------|
| `NOW()` | `GETDATE()` | Current timestamp |
| `TODAY()` | `CAST(GETDATE() AS DATE)` | Current date only |
| `MAKEDATE()` | `DATEFROMPARTS()` | Construct date from parts |
| `YEAR()`, `MONTH()`, `DAY()` | Same | Extract date parts |
| `DATEADD()` | `DATEADD()` | Add time intervals |
| `DATEDIFF()` | `DATEDIFF()` | Calculate date differences |

### String Functions

| Tableau Function | Fabric Equivalent | Notes |
|-----------------|-------------------|-------|
| `LENGTH()` | `LEN()` | String length |
| `SUBSTR()` | `SUBSTRING()` | Extract substring |
| `CONTAINS()` | `CHARINDEX()` | String search |
| `FIND()` | `CHARINDEX()` | Find string position |
| `UPPER()`, `LOWER()` | Same | Case conversion |
| `TRIM()`, `LTRIM()`, `RTRIM()` | Same | Whitespace removal |
| `REPLACE()` | `REPLACE()` | String replacement |

### Aggregate Functions

| Tableau Function | Fabric Equivalent | Notes |
|-----------------|-------------------|-------|
| `SUM()`, `AVG()`, `COUNT()` | Same | Basic aggregates |
| `MIN()`, `MAX()` | Same | Min/Max values |
| `STDEV()`, `STDEVP()` | Same | Standard deviation |
| `VAR()`, `VARP()` | Same | Variance |
| `MEDIAN()` | `PERCENTILE_CONT(0.5)` | Requires manual review |

### Logical Functions

| Tableau Function | Fabric Equivalent | Notes |
|-----------------|-------------------|-------|
| `IF()` | `IIF()` | Conditional logic |
| `IFNULL()` | `ISNULL()` | Null handling |
| `ZN()` | `ISNULL(expr, 0)` | Zero if null |

### Mathematical Functions

| Tableau Function | Fabric Equivalent | Notes |
|-----------------|-------------------|-------|
| `LN()` | `LOG()` | Natural logarithm |
| `LOG()` | `LOG10()` | Base-10 logarithm |
| `ROUND()`, `CEILING()`, `FLOOR()` | Same | Rounding functions |
| `SQRT()`, `POWER()`, `ABS()` | Same | Math operations |

## 🏗️ Architecture

### Project Structure

```
Tableau_Fabric_SQL_Converter/
├── components/              # Modular components
│   ├── __init__.py         # Package initialization
│   ├── sql_mappings.py     # Function mapping dictionaries
│   ├── data_cleaner.py     # Input cleaning with pandas
│   ├── sql_parser.py       # Conversion engine (sqlparse + regex)
│   ├── file_handler.py     # File I/O with generators
│   ├── visualizer.py       # Matplotlib visualizations
│   └── ui_controller.py    # Tkinter GUI
├── tests/                   # Test suite
│   ├── test_mappings.py    # Mapping tests
│   ├── test_parser.py      # Conversion logic tests
│   ├── test_file_handler.py # File I/O tests
│   └── sample_queries/     # Sample SQL files
├── main/
│   └── main.py             # Application entry point
├── assets/                  # Assets and outputs
├── requirements.txt         # Dependencies
└── README.md               # This file
```

### Key Design Patterns

1. **Hash Maps (Dictionaries)**: SQL function mappings with case-insensitive lookups
2. **Generator Functions**: Memory-efficient line-by-line file processing
3. **Operator Overloading**: SQLFragment class with `__add__` for combining queries
4. **Modular Architecture**: Separate concerns for maintainability
5. **Comprehensive Documentation**: Docstrings and inline comments throughout

## 🧪 Testing

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run specific test module:
```bash
pytest tests/test_parser.py
```

Run with coverage report:
```bash
pytest --cov=components tests/
```

Run with verbose output:
```bash
pytest -v tests/
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end conversion testing
- **Sample Query Tests**: Real-world SQL conversion validation
- **Hash Comparison**: Exact output verification

### Sample Test Files

Located in `tests/sample_queries/`:
- `tableau_simple.sql` - Basic SELECT with common functions
- `tableau_date_functions.sql` - Date operations
- `tableau_string_functions.sql` - String operations
- `tableau_aggregates.sql` - Aggregate functions

Each has a corresponding `_expected.sql` file for verification.

## 📖 Examples

### Example 1: Simple Date Function Conversion

**Input (Tableau):**
```sql
SELECT 
    customer_name,
    order_date,
    NOW() AS current_time
FROM customers
WHERE order_date >= DATEADD('year', -1, NOW());
```

**Output (Fabric):**
```sql
SELECT customer_name,
       order_date,
       GETDATE() AS current_time
FROM customers
WHERE order_date >= DATEADD('year', -1, GETDATE());
```

### Example 2: String Function Conversion

**Input (Tableau):**
```sql
SELECT 
    product_id,
    UPPER(product_name) AS name_upper,
    LEN(description) AS desc_length,
    SUBSTR(product_code, 1, 3) AS category
FROM products
WHERE LEN(product_name) > 5;
```

**Output (Fabric):**
```sql
SELECT product_id,
       UPPER(product_name) AS name_upper,
       LEN(description) AS desc_length,
       SUBSTRING(product_code, 1, 3) AS category
FROM products
WHERE LEN(product_name) > 5;
```

### Example 3: Logical Function Conversion

**Input (Tableau):**
```sql
SELECT 
    user_id,
    IF(status = 1, 'Active', 'Inactive') AS status_text,
    IFNULL(last_login, 'Never') AS last_login_display
FROM users;
```

**Output (Fabric):**
```sql
SELECT user_id,
       IIF(status = 1, 'Active', 'Inactive') AS status_text,
       ISNULL(last_login, 'Never') AS last_login_display
FROM users;
```

## ⚠️ Known Limitations

1. **MEDIAN Function**: Requires manual adjustment to add `WITHIN GROUP` clause
2. **Complex Window Functions**: May require manual review
3. **Custom UDFs**: User-defined functions are flagged for manual handling
4. **Nested Functions**: Deep nesting may need verification
5. **CAST Conversions**: STR(), INT(), FLOAT() conversions flagged for review
6. **String Pattern Matching**: Complex CONTAINS/STARTSWITH patterns may need adjustment

### Flagged Items

When the converter encounters syntax it cannot automatically convert, it:
- Flags the item in the "Flagged Items" section
- Provides a reason for flagging
- Preserves the original syntax for manual review
- Includes the item in conversion metrics

## 🛠️ Creating an Executable

To package the application as a Windows executable:

```bash
pyinstaller --onefile --windowed --name "Tableau_Fabric_SQL_Converter" main/main.py
```

The executable will be created in the `dist/` directory.

### PyInstaller Options Explained

- `--onefile`: Package everything into a single executable
- `--windowed`: Hide console window (GUI mode)
- `--name`: Name of the output executable
- Add `--icon=assets/icon.ico` to include a custom icon

## 👥 Authors

**AAI551 Project Team**
- Engineering Programming with Python
- Fall 2025

## 📄 License

This project is created for educational purposes as part of the AAI551 course.

## 🙏 Acknowledgments

- **sqlparse**: For SQL parsing capabilities
- **pandas**: For efficient data manipulation
- **matplotlib**: For visualization generation
- **Tkinter**: For GUI framework

## 📞 Support

For issues, questions, or contributions, please refer to the course materials or contact the project team.

## 🔄 Version History

- **v1.0.0** (2025) - Initial release
  - Core conversion functionality
  - GUI interface
  - Visualization module
  - Comprehensive test suite

---

**Note**: This application handles common SQL conversion patterns. Complex or custom SQL may require manual review. Always verify converted SQL before production use.

