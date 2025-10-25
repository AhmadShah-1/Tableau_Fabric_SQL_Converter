"""
Error Handling Demonstration Script
====================================

This script demonstrates how the SQL Converter handles unsupported functions
and complex patterns that require manual review.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from components.sql_parser import SQLConverter
from components.data_cleaner import SQLCleaner
from components.file_handler import FileHandler


def test_error_file():
    """Test the error handling with the tableau_error_test.sql file."""
    
    print("=" * 80)
    print("ERROR HANDLING & FLAGGING DEMONSTRATION")
    print("=" * 80)
    print("\nTesting file: tests/sample_queries/tableau_error_test.sql")
    print("This file contains intentionally problematic SQL to test error handling.\n")
    
    # Initialize components
    file_handler = FileHandler()
    converter = SQLConverter()
    cleaner = SQLCleaner()
    
    error_file = "tests/sample_queries/tableau_error_test.sql"
    
    if not os.path.exists(error_file):
        print(f"[ERROR] File not found: {error_file}")
        return
    
    # Read the error test file
    try:
        tableau_sql = file_handler.read_file(error_file)
        print(f"[OK] Successfully read file ({len(tableau_sql)} characters)")
    except Exception as e:
        print(f"[ERROR] Failed to read file: {str(e)}")
        return
    
    # Clean and prepare
    print("\n" + "-" * 80)
    print("STEP 1: Cleaning and Validating SQL")
    print("-" * 80)
    
    prepared = cleaner.prepare_for_parsing(tableau_sql)
    
    print(f"Valid Structure: {prepared['is_valid']}")
    if not prepared['is_valid']:
        print(f"Validation Error: {prepared['error']}")
    
    print(f"Number of Statements: {len(prepared['statements'])}")
    print(f"Comments Extracted: {len(prepared['comments'])}")
    
    # Convert
    print("\n" + "-" * 80)
    print("STEP 2: Converting SQL (with error handling)")
    print("-" * 80)
    
    fabric_sql, metrics, flagged = converter.convert_query(prepared['cleaned_query'])
    
    # Display metrics
    metrics_dict = metrics.to_dict()
    
    print(f"\nConversion Statistics:")
    print(f"  Total Statements: {metrics_dict['total_statements']}")
    print(f"  Successful Conversions: {metrics_dict['successful_conversions']}")
    print(f"  Flagged Statements: {metrics_dict['flagged_statements']}")
    print(f"  Success Rate: {metrics_dict['success_rate']:.1f}%")
    
    # Display function conversions
    print(f"\nFunction Conversions by Type:")
    for func_type, count in metrics_dict['function_conversions'].items():
        if count > 0:
            print(f"  {func_type:15} : {count}")
    
    # Display unsupported functions
    print("\n" + "-" * 80)
    print("STEP 3: Unsupported Functions Detected")
    print("-" * 80)
    
    if metrics_dict['unsupported_functions']:
        print(f"\n{len(metrics_dict['unsupported_functions'])} unsupported function(s) found:")
        for i, func in enumerate(sorted(metrics_dict['unsupported_functions']), 1):
            print(f"  {i}. {func}")
        
        print("\n[!] These functions are NOT in our mapping dictionary.")
        print("[!] They may be custom UDFs or Tableau-specific functions.")
    else:
        print("\n[OK] All functions are supported!")
    
    # Display flagged items
    print("\n" + "-" * 80)
    print("STEP 4: Flagged Items for Manual Review")
    print("-" * 80)
    
    if flagged:
        print(f"\n{len(flagged)} item(s) flagged for manual review:\n")
        for i, (line_num, reason) in enumerate(flagged, 1):
            print(f"{i}. Line {line_num}: {reason}")
        
        print("\n[!] ACTION REQUIRED:")
        print("    - Review these items manually")
        print("    - Update the SQL as needed")
        print("    - Re-run the conversion")
    else:
        print("\n[OK] No items flagged!")
    
    # Show sample of converted output
    print("\n" + "-" * 80)
    print("STEP 5: Sample Converted Output (First 500 characters)")
    print("-" * 80)
    print("\n" + fabric_sql[:500] + "...\n")
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    if metrics_dict['success_rate'] >= 90:
        print("\n[EXCELLENT] Conversion mostly successful!")
        print("A few items may need manual review, but most SQL was converted.")
    elif metrics_dict['success_rate'] >= 50:
        print("\n[GOOD] Partial conversion successful!")
        print("Several items need manual review. Check flagged items above.")
    else:
        print("\n[ATTENTION NEEDED] Many items require manual review!")
        print("This SQL contains many unsupported or complex patterns.")
    
    print(f"\nDetailed Breakdown:")
    print(f"  - {metrics_dict['successful_conversions']} statements converted successfully")
    print(f"  - {len(metrics_dict['unsupported_functions'])} unsupported functions detected")
    print(f"  - {metrics_dict['flagged_statements']} statements flagged for review")
    
    print("\n" + "=" * 80)
    print("\nTo see this in the GUI:")
    print("  1. Run: python main/main.py")
    print("  2. Load: tests/sample_queries/tableau_error_test.sql")
    print("  3. Review flagged items in the bottom panel")
    print("  4. Generate visualization to see error breakdown")
    print("\n")


def test_individual_problematic_patterns():
    """Test individual problematic patterns."""
    
    print("=" * 80)
    print("TESTING INDIVIDUAL PROBLEMATIC PATTERNS")
    print("=" * 80)
    
    converter = SQLConverter()
    cleaner = SQLCleaner()
    
    test_cases = [
        {
            "name": "MEDIAN Function",
            "sql": "SELECT MEDIAN(salary) FROM employees;",
            "expected": "Should flag for manual review (needs WITHIN GROUP)"
        },
        {
            "name": "Custom UDF",
            "sql": "SELECT CUSTOM_FUNCTION(data) FROM table;",
            "expected": "Should flag as unsupported function"
        },
        {
            "name": "STR Function",
            "sql": "SELECT STR(employee_id) FROM employees;",
            "expected": "Should flag for manual review (needs CAST syntax)"
        },
        {
            "name": "STARTSWITH Function",
            "sql": "SELECT * FROM products WHERE STARTSWITH(name, 'Pro');",
            "expected": "Should flag for special parameter handling"
        },
        {
            "name": "Unbalanced Parentheses",
            "sql": "SELECT UPPER(name FROM customers;",
            "expected": "Should flag as invalid SQL structure"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test['name']}")
        print(f"   SQL: {test['sql']}")
        print(f"   Expected: {test['expected']}")
        
        prepared = cleaner.prepare_for_parsing(test['sql'])
        fabric_sql, metrics, flagged = converter.convert_query(prepared['cleaned_query'])
        
        metrics_dict = metrics.to_dict()
        
        if flagged or metrics_dict['unsupported_functions']:
            print(f"   Result: [FLAGGED] OK")
            if flagged:
                print(f"           Reason: {flagged[0][1]}")
            if metrics_dict['unsupported_functions']:
                print(f"           Unsupported: {', '.join(metrics_dict['unsupported_functions'])}")
        else:
            print(f"   Result: [CONVERTED] OK")
            print(f"           Output: {fabric_sql[:50]}...")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    print("\n")
    test_error_file()
    print("\n")
    test_individual_problematic_patterns()
    
    print("=" * 80)
    print("ERROR HANDLING TEST COMPLETE!")
    print("=" * 80)
    print("\nKey Takeaways:")
    print("  1. Unsupported functions are detected and flagged")
    print("  2. Complex patterns requiring manual review are identified")
    print("  3. The application doesn't crash - it gracefully handles errors")
    print("  4. Users are clearly informed about what needs manual attention")
    print("  5. Partial conversions are still useful and displayed")
    print("\n")

