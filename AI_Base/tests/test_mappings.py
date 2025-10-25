"""
Test Module for SQL Mappings
=============================

Tests the TableauFabricMappings class to ensure all mappings are correct
and accessible.
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.sql_mappings import TableauFabricMappings


class TestTableauFabricMappings:
    """Test cases for the TableauFabricMappings class."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.mappings = TableauFabricMappings()
    
    def test_initialization(self):
        """Test that mappings object initializes correctly."""
        assert self.mappings is not None
        assert len(self.mappings.function_mappings) > 0
    
    def test_date_function_mappings(self):
        """Test that date functions are mapped correctly."""
        # Test NOW -> GETDATE
        assert self.mappings.get_fabric_function('NOW') == 'GETDATE'
        assert self.mappings.get_fabric_function('now') == 'GETDATE'  # Case insensitive
        
        # Test TODAY -> CAST(GETDATE() AS DATE)
        assert self.mappings.get_fabric_function('TODAY') == 'CAST(GETDATE() AS DATE)'
        
        # Test MAKEDATE -> DATEFROMPARTS
        assert self.mappings.get_fabric_function('MAKEDATE') == 'DATEFROMPARTS'
    
    def test_string_function_mappings(self):
        """Test that string functions are mapped correctly."""
        # Test LENGTH -> LEN
        assert self.mappings.get_fabric_function('LENGTH') == 'LEN'
        
        # Test SUBSTR -> SUBSTRING
        assert self.mappings.get_fabric_function('SUBSTR') == 'SUBSTRING'
        
        # Test CONTAINS -> CHARINDEX
        assert self.mappings.get_fabric_function('CONTAINS') == 'CHARINDEX'
        
        # Test FIND -> CHARINDEX
        assert self.mappings.get_fabric_function('FIND') == 'CHARINDEX'
    
    def test_aggregate_function_mappings(self):
        """Test that aggregate functions are mapped correctly."""
        # Test STDEV
        assert self.mappings.get_fabric_function('STDEV') == 'STDEV'
        
        # Test MEDIAN -> PERCENTILE_CONT
        assert self.mappings.get_fabric_function('MEDIAN') == 'PERCENTILE_CONT(0.5)'
    
    def test_logical_function_mappings(self):
        """Test that logical functions are mapped correctly."""
        # Test IF -> IIF
        assert self.mappings.get_fabric_function('IF') == 'IIF'
        
        # Test IFNULL -> ISNULL
        assert self.mappings.get_fabric_function('IFNULL') == 'ISNULL'
        
        # Test ZN -> ISNULL
        assert self.mappings.get_fabric_function('ZN') == 'ISNULL'
    
    def test_mathematical_function_mappings(self):
        """Test that mathematical functions are mapped correctly."""
        # Test LN -> LOG
        assert self.mappings.get_fabric_function('LN') == 'LOG'
        
        # Test LOG -> LOG10
        assert self.mappings.get_fabric_function('LOG') == 'LOG10'
        
        # Test functions that stay the same
        assert self.mappings.get_fabric_function('ROUND') == 'ROUND'
        assert self.mappings.get_fabric_function('SQRT') == 'SQRT'
    
    def test_case_insensitive_lookup(self):
        """Test that function lookups are case-insensitive."""
        # Test various case combinations
        assert self.mappings.get_fabric_function('NOW') == 'GETDATE'
        assert self.mappings.get_fabric_function('now') == 'GETDATE'
        assert self.mappings.get_fabric_function('Now') == 'GETDATE'
        assert self.mappings.get_fabric_function('nOw') == 'GETDATE'
    
    def test_is_mapped_function(self):
        """Test the is_mapped_function method."""
        # Test valid mappings
        assert self.mappings.is_mapped_function('NOW') == True
        assert self.mappings.is_mapped_function('SUBSTR') == True
        assert self.mappings.is_mapped_function('MEDIAN') == True
        
        # Test invalid/unmapped functions
        assert self.mappings.is_mapped_function('NOTAREALFUNCTION') == False
        assert self.mappings.is_mapped_function('XYZABC') == False
    
    def test_requires_special_handling(self):
        """Test identification of functions requiring special handling."""
        # Functions that need special handling
        assert self.mappings.requires_special_handling('MEDIAN') == True
        assert self.mappings.requires_special_handling('TODAY') == True
        assert self.mappings.requires_special_handling('IF') == True
        
        # Functions that don't need special handling
        assert self.mappings.requires_special_handling('SUM') == False
        assert self.mappings.requires_special_handling('UPPER') == False
    
    def test_get_all_tableau_functions(self):
        """Test retrieval of all Tableau functions."""
        all_functions = self.mappings.get_all_tableau_functions()
        
        assert isinstance(all_functions, list)
        assert len(all_functions) > 0
        assert 'NOW' in all_functions
        assert 'SUBSTR' in all_functions
        assert 'MEDIAN' in all_functions
    
    def test_get_mapping_statistics(self):
        """Test mapping statistics retrieval."""
        stats = self.mappings.get_mapping_statistics()
        
        assert isinstance(stats, dict)
        assert 'total_mappings' in stats
        assert 'date_functions' in stats
        assert 'string_functions' in stats
        assert 'aggregate_functions' in stats
        assert 'special_handling_count' in stats
        
        # Verify counts are reasonable
        assert stats['total_mappings'] > 0
        assert stats['date_functions'] > 0
        assert stats['string_functions'] > 0
        assert stats['aggregate_functions'] > 0
    
    def test_unmapped_function_returns_none(self):
        """Test that unmapped functions return None."""
        result = self.mappings.get_fabric_function('NONEXISTENT_FUNCTION')
        assert result is None
    
    def test_reverse_mappings(self):
        """Test that reverse mappings are created correctly."""
        assert len(self.mappings.reverse_mappings) > 0
        
        # Test a reverse lookup
        assert 'GETDATE' in self.mappings.reverse_mappings
        assert self.mappings.reverse_mappings['GETDATE'] == 'NOW'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

