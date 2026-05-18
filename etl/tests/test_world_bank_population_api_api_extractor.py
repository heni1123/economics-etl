try:
    from extractors.world_bank_population_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(
        status=200,
        json=AsyncMock(return_value=[None, [{"country": "Country A", "population": 1000}]]),
    )
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    assert result == [{"country": "Country A", "population": 1000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with no data, expect empty list."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    extractor._fetch_page = AsyncMock(return_value={"data": []})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling for HTTP errors."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception, match="Network error"):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters, expect success."""
    mock_http_session.get.return_value = AsyncMock(
        status=200,
        json=AsyncMock(return_value=[None, {"data": [{"country": "Country B", "population": 2000}]}]),
    )
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"page": 1})
    assert result == {"data": [{"country": "Country B", "population": 2000}]}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling for non-200 status."""
    mock_http_session.get.return_value = AsyncMock(status=404)
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception, match="HTTP error: 404"):
        await extractor._fetch_page({"page": 1})

@pytest.mark.asyncio
async def test_handle_rate_limit_happy_path():
    """Test _handle_rate_limit method with 429 status, expect sleep."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    response = AsyncMock(status=429)
    with mock.patch("asyncio.sleep", return_value=None) as sleep_mock:
        await extractor._handle_rate_limit(response)
        sleep_mock.assert_called_once_with(2)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful response."""
    mock_http_session.get.return_value = AsyncMock(status=200)
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")
    assert result.status == 200

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling for client errors."""
    mock_http_session.get.side_effect = aiohttp.ClientError("Client error")
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(aiohttp.ClientError, match="Client error"):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")

@pytest.mark.asyncio
async def test_close():
    """Test close method to ensure session is closed."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    extractor.session.close = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_called_once()