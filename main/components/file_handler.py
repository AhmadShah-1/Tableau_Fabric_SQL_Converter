"""
File Handler Module

This module handles file I/O operations for SQL conversion, including reading, writing, validation, and basic file utilities.
"""

import os

class FileHandler:
    def __init__(self):
        # Specify the supported file extensions and the encoding type
        self.supported_extensions = ['.sql', '.txt']
        self.encoding = 'utf-8'
    
    def read_file(self, file_path):
        """
        Input: File path
        Output: String containing the entire file content
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
        Input: File path and content to write
        Output: Boolean indicating if write was successful
        """

        try:
            # Create directory if it doesn't exist
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w', encoding=self.encoding) as file:
                file.write(content)
            
            return True

        except Exception as e:
            raise IOError(f"Error writing file {file_path}: {str(e)}")
    
    def validate_file(self, file_path):
        """
        Validate that a file exists and is a supported SQL file.
        Input: File path
        Output: Tuple containing:
            - Boolean indicating if file is valid
            - Error message if file is not valid
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
    
    def generate_output_filename(self, input_path):
        """
        Generate an appropriate output filename based on the input filename.
        Input: Input file path
        Output: Suggested output filename
        """

        # Get the input file name and directory
        directory = os.path.dirname(input_path)
        filename = os.path.basename(input_path)
        name, ext = os.path.splitext(filename)
        
        # Generate output filename with _fabric tag
        output_filename = f"{name}_fabric{ext}"
        output_path = os.path.join(directory, output_filename)
        
        return output_path
    
    def get_file_info(self, file_path):
        """
        Get information about a file.
        Input: File path
        Output: Dictionary containing file information
        """
        if not os.path.exists(file_path):
            return None
        
        stat_info = os.stat(file_path)
        
        return {
            'path': file_path,
            'filename': os.path.basename(file_path),
            'size_kb': stat_info.st_size / 1024,
            'modified_time': stat_info.st_mtime,
            'extension': os.path.splitext(file_path)[1]
        }
    
    
