try:
    from pipeline.error_handler import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
import logging

@pytest.fixture
def logger():
    return logging.getLogger("test_logger")

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(logger):
    """Test retry_with_backoff with a successful function call."""
    error_handler = ErrorHandler(logger)

    async def successful_function():
        return "Success"

    result = await error_handler.retry_with_backoff(successful_function)
    assert result == "Success"

@pytest.mark.asyncio
async def test_retry_with_backoff_empty_input(logger):
    """Test retry_with_backoff with empty input."""
    error_handler = ErrorHandler(logger)

    async def function_with_no_return():
        return None

    result = await error_handler.retry_with_backoff(function_with_no_return)
    assert result is None

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(logger):
    """Test retry_with_backoff with a function that raises an exception."""
    error_handler = ErrorHandler(logger)

    async def failing_function():
        raise Exception("Simulated failure")

    with mock.patch.object(logger, 'error') as mock_error:
        result = await error_handler.retry_with_backoff(failing_function, max_retries=2, backoff_factor=0.1)
        assert result is None
        assert mock_error.call_count == 3  # 2 retries + 1 final error log

def test_log_audit_trail(logger):
    """Test log_audit_trail logs the correct information."""
    error_handler = ErrorHandler(logger)

    with mock.patch.object(logger, 'info') as mock_info:
        error_handler.log_audit_trail(10, 5, "success")
        mock_info.assert_called_once_with("Audit Trail - Rows Extracted: 10, Rows Loaded: 5, Status: success, Error Message: None")

def test_log_audit_trail_with_error_message(logger):
    """Test log_audit_trail with an error message."""
    error_handler = ErrorHandler(logger)

    with mock.patch.object(logger, 'info') as mock_info:
        error_handler.log_audit_trail(0, 0, "failed", "Some error occurred")
        mock_info.assert_called_once_with("Audit Trail - Rows Extracted: 0, Rows Loaded: 0, Status: failed, Error Message: Some error occurred")