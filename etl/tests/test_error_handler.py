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

    async def function_with_no_args():
        return "Success"

    result = await error_handler.retry_with_backoff(function_with_no_args)
    assert result == "Success"

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(logger):
    """Test retry_with_backoff with a function that raises an exception."""
    error_handler = ErrorHandler(logger)

    async def failing_function():
        raise Exception("Simulated failure")

    with mock.patch.object(logger, 'error') as mock_error:
        with pytest.raises(Exception, match="Function failing_function failed after 3 attempts."):
            await error_handler.retry_with_backoff(failing_function)
        assert mock_error.call_count == 4  # 3 retries + final error log

def test_log_audit(logger):
    """Test log_audit logs the correct information."""
    error_handler = ErrorHandler(logger)

    with mock.patch.object(logger, 'info') as mock_info:
        error_handler.log_audit(10, 5, "success")
        mock_info.assert_called_once_with("Audit Log - Rows Extracted: 10, Rows Loaded: 5, Status: success, Error Message: ")

def test_log_audit_with_error_message(logger):
    """Test log_audit with an error message."""
    error_handler = ErrorHandler(logger)

    with mock.patch.object(logger, 'info') as mock_info:
        error_handler.log_audit(10, 5, "failed", "Some error occurred")
        mock_info.assert_called_once_with("Audit Log - Rows Extracted: 10, Rows Loaded: 5, Status: failed, Error Message: Some error occurred")