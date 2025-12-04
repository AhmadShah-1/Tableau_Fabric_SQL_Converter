"""
SQL Mappings Module

This module contains hash map (dictionary) mappings for converting Tableau SQL syntax
to Microsoft Fabric SQL syntax. 

It includes mappings for common functions across DATE, STRING, and AGGREGATE categories. (they are case insensitive, and may not encompass all functions)
"""


class TableauFabricMappings:
    '''
    All SQL functions within a Hashmap for O(1) lookup
    '''
    
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
        '''
        Initialize the mappings class and create case-insensitive lookup dictionaries
        using dictionary comprehension.
        '''
        
        # Create case-insensitive mappings using dictionary comprehension
        # This makes it so that we do not need to worry about case sensitivity, and just use a unified format
        self.function_mappings = {key.upper(): value for key, value in self._BASE_FUNCTION_MAPPINGS.items()}
        
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
    
    # Get the Fabric equivalent of a Tableau function.
    def get_fabric_function(self, tableau_function):
        '''
        Returns the Fabric equivalent of a Tableau function. (Uppercase)
        '''
        return self.function_mappings.get(tableau_function.upper())
    
    # Check if a function has a mapping defined.
    def is_mapped_function(self, function_name):
        '''
        Returns True if a function has a mapping defined. (Uppercase)
        '''
        return function_name.upper() in self.function_mappings
    
    # Check if a function need special handling (not simple one to one mapping)
    # TODO: later addition, try using an api call to a lakehouse endpoint to check for verification of every fucntion translation that requires special handling
    def requires_special_handling(self, function_name):
        '''
        Returns True if a function requires special parameter handling beyond simple replacement. (Uppercase)
        '''
        return function_name.upper() in self.special_handling_functions
    
    # Get a list of all supported Tableau functions.
    def get_all_tableau_functions(self):
        '''
        Returns a list of all supported Tableau functions
        '''
        return list(self.function_mappings.keys())
    
    # Get statistics about the available mappings.
    def get_mapping_statistics(self):
        '''      
        TODO: I wanted to remove statistics and keep it simple (Just flag lines with errors)
        returns a dictionary containing mapping statistics
        {
            'total_mappings': total number of mappings,
            'date_functions': number of date functions,
            'string_functions': number of string functions,
            'aggregate_functions': number of aggregate functions,
            'special_handling_count': number of functions that require special handling
        }
        '''
        dates = ['DATEADD', 'DATEDIFF', 'DATEPART', 'DATENAME', 'NOW', 'TODAY', 'YEAR', 'MONTH', 'DAY', 'MAKEDATE', 'MAKEDATETIME']
        strings = ['LEN', 'LENGTH', 'SUBSTR', 'CONTAINS', 'LEFT', 'RIGHT', 'TRIM', 'LTRIM', 'RTRIM', 'UPPER', 'LOWER', 'REPLACE', 'SPLIT', 'FIND', 'STARTSWITH', 'ENDSWITH']
        aggregates = ['SUM', 'AVG', 'COUNT', 'MIN', 'MAX', 'STDEV', 'STDEVP', 'VAR', 'VARP', 'MEDIAN']

        # Count functions by category using dictionary comprehension
        date_functions = len([f for f in self._BASE_FUNCTION_MAPPINGS.keys() if f in dates])
        string_functions = len([f for f in self._BASE_FUNCTION_MAPPINGS.keys() if f in strings])
        aggregate_functions = len([f for f in self._BASE_FUNCTION_MAPPINGS.keys() if f in aggregates])
        
        return {
            'total_mappings': len(self.function_mappings),
            'date_functions': date_functions,
            'string_functions': string_functions,
            'aggregate_functions': aggregate_functions,
            'special_handling_count': len(self.special_handling_functions)
        }

