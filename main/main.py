'''
Main Fabric SQL Converter Entry
'''

import sys 
import tkinter as tk


from components.ui_controller import SQLConverterUI

def print_banner():
    """Print application startup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║        Tableau to Fabric SQL Converter v1.0.0                     ║
    ║        AAI551 Engineering Programming with Python                 ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)




# Main Application Entry Point
def main():
    try:
        root = tk.Tk()
        app = SQLConverterUI(root)
        app.run()

    except Exception as e:
        error_msg = f"Failed to start application:\n\n{str(e)}"
        print(error_msg)
        sys.exit(1)


if __name__ == "__main__":
    print_banner()
    main()

# I MADE A CHANGE