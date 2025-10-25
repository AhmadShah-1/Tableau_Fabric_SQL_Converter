# Quick Start Guide - Tableau to Fabric SQL Converter

## 🚀 Get Started in 3 Minutes

### Step 1: Install Dependencies (30 seconds)

```bash
cd Tableau_Fabric_SQL_Converter
python -m pip install pandas matplotlib sqlparse pytest
```

### Step 2: Verify Installation (30 seconds)

Run the test suite to ensure everything works:

```bash
python -m pytest tests/ -v
```

You should see: **57 passed** ✅

### Step 3: Launch the Application (10 seconds)

```bash
python main/main.py
```

The GUI window will open automatically!

---

## 📖 Basic Usage

### Converting Your First SQL File

1. **Click "Browse..."** in the File Selection section
2. **Select a Tableau SQL file** (`.sql` or `.txt`)
3. **Click "Load & Convert"** to process the file
4. **Review the results**:
   - Left pane: Original Tableau SQL
   - Right pane: Converted Fabric SQL
   - Bottom section: Any flagged items for manual review

5. **Click "💾 Save Converted SQL"** to save the result
6. **Click "📊 Generate Visualization"** to see conversion statistics

---

## 📝 Try the Sample Files

Test with the included sample queries:

```bash
# The sample queries are in: tests/sample_queries/

# Try these files:
- tableau_simple.sql          (Basic functions)
- tableau_date_functions.sql  (Date operations)
- tableau_string_functions.sql (String operations)
- tableau_aggregates.sql      (Aggregate functions)
```

### Example: Converting Simple Query

**Input (Tableau):**
```sql
SELECT 
    NOW() AS current_time,
    UPPER(name) AS name_upper,
    SUBSTR(code, 1, 3) AS category
FROM customers;
```

**Output (Fabric):**
```sql
SELECT GETDATE() AS CURRENT_TIME,
       UPPER(NAME) AS NAME_UPPER,
       SUBSTRING(CODE, 1, 3) AS CATEGORY
FROM CUSTOMERS;
```

---

## 🔍 Understanding the Results

### Success Indicators

✅ **Green Status**: Conversion completed successfully  
⚠️ **Yellow Status**: Some items may need review  
❌ **Red Status**: Multiple items need manual attention

### Flagged Items

Items that can't be automatically converted appear in the "Flagged Items" section with:
- Line number
- Reason for flagging
- Original syntax preserved

**Common flagged items:**
- MEDIAN function (needs WITHIN GROUP clause)
- Complex CAST operations
- Custom user-defined functions

---

## 📊 Understanding the Visualization

The visualization shows 5 key metrics:

1. **Success Rate Bar**: Overall conversion percentage
2. **Function Breakdown**: Conversions by type (DATE, STRING, etc.)
3. **Statistics**: Total statements, successful, flagged
4. **Flagged Items**: Details on items needing review
5. **Summary**: Overall status and recommendations

Visualizations are automatically saved to: `assets/conversion_report_YYYYMMDD_HHMMSS.png`

---

## 🛠️ Troubleshooting

### Issue: Application won't start

**Solution:**
```bash
python -m pip install --upgrade pandas matplotlib sqlparse
python main/main.py
```

### Issue: Tests failing

**Solution:**
```bash
# Reinstall dependencies
python -m pip install -r requirements.txt --force-reinstall

# Run tests again
python -m pytest tests/ -v
```

### Issue: Tkinter not found

**Solution:**
- **Windows**: Reinstall Python with "tcl/tk" option enabled
- **Linux**: `sudo apt-get install python3-tk`
- **macOS**: Tkinter is included, ensure using system Python

---

## 📚 Supported Functions

### Most Common Functions (Fully Automated)

| Category | Tableau → Fabric |
|----------|------------------|
| **Date** | NOW() → GETDATE() |
|          | TODAY() → CAST(GETDATE() AS DATE) |
|          | MAKEDATE() → DATEFROMPARTS() |
| **String** | LENGTH() → LEN() |
|            | SUBSTR() → SUBSTRING() |
| **Logical** | IF() → IIF() |
|             | IFNULL() → ISNULL() |

See `README.md` for the complete function list (50+ mappings)!

---

## ⌨️ Keyboard Shortcuts

- **Ctrl+A**: Select all in text area
- **Ctrl+C**: Copy selected text
- **Ctrl+V**: Paste text
- Mouse scroll or scrollbars to navigate SQL

---

## 🎯 Next Steps

1. ✅ Convert your first SQL file
2. 📊 Generate and review visualizations
3. 📖 Read `README.md` for advanced features
4. 🧪 Explore sample queries in `tests/sample_queries/`
5. 📦 Package as executable (see README)

---

## 💡 Tips

- **Always review flagged items** before using converted SQL in production
- **Test converted SQL** in a development environment first
- **Keep backups** of original Tableau SQL files
- **Generate visualizations** to track conversion patterns
- **Use the Help button** in the app for quick reference

---

## 🆘 Need Help?

1. **Click "❓ Help"** in the application for quick reference
2. **Read** `README.md` for comprehensive documentation
3. **Review** `IMPLEMENTATION_SUMMARY.md` for technical details
4. **Check** test files in `tests/` for examples

---

## 📦 File Structure Quick Reference

```
Tableau_Fabric_SQL_Converter/
├── main/main.py              ← Start here!
├── components/               ← Core modules
├── tests/                    ← Sample queries & tests
├── README.md                 ← Full documentation
├── QUICKSTART.md            ← This file
└── requirements.txt          ← Dependencies
```

---

**Happy Converting! 🎉**

*Remember: This tool handles common conversions automatically and flags complex patterns for your review.*

