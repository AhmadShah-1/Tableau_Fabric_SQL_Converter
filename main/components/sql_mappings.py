"""
SQL Mappings Module
===================

This module contains hash map (dictionary) mappings for converting Tableau SQL syntax
to Microsoft Fabric SQL syntax. It includes mappings for common functions across
DATE, STRING, and AGGREGATE categories.

The mappings use dictionary comprehension for case-insensitive lookups to handle
various SQL formatting styles.
"""


class TableauFabricMappings:
    """
    All SQL functions within a Hashmap for O(1) lookup
    """
    
    # Tableau function name -> Fabric function name
    _BASE_FUNCTION_MAPPINGS = {
        # DATE Functions
        'DATEADD': 'DATEADD',  # Same in both, but parameter order may differ
        'DATEDIFF': 'DATEDIFF',  # Same in both, but parameter order may differ
        'DATEPART': 'DATEPART',
        'DATENAME': 'DATENAME',
        'NOW': 'GETDATE',  # Tableau NOW() -> Fabric GETDATE()
        'TODAY': 'CAST(GETDATE() AS DATE)',  # Tableau TODAY() -> Fabric date cast
        'YEAR': 'YEAR',
        'MONTH': 'MONTH',
        'DAY': 'DAY',
        'MAKEDATE': 'DATEFROMPARTS',  # Tableau MAKEDATE -> Fabric DATEFROMPARTS
        'MAKEDATETIME': 'DATETIMEFROMPARTS',
        
        # STRING Functions
        'LEN': 'LEN',  
        'LENGTH': 'LEN',  # Tableau LENGTH -> Fabric LEN
        'SUBSTR': 'SUBSTRING',  # Tableau SUBSTR -> Fabric SUBSTRING
        'CONTAINS': 'CHARINDEX',  # Tableau CONTAINS -> Fabric CHARINDEX
        'LEFT': 'LEFT',
        'RIGHT': 'RIGHT',
        'TRIM': 'TRIM',
        'LTRIM': 'LTRIM',
        'RTRIM': 'RTRIM',
        'UPPER': 'UPPER',
        'LOWER': 'LOWER',
        'REPLACE': 'REPLACE',
        'SPLIT': 'STRING_SPLIT',  # Tableau SPLIT -> Fabric STRING_SPLIT
        'FIND': 'CHARINDEX',  # Tableau FIND -> Fabric CHARINDEX
        'STARTSWITH': 'CHARINDEX',  # Will need special handling in parser
        'ENDSWITH': 'CHARINDEX',  # Will need special handling in parser
        
        # AGGREGATE Functions
        'SUM': 'SUM',
        'AVG': 'AVG',
        'COUNT': 'COUNT',
        'MIN': 'MIN',
        'MAX': 'MAX',
        'STDEV': 'STDEV',  # Tableau STDEV -> Fabric STDEV
        'STDEVP': 'STDEVP',
        'VAR': 'VAR',
        'VARP': 'VARP',
        'MEDIAN': 'PERCENTILE_CONT(0.5)',  # Tableau MEDIAN -> Fabric PERCENTILE_CONT
        
        # LOGICAL Functions
        'IF': 'IIF',  # Tableau IF -> Fabric IIF
        'IFNULL': 'ISNULL',  # Tableau IFNULL -> Fabric ISNULL
        'ISNULL': 'ISNULL',
        'ZN': 'ISNULL',  # Tableau ZN (zero if null) -> Fabric ISNULL
        
        # CONVERSION Functions
        'STR': 'CAST',  # Tableau STR -> Fabric CAST
        'INT': 'CAST',  # Will need special handling
        'FLOAT': 'CAST',  # Will need special handling
        'DATE': 'CAST',  # Will need special handling
        
        # MATHEMATICAL Functions
        'ABS': 'ABS',
        'ROUND': 'ROUND',
        'CEILING': 'CEILING',
        'FLOOR': 'FLOOR',
        'SQRT': 'SQRT',
        'POWER': 'POWER',
        'EXP': 'EXP',
        'LN': 'LOG',  # Tableau LN (natural log) -> Fabric LOG
        'LOG': 'LOG10',  # Tableau LOG (base 10) -> Fabric LOG10
    }
    
    def __init__(self):
        """
        Initialize the mappings class and create case-insensitive lookup dictionaries
        using dictionary comprehension.
        """
        
        # Create case-insensitive mappings using dictionary comprehension
        # This allows lookups regardless of SQL case conventions
        self.function_mappings = {
            key.upper(): value 
            for key, value in self._BASE_FUNCTION_MAPPINGS.items()
        }
        
        # Removed unused reverse and syntax pattern maps to simplify module
        
        # Functions requiring special parameter handling
        self.special_handling_functions = {
            'MEDIAN',  # Needs WITHIN GROUP clause
            'PERCENTILE_CONT',
            'CONTAINS',
            'STARTSWITH',
            'ENDSWITH',
            'IF',
            'TODAY',
            'STR',
            'INT',
            'FLOAT',
            'DATE',
        }
    
    def get_fabric_function(self, tableau_function):
        """
        Get the Fabric equivalent of a Tableau function.
        
        Args:
            tableau_function (str): The Tableau function name
            
        Returns:
            str: The Fabric function name, or None if no mapping exists
        """
        return self.function_mappings.get(tableau_function.upper())
    
    def is_mapped_function(self, function_name):
        """
        Check if a function has a mapping defined.
        
        Args:
            function_name (str): The function name to check
            
        Returns:
            bool: True if mapping exists, False otherwise
        """
        return function_name.upper() in self.function_mappings
    
    def requires_special_handling(self, function_name):
        """
        Check if a function requires special parameter handling beyond simple replacement.
        
        Args:
            function_name (str): The function name to check
            
        Returns:
            bool: True if special handling is needed, False otherwise
        """
        return function_name.upper() in self.special_handling_functions
    
    def get_all_tableau_functions(self):
        """
        Get a list of all supported Tableau functions.
        
        Returns:
            list: List of Tableau function names
        """
        return list(self.function_mappings.keys())
    
    def get_mapping_statistics(self):
        """
        Get statistics about the available mappings.
        
        Returns:
            dict: Dictionary containing mapping statistics
        """
        # Count functions by category using dictionary comprehension
        date_functions = len([f for f in self._BASE_FUNCTION_MAPPINGS.keys() 
                             if f in ['DATEADD', 'DATEDIFF', 'DATEPART', 'DATENAME', 
                                     'NOW', 'TODAY', 'YEAR', 'MONTH', 'DAY', 
                                     'MAKEDATE', 'MAKEDATETIME']])
        
        string_functions = len([f for f in self._BASE_FUNCTION_MAPPINGS.keys() 
                               if f in ['LEN', 'LENGTH', 'SUBSTR', 'CONTAINS', 'LEFT', 
                                       'RIGHT', 'TRIM', 'LTRIM', 'RTRIM', 'UPPER', 
                                       'LOWER', 'REPLACE', 'SPLIT', 'FIND', 
                                       'STARTSWITH', 'ENDSWITH']])
        
        aggregate_functions = len([f for f in self._BASE_FUNCTION_MAPPINGS.keys() 
                                  if f in ['SUM', 'AVG', 'COUNT', 'MIN', 'MAX', 
                                          'STDEV', 'STDEVP', 'VAR', 'VARP', 'MEDIAN']])
        
        return {
            'total_mappings': len(self.function_mappings),
            'date_functions': date_functions,
            'string_functions': string_functions,
            'aggregate_functions': aggregate_functions,
            'special_handling_count': len(self.special_handling_functions)
        }


# Singleton instance removed to avoid hidden global state; instantiate where needed

