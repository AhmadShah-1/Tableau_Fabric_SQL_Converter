"""
Components Package
This package contains all the modular components for the Tableau to Fabric SQL Converter.

Modules:
    - sql_mappings: Dictionary mappings for Tableau to Fabric SQL syntax conversion
    - data_cleaner: Input data cleaning and normalization using pandas
    - sql_parser: SQL parsing and conversion engine using sqlparse
    - file_handler: File I/O operations with generator functions
    - ui_controller: Tkinter-based user interface controller
"""

__version__ = "1.0.0"
__author__ = "AAI551 Project Team"

# Export main components for easier imports
from .sql_mappings import TableauFabricMappings
from .data_cleaner import SQLCleaner
from .sql_parser import SQLConverter
from .file_handler import FileHandler
from .ui_controller import SQLConverterUI

__all__ = [
    'TableauFabricMappings',
    'SQLCleaner',
    'SQLConverter',
    'FileHandler',
    'SQLConverterUI'
]

