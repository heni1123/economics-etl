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
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"data": sample_records}))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty response, expect empty list."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"data": []}))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with HTTP error, expect exception raised."""
    mock_http_session.get.side_effect = aiohttp.ClientError("Connection error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(aiohttp.ClientError):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"data": sample_records}))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"per_page": 10})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_response(mock_http_session):
    """Test _fetch_page method with empty response, expect empty dict."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"data": []}))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"per_page": 10})
    assert result == {"data": []}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with HTTP error, expect exception raised."""
    mock_http_session.get.side_effect = aiohttp.ClientError("Connection error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(aiohttp.ClientError):
        await extractor._fetch_page({"per_page": 10})

@pytest.mark.asyncio
async def test_handle_rate_limit_happy_path(mock_http_session):
    """Test _handle_rate_limit method with rate limit response, expect backoff handling."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    response = AsyncMock(status=429)
    await extractor._handle_rate_limit(response)  # No exception should be raised

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session, sample_records):
    """Test _retry_with_backoff method with successful fetch, expect successful response."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"data": sample_records}))
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com", params={})
    assert result == mock_http_session.get.return_value

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with HTTP error, expect exception raised."""
    mock_http_session.get.side_effect = aiohttp.ClientError("Connection error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(aiohttp.ClientError):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com", params={})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to be closed without errors."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    extractor.session = mock_http_session
    await extractor.close()  # No exception should be raised
    assert extractor.session is None  # Ensure session is set to None after closing