try:
    from extractors.world_bank_population_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session, sample_records):
    """Test extract method with valid input, expect successful extraction."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": sample_records})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with no data returned, expect empty list."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": []})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with an error during extraction, expect logging of error."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Network error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        result = await extractor.extract()
        assert result == []
        mock_logger.assert_called_once_with("Error during extraction: Network error")

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": sample_records})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_data(mock_http_session):
    """Test _fetch_page method with no data returned, expect empty response."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": []})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"page": 1})
    assert result == {"data": []}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with an error during fetch, expect exception."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Fetch error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception, match="Fetch error"):
        await extractor._fetch_page({"page": 1})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method, expect waiting on rate limit."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(AsyncMock())
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful fetch on first attempt."""
    async def mock_function(params):
        return {"data": []}
    
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    result = await extractor._retry_with_backoff(mock_function, {"page": 1})
    assert result == {"data": []}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with retries on failure, expect final exception."""
    async def mock_function(params):
        raise Exception("Retry error")
    
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    with pytest.raises(Exception, match="Max retries exceeded"):
        await extractor._retry_with_backoff(mock_function, {"page": 1})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to be closed without errors."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {}})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_called_once()