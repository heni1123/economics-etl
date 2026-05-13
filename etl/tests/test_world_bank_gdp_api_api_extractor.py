try:
    from extractors.world_bank_gdp_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[None, [{"gdp": 1000}]]))
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    assert result == [{"gdp": 1000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[None, [{"gdp": 1000}]]))
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({})
    assert result == [{"gdp": 1000}]

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty parameters."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({})
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling."""
    mock_http_session.get.return_value = AsyncMock(status=500)
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    mock_http_session.get.return_value = AsyncMock(status=429)
    with mock.patch.object(extractor, '_fetch_page', return_value=AsyncMock(return_value=[{"gdp": 1000}])):
        await extractor._handle_rate_limit(mock_http_session.get)
        result = await extractor._fetch_page({})
        assert result == [{"gdp": 1000}]

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful retry."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    mock_http_session.get.side_effect = [AsyncMock(status=500), AsyncMock(status=200, json=AsyncMock(return_value=[None, [{"gdp": 1000}]]))]
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")
    assert result == [{"gdp": 1000}]

@pytest.mark.asyncio
async def test_retry_with_backoff_exceed_max_attempts(mock_http_session):
    """Test _retry_with_backoff method exceeding max attempts."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    mock_http_session.get.side_effect = AsyncMock(side_effect=Exception("Network error"))
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")

@pytest.mark.asyncio
async def test_close_happy_path():
    """Test close method to ensure session is closed."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_called_once()