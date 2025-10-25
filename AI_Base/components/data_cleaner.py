"""
Data Cleaner Module
===================

This module uses pandas to clean and normalize SQL input data before processing.
It handles whitespace, tabs, line endings, and other inconsistencies that might
interfere with SQL parsing and conversion.
"""

import pandas as pd
import re


class SQLCleaner:
    """
    A class for cleaning and normalizing SQL query strings using pandas Series operations.
    
    This class leverages pandas string methods (mapping functions) to efficiently
    clean and standardize SQL input, making it ready for parsing and conversion.
    """
    
    def __init__(self):
        """Initialize the SQLCleaner with default cleaning configurations."""
        # Regex patterns for cleaning
        self.whitespace_pattern = re.compile(r'\s+')
        self.comment_pattern = re.compile(r'--.*$', re.MULTILINE)
        self.multiline_comment_pattern = re.compile(r'/\*.*?\*/', re.DOTALL)
        
    def clean_query(self, query):
        """
        Clean a single SQL query string.
        
        This method normalizes whitespace, standardizes line endings, and removes
        unnecessary characters while preserving SQL structure.
        
        Args:
            query (str): The raw SQL query string to clean
            
        Returns:
            str: The cleaned SQL query string
        """
        if not query or not isinstance(query, str):
            return ""
        
        # Step 1: Remove carriage returns and standardize line endings
        cleaned = query.replace('\r\n', '\n').replace('\r', '\n')
        
        # Step 2: Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Step 3: Normalize multiple spaces/tabs to single space, but preserve indentation
        lines = cleaned.split('\n')
        normalized_lines = []
        for line in lines:
            # Collapse multiple spaces/tabs to single space, but keep the line's leading indentation
            normalized = self.whitespace_pattern.sub(' ', line)
            normalized_lines.append(normalized)
        cleaned = '\n'.join(normalized_lines)
        
        # Step 4: Remove empty lines
        lines = [line for line in cleaned.split('\n') if line.strip()]
        cleaned = '\n'.join(lines)
        
        return cleaned
    
    def clean_query_batch(self, queries):
        """
        Clean multiple SQL queries using pandas Series for efficient processing.
        
        This method demonstrates the use of pandas mapping functions to process
        multiple queries efficiently.
        
        Args:
            queries (list): List of SQL query strings
            
        Returns:
            list: List of cleaned SQL query strings
        """
        if not queries:
            return []
        
        # Convert to pandas Series for efficient string operations
        query_series = pd.Series(queries)
        
        # Use pandas string methods (mapping) to clean efficiently
        # Step 1: Replace carriage returns
        query_series = query_series.str.replace('\r\n', '\n', regex=False)
        query_series = query_series.str.replace('\r', '\n', regex=False)
        
        # Step 2: Strip whitespace
        query_series = query_series.str.strip()
        
        # Step 3: Apply custom cleaning function using map
        query_series = query_series.map(self._normalize_whitespace)
        
        # Step 4: Remove None values and empty strings
        query_series = query_series.fillna('')
        
        return query_series.tolist()
    
    def _normalize_whitespace(self, text):
        """
        Internal helper to normalize whitespace in a text string.
        
        Args:
            text (str): Text to normalize
            
        Returns:
            str: Text with normalized whitespace
        """
        if not isinstance(text, str):
            return ""
        
        lines = text.split('\n')
        lines = [self.whitespace_pattern.sub(' ', line.strip()) for line in lines]
        lines = [line for line in lines if line]
        return '\n'.join(lines)
    
    def extract_comments(self, query):
        """
        Extract SQL comments from a query for separate handling.
        
        Args:
            query (str): SQL query string
            
        Returns:
            tuple: (query_without_comments, list_of_comments)
        """
        if not query or not isinstance(query, str):
            return "", []
        
        comments = []
        
        # Extract multi-line comments /* ... */
        multiline_comments = self.multiline_comment_pattern.findall(query)
        comments.extend(multiline_comments)
        query_no_multiline = self.multiline_comment_pattern.sub('', query)
        
        # Extract single-line comments --
        single_line_comments = self.comment_pattern.findall(query_no_multiline)
        comments.extend(single_line_comments)
        query_no_comments = self.comment_pattern.sub('', query_no_multiline)
        
        return query_no_comments.strip(), comments
    
    def split_statements(self, query):
        """
        Split a multi-statement SQL script into individual statements.
        
        Args:
            query (str): SQL script potentially containing multiple statements
            
        Returns:
            list: List of individual SQL statements
        """
        if not query or not isinstance(query, str):
            return []
        
        # Remove comments first to avoid splitting on semicolons in comments
        query_no_comments, _ = self.extract_comments(query)
        
        # Split on semicolons
        statements = query_no_comments.split(';')
        
        # Clean and filter empty statements
        statements = [stmt.strip() for stmt in statements if stmt.strip()]
        
        return statements
    
    def validate_query_structure(self, query):
        """
        Perform basic validation on query structure.
        
        Args:
            query (str): SQL query to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        if not query or not isinstance(query, str):
            return False, "Query is empty or not a string"
        
        cleaned = query.strip()
        
        if not cleaned:
            return False, "Query is empty after cleaning"
        
        # Check for basic SQL keywords
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'WITH']
        has_keyword = any(keyword in cleaned.upper() for keyword in sql_keywords)
        
        if not has_keyword:
            return False, "Query does not contain recognized SQL keywords"
        
        # Check for balanced parentheses
        if cleaned.count('(') != cleaned.count(')'):
            return False, "Unbalanced parentheses in query"
        
        return True, None
    
    def prepare_for_parsing(self, query):
        """
        Prepare a query for parsing by applying all cleaning and validation steps.
        
        This is the main method to call before sending a query to the parser.
        
        Args:
            query (str): Raw SQL query
            
        Returns:
            dict: Dictionary containing:
                - 'cleaned_query': The cleaned query string
                - 'is_valid': Boolean indicating if query is valid
                - 'error': Error message if not valid
                - 'comments': Extracted comments
                - 'statements': List of individual statements if multi-statement
        """
        # Step 1: Clean the query
        cleaned = self.clean_query(query)
        
        # Step 2: Validate structure
        is_valid, error = self.validate_query_structure(cleaned)
        
        # Step 3: Extract comments
        query_no_comments, comments = self.extract_comments(cleaned)
        
        # Step 4: Split into statements
        statements = self.split_statements(query_no_comments)
        
        return {
            'cleaned_query': query_no_comments,
            'is_valid': is_valid,
            'error': error,
            'comments': comments,
            'statements': statements,
            'original_query': query
        }

