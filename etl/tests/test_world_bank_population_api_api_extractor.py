try:
    from extractors.world_bank_population_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input, expect successful extraction."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    result = await extractor.extract()
    assert result == [{"country": "A", "population": 1000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input, expect empty result."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    extractor._fetch_page = AsyncMock(return_value={"data": []})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling, expect logging error."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Network error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        result = await extractor.extract()
        assert result == []
        mock_logger.assert_called_once_with("Error during extraction: Network error")

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    result = await extractor._fetch_page({"per_page": 1, "page": 1})
    assert result == {"data": [{"country": "A", "population": 1000}]}

@pytest.mark.asyncio
async def test_fetch_page_empty_response(mock_http_session):
    """Test _fetch_page method with empty response, expect empty data."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    result = await extractor._fetch_page({"per_page": 1, "page": 1})
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling, expect logging error."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Fetch error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        with pytest.raises(Exception):
            await extractor._fetch_page({"per_page": 1, "page": 1})
        mock_logger.assert_called_once_with("Error during extraction: Fetch error")

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session):
    """Test _make_request method with valid URL, expect successful request."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    result = await extractor._make_request("http://example.com?per_page=1")
    assert result == {"data": [{"country": "A", "population": 1000}]}

@pytest.mark.asyncio
async def test_make_request_rate_limit_handling(mock_http_session):
    """Test _make_request method handling rate limit, expect waiting."""
    mock_http_session.get = AsyncMock(side_effect=[AsyncMock(status=429), AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]}))])
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    with mock.patch.object(extractor.logger, 'warning') as mock_logger:
        result = await extractor._make_request("http://example.com?per_page=1")
        assert result == {"data": [{"country": "A", "population": 1000}]}
        mock_logger.assert_called_once_with("Rate limit exceeded. Waiting for 60 seconds.")

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method error handling, expect logging error."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Request error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        with pytest.raises(Exception):
            await extractor._make_request("http://example.com?per_page=1")
        mock_logger.assert_called_once_with("Max retries exceeded for _make_request.")

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method, expect waiting."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(AsyncMock())
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful request."""
    mock_http_session.get = AsyncMock(return_value=AsyncMock(status=200, json=AsyncMock(return_value={"data": [{"country": "A", "population": 1000}]})))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    result = await extractor._retry_with_backoff(extractor._make_request, "http://example.com?per_page=1")
    assert result == {"data": [{"country": "A", "population": 1000}]}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling, expect logging error."""
    mock_http_session.get = AsyncMock(side_effect=Exception("Request error"))
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    with mock.patch.object(extractor.logger, 'error') as mock_logger:
        with pytest.raises(Exception):
            await extractor._retry_with_backoff(extractor._make_request, "http://example.com?per_page=1")
        mock_logger.assert_called_once_with("Max retries exceeded for _make_request.")

@pytest.mark.asyncio
async def test_close_happy_path():
    """Test close method, expect session to close without errors."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 1}})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_called_once()