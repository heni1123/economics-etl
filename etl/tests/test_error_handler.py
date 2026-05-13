try:
    from pipeline.error_handler import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_execute_with_retry_happy_path(mock_http_session):
    """Test execute_with_retry with a successful function call."""
    async def successful_function():
        return "Success"

    result = await error_handler.execute_with_retry(successful_function)
    assert result == "Success"

@pytest.mark.asyncio
async def test_execute_with_retry_empty_input():
    """Test execute_with_retry with empty input."""
    async def empty_function():
        return None

    result = await error_handler.execute_with_retry(empty_function)
    assert result is None

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

def test_log_audit_happy_path(caplog):
    """Test log_audit with valid input."""
    error_handler.log_audit(100, 90, "Success")
    assert "Audit Log - Rows Extracted: 100, Rows Loaded: 90, Status: Success, Error: None" in caplog.text

def test_log_audit_empty_error_message(caplog):
    """Test log_audit with empty error message."""
    error_handler.log_audit(100, 90, "Failed", None)
    assert "Audit Log - Rows Extracted: 100, Rows Loaded: 90, Status: Failed, Error: None" in caplog.text

def test_log_audit_with_error_message(caplog):
    """Test log_audit with an error message."""
    error_handler.log_audit(100, 0, "Failed", "Some error occurred")
    assert "Audit Log - Rows Extracted: 100, Rows Loaded: 0, Status: Failed, Error: Some error occurred" in caplog.text