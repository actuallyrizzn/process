"""Tests for the utils module."""

import pytest
from unittest.mock import Mock, patch

from process.utils import (
    is_valid_url,
    convert_bytes_to_readable_size,
    handle_errors,
    safe_file_operation
)


class TestIsValidUrl:
    """Test is_valid_url function."""
    
    def test_valid_urls(self):
        """Test various valid URLs."""
        valid_urls = [
            "https://www.example.com",
            "http://example.com",
            "https://example.com/path",
            "https://example.com/path?param=value",
            "https://sub.example.com",
            "https://example.com:8080",
            "https://example.com/path#fragment"
        ]
        
        for url in valid_urls:
            assert is_valid_url(url) is True
    
    def test_invalid_urls(self):
        """Test various invalid URLs."""
        invalid_urls = [
            "",
            None,
            "not-a-url",
            "ftp://example.com",  # FTP not supported by validators
            "example.com",  # Missing protocol
            "https://",  # Missing domain
            "https://.com",  # Missing domain
            "https://example",  # Missing TLD
        ]
        
        for url in invalid_urls:
            assert is_valid_url(url) is False
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Empty string
        assert is_valid_url("") is False
        
        # Whitespace
        assert is_valid_url("   ") is False
        
        # Very long URL
        long_url = "https://example.com/" + "a" * 1000
        assert is_valid_url(long_url) is True


class TestConvertBytesToReadableSize:
    """Test convert_bytes_to_readable_size function."""
    
    def test_zero_bytes(self):
        """Test zero bytes."""
        assert convert_bytes_to_readable_size(0) == "0 bytes"
    
    def test_bytes(self):
        """Test bytes conversion."""
        assert convert_bytes_to_readable_size(512) == "512.0 bytes"
        assert convert_bytes_to_readable_size(1023) == "1023.0 bytes"
    
    def test_kilobytes(self):
        """Test kilobytes conversion."""
        assert convert_bytes_to_readable_size(1024) == "1.0 KB"
        assert convert_bytes_to_readable_size(1536) == "1.5 KB"
        assert convert_bytes_to_readable_size(2048) == "2.0 KB"
    
    def test_megabytes(self):
        """Test megabytes conversion."""
        assert convert_bytes_to_readable_size(1024 * 1024) == "1.0 MB"
        assert convert_bytes_to_readable_size(1.5 * 1024 * 1024) == "1.5 MB"
    
    def test_gigabytes(self):
        """Test gigabytes conversion."""
        assert convert_bytes_to_readable_size(1024 * 1024 * 1024) == "1.0 GB"
        assert convert_bytes_to_readable_size(2.5 * 1024 * 1024 * 1024) == "2.5 GB"
    
    def test_terabytes(self):
        """Test terabytes conversion."""
        assert convert_bytes_to_readable_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"
    
    def test_custom_decimals(self):
        """Test custom decimal places."""
        assert convert_bytes_to_readable_size(1536, 0) == "1 KB"
        assert convert_bytes_to_readable_size(1536, 3) == "1.500 KB"
    
    def test_negative_bytes(self):
        """Test negative bytes raises ValueError."""
        with pytest.raises(ValueError, match="Byte size cannot be negative"):
            convert_bytes_to_readable_size(-1)
    
    def test_float_input(self):
        """Test float input."""
        assert convert_bytes_to_readable_size(1024.5) == "1.0 KB"


class TestHandleErrors:
    """Test handle_errors decorator."""
    
    def test_successful_function(self):
        """Test decorator with successful function."""
        @handle_errors
        def successful_func():
            return "success"
        
        result = successful_func()
        assert result == "success"
    
    def test_function_with_exception(self):
        """Test decorator with function that raises exception."""
        @handle_errors
        def failing_func():
            raise ValueError("test error")
        
        result = failing_func()
        assert result is None
    
    def test_function_with_args(self):
        """Test decorator with function that takes arguments."""
        @handle_errors
        def func_with_args(a, b):
            return a + b
        
        result = func_with_args(2, 3)
        assert result == 5
    
    def test_function_with_kwargs(self):
        """Test decorator with function that takes keyword arguments."""
        @handle_errors
        def func_with_kwargs(a, b=0):
            return a + b
        
        result = func_with_kwargs(2, b=3)
        assert result == 5


class TestSafeFileOperation:
    """Test safe_file_operation decorator."""
    
    def test_successful_file_operation(self):
        """Test decorator with successful file operation."""
        @safe_file_operation("test operation")
        def successful_file_op():
            return "success"
        
        result = successful_file_op()
        assert result == "success"
    
    def test_file_not_found_error(self):
        """Test decorator with FileNotFoundError."""
        @safe_file_operation("test operation")
        def file_not_found_op():
            raise FileNotFoundError("file not found")
        
        result = file_not_found_op()
        assert result is None
    
    def test_permission_error(self):
        """Test decorator with PermissionError."""
        @safe_file_operation("test operation")
        def permission_error_op():
            raise PermissionError("permission denied")
        
        result = permission_error_op()
        assert result is None
    
    def test_io_error(self):
        """Test decorator with IOError."""
        @safe_file_operation("test operation")
        def io_error_op():
            raise IOError("I/O error")
        
        result = io_error_op()
        assert result is None
    
    def test_generic_exception(self):
        """Test decorator with generic exception."""
        @safe_file_operation("test operation")
        def generic_error_op():
            raise Exception("generic error")
        
        result = generic_error_op()
        assert result is None
    
    def test_custom_operation_name(self):
        """Test decorator with custom operation name."""
        @safe_file_operation("custom operation")
        def custom_op():
            raise FileNotFoundError("file not found")
        
        result = custom_op()
        assert result is None 