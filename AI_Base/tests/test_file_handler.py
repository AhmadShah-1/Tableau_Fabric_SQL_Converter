"""
Test Module for File Handler
=============================

Tests the FileHandler class and file I/O operations including generator functions.
"""

import pytest
import sys
import os
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.file_handler import FileHandler


class TestFileHandler:
    """Test cases for the FileHandler class."""
    
    def setup_method(self):
        """Setup test fixtures - create temporary directory."""
        self.handler = FileHandler()
        self.test_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.test_dir, 'test.sql')
    
    def teardown_method(self):
        """Cleanup test fixtures - remove temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_handler_initialization(self):
        """Test FileHandler initialization."""
        assert self.handler is not None
        assert self.handler.supported_extensions == ['.sql', '.txt']
        assert self.handler.encoding == 'utf-8'
    
    def test_write_and_read_file(self):
        """Test writing and reading a file."""
        content = "SELECT * FROM customers;"
        
        # Write file
        result = self.handler.write_file(self.test_file, content)
        assert result == True
        assert os.path.exists(self.test_file)
        
        # Read file
        read_content = self.handler.read_file(self.test_file)
        assert read_content == content
    
    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        nonexistent = os.path.join(self.test_dir, 'nonexistent.sql')
        
        with pytest.raises(FileNotFoundError):
            self.handler.read_file(nonexistent)
    
    def test_read_file_generator(self):
        """Test generator function for reading file line-by-line."""
        # Create test file with multiple lines
        content = "Line 1\nLine 2\nLine 3\n"
        self.handler.write_file(self.test_file, content)
        
        # Read using generator
        lines = list(self.handler.read_file_generator(self.test_file))
        
        assert len(lines) == 3
        assert lines[0] == (1, "Line 1")
        assert lines[1] == (2, "Line 2")
        assert lines[2] == (3, "Line 3")
    
    def test_generator_memory_efficiency(self):
        """Test that generator doesn't load entire file into memory."""
        # Create a larger test file
        large_content = "\n".join([f"Line {i}" for i in range(1000)])
        self.handler.write_file(self.test_file, large_content)
        
        # Use generator - should not raise memory error even for large files
        line_count = 0
        for line_num, line_content in self.handler.read_file_generator(self.test_file):
            line_count += 1
            # Process one line at a time
            assert line_content.startswith("Line")
        
        assert line_count == 1000
    
    def test_validate_file_valid(self):
        """Test validation of a valid SQL file."""
        # Create valid SQL file
        self.handler.write_file(self.test_file, "SELECT * FROM table;")
        
        is_valid, error = self.handler.validate_file(self.test_file)
        
        assert is_valid == True
        assert error is None
    
    def test_validate_file_nonexistent(self):
        """Test validation of nonexistent file."""
        nonexistent = os.path.join(self.test_dir, 'nonexistent.sql')
        
        is_valid, error = self.handler.validate_file(nonexistent)
        
        assert is_valid == False
        assert "does not exist" in error
    
    def test_validate_file_unsupported_extension(self):
        """Test validation of file with unsupported extension."""
        unsupported_file = os.path.join(self.test_dir, 'test.xyz')
        self.handler.write_file(unsupported_file, "content")
        
        is_valid, error = self.handler.validate_file(unsupported_file)
        
        assert is_valid == False
        assert "Unsupported file type" in error
    
    def test_validate_file_empty(self):
        """Test validation of empty file."""
        # Create empty file
        open(self.test_file, 'w').close()
        
        is_valid, error = self.handler.validate_file(self.test_file)
        
        assert is_valid == False
        assert "empty" in error.lower()
    
    def test_generate_output_filename(self):
        """Test generation of output filename."""
        input_path = "/path/to/tableau_query.sql"
        
        output_path = self.handler.generate_output_filename(input_path)
        
        assert "tableau_query_fabric.sql" in output_path
        assert output_path.endswith(".sql")
    
    def test_get_file_info(self):
        """Test getting file information."""
        content = "SELECT * FROM table;"
        self.handler.write_file(self.test_file, content)
        
        info = self.handler.get_file_info(self.test_file)
        
        assert info is not None
        assert info['filename'] == 'test.sql'
        assert info['size_bytes'] == len(content)
        assert info['extension'] == '.sql'
        assert 'modified_time' in info
    
    def test_get_file_info_nonexistent(self):
        """Test getting info for nonexistent file."""
        nonexistent = os.path.join(self.test_dir, 'nonexistent.sql')
        
        info = self.handler.get_file_info(nonexistent)
        
        assert info is None
    
    def test_count_lines(self):
        """Test counting lines in a file."""
        content = "Line 1\nLine 2\nLine 3\nLine 4\n"
        self.handler.write_file(self.test_file, content)
        
        count = self.handler.count_lines(self.test_file)
        
        assert count == 4
    
    def test_count_lines_empty_file(self):
        """Test counting lines in empty file."""
        open(self.test_file, 'w').close()
        
        count = self.handler.count_lines(self.test_file)
        
        assert count == 0
    
    def test_create_backup(self):
        """Test creating backup of a file."""
        content = "Original content"
        self.handler.write_file(self.test_file, content)
        
        backup_path = self.handler.create_backup(self.test_file)
        
        assert backup_path is not None
        assert os.path.exists(backup_path)
        assert 'backup' in backup_path
        
        # Verify backup content matches original
        backup_content = self.handler.read_file(backup_path)
        assert backup_content == content
    
    def test_create_backup_nonexistent(self):
        """Test creating backup of nonexistent file."""
        nonexistent = os.path.join(self.test_dir, 'nonexistent.sql')
        
        backup_path = self.handler.create_backup(nonexistent)
        
        assert backup_path is None
    
    def test_process_file_with_generator(self):
        """Test processing file with generator and processor function."""
        # Create test file
        content = "line1\nline2\nline3\n"
        self.handler.write_file(self.test_file, content)
        
        # Define processor function
        def uppercase_processor(line_num, line):
            return line.upper()
        
        # Process file
        processed_lines, errors = self.handler.process_file_with_generator(
            self.test_file, 
            uppercase_processor
        )
        
        assert len(processed_lines) == 3
        assert processed_lines[0] == "LINE1"
        assert processed_lines[1] == "LINE2"
        assert processed_lines[2] == "LINE3"
        assert len(errors) == 0
    
    def test_process_file_with_errors(self):
        """Test processing file with processor that raises errors."""
        # Create test file
        content = "line1\nline2\nline3\n"
        self.handler.write_file(self.test_file, content)
        
        # Define processor that fails on line 2
        def faulty_processor(line_num, line):
            if line_num == 2:
                raise ValueError("Error on line 2")
            return line.upper()
        
        # Process file
        processed_lines, errors = self.handler.process_file_with_generator(
            self.test_file,
            faulty_processor
        )
        
        # Should have 3 lines (error line kept as original)
        assert len(processed_lines) == 3
        # Should have 1 error
        assert len(errors) == 1
        assert errors[0][0] == 2  # Error on line 2
    
    def test_write_file_creates_directory(self):
        """Test that write_file creates directories if they don't exist."""
        nested_path = os.path.join(self.test_dir, 'subdir1', 'subdir2', 'test.sql')
        content = "SELECT * FROM table;"
        
        result = self.handler.write_file(nested_path, content)
        
        assert result == True
        assert os.path.exists(nested_path)
        
        # Verify content
        read_content = self.handler.read_file(nested_path)
        assert read_content == content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

