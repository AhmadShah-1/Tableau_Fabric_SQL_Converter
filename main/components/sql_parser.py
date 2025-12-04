"""
SQL Parser Module
=================

This module handles the core SQL conversion logic, transforming Tableau SQL syntax
to Microsoft Fabric SQL syntax using a regex and formatting it with SQLParse.
"""

import sqlparse
from .Regex_remapping import apply_regex_remapping


class ConversionMetrics:
    """
    Tracks metrics for SQL conversion operations.
    """
    
    def __init__(self):
        self.total_statements = 0
        self.successful_conversions = 0
        self.flagged_statements = 0
        self.function_conversions = {
            'DATE': 0,
            'STRING': 0,
            'AGGREGATE': 0,
            'LOGICAL': 0,
            'MATHEMATICAL': 0,
            'OTHER': 0
        }
        self.flagged_lines = []  # List of (line_number, reason)
        self.unsupported_functions = set()
    
    def add_successful_conversion(self):
        self.successful_conversions += 1
    
    def add_flagged_statement(self, line_number, reason):
        self.flagged_statements += 1
        self.flagged_lines.append((line_number, reason))
    
    def add_function_conversion(self, function_type):
        if function_type in self.function_conversions:
            self.function_conversions[function_type] += 1
        else:
            self.function_conversions['OTHER'] += 1
    
    def add_unsupported_function(self, function_name):
        self.unsupported_functions.add(function_name)
    
    def get_success_rate(self):
        if self.total_statements == 0:
            return 0.0
        return (self.successful_conversions / self.total_statements) * 100
    
    def to_dict(self):
        return {
            'total_statements': self.total_statements,
            'successful_conversions': self.successful_conversions,
            'flagged_statements': self.flagged_statements,
            'success_rate': self.get_success_rate(),
            'function_conversions': self.function_conversions.copy(),
            'flagged_lines': self.flagged_lines.copy(),
            'unsupported_functions': list(self.unsupported_functions)
        }


class SQLConverter:
    """
    Thin wrapper around RegexRemapper that provides metrics and optional sqlparse-based formatting of the final SQL for readability.
    """

    def __init__(self):
        self.metrics = ConversionMetrics()
    
    def convert_query(self, tableau_query):
        """
        Convert a Tableau SQL query to Fabric SQL.

        Input: Tableau SQL query
        Output: Tuple containing:
            - Converted Fabric SQL query
            - Conversion metrics
            - List of flagged items
        """

        if not tableau_query or not isinstance(tableau_query, str):
            return "", self.metrics, []
        
        # Reset metrics for this conversion
        self.metrics = ConversionMetrics()
        self.metrics.total_statements = 1
        
        try:
            # Regex-based remapping (primary conversion)
            remapped_sql, flags = apply_regex_remapping(tableau_query)
            for (ln, reason) in flags:
                self.metrics.add_flagged_statement(ln, reason)

            # Formatting via sqlparse
            '''
            We use sqlparse to only increase the readability of the SQL query. If it fails, 
            we just equate the reamapped_SQL to the fabric_sql
            '''
            try:
                parsed = sqlparse.parse(remapped_sql)
                if parsed:
                    formatted = [sqlparse.format(str(statement), reindent=True, keyword_case='upper') for statement in parsed]
                    fabric_sql = "\n".join(formatted)
                else:
                    fabric_sql = remapped_sql
            except Exception:
                fabric_sql = remapped_sql
            
            # If there are no errors, we confirm the conversion was successful
            if not self.metrics.flagged_lines and not self.metrics.unsupported_functions:
                self.metrics.add_successful_conversion()
            
            # Return the converted Fabric SQL query, the conversion metrics, and the list of flagged items
            return fabric_sql, self.metrics, self.metrics.flagged_lines

        except Exception as e:
            error_msg = f"Conversion error: {str(e)}"
            self.metrics.add_flagged_statement(0, error_msg)
            return tableau_query, self.metrics, [(0, error_msg)]
