try:
    from extractors.exchange_rates_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session, sample_records):
    """Test extract method with valid input."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._parse_response = mock.Mock(return_value=sample_records)
    extractor._fetch_page = AsyncMock(return_value={"result": "success"})
    
    result = await extractor.extract()
    
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty input."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._fetch_page = AsyncMock(return_value={})
    
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._fetch_page = AsyncMock(side_effect=Exception("Fetch error"))
    
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._retry_with_backoff = AsyncMock(return_value={"result": "success"})
    
    result = await extractor._fetch_page({})
    
    assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_fetch_page_empty_input(mock_http_session):
    """Test _fetch_page method with empty parameters."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._retry_with_backoff = AsyncMock(return_value={})
    
    result = await extractor._fetch_page({})
    
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._retry_with_backoff = AsyncMock(side_effect=Exception("Fetch error"))
    
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session):
    """Test _make_request method with valid parameters."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    mock_http_session.get.return_value.__aenter__.return_value = AsyncMock(status=200, json=AsyncMock(return_value={"result": "success"}))
    
    result = await extractor._make_request({})
    
    assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_make_request_rate_limit_handling(mock_http_session):
    """Test _make_request method handling rate limit."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    mock_http_session.get.return_value.__aenter__.return_value = AsyncMock(status=429)
    
    with mock.patch.object(extractor, '_handle_rate_limit', return_value=None) as mock_handle:
        await extractor._make_request({})
        mock_handle.assert_called_once()

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("Request error")
    
    with pytest.raises(Exception):
        await extractor._make_request({})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    response = AsyncMock()
    
    await extractor._handle_rate_limit(response)
    
    # Check if the logger warning was called
    extractor.logger.warning.assert_called_with("Rate limit exceeded. Waiting for 60 seconds.")

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful request."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._make_request = AsyncMock(return_value={"result": "success"})
    
    result = await extractor._retry_with_backoff(extractor._make_request, {})
    
    assert result == {"result": "success"}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor._make_request = AsyncMock(side_effect=aiohttp.ClientError("Client error"))
    
    with pytest.raises(aiohttp.ClientError):
        await extractor._retry_with_backoff(extractor._make_request, {})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method when session is initialized."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    await extractor.start()
    
    await extractor.close()
    
    assert extractor.session is None

@pytest.mark.asyncio
async def test_start_happy_path(mock_http_session):
    """Test start method initializes the session."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    
    await extractor.start()
    
    assert extractor.session is not None

def test_parse_response_happy_path(sample_records):
    """Test _parse_response method with valid response."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    response = {
        "result": "success",
        "provider": "test_provider",
        "time_last_update_unix": 1234567890,
        "time_last_update_utc": "2023-01-01T00:00:00Z",
        "time_next_update_unix": 1234567891,
        "time_next_update_utc": "2023-01-01T01:00:00Z",
        "base_code": "USD",
        "rates": {
            "EUR": 0.85,
            "GBP": 0.75,
            "JPY": 110.0,
            "CHF": 0.92
        }
    }
    
    result = extractor._parse_response(response)
    
    assert result == [{
        "result": "success",
        "provider": "test_provider",
        "time_last_update_unix": 1234567890,
        "time_last_update_utc": "2023-01-01T00:00:00Z",
        "time_next_update_unix": 1234567891,
        "time_next_update_utc": "2023-01-01T01:00:00Z",
        "base_code": "USD",
        "rates.EUR": 0.85,
        "rates.GBP": 0.75,
        "rates.JPY": 110.0,
        "rates.CHF": 0.92,
    }]

def test_parse_response_empty_input():
    """Test _parse_response method with empty response."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    
    result = extractor._parse_response({})
    
    assert result == [{
        "result": None,
        "provider": None,
        "time_last_update_unix": None,
        "time_last_update_utc": None,
        "time_next_update_unix": None,
        "time_next_update_utc": None,
        "base_code": None,
        "rates.EUR": None,
        "rates.GBP": None,
        "rates.JPY": None,
        "rates.CHF": None,
    }]