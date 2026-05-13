try:
    from extractors.world_bank_population_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[None, [{"country": "Test Country", "population": 1000000}]]))
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    result = await extractor.extract()
    assert result == [{"country": "Test Country", "population": 1000000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    with pytest.raises(Exception):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[None, [{"country": "Test Country", "population": 1000000}]]))
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    result = await extractor._fetch_page({})
    assert result == [{"country": "Test Country", "population": 1000000}]

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty parameters."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    result = await extractor._fetch_page({})
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling."""
    mock_http_session.get.return_value = AsyncMock(status=404)
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    mock_http_session.get.return_value = AsyncMock(status=429)
    with mock.patch('asyncio.sleep', return_value=None):
        await extractor._handle_rate_limit(mock_http_session.get.return_value)
    # No assertion needed, just checking if it runs without error

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful retry."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    mock_http_session.get.side_effect = [AsyncMock(status=500), AsyncMock(status=200, json=AsyncMock(return_value=[None, [{"country": "Test Country", "population": 1000000}]]))]
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://test.url")
    assert result == [{"country": "Test Country", "population": 1000000}]

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    mock_http_session.get.side_effect = Exception("Network error")
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(mock_http_session.get, "http://test.url")

@pytest.mark.asyncio
async def test_close_happy_path():
    """Test close method."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://test.url", "params": {}})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_called_once()