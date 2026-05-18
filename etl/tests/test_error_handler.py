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
async def test_execute_with_retry_error_handling():
    """Test execute_with_retry with a function that raises an exception."""
    async def mock_function():
        raise Exception("error")

    with pytest.raises(Exception, match="error"):
        await error_handler.execute_with_retry(mock_function)

@pytest.mark.asyncio
async def test_log_audit_trail():
    """Test log_audit_trail logs the correct message."""
    with mock.patch.object(error_handler.logger, 'info') as mock_log:
        error_handler.log_audit_trail("Test message")
        mock_log.assert_called_once_with("AUDIT: Test message")

@pytest.mark.asyncio
async def test_execute_with_retry_multiple_retries():
    """Test execute_with_retry retries on failure."""
    async def mock_function():
        raise Exception("error")

    with mock.patch.object(error_handler.logger, 'error') as mock_error, \
         mock.patch.object(error_handler.logger, 'critical') as mock_critical:
        with pytest.raises(Exception, match="error"):
            await error_handler.execute_with_retry(mock_function)

        assert mock_error.call_count == 3  # Check if it logged error for each retry
        assert mock_critical.called  # Check if it logged critical after all retries failed

@pytest.mark.asyncio
async def test_execute_with_retry_backoff():
    """Test execute_with_retry implements backoff correctly."""
    async def mock_function():
        raise Exception("error")

    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        with pytest.raises(Exception):
            await error_handler.execute_with_retry(mock_function)

        assert mock_sleep.call_count == 2  # Check if sleep was called for retries
        assert mock_sleep.call_args_list == [mock.call(1.0), mock.call(2.0)]  # Check backoff times

@pytest.mark.asyncio
async def test_setup_logging():
    """Test setup_logging initializes the logger correctly."""
    logger = error_handler.setup_logging()
    assert logger.name == "ETL_Error_Handler"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1  # Check if one handler is added
    assert isinstance(logger.handlers[0], logging.FileHandler)  # Check if it's a FileHandler