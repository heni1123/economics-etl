try:
    from extractors.world_bank_population_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract with valid input, expect success."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    result = await extractor.extract()
    assert result == [{"country": "A", "population": 1000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract with empty input, expect empty list."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    extractor._fetch_page = AsyncMock(return_value={})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract error handling for server error."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Server error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    with pytest.raises(Exception, match="Server error"):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test fetch_page with valid parameters, expect valid response."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"page": 1})
    assert result == {"data": [{"country": "A", "population": 1000}]}

@pytest.mark.asyncio
async def test_fetch_page_rate_limit_handling(mock_http_session):
    """Test fetch_page handling for rate limit error."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=429))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception, match="Rate limit exceeded"):
        await extractor._fetch_page({"page": 1})

@pytest.mark.asyncio
async def test_fetch_page_server_error(mock_http_session):
    """Test fetch_page handling for server error."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=500))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception, match="Server error: 500"):
        await extractor._fetch_page({"page": 1})

@pytest.mark.asyncio
async def test_handle_rate_limit():
    """Test handle_rate_limit method."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with mock.patch('asyncio.sleep', return_value=None):
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await extractor._handle_rate_limit(AsyncMock())

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test retry_with_backoff with successful fetch."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._retry_with_backoff(extractor._fetch_page, {"page": 1})
    assert result == {"data": [{"country": "A", "population": 1000}]}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test retry_with_backoff error handling."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Fetch error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception, match="Fetch error"):
        await extractor._retry_with_backoff(extractor._fetch_page, {"page": 1})

@pytest.mark.asyncio
async def test_close():
    """Test close method to ensure session is closed."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_awaited_once()