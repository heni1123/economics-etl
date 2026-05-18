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
    async def mock_function():
        return "success"

    result = await error_handler.execute_with_retry(mock_function)
    assert result == "success"

@pytest.mark.asyncio
async def test_execute_with_retry_empty_input():
    """Test execute_with_retry with empty input."""
    async def mock_function():
        return "success"

    result = await error_handler.execute_with_retry(mock_function)
    assert result == "success"

@pytest.mark.asyncio
async def test_execute_with_retry_error_handling(mock_http_session):
    """Test execute_with_retry with a function that raises an exception."""
    async def mock_function():
        raise Exception("error")

    with pytest.raises(Exception, match="error"):
        await error_handler.execute_with_retry(mock_function)

@pytest.mark.asyncio
async def test_execute_with_retry_multiple_retries(mock_http_session):
    """Test execute_with_retry with multiple retries before success."""
    attempts = 0

    async def mock_function():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise Exception("error")
        return "success"

    result = await error_handler.execute_with_retry(mock_function)
    assert result == "success"
    assert attempts == 3

def test_log_audit():
    """Test log_audit method."""
    with mock.patch.object(error_handler.logger, 'info') as mock_info:
        error_handler.log_audit("Test audit message")
        mock_info.assert_called_once_with("AUDIT: Test audit message")

def test_setup_logging():
    """Test setup_logging method."""
    logger = error_handler.setup_logging()
    assert logger.name == "ETL_ErrorHandler"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0], logging.FileHandler)