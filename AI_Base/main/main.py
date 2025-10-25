"""
Tableau to Fabric SQL Converter - Main Application Entry Point
===============================================================

This is the main entry point for the Tableau to Fabric SQL Converter application.
It initializes all components and launches the graphical user interface.

Author: AAI551 Project Team
Version: 1.0.0

Usage:
    python main.py
    
    Or run the compiled executable:
    Tableau_Fabric_SQL_Converter.exe
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add the parent directory to Python path to enable component imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components
try:
    from components.ui_controller import SQLConverterUI
    from components.sql_parser import SQLConverter
    from components.sql_mappings import TableauFabricMappings
    from components.data_cleaner import SQLCleaner
    from components.file_handler import FileHandler
except ImportError as e:
    print(f"Error importing components: {e}")
    print("Please ensure all required packages are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def main():
    """
    Main application entry point.
    
    Initializes the Tkinter root window and launches the SQL Converter UI.
    Handles any startup errors gracefully.
    """
    try:
        # Create root window
        root = tk.Tk()
        
        # Set application icon (if available)
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except:
            pass  # Icon is optional
        
        # Initialize UI controller
        app = SQLConverterUI(root)
        
        # Run the application
        app.run()
        
    except Exception as e:
        # Show error message if UI fails to start
        error_msg = f"Failed to start application:\n\n{str(e)}"
        
        try:
            # Try to show GUI error dialog
            error_root = tk.Tk()
            error_root.withdraw()
            messagebox.showerror("Startup Error", error_msg)
            error_root.destroy()
        except:
            # Fallback to console error
            print(error_msg)
        
        sys.exit(1)


def check_dependencies():
    """
    Check if all required dependencies are installed.
    
    Returns:
        tuple: (all_installed: bool, missing_packages: list)
    """
    required_packages = {
        'pandas': 'pandas',
        'matplotlib': 'matplotlib',
        'sqlparse': 'sqlparse'
    }
    
    missing = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)
    
    return len(missing) == 0, missing


def print_banner():
    """Print application startup banner."""
    banner = """
    +===================================================================+
    |                                                                   |
    |        Tableau to Fabric SQL Converter v1.0.0                    |
    |        AAI551 Engineering Programming with Python                |
    |                                                                   |
    +===================================================================+
    """
    print(banner)


if __name__ == "__main__":
    """
    Application entry point when run as a script.
    
    Performs dependency checks and launches the main application.
    """
    # Print banner
    print_banner()
    
    # Check dependencies
    print("Checking dependencies...")
    all_installed, missing = check_dependencies()
    
    if not all_installed:
        print("\n[ERROR] Missing required packages:")
        for package in missing:
            print(f"   - {package}")
        print("\nPlease install missing packages using:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    print("[OK] All dependencies installed\n")
    print("Starting application...\n")
    
    # Launch application
    main()

