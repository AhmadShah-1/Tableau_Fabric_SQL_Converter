# Error Handling Guide

## Overview

This guide explains how the Tableau to Fabric SQL Converter handles errors, unsupported functions, and complex patterns that require manual review.

---

## Error Categories

### 1. **Unsupported Functions** 🚫

Functions that are not in our mapping dictionary will be **flagged as unsupported**.

**Examples:**
- Custom User-Defined Functions (UDFs)
- Tableau-specific calculation functions
- Unknown or proprietary functions

```sql
-- These will be flagged as unsupported:
SELECT 
    CUSTOM_ENCRYPT(ssn) AS encrypted,
    MY_UDF_FUNCTION(data) AS processed,
    WINDOW_AVG(sales_amount) AS moving_avg,
    RUNNING_SUM(quantity) AS cumulative
FROM customers;
```

**What happens:**
- Function is added to "Unsupported Functions" list
- Original syntax is preserved
- User is alerted in the "Flagged Items" section
- Metrics show function as unsupported

---

### 2. **Functions Requiring Special Handling** ⚠️

Some functions need more than simple name replacement and are **flagged for manual review**.

#### MEDIAN Function
```sql
-- Tableau:
SELECT MEDIAN(salary) FROM employees;

-- Fabric requires WITHIN GROUP clause:
SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) FROM employees;
```

#### CAST Operations (STR, INT, FLOAT, DATE)
```sql
-- Tableau:
SELECT STR(employee_id), INT(salary_string) FROM employees;

-- Fabric requires explicit CAST:
SELECT CAST(employee_id AS VARCHAR), CAST(salary_string AS INT) FROM employees;
```

#### String Pattern Functions (STARTSWITH, ENDSWITH)
```sql
-- Tableau:
SELECT * FROM products WHERE STARTSWITH(name, 'Pro');

-- Fabric requires CHARINDEX with additional logic:
SELECT * FROM products WHERE CHARINDEX('Pro', name) = 1;
```

**What happens:**
- Function is recognized but flagged for review
- Reason for flagging is provided
- User must manually adjust the syntax

---

### 3. **Syntax Errors** ❌

Structural SQL errors that prevent proper parsing.

**Examples:**
```sql
-- Unbalanced parentheses:
SELECT UPPER(name FROM customers;

-- Invalid SQL keywords:
SELEKT * FROM table;

-- Missing closing quotes:
SELECT * FROM customers WHERE name = 'John;
```

**What happens:**
- Validation error is detected
- Error message explains the issue
- Conversion may proceed with best effort
- User is alerted to check the output

---

### 4. **Tableau-Specific Features** 🎯

Features unique to Tableau that don't have direct Fabric equivalents.

#### Level of Detail (LOD) Expressions
```sql
-- Tableau LOD expressions:
SELECT 
    {FIXED [Region]: SUM([Sales])} AS region_total,
    {INCLUDE [Category]: AVG([Profit])} AS category_avg_profit
FROM orders;
```

#### Table Calculations
```sql
-- Tableau table calculations:
SELECT 
    LOOKUP(revenue, -1) AS previous_month,
    PREVIOUS_VALUE(revenue) AS prev_value,
    INDEX() AS row_index,
    FIRST() AS is_first_row
FROM monthly_revenue;
```

**What happens:**
- These are flagged as unsupported
- User must rewrite using Fabric window functions
- Documentation suggests alternatives

---

### 5. **Complex Nested Patterns** 🔄

Deeply nested functions that are difficult to parse automatically.

```sql
-- Complex nesting:
SELECT 
    IF(
        MEDIAN(
            IF(status = 'COMPLETE', 
               DATEDIFF('day', order_date, ship_date), 
               NULL)
        ) > 5,
        'SLOW',
        'FAST'
    ) AS shipping_speed
FROM orders;
```

**What happens:**
- Inner functions may convert, but outer structure is flagged
- User should verify the complete logic
- Simplification recommended

---

## How Errors Are Presented to Users

### In the GUI

1. **Status Bar**
   - Shows overall success rate
   - Indicates number of flagged items
   - Color-coded (Green = good, Yellow = review, Red = attention needed)

2. **Flagged Items Section** (Bottom Panel)
   ```
   ⚠ 5 ITEM(S) REQUIRE MANUAL REVIEW:
   ════════════════════════════════════════════════════════════════════
   
   Line 0: MEDIAN function requires manual review
   Line 0: CUSTOM_ENCRYPT function not supported
   Line 0: STR conversion requires manual review
   Line 0: WINDOW_AVG function not supported
   
   Unsupported Functions: CUSTOM_ENCRYPT, WINDOW_AVG, MY_UDF_FUNCTION
   ```

3. **Visualization**
   - Flagged items panel shows count and reasons
   - Success rate chart shows percentage
   - Function breakdown highlights unsupported types

### In the Conversion Metrics

```python
{
    'total_statements': 15,
    'successful_conversions': 8,
    'flagged_statements': 7,
    'success_rate': 53.3,
    'unsupported_functions': ['CUSTOM_ENCRYPT', 'WINDOW_AVG', 'MY_UDF_FUNCTION'],
    'flagged_lines': [
        (0, 'MEDIAN function requires manual review'),
        (0, 'STR conversion requires manual review'),
        # ... more flagged items
    ]
}
```

---

## Testing Error Handling

### Use the Error Test File

```bash
# Run the error handling test:
python test_error_handling.py
```

This will demonstrate:
- Detection of unsupported functions
- Flagging of complex patterns
- Graceful error handling (no crashes)
- Clear user feedback

### Load in GUI

```bash
# 1. Start the application:
python main/main.py

# 2. Load the error test file:
#    Click "Browse..." → Select: tests/sample_queries/tableau_error_test.sql

# 3. Click "Load & Convert"

# 4. Review the flagged items section
```

---

## Best Practices for Handling Errors

### For Users

1. **Always Review Flagged Items**
   - Don't assume automatic conversion is perfect
   - Check each flagged item before using in production

2. **Test Converted SQL**
   - Run in development environment first
   - Verify results match expectations

3. **Simplify Complex Queries**
   - Break down nested functions
   - Use CTEs for clarity
   - Comment complex logic

4. **Keep Backups**
   - Save original Tableau SQL
   - Document manual changes made

### For Developers

1. **Add New Mappings**
   - Edit `components/sql_mappings.py`
   - Add new functions to `_BASE_FUNCTION_MAPPINGS`
   - Update tests

2. **Improve Error Messages**
   - Make messages specific and actionable
   - Provide suggestions when possible
   - Include documentation links

3. **Extend Special Handling**
   - Add logic to `_convert_special_function()` in `sql_parser.py`
   - Handle parameters appropriately
   - Test thoroughly

---

## Summary of Functions That Will Cause Alerts

### ✅ **Converted Successfully** (No Alerts)
- NOW() → GETDATE()
- UPPER(), LOWER(), TRIM()
- SUM(), AVG(), COUNT()
- YEAR(), MONTH(), DAY()
- SUBSTR() → SUBSTRING()
- LENGTH() → LEN()
- IF() → IIF()
- IFNULL() → ISNULL()

### ⚠️ **Flagged for Review** (Manual Attention Needed)
- MEDIAN() - Needs WITHIN GROUP
- STR(), INT(), FLOAT(), DATE() - Need CAST syntax
- STARTSWITH(), ENDSWITH() - Need CHARINDEX logic
- TODAY() - Works but may need verification

### 🚫 **Unsupported** (Not in Mappings)
- Custom UDFs (CUSTOM_*, MY_*, etc.)
- Window calculations (WINDOW_AVG, RUNNING_SUM, etc.)
- Table calculations (LOOKUP, INDEX, FIRST, LAST, etc.)
- LOD expressions ({FIXED}, {INCLUDE}, {EXCLUDE})
- Tableau-specific functions (REGEXP_EXTRACT, FINDNTH, etc.)
- Unknown functions

---

## Error Handling Flow

```
SQL Input
    ↓
[Validation]
    ├─ Valid → Proceed to conversion
    └─ Invalid → Flag syntax error
         ↓
[Function Detection]
    ├─ In Mappings → Convert
    ├─ Special Handling → Convert + Flag for review
    └─ Not in Mappings → Flag as unsupported
         ↓
[Metrics Collection]
    └─ Track success rate, function types, errors
         ↓
[User Feedback]
    ├─ Display flagged items
    ├─ Show unsupported functions
    └─ Generate visualization
         ↓
[User Action]
    ├─ Review flagged items
    ├─ Manually adjust SQL
    └─ Re-run conversion if needed
```

---

## Quick Reference Table

| Pattern | Behavior | Action Required |
|---------|----------|-----------------|
| `NOW()` | ✅ Converts | None |
| `MEDIAN()` | ⚠️ Flags | Add WITHIN GROUP |
| `CUSTOM_FUNC()` | 🚫 Unsupported | Replace or remove |
| `STR()` | ⚠️ Flags | Use CAST() |
| `WINDOW_AVG()` | 🚫 Unsupported | Use window function |
| `{FIXED}` | 🚫 Unsupported | Rewrite query |
| Unbalanced `()` | ❌ Error | Fix syntax |

---

## Additional Resources

- **README.md** - Full documentation
- **QUICKSTART.md** - Quick start guide  
- **Test file**: `tests/sample_queries/tableau_error_test.sql`
- **Test script**: `test_error_handling.py`

---

**Remember**: The converter is a tool to assist migration, not replace human review. Always verify converted SQL before production use!

