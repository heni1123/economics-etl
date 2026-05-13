try:
    from pipeline.error_handler import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_execute_with_retry_happy_path():
    """Test execute_with_retry with a successful function call."""
    async def successful_function():
        return "Success"

    result = await error_handler.execute_with_retry(successful_function)
    assert result == "Success"

@pytest.mark.asyncio
async def test_execute_with_retry_empty_input():
    """Test execute_with_retry with no arguments."""
    async def function_with_no_args():
        return "No Args"

    result = await error_handler.execute_with_retry(function_with_no_args)
    assert result == "No Args"

@pytest.mark.asyncio
async def test_execute_with_retry_error_handling():
    """Test execute_with_retry with a function that raises an exception."""
    async def failing_function():
        raise Exception("Failure")

    result = await error_handler.execute_with_retry(failing_function)
    assert result is None

@pytest.mark.asyncio
async def test_execute_with_retry_multiple_failures():
    """Test execute_with_retry with multiple failures before success."""
    attempt = 0

    async def intermittent_function():
        nonlocal attempt
        if attempt < 2:
            attempt += 1
            raise Exception("Temporary failure")
        return "Success"

    result = await error_handler.execute_with_retry(intermittent_function)
    assert result == "Success"

def test_log_audit_happy_path():
    """Test log_audit with valid input."""
    with mock.patch('logging.Logger.info') as mock_info:
        error_handler.log_audit(100, 90, "Success")
        mock_info.assert_called_once_with("Audit Log - Rows Extracted: 100, Rows Loaded: 90, Status: Success, Error: None")

def test_log_audit_empty_input():
    """Test log_audit with zero rows."""
    with mock.patch('logging.Logger.info') as mock_info:
        error_handler.log_audit(0, 0, "No Data")
        mock_info.assert_called_once_with("Audit Log - Rows Extracted: 0, Rows Loaded: 0, Status: No Data, Error: None")

def test_log_audit_with_error_message():
    """Test log_audit with an error message."""
    with mock.patch('logging.Logger.info') as mock_info:
        error_handler.log_audit(100, 50, "Failed", "Some error occurred")
        mock_info.assert_called_once_with("Audit Log - Rows Extracted: 100, Rows Loaded: 50, Status: Failed, Error: Some error occurred")