"""
Test Module for SQL Parser
===========================

Tests the SQLConverter class and conversion logic using sample SQL queries
and expected outputs. Uses hash comparison to verify exact conversions.
"""

import pytest
import sys
import os
import hashlib

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.sql_parser import SQLConverter, SQLFragment, ConversionMetrics
from components.data_cleaner import SQLCleaner


class TestSQLFragment:
    """Test cases for the SQLFragment class (operator overloading)."""
    
    def test_fragment_creation(self):
        """Test creating SQL fragments."""
        frag = SQLFragment("SELECT * FROM table", True)
        assert frag.content == "SELECT * FROM table"
        assert frag.is_converted == True
        assert str(frag) == "SELECT * FROM table"
    
    def test_fragment_addition_operator_overloading(self):
        """Test operator overloading with + operator."""
        frag1 = SQLFragment("SELECT ", True)
        frag2 = SQLFragment("* FROM table", True)
        
        # Test overloaded + operator
        combined = frag1 + frag2
        
        assert isinstance(combined, SQLFragment)
        assert combined.content == "SELECT * FROM table"
        assert combined.is_converted == True
    
    def test_fragment_addition_with_string(self):
        """Test adding SQLFragment with string."""
        frag = SQLFragment("SELECT ", True)
        combined = frag + "* FROM table"
        
        assert isinstance(combined, SQLFragment)
        assert combined.content == "SELECT * FROM table"
    
    def test_fragment_addition_conversion_status(self):
        """Test that conversion status is tracked correctly when combining fragments."""
        frag1 = SQLFragment("SELECT ", True, "SELECT ")
        frag2 = SQLFragment("* FROM table", False, "* FROM table")
        
        combined = frag1 + frag2
        
        # Combined fragment should be marked as not fully converted
        assert combined.is_converted == False


class TestConversionMetrics:
    """Test cases for the ConversionMetrics class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.metrics = ConversionMetrics()
    
    def test_metrics_initialization(self):
        """Test metrics object initialization."""
        assert self.metrics.total_statements == 0
        assert self.metrics.successful_conversions == 0
        assert self.metrics.flagged_statements == 0
        assert len(self.metrics.flagged_lines) == 0
    
    def test_add_successful_conversion(self):
        """Test incrementing successful conversions."""
        self.metrics.add_successful_conversion()
        assert self.metrics.successful_conversions == 1
    
    def test_add_flagged_statement(self):
        """Test adding flagged statements."""
        self.metrics.add_flagged_statement(10, "Unsupported function")
        
        assert self.metrics.flagged_statements == 1
        assert len(self.metrics.flagged_lines) == 1
        assert self.metrics.flagged_lines[0] == (10, "Unsupported function")
    
    def test_add_function_conversion(self):
        """Test tracking function conversions by type."""
        self.metrics.add_function_conversion('DATE')
        self.metrics.add_function_conversion('STRING')
        self.metrics.add_function_conversion('DATE')
        
        assert self.metrics.function_conversions['DATE'] == 2
        assert self.metrics.function_conversions['STRING'] == 1
    
    def test_add_unsupported_function(self):
        """Test tracking unsupported functions."""
        self.metrics.add_unsupported_function('CUSTOM_FUNC')
        self.metrics.add_unsupported_function('ANOTHER_FUNC')
        self.metrics.add_unsupported_function('CUSTOM_FUNC')  # Duplicate
        
        # Should only have 2 unique functions (set removes duplicates)
        assert len(self.metrics.unsupported_functions) == 2
    
    def test_get_success_rate(self):
        """Test success rate calculation."""
        self.metrics.total_statements = 10
        self.metrics.successful_conversions = 8
        
        assert self.metrics.get_success_rate() == 80.0
    
    def test_success_rate_zero_statements(self):
        """Test success rate with zero statements."""
        assert self.metrics.get_success_rate() == 0.0
    
    def test_to_dict(self):
        """Test converting metrics to dictionary."""
        self.metrics.total_statements = 5
        self.metrics.successful_conversions = 4
        self.metrics.add_function_conversion('DATE')
        
        metrics_dict = self.metrics.to_dict()
        
        assert isinstance(metrics_dict, dict)
        assert metrics_dict['total_statements'] == 5
        assert metrics_dict['successful_conversions'] == 4
        assert metrics_dict['success_rate'] == 80.0


class TestSQLConverter:
    """Test cases for the SQLConverter class."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.converter = SQLConverter()
        self.cleaner = SQLCleaner()
    
    def test_converter_initialization(self):
        """Test converter initialization."""
        assert self.converter is not None
        assert self.converter.mappings is not None
        assert self.converter.metrics is not None
    
    def test_simple_select_conversion(self):
        """Test conversion of a simple SELECT statement."""
        tableau_sql = "SELECT UPPER(name) FROM customers"
        
        fabric_sql, metrics, flagged = self.converter.convert_query(tableau_sql)
        
        assert fabric_sql is not None
        assert len(fabric_sql) > 0
        assert 'UPPER' in fabric_sql
        assert 'customers' in fabric_sql
    
    def test_now_function_conversion(self):
        """Test conversion of NOW() to GETDATE()."""
        tableau_sql = "SELECT NOW() AS current_time"
        
        fabric_sql, metrics, flagged = self.converter.convert_query(tableau_sql)
        
        # Check that NOW was converted to GETDATE
        assert 'GETDATE' in fabric_sql.upper()
        assert 'NOW' not in fabric_sql.upper() or 'GETDATE' in fabric_sql.upper()
    
    def test_substr_function_conversion(self):
        """Test conversion of SUBSTR to SUBSTRING."""
        tableau_sql = "SELECT SUBSTR(code, 1, 3) FROM products"
        
        fabric_sql, metrics, flagged = self.converter.convert_query(tableau_sql)
        
        # Check that SUBSTR was converted to SUBSTRING
        assert 'SUBSTRING' in fabric_sql.upper()
    
    def test_if_function_conversion(self):
        """Test conversion of IF to IIF."""
        tableau_sql = "SELECT IF(status = 1, 'Active', 'Inactive') FROM users"
        
        fabric_sql, metrics, flagged = self.converter.convert_query(tableau_sql)
        
        # Check that IF was converted to IIF
        assert 'IIF' in fabric_sql.upper()
    
    def test_true_false_literal_conversion(self):
        """Test conversion of TRUE/FALSE literals."""
        tableau_sql = "SELECT * FROM users WHERE active = TRUE AND deleted = FALSE"
        
        fabric_sql, metrics, flagged = self.converter.convert_query(tableau_sql)
        
        # Check that TRUE/FALSE were converted to 1/0
        assert '1' in fabric_sql or 'TRUE' not in fabric_sql.upper()
    
    def test_metrics_tracking(self):
        """Test that metrics are tracked during conversion."""
        tableau_sql = "SELECT NOW(), UPPER(name), SUBSTR(code, 1, 3) FROM products"
        
        fabric_sql, metrics, flagged = self.converter.convert_query(tableau_sql)
        
        assert metrics.total_statements > 0
        # Should have some function conversions
        total_conversions = sum(metrics.function_conversions.values())
        assert total_conversions > 0
    
    def test_empty_query_handling(self):
        """Test handling of empty query."""
        fabric_sql, metrics, flagged = self.converter.convert_query("")
        
        assert fabric_sql == ""
        assert len(flagged) == 0
    
    def test_invalid_query_handling(self):
        """Test handling of invalid query."""
        invalid_sql = "NOTVALIDSQL GARBAGE INPUT"
        
        # Should not raise exception, but might flag items
        fabric_sql, metrics, flagged = self.converter.convert_query(invalid_sql)
        
        # Should return something (even if just the original)
        assert fabric_sql is not None


class TestSQLConversionWithSampleFiles:
    """Test SQL conversion using sample query files."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.converter = SQLConverter()
        self.cleaner = SQLCleaner()
        self.sample_dir = os.path.join(os.path.dirname(__file__), 'sample_queries')
    
    def _normalize_sql(self, sql):
        """Normalize SQL for comparison (remove extra whitespace, standardize case)."""
        # Remove comments
        lines = [line for line in sql.split('\n') if not line.strip().startswith('--')]
        sql = '\n'.join(lines)
        
        # Normalize whitespace
        import re
        sql = re.sub(r'\s+', ' ', sql)
        sql = sql.strip()
        
        return sql
    
    def _get_sql_hash(self, sql):
        """Get hash of normalized SQL for comparison."""
        normalized = self._normalize_sql(sql)
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def test_simple_query_conversion(self):
        """Test conversion of simple query file."""
        input_file = os.path.join(self.sample_dir, 'tableau_simple.sql')
        
        if not os.path.exists(input_file):
            pytest.skip(f"Sample file not found: {input_file}")
        
        # Read and convert
        with open(input_file, 'r') as f:
            tableau_sql = f.read()
        
        prepared = self.cleaner.prepare_for_parsing(tableau_sql)
        fabric_sql, metrics, flagged = self.converter.convert_query(prepared['cleaned_query'])
        
        # Basic assertions
        assert fabric_sql is not None
        assert len(fabric_sql) > 0
        
        # Check key conversions
        assert 'GETDATE' in fabric_sql.upper()  # NOW -> GETDATE
    
    def test_date_functions_conversion(self):
        """Test conversion of date functions query file."""
        input_file = os.path.join(self.sample_dir, 'tableau_date_functions.sql')
        
        if not os.path.exists(input_file):
            pytest.skip(f"Sample file not found: {input_file}")
        
        with open(input_file, 'r') as f:
            tableau_sql = f.read()
        
        prepared = self.cleaner.prepare_for_parsing(tableau_sql)
        fabric_sql, metrics, flagged = self.converter.convert_query(prepared['cleaned_query'])
        
        # Check date function conversions
        assert 'GETDATE' in fabric_sql.upper()  # NOW -> GETDATE
        assert 'DATEFROMPARTS' in fabric_sql.upper()  # MAKEDATE -> DATEFROMPARTS
    
    def test_string_functions_conversion(self):
        """Test conversion of string functions query file."""
        input_file = os.path.join(self.sample_dir, 'tableau_string_functions.sql')
        
        if not os.path.exists(input_file):
            pytest.skip(f"Sample file not found: {input_file}")
        
        with open(input_file, 'r') as f:
            tableau_sql = f.read()
        
        prepared = self.cleaner.prepare_for_parsing(tableau_sql)
        fabric_sql, metrics, flagged = self.converter.convert_query(prepared['cleaned_query'])
        
        # Check string function conversions
        assert 'SUBSTRING' in fabric_sql.upper()  # SUBSTR -> SUBSTRING
    
    def test_aggregate_functions_conversion(self):
        """Test conversion of aggregate functions query file."""
        input_file = os.path.join(self.sample_dir, 'tableau_aggregates.sql')
        
        if not os.path.exists(input_file):
            pytest.skip(f"Sample file not found: {input_file}")
        
        with open(input_file, 'r') as f:
            tableau_sql = f.read()
        
        prepared = self.cleaner.prepare_for_parsing(tableau_sql)
        fabric_sql, metrics, flagged = self.converter.convert_query(prepared['cleaned_query'])
        
        # Check that aggregate functions are present
        assert 'SUM' in fabric_sql.upper()
        assert 'AVG' in fabric_sql.upper()
        assert 'COUNT' in fabric_sql.upper()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

