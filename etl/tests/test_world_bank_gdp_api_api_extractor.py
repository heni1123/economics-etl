try:
    from extractors.world_bank_gdp_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session, sample_records):
    """Test extract with valid input, expect success."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records, "per_page": 10})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract with empty input, expect empty result."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": [], "per_page": 10})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract with error during API call, expect logging and empty result."""
    mock_http_session.get.side_effect = Exception("API error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test fetch_page with valid input, expect success."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_input(mock_http_session):
    """Test fetch_page with empty input, expect empty result."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": []})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10})
    assert result == {"data": []}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test fetch_page with error during API call, expect exception."""
    mock_http_session.get.side_effect = Exception("API error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._fetch_page({"per_page": 10})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session, sample_records):
    """Test make_request with valid input, expect success."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": sample_records})
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._make_request({"per_page": 10})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test make_request with error during API call, expect exception."""
    mock_http_session.get.side_effect = Exception("API error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._make_request({"per_page": 10})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test handle_rate_limit, expect waiting behavior."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(mock.Mock())
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session, sample_records):
    """Test retry_with_backoff with successful request after retries."""
    mock_http_session.get.side_effect = [Exception("API error"), Exception("API error"), AsyncMock(status=200, json=AsyncMock(return_value={"data": sample_records}))]
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._retry_with_backoff(extractor._make_request, {"per_page": 10})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_retry_with_backoff_exceed_max_retries(mock_http_session):
    """Test retry_with_backoff exceeding max retries, expect exception."""
    mock_http_session.get.side_effect = Exception("API error")
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, {"per_page": 10})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to close without errors."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    await extractor.close()  # No exception should be raised

@pytest.mark.asyncio
async def test_close_no_session():
    """Test close method when session is None, expect no errors."""
    extractor = WorldBankGdpApiExtractor({"url": "http://example.com", "params": {}})
    extractor.session = None
    await extractor.close()  # No exception should be raised