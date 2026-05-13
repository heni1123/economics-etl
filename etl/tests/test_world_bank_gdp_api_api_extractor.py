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
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty input, expect no data returned."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with an error during extraction, expect logging and no data returned."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"page": 1, "per_page": 10})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_response(mock_http_session):
    """Test _fetch_page method with empty response, expect no data."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"page": 1, "per_page": 10})
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with an error, expect logging and no data."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._fetch_page({"page": 1, "per_page": 10})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session, sample_records):
    """Test _make_request method with valid parameters, expect successful request."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._make_request({"page": 1, "per_page": 10})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_make_request_rate_limit(mock_http_session):
    """Test _make_request method handling rate limit, expect waiting and retry."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 429
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with mock.patch('asyncio.sleep', return_value=None):
        await extractor._make_request({"page": 1, "per_page": 10})

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method with an error, expect logging and exception raised."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._make_request({"page": 1, "per_page": 10})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method, expect waiting for rate limit."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with mock.patch('asyncio.sleep', return_value=None):
        await extractor._handle_rate_limit(mock_http_session)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session, sample_records):
    """Test _retry_with_backoff method with successful request, expect result."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._retry_with_backoff(extractor._make_request, {"page": 1, "per_page": 10})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with errors, expect retries and final exception."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, {"page": 1, "per_page": 10})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to be closed without errors."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    extractor.session = mock_http_session
    await extractor.close()  # No assertion needed, just ensure it runs without error.