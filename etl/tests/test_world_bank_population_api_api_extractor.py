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
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty response, expect empty list."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with an error during extraction, expect logging and empty list."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10, "page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_response(mock_http_session):
    """Test _fetch_page method with empty response, expect empty dict."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10, "page": 1})
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with an error during fetch, expect logging and empty dict."""
    mock_http_session.get.side_effect = Exception("Fetch error")
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10, "page": 1})
    assert result == {}

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session, sample_records):
    """Test _make_request method with valid parameters, expect successful request."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._make_request({"per_page": 10, "page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_make_request_rate_limit(mock_http_session):
    """Test _make_request method handling rate limit, expect waiting and retry."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 429
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with mock.patch.object(extractor, '_handle_rate_limit', return_value=None) as mock_handle_rate_limit:
        await extractor._make_request({"per_page": 10, "page": 1})
        mock_handle_rate_limit.assert_called_once()

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method with an error during request, expect logging and exception."""
    mock_http_session.get.side_effect = Exception("Request error")
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._make_request({"per_page": 10, "page": 1})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method, expect waiting for rate limit."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(mock_http_session)
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session, sample_records):
    """Test _retry_with_backoff method with successful request, expect result."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._retry_with_backoff(extractor._make_request, {"per_page": 10, "page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with errors, expect retries and final exception."""
    mock_http_session.get.side_effect = Exception("Request error")
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, {"per_page": 10, "page": 1})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to close without errors."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    extractor.session = mock_http_session
    await extractor.close()
    assert extractor.session is None

@pytest.mark.asyncio
async def test_close_no_session():
    """Test close method when no session exists, expect no errors."""
    extractor = WorldBankPopulationApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    await extractor.close()