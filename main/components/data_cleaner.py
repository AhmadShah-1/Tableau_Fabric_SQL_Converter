'''
Lightweight SQL cleaning utilities: normalize whitespace, strip comments, split statements,
and basic structural validation.
'''

import re


class SQLCleaner:
    def __init__(self):
        # Regex patterns for cleaning (Removing whitespace, comments, and multi line comments)
        self.whitespace_pattern = re.compile(r'\s+')  # Multiple spaces to single space
        self.comment_pattern = re.compile(r'--.*$', re.MULTILINE)  
        self.multiline_comment_pattern = re.compile(r'/\*.*?\*/', re.DOTALL)  # Multi line comments

    def clean_query(self, query):
        '''
        This function actually performs the cleaning of the query
        Args: query (str): Raw SQL Query
        Returns: str: Cleaned SQL Query
        '''

        if not query or not isinstance(query, str):
            return ""
        
        # Remove carriage returns and standardize line endings
        cleaned = query.replace('\r\n', '\n').replace('\r', '\n')
        
        # Strip leading/trailing whitespace
        cleaned = cleaned.strip()
        
        # Normalize internal whitespace (multiple spaces/tabs to single space)
        # But preserve newlines for readability
        lines = cleaned.split('\n')
        lines = [self.whitespace_pattern.sub(' ', line.strip()) for line in lines]
        cleaned = '\n'.join(lines)
        
        # Remove empty lines
        lines = [line for line in cleaned.split('\n') if line.strip()]
        cleaned = '\n'.join(lines)
        
        return cleaned
    
    def extract_comments(self, query):
        """
        Extracts SQL comments from a query for separate handling.
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
        Input: SQL script as a string
        Output: List of individual SQL statements
        """
        if not query or not isinstance(query, str):
            return []
        
        # Remove comments first to avoid splitting on semicolons in comments
        query_no_comments, _ = self.extract_comments(query)                         # Currently list of comments is not used but the data is
        
        # Split on semicolons
        statements = query_no_comments.split(';')
        
        # Clean and filter empty statements so lines with only whitespace are removed
        statements = [stmt.strip() for stmt in statements if stmt.strip()]  
        
        return statements

    
    def prepare_for_parsing(self, query):
        """
        Prepare a query for parsing by applying all cleaning and validation steps.
        Input: Raw SQL String query
        Output: Dictionary containing:
            - 'cleaned_query': The cleaned query string
            - 'comments': Extracted comments
            - 'statements': List of individual statements if multi-statement
            - 'original_query': The original query string
        """
        # Clean the query
        cleaned = self.clean_query(query)

        # Extract comments
        query_no_comments, comments = self.extract_comments(cleaned)
        
        # Split into statements
        statements = self.split_statements(query_no_comments)
        
        return {
            'cleaned_query': query_no_comments,
            'comments': comments,
            'statements': statements,
            'original_query': query
        }

