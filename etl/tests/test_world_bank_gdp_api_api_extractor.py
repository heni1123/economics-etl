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
    mock_http_session.get = AsyncMock(return_value=AsyncMock(
        status=200,
        json=AsyncMock(return_value={'data': sample_records})
    ))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with no data returned, expect empty list."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(
        status=200,
        json=AsyncMock(return_value={})
    ))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with an error during extraction, expect logging and exit."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Network error"))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        result = await extractor.extract()
        assert result == []
        mock_logger.assert_called_once_with("Error during extraction: Network error")

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(
        status=200,
        json=AsyncMock(return_value={'data': sample_records})
    ))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10, "page": 1})
    assert result == {'data': sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_response(mock_http_session):
    """Test _fetch_page method with empty response, expect empty dict."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(
        status=200,
        json=AsyncMock(return_value={})
    ))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10, "page": 1})
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with an error during fetch, expect logging and exit."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Fetch error"))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        result = await extractor._fetch_page({"per_page": 10, "page": 1})
        assert result == {}
        mock_logger.assert_called_once_with("Error during extraction: Fetch error")

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session):
    """Test _make_request method with valid URL, expect successful response."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(
        status=200,
        json=AsyncMock(return_value={'data': []})
    ))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._make_request("http://example.com?param=value")
    assert result == {'data': []}

@pytest.mark.asyncio
async def test_make_request_rate_limit(mock_http_session):
    """Test _make_request method handling rate limit response, expect waiting."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(
        status=429,
        json=AsyncMock(return_value={})
    ))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch.object(extractor.logger, 'warning') as mock_logger:
        await extractor._make_request("http://example.com?param=value")
        mock_logger.assert_called_once_with("Rate limit exceeded. Waiting for 60 seconds.")

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful request, expect result."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(
        status=200,
        json=AsyncMock(return_value={'data': []})
    ))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._retry_with_backoff(extractor._make_request, "http://example.com?param=value")
    assert result == {'data': []}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with failure, expect retries and logging."""
    mock_http_session.get = AsyncMock(side_effect=aiohttp.ClientError("Client error"))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch.object(extractor.logger, 'warning') as mock_logger:
        with pytest.raises(aiohttp.ClientError):
            await extractor._retry_with_backoff(extractor._make_request, "http://example.com?param=value")
        assert mock_logger.call_count == 3  # Expecting 3 retries

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to be closed without errors."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_awaited_once()