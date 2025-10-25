"""
SQL Parser Module
=================

This module handles the core SQL conversion logic, transforming Tableau SQL syntax
to Microsoft Fabric SQL syntax using the sqlparse library with regex fallback.

It includes operator overloading for combining SQL fragments and tracks conversion
metrics for each query processed.
"""

import sqlparse
from sqlparse.sql import Token, Identifier, Function, Parenthesis
from sqlparse.tokens import Keyword, Name, Literal, Punctuation
import re
from .sql_mappings import TableauFabricMappings


class SQLFragment:
    """
    Represents a fragment of SQL code that can be combined using operator overloading.
    
    This class demonstrates operator overloading by implementing __add__ to allow
    SQL fragments to be combined using the + operator.
    """
    
    def __init__(self, content, is_converted=True, original=None):
        """
        Initialize a SQL fragment.
        
        Args:
            content (str): The SQL fragment text
            is_converted (bool): Whether this fragment has been successfully converted
            original (str): The original text before conversion (if applicable)
        """
        self.content = content
        self.is_converted = is_converted
        self.original = original if original else content
    
    def __add__(self, other):
        """
        Operator overloading: Combine two SQL fragments using +.
        
        Args:
            other (SQLFragment or str): Another SQL fragment to combine
            
        Returns:
            SQLFragment: A new fragment containing both fragments
        """
        if isinstance(other, SQLFragment):
            # Combine two fragments
            new_content = self.content + other.content
            new_original = self.original + other.original
            # Only consider converted if both fragments are converted
            is_converted = self.is_converted and other.is_converted
            return SQLFragment(new_content, is_converted, new_original)
        elif isinstance(other, str):
            # Combine with a string
            return SQLFragment(self.content + other, self.is_converted, self.original + other)
        else:
            raise TypeError(f"Cannot add SQLFragment with {type(other)}")
    
    def __str__(self):
        """String representation of the fragment."""
        return self.content
    
    def __repr__(self):
        """Debug representation of the fragment."""
        return f"SQLFragment(converted={self.is_converted}, content='{self.content[:50]}...')"


class ConversionMetrics:
    """
    Tracks metrics for SQL conversion operations.
    
    Used to generate statistics for visualization and reporting.
    """
    
    def __init__(self):
        """Initialize conversion metrics counters."""
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
        self.flagged_lines = []  # List of (line_number, reason) tuples
        self.unsupported_functions = set()
    
    def add_successful_conversion(self):
        """Increment successful conversion counter."""
        self.successful_conversions += 1
    
    def add_flagged_statement(self, line_number, reason):
        """
        Add a flagged statement that needs user review.
        
        Args:
            line_number (int): Line number in the original query
            reason (str): Reason for flagging
        """
        self.flagged_statements += 1
        self.flagged_lines.append((line_number, reason))
    
    def add_function_conversion(self, function_type):
        """
        Record a function conversion by type.
        
        Args:
            function_type (str): Type of function (DATE, STRING, AGGREGATE, etc.)
        """
        if function_type in self.function_conversions:
            self.function_conversions[function_type] += 1
        else:
            self.function_conversions['OTHER'] += 1
    
    def add_unsupported_function(self, function_name):
        """
        Record an unsupported function.
        
        Args:
            function_name (str): Name of the unsupported function
        """
        self.unsupported_functions.add(function_name)
    
    def get_success_rate(self):
        """
        Calculate the conversion success rate.
        
        Returns:
            float: Success rate as a percentage (0-100)
        """
        if self.total_statements == 0:
            return 0.0
        return (self.successful_conversions / self.total_statements) * 100
    
    def to_dict(self):
        """
        Convert metrics to a dictionary for easy serialization.
        
        Returns:
            dict: Dictionary containing all metrics
        """
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
    Main SQL conversion engine that transforms Tableau SQL to Fabric SQL.
    
    Uses sqlparse for SQL tokenization and applies mappings with regex fallback
    for patterns that sqlparse doesn't handle well.
    """
    
    def __init__(self):
        """Initialize the SQL converter with mappings and patterns."""
        self.mappings = TableauFabricMappings()
        self.metrics = ConversionMetrics()
        
        # Regex patterns for special cases
        self.patterns = {
            # IF(condition, true_value, false_value) -> IIF(condition, true_value, false_value)
            'if_function': re.compile(r'\bIF\s*\(', re.IGNORECASE),
            
            # IFNULL(expr, alt) -> ISNULL(expr, alt)
            'ifnull_function': re.compile(r'\bIFNULL\s*\(', re.IGNORECASE),
            
            # CONTAINS(string, substring) -> CHARINDEX(substring, string) > 0
            'contains_function': re.compile(r'\bCONTAINS\s*\((.*?),\s*(.*?)\)', re.IGNORECASE),
            
            # Tableau boolean literals
            'true_literal': re.compile(r'\bTRUE\b', re.IGNORECASE),
            'false_literal': re.compile(r'\bFALSE\b', re.IGNORECASE),
            
            # Tableau comment style //
            'tableau_comment': re.compile(r'//'),
            
            # Functions that require manual rewrite
            'startswith_function': re.compile(r'\bSTARTSWITH\s*\(', re.IGNORECASE),
            'endswith_function': re.compile(r'\bENDSWITH\s*\(', re.IGNORECASE),
        }
        # LOD expressions
        self.lod_pattern = re.compile(r'\{\s*(FIXED|INCLUDE|EXCLUDE)\b', re.IGNORECASE)
        
        # Function category mappings for metrics
        self.function_categories = {
            'DATE': ['DATEADD', 'DATEDIFF', 'DATEPART', 'NOW', 'TODAY', 'YEAR', 'MONTH', 'DAY', 
                    'MAKEDATE', 'MAKEDATETIME', 'DATENAME'],
            'STRING': ['LEN', 'LENGTH', 'SUBSTR', 'CONTAINS', 'LEFT', 'RIGHT', 'TRIM', 
                      'UPPER', 'LOWER', 'REPLACE', 'SPLIT', 'FIND', 'STARTSWITH', 'ENDSWITH'],
            'AGGREGATE': ['SUM', 'AVG', 'COUNT', 'MIN', 'MAX', 'STDEV', 'STDEVP', 
                         'VAR', 'VARP', 'MEDIAN'],
            'LOGICAL': ['IF', 'IFNULL', 'ISNULL', 'ZN'],
            'MATHEMATICAL': ['ABS', 'ROUND', 'CEILING', 'FLOOR', 'SQRT', 'POWER', 'EXP', 'LN', 'LOG']
        }
    
    def convert_query(self, tableau_query):
        """
        Convert a Tableau SQL query to Fabric SQL.
        
        This is the main entry point for conversion. It applies both sqlparse-based
        conversion and regex-based fallbacks for special cases.
        
        Args:
            tableau_query (str): The Tableau SQL query to convert
            
        Returns:
            tuple: (converted_query: str, metrics: ConversionMetrics, flagged_items: list)
        """
        if not tableau_query or not isinstance(tableau_query, str):
            return "", self.metrics, []
        
        # Reset metrics for this conversion
        self.metrics = ConversionMetrics()
        self.metrics.total_statements = 1
        
        try:
            # Step 1: Apply regex-based preprocessing for special patterns
            preprocessed = self._preprocess_with_regex(tableau_query)
            
            # Step 2: Parse SQL using sqlparse
            parsed = sqlparse.parse(preprocessed)
            
            if not parsed:
                self.metrics.add_flagged_statement(0, "Unable to parse SQL")
                return tableau_query, self.metrics, [(0, "Unable to parse SQL")]
            
            # Step 3: Convert each statement
            converted_statements = []
            for stmt in parsed:
                converted_stmt = self._convert_statement(stmt)
                converted_statements.append(str(converted_stmt))
            
            # Step 4: Join statements
            fabric_query = '\n'.join(converted_statements)
            
            # Step 5: Apply post-processing cleanup
            fabric_query = self._postprocess_query(fabric_query)

            # Step 5.5: Attach accurate line numbers to flagged items
            self._attach_flag_line_numbers(tableau_query)
            
            # Update metrics - mark as successful only if no flags
            if not self.metrics.flagged_lines and not self.metrics.unsupported_functions:
                self.metrics.add_successful_conversion()
            
            return fabric_query, self.metrics, self.metrics.flagged_lines
            
        except Exception as e:
            # If conversion fails, flag for user review
            error_msg = f"Conversion error: {str(e)}"
            self.metrics.add_flagged_statement(0, error_msg)
            return tableau_query, self.metrics, [(0, error_msg)]
    
    def _preprocess_with_regex(self, query):
        """
        Preprocess the query using regex for patterns sqlparse might not handle well.
        
        Args:
            query (str): Original query
            
        Returns:
            str: Preprocessed query
        """
        # Replace Tableau IF with IIF
        query = self.patterns['if_function'].sub('IIF(', query)
        
        # Replace IFNULL with ISNULL
        query = self.patterns['ifnull_function'].sub('ISNULL(', query)
        
        # Replace TRUE/FALSE literals
        query = self.patterns['true_literal'].sub('1', query)
        query = self.patterns['false_literal'].sub('0', query)
        
        # Replace Tableau-style comments
        query = self.patterns['tableau_comment'].sub('--', query)
        
        # Apply additional function conversions via regex for common functions
        # Track conversions BEFORE replacing for metrics
        original_upper = query.upper()
        
        # NOW() -> GETDATE()
        if re.search(r'\bNOW\s*\(', query, re.IGNORECASE):
            query = re.sub(r'\bNOW\s*\(', 'GETDATE(', query, flags=re.IGNORECASE)
            self.metrics.add_function_conversion('DATE')
        
        # SUBSTR -> SUBSTRING
        if re.search(r'\bSUBSTR\s*\(', query, re.IGNORECASE):
            query = re.sub(r'\bSUBSTR\s*\(', 'SUBSTRING(', query, flags=re.IGNORECASE)
            self.metrics.add_function_conversion('STRING')
        
        # LENGTH -> LEN
        if re.search(r'\bLENGTH\s*\(', query, re.IGNORECASE):
            query = re.sub(r'\bLENGTH\s*\(', 'LEN(', query, flags=re.IGNORECASE)
            self.metrics.add_function_conversion('STRING')
        
        # MAKEDATE -> DATEFROMPARTS
        if re.search(r'\bMAKEDATE\s*\(', query, re.IGNORECASE):
            query = re.sub(r'\bMAKEDATE\s*\(', 'DATEFROMPARTS(', query, flags=re.IGNORECASE)
            self.metrics.add_function_conversion('DATE')
        
        # MAKEDATETIME -> DATETIMEFROMPARTS
        if re.search(r'\bMAKEDATETIME\s*\(', query, re.IGNORECASE):
            query = re.sub(r'\bMAKEDATETIME\s*\(', 'DATETIMEFROMPARTS(', query, flags=re.IGNORECASE)
            self.metrics.add_function_conversion('DATE')
        
        # ZN -> ISNULL
        if re.search(r'\bZN\s*\(', query, re.IGNORECASE):
            query = re.sub(r'\bZN\s*\(', 'ISNULL(', query, flags=re.IGNORECASE)
            self.metrics.add_function_conversion('LOGICAL')
        
        # LN -> LOG
        if re.search(r'\bLN\s*\(', query, re.IGNORECASE):
            query = re.sub(r'\bLN\s*\(', 'LOG(', query, flags=re.IGNORECASE)
            self.metrics.add_function_conversion('MATHEMATICAL')

        # Normalize Tableau field brackets: [field] -> field
        query = re.sub(r'\[([^\]]+)\]', r'\1', query)

        # INT(x) -> CAST(x AS INT)
        try:
            query, _ = re.subn(r'\bINT\s*\(\s*([^\)]+?)\s*\)', r'CAST(\1 AS INT)', query, flags=re.IGNORECASE)
        except re.error:
            pass

        # STR(x) -> CAST(x AS VARCHAR(20))  (default width 20)
        try:
            query, _ = re.subn(r'\bSTR\s*\(\s*([^\)]+?)\s*\)', r'CAST(\1 AS VARCHAR(20))', query, flags=re.IGNORECASE)
        except re.error:
            pass

        # SPLIT(str, 'delim', 1) -> first token: SUBSTRING(str, 1, CHARINDEX('delim', str) - 1)
        # Only handle the common case index=1 to match expected output
        def _replace_split(m):
            s = m.group(1).strip()
            delim = m.group(2)
            idx = m.group(3)
            if idx.strip() == '1':
                return f"SUBSTRING({s}, 1, CHARINDEX('{delim}', {s}) - 1)"
            # leave others for manual review
            self.metrics.add_flagged_statement(0, 'SPLIT with index != 1 requires manual rewrite')
            return m.group(0)
        try:
            query = re.sub(r"\bSPLIT\s*\(\s*([^,]+?)\s*,\s*'([^']*)'\s*,\s*(\d+)\s*\)", _replace_split, query, flags=re.IGNORECASE)
        except re.error:
            pass

        # STARTSWITH / ENDSWITH → manual review
        if self.patterns['startswith_function'].search(query):
            self.metrics.add_flagged_statement(0, 'STARTSWITH requires manual rewrite (use CHARINDEX(...) = 1 or LIKE)')
            self.metrics.add_function_conversion('STRING')
        if self.patterns['endswith_function'].search(query):
            self.metrics.add_flagged_statement(0, 'ENDSWITH requires manual rewrite (use RIGHT(...) or LIKE %suffix)')
            self.metrics.add_function_conversion('STRING')

        # CONTAINS → manual review (varied semantics)
        if re.search(r'\bCONTAINS\s*\(', query, re.IGNORECASE):
            self.metrics.add_flagged_statement(0, 'CONTAINS requires manual review (consider CHARINDEX(...) > 0)')
            self.metrics.add_function_conversion('STRING')

        # LOD expressions {FIXED|INCLUDE|EXCLUDE ...}
        if self.lod_pattern.search(query):
            self.metrics.add_flagged_statement(0, 'LOD expression {FIXED/INCLUDE/EXCLUDE} not supported')
        
        return query
    
    def _convert_statement(self, statement):
        """
        Convert a single SQL statement using sqlparse tokens.
        
        Args:
            statement (sqlparse.sql.Statement): Parsed SQL statement
            
        Returns:
            SQLFragment: Converted statement as a SQL fragment
        """
        # First, scan the statement for function names to detect unsupported ones
        self._scan_for_functions(statement)
        
        converted_tokens = []
        
        for token in statement.tokens:
            converted_token = self._convert_token(token)
            converted_tokens.append(converted_token)
        
        # Combine all fragments using operator overloading
        if converted_tokens:
            result = converted_tokens[0]
            for token in converted_tokens[1:]:
                result = result + token
            return result
        
        return SQLFragment("", True)
    
    def _scan_for_functions(self, token):
        """
        Recursively scan tokens for function names to detect unsupported functions.
        
        Args:
            token: SQL token to scan
        """
        if isinstance(token, Function):
            func_name = token.get_name()
            if func_name:
                func_name_upper = func_name.upper()
                # Check if it's an unsupported function
                allowed_fabric = {
                    'IIF','GETDATE','DATEFROMPARTS','DATETIMEFROMPARTS','LEN','SUBSTRING',
                    'CHARINDEX','LOG','LOG10','ISNULL','TRIM','LTRIM','RTRIM','YEAR','MONTH','DAY',
                    'SUM','AVG','COUNT','MIN','MAX','STDEV','STDEVP','VAR','VARP'
                }
                if (not self.mappings.is_mapped_function(func_name)) and (func_name_upper not in allowed_fabric):
                    self.metrics.add_unsupported_function(func_name)
                    self.metrics.add_flagged_statement(0, f"{func_name} function not supported")
                # Explicit, known Tableau-only/table calc/window-like names
                tableau_only = {
                    'WINDOW_AVG','RUNNING_SUM','RUNNING_AVG','INDEX','FIRST','LAST',
                    'LOOKUP','PREVIOUS_VALUE','FINDNTH','REGEXP_EXTRACT','PERCENTILE',
                }
                if func_name_upper in tableau_only:
                    self.metrics.add_unsupported_function(func_name_upper)
                    self.metrics.add_flagged_statement(0, f"{func_name_upper} function not supported")
        
        # Recursively check child tokens
        if hasattr(token, 'tokens'):
            for child_token in token.tokens:
                self._scan_for_functions(child_token)

    def _attach_flag_line_numbers(self, original_query):
        """
        Derive line numbers for flagged/unsupported items by scanning the
        original (cleaned) query for occurrences of problem functions.
        
        This supplements flags added during parsing that may not include
        line numbers (e.g., set to 0).
        """
        if not original_query:
            return
        lines = original_query.split("\n")

        derived_flags = []

        # Unsupported functions → mark lines where they appear
        for func in sorted(self.metrics.unsupported_functions):
            try:
                pattern = re.compile(r"\b" + re.escape(func) + r"\s*\(", re.IGNORECASE)
                for idx, line in enumerate(lines, start=1):
                    if pattern.search(line):
                        derived_flags.append((idx, f"{func} function not supported"))
            except Exception:
                # Best effort only
                pass

        # Functions we explicitly flagged via special handling but without line info
        special_to_reason = {
            'MEDIAN': 'MEDIAN function requires manual review',
            'STR': 'STR conversion requires manual review',
            'INT': 'INT conversion requires manual review',
            'FLOAT': 'FLOAT conversion requires manual review',
            'DATE': 'DATE conversion requires manual review',
        }
        for func, reason in special_to_reason.items():
            pattern = re.compile(r"\b" + func + r"\s*\(", re.IGNORECASE)
            # Only add if reason already recorded or function exists in text
            if any(reason in r for _, r in self.metrics.flagged_lines) or pattern.search(original_query):
                for idx, line in enumerate(lines, start=1):
                    if pattern.search(line):
                        derived_flags.append((idx, reason))

        # Merge with existing flags (replace 0-line entries with derived ones)
        existing_nonzero = [(ln, rsn) for ln, rsn in self.metrics.flagged_lines if ln and ln > 0]

        # Deduplicate while preserving reasons per line
        seen = set()
        merged = []
        for item in existing_nonzero + derived_flags:
            key = (item[0], item[1])
            if key not in seen:
                seen.add(key)
                merged.append(item)

        self.metrics.flagged_lines = merged
    
    def _convert_token(self, token):
        """
        Convert a single SQL token recursively.
        
        Args:
            token (sqlparse.sql.Token): Token to convert
            
        Returns:
            SQLFragment: Converted token as a SQL fragment
        """
        # Handle Function tokens (this is where most conversions happen)
        if isinstance(token, Function):
            return self._convert_function(token)
        
        # Handle Identifier tokens
        elif isinstance(token, Identifier):
            return SQLFragment(str(token), True, str(token))
        
        # Handle Parenthesis (recursive)
        elif isinstance(token, Parenthesis):
            return self._convert_parenthesis(token)
        
        # Handle regular tokens (keywords, literals, etc.)
        else:
            return SQLFragment(str(token), True, str(token))
    
    def _convert_function(self, func_token):
        """
        Convert a SQL function from Tableau to Fabric syntax.
        
        Args:
            func_token (sqlparse.sql.Function): Function token to convert
            
        Returns:
            SQLFragment: Converted function as a SQL fragment
        """
        # Get the function name
        func_name = func_token.get_name()
        
        if not func_name:
            return SQLFragment(str(func_token), True, str(func_token))
        
        func_name_upper = func_name.upper()
        
        # Check if we have a mapping for this function
        if self.mappings.is_mapped_function(func_name):
            fabric_func = self.mappings.get_fabric_function(func_name)
            
            # Record the conversion in metrics
            category = self._get_function_category(func_name_upper)
            self.metrics.add_function_conversion(category)
            
            # For functions requiring special handling, use custom conversion
            if self.mappings.requires_special_handling(func_name):
                return self._convert_special_function(func_token, func_name_upper, fabric_func)
            
            # For simple mappings, replace the function name (case-insensitive)
            original_str = str(func_token)
            # Use regex for case-insensitive replacement
            import re
            pattern = re.compile(re.escape(func_name), re.IGNORECASE)
            converted_str = pattern.sub(fabric_func, original_str, count=1)
            return SQLFragment(converted_str, True, original_str)
        
        else:
            # Function not in our mappings - flag for user review
            self.metrics.add_unsupported_function(func_name)
            # Return original, mark as not converted
            return SQLFragment(str(func_token), False, str(func_token))
    
    def _convert_special_function(self, func_token, func_name, fabric_func):
        """
        Handle functions that require special parameter or syntax conversion.
        
        Args:
            func_token: The function token
            func_name (str): Tableau function name (uppercase)
            fabric_func (str): Fabric function name
            
        Returns:
            SQLFragment: Converted function
        """
        original_str = str(func_token)
        
        # Handle specific special cases
        if func_name == 'MEDIAN':
            # MEDIAN(column) -> PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY column)
            # This is complex, so we flag it for now
            self.metrics.add_flagged_statement(0, f"MEDIAN function requires manual review")
            return SQLFragment(original_str, False, original_str)
        
        elif func_name == 'TODAY':
            # TODAY() -> CAST(GETDATE() AS DATE)
            return SQLFragment(fabric_func, True, original_str)
        
        elif func_name in ['STR', 'INT', 'FLOAT', 'DATE']:
            # These need CAST syntax: STR(value) -> CAST(value AS VARCHAR)
            # For now, flag for manual review as we need to extract parameters
            self.metrics.add_flagged_statement(0, f"{func_name} conversion requires manual review")
            return SQLFragment(original_str, False, original_str)
        
        else:
            # Default: simple replacement
            converted_str = original_str.replace(func_name, fabric_func, 1)
            return SQLFragment(converted_str, True, original_str)
    
    def _convert_parenthesis(self, paren_token):
        """
        Convert contents within parentheses recursively.
        
        Args:
            paren_token (sqlparse.sql.Parenthesis): Parenthesis token
            
        Returns:
            SQLFragment: Converted parenthesis content
        """
        # Process tokens inside parentheses
        inner_fragments = []
        for token in paren_token.tokens:
            converted = self._convert_token(token)
            inner_fragments.append(converted)
        
        # Combine inner fragments
        if inner_fragments:
            result = inner_fragments[0]
            for frag in inner_fragments[1:]:
                result = result + frag
            return result
        
        return SQLFragment(str(paren_token), True, str(paren_token))
    
    def _get_function_category(self, func_name):
        """
        Determine the category of a function for metrics tracking.
        
        Args:
            func_name (str): Function name (uppercase)
            
        Returns:
            str: Function category (DATE, STRING, AGGREGATE, LOGICAL, MATHEMATICAL, OTHER)
        """
        for category, functions in self.function_categories.items():
            if func_name in functions:
                return category
        return 'OTHER'
    
    def _postprocess_query(self, query):
        """
        Apply final cleanup and formatting to the converted query.
        
        Args:
            query (str): Converted query
            
        Returns:
            str: Cleaned and formatted query
        """
        # Format the SQL for readability
        formatted = sqlparse.format(
            query,
            reindent=True,
            keyword_case='upper',
            indent_width=4
        )
        
        return formatted
    
    def get_metrics(self):
        """
        Get the current conversion metrics.
        
        Returns:
            ConversionMetrics: Current metrics object
        """
        return self.metrics
    
    def reset_metrics(self):
        """Reset the metrics for a new conversion session."""
        self.metrics = ConversionMetrics()

