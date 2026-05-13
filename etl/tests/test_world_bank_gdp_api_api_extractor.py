try:
    from extractors.world_bank_gdp_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session, sample_records):
    """Test extract method with valid input, expect successful extraction."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with no data, expect empty result."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": []})
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with an error during extraction, expect logging of error."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        result = await extractor.extract()
        assert result == []
        mock_logger.assert_called_once_with("Error during extraction: Network error")

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_input(mock_http_session):
    """Test _fetch_page method with no data, expect empty result."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": []})
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"page": 1})
    assert result == {"data": []}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with an error during fetch, expect logging of error."""
    mock_http_session.get.side_effect = Exception("Fetch error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        with pytest.raises(Exception):
            await extractor._fetch_page({"page": 1})
        mock_logger.assert_called_once_with("Max retries reached. Last error: Fetch error")

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session, sample_records):
    """Test _make_request method with valid parameters, expect successful request."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._make_request({"param": "value"})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_make_request_rate_limit_handling(mock_http_session):
    """Test _make_request method handling rate limit response."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 429
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch.object(extractor, '_handle_rate_limit') as mock_handle_rate_limit:
        await extractor._make_request({"param": "value"})
        mock_handle_rate_limit.assert_called_once()

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method with an error during request, expect logging of error."""
    mock_http_session.get.side_effect = Exception("Request error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        with pytest.raises(Exception):
            await extractor._make_request({"param": "value"})
        mock_logger.assert_called_once_with("Max retries reached. Last error: Request error")

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method, expect waiting for specified time."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(mock.Mock())
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful request."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": []})
    result = await extractor._retry_with_backoff(extractor._make_request, {"param": "value"})
    assert result == {"data": []}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with errors, expect retries and logging."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    mock_http_session.get.side_effect = Exception("Retry error")
    with mock.patch.object(extractor.logger, 'warning') as mock_warning:
        with pytest.raises(Exception):
            await extractor._retry_with_backoff(extractor._make_request, {"param": "value"})
        assert mock_warning.call_count == 3  # Check if it retried 3 times

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to be closed."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    extractor.session = mock_http_session
    await extractor.close()
    mock_http_session.close.assert_called_once()