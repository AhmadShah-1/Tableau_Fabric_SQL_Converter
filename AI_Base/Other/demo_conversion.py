"""
Demonstration Script - Tableau to Fabric SQL Converter
=======================================================

This script demonstrates the SQL conversion functionality without the GUI.
Use this for quick testing or integration into other scripts.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from components.sql_parser import SQLConverter
from components.data_cleaner import SQLCleaner
from components.sql_mappings import TableauFabricMappings


def demo_basic_conversion():
    """Demonstrate basic SQL conversion."""
    print("=" * 80)
    print("DEMO 1: Basic Function Conversion")
    print("=" * 80)
    
    # Initialize components
    converter = SQLConverter()
    cleaner = SQLCleaner()
    
    # Sample Tableau SQL
    tableau_sql = """
    SELECT 
        NOW() AS current_time,
        UPPER(customer_name) AS name_upper,
        SUBSTR(product_code, 1, 3) AS category,
        IF(status = 1, 'Active', 'Inactive') AS status_text
    FROM customers;
    """
    
    print("\nTABLEAU SQL (Input):")
    print("-" * 80)
    print(tableau_sql)
    
    # Clean and convert
    prepared = cleaner.prepare_for_parsing(tableau_sql)
    fabric_sql, metrics, flagged = converter.convert_query(prepared['cleaned_query'])
    
    print("\nFABRIC SQL (Output):")
    print("-" * 80)
    print(fabric_sql)
    
    print("\nCONVERSION METRICS:")
    print("-" * 80)
    metrics_dict = metrics.to_dict()
    print(f"Success Rate: {metrics_dict['success_rate']:.1f}%")
    print(f"Total Statements: {metrics_dict['total_statements']}")
    print(f"Function Conversions: {sum(metrics_dict['function_conversions'].values())}")
    print(f"Flagged Items: {len(flagged)}")
    
    if flagged:
        print("\nFlagged Items:")
        for line_num, reason in flagged:
            print(f"  - Line {line_num}: {reason}")
    
    print("\n")


def demo_date_functions():
    """Demonstrate date function conversions."""
    print("=" * 80)
    print("DEMO 2: Date Function Conversions")
    print("=" * 80)
    
    converter = SQLConverter()
    cleaner = SQLCleaner()
    
    tableau_sql = """
    SELECT 
        order_id,
        NOW() AS current_timestamp,
        YEAR(order_date) AS order_year,
        MAKEDATE(2024, 1, 1) AS start_of_year,
        DATEADD('day', 30, order_date) AS due_date
    FROM orders;
    """
    
    print("\nTABLEAU SQL (Input):")
    print("-" * 80)
    print(tableau_sql)
    
    prepared = cleaner.prepare_for_parsing(tableau_sql)
    fabric_sql, metrics, flagged = converter.convert_query(prepared['cleaned_query'])
    
    print("\nFABRIC SQL (Output):")
    print("-" * 80)
    print(fabric_sql)
    print("\n")


def demo_string_functions():
    """Demonstrate string function conversions."""
    print("=" * 80)
    print("DEMO 3: String Function Conversions")
    print("=" * 80)
    
    converter = SQLConverter()
    cleaner = SQLCleaner()
    
    tableau_sql = """
    SELECT 
        product_id,
        UPPER(product_name) AS name_upper,
        LOWER(category) AS category_lower,
        LENGTH(description) AS desc_length,
        SUBSTR(product_code, 1, 5) AS short_code,
        TRIM(product_name) AS trimmed_name
    FROM products;
    """
    
    print("\nTABLEAU SQL (Input):")
    print("-" * 80)
    print(tableau_sql)
    
    prepared = cleaner.prepare_for_parsing(tableau_sql)
    fabric_sql, metrics, flagged = converter.convert_query(prepared['cleaned_query'])
    
    print("\nFABRIC SQL (Output):")
    print("-" * 80)
    print(fabric_sql)
    print("\n")


def demo_mapping_statistics():
    """Show available function mappings."""
    print("=" * 80)
    print("DEMO 4: Available Function Mappings")
    print("=" * 80)
    
    mappings = TableauFabricMappings()
    stats = mappings.get_mapping_statistics()
    
    print(f"\nTotal Function Mappings: {stats['total_mappings']}")
    print(f"Date Functions: {stats['date_functions']}")
    print(f"String Functions: {stats['string_functions']}")
    print(f"Aggregate Functions: {stats['aggregate_functions']}")
    print(f"Functions Requiring Special Handling: {stats['special_handling_count']}")
    
    print("\nSample Mappings:")
    sample_functions = ['NOW', 'SUBSTR', 'IF', 'MAKEDATE', 'LENGTH', 'IFNULL']
    for func in sample_functions:
        fabric_func = mappings.get_fabric_function(func)
        print(f"  {func:15} -> {fabric_func}")
    
    print("\n")


def demo_file_conversion():
    """Demonstrate converting a file from tests."""
    print("=" * 80)
    print("DEMO 5: Converting Sample File")
    print("=" * 80)
    
    sample_file = "tests/sample_queries/tableau_simple.sql"
    
    if not os.path.exists(sample_file):
        print(f"Sample file not found: {sample_file}")
        return
    
    from components.file_handler import FileHandler
    
    file_handler = FileHandler()
    converter = SQLConverter()
    cleaner = SQLCleaner()
    
    # Read file
    print(f"\nReading file: {sample_file}")
    tableau_sql = file_handler.read_file(sample_file)
    
    print("\nFile Contents:")
    print("-" * 80)
    print(tableau_sql[:500] + "..." if len(tableau_sql) > 500 else tableau_sql)
    
    # Convert
    prepared = cleaner.prepare_for_parsing(tableau_sql)
    fabric_sql, metrics, flagged = converter.convert_query(prepared['cleaned_query'])
    
    print("\nConversion Results:")
    print("-" * 80)
    metrics_dict = metrics.to_dict()
    print(f"[OK] Success Rate: {metrics_dict['success_rate']:.1f}%")
    print(f"[OK] Function Conversions: {sum(metrics_dict['function_conversions'].values())}")
    
    if flagged:
        print(f"[!] Flagged Items: {len(flagged)}")
    else:
        print("[OK] No Flagged Items")
    
    print("\n")


def main():
    """Run all demonstrations."""
    print("\n")
    print("+" + "=" * 78 + "+")
    print("|" + " " * 15 + "Tableau to Fabric SQL Converter - DEMO" + " " * 24 + "|")
    print("|" + " " * 20 + "Programmatic Conversion Examples" + " " * 25 + "|")
    print("+" + "=" * 78 + "+")
    print("\n")
    
    try:
        demo_basic_conversion()
        demo_date_functions()
        demo_string_functions()
        demo_mapping_statistics()
        demo_file_conversion()
        
        print("=" * 80)
        print("DEMO COMPLETE!")
        print("=" * 80)
        print("\nTo use the GUI application, run:")
        print("  python main/main.py")
        print("\nFor more information, see:")
        print("  - README.md (comprehensive documentation)")
        print("  - QUICKSTART.md (quick start guide)")
        print("  - IMPLEMENTATION_SUMMARY.md (technical details)")
        print("\n")
        
    except Exception as e:
        print(f"\n[ERROR] Error during demo: {str(e)}")
        print("Please ensure all dependencies are installed:")
        print("  python -m pip install -r requirements.txt")


if __name__ == "__main__":
    main()

