"""
File Handler Module
===================

This module handles file I/O operations for SQL conversion, including generator
functions for memory-efficient line-by-line reading and processing of large SQL files.
"""

import os
from pathlib import Path


class FileHandler:
    """
    Handles file operations for SQL conversion with memory-efficient processing.
    
    Uses generator functions to read files line-by-line without loading entire
    files into memory, which is essential for processing large SQL scripts.
    """
    
    def __init__(self):
        """Initialize the FileHandler."""
        self.supported_extensions = ['.sql', '.txt']
        self.encoding = 'utf-8'
    
    def read_file_generator(self, file_path):
        """
        Generator function to read a file line-by-line for memory efficiency.
        
        This generator yields one line at a time, allowing processing of large files
        without loading them entirely into memory.
        
        Args:
            file_path (str): Path to the file to read
            
        Yields:
            tuple: (line_number, line_content) for each line in the file
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as file:
                for line_number, line in enumerate(file, start=1):
                    yield line_number, line.rstrip('\n\r')
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    def read_file(self, file_path):
        """
        Read an entire file into memory.
        
        Use this for smaller files or when you need the entire content at once.
        
        Args:
            file_path (str): Path to the file to read
            
        Returns:
            str: Complete file contents
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            IOError: If there's an error reading the file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding=self.encoding, errors='replace') as file:
                return file.read()
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    def write_file(self, file_path, content):
        """
        Write content to a file, creating directories if needed.
        
        Args:
            file_path (str): Path where the file should be written
            content (str): Content to write to the file
            
        Returns:
            bool: True if write was successful
            
        Raises:
            IOError: If there's an error writing the file
        """
        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # Write the file
            with open(file_path, 'w', encoding=self.encoding) as file:
                file.write(content)
            
            return True
        except Exception as e:
            raise IOError(f"Error writing file {file_path}: {str(e)}")
    
    def validate_file(self, file_path):
        """
        Validate that a file exists and is a supported SQL file.
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            tuple: (is_valid: bool, error_message: str or None)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"File does not exist: {file_path}"
        
        # Check if it's a file (not a directory)
        if not os.path.isfile(file_path):
            return False, f"Path is not a file: {file_path}"
        
        # Check file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext not in self.supported_extensions:
            return False, f"Unsupported file type. Supported: {', '.join(self.supported_extensions)}"
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        # Check if file is empty
        if os.path.getsize(file_path) == 0:
            return False, "File is empty"
        
        return True, None
    
    def process_file_with_generator(self, input_path, processor_func):
        """
        Process a file line-by-line using a generator and a processing function.
        
        This method demonstrates the use of generator functions for efficient
        processing of large files. It detects erroneous lines and collects them
        for user review.
        
        Args:
            input_path (str): Path to the input file
            processor_func (callable): Function to process each line (line_num, line) -> processed_line
            
        Returns:
            tuple: (processed_lines: list, errors: list of (line_num, error_msg))
        """
        processed_lines = []
        errors = []
        
        try:
            # Use the generator to read file line-by-line
            for line_number, line in self.read_file_generator(input_path):
                try:
                    # Process the line using the provided function
                    processed = processor_func(line_number, line)
                    processed_lines.append(processed)
                except Exception as e:
                    # Capture errors for specific lines
                    error_msg = f"Error processing line {line_number}: {str(e)}"
                    errors.append((line_number, error_msg))
                    # Keep the original line
                    processed_lines.append(line)
            
            return processed_lines, errors
            
        except Exception as e:
            raise IOError(f"Error processing file: {str(e)}")
    
    def generate_output_filename(self, input_path):
        """
        Generate an appropriate output filename based on the input filename.
        
        Args:
            input_path (str): Path to the input file
            
        Returns:
            str: Suggested output filename
        """
        # Get the input file name and directory
        directory = os.path.dirname(input_path)
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        
        # Generate output filename with _fabric suffix
        output_filename = f"{name}_fabric{ext}"
        output_path = os.path.join(directory, output_filename)
        
        return output_path
    
    def get_file_info(self, file_path):
        """
        Get information about a file.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            dict: Dictionary containing file information
        """
        if not os.path.exists(file_path):
            return None
        
        stat_info = os.stat(file_path)
        
        return {
            'path': file_path,
            'filename': os.path.basename(file_path),
            'size_bytes': stat_info.st_size,
            'size_kb': stat_info.st_size / 1024,
            'size_mb': stat_info.st_size / (1024 * 1024),
            'modified_time': stat_info.st_mtime,
            'extension': os.path.splitext(file_path)[1]
        }
    
    def count_lines(self, file_path):
        """
        Count the number of lines in a file using a generator for efficiency.
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            int: Number of lines in the file
        """
        count = 0
        try:
            for _, _ in self.read_file_generator(file_path):
                count += 1
        except Exception:
            return 0
        
        return count
    
    def create_backup(self, file_path):
        """
        Create a backup of a file before overwriting.
        
        Args:
            file_path (str): Path to the file to backup
            
        Returns:
            str: Path to the backup file
        """
        if not os.path.exists(file_path):
            return None
        
        # Generate backup filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        name, ext = os.path.splitext(filename)
        
        # Find a unique backup filename
        counter = 1
        while True:
            backup_filename = f"{name}_backup{counter}{ext}"
            backup_path = os.path.join(directory, backup_filename)
            if not os.path.exists(backup_path):
                break
            counter += 1
        
        # Copy the file
        try:
            content = self.read_file(file_path)
            self.write_file(backup_path, content)
            return backup_path
        except Exception as e:
            raise IOError(f"Error creating backup: {str(e)}")

