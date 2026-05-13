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
    extractor.session = mock_http_session
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    
    result = await extractor.extract()
    
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty input."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[])
    
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.side_effect = Exception("Network error")
    
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    
    result = await extractor._fetch_page({})
    
    assert result == sample_records

@pytest.mark.asyncio
async def test_fetch_page_empty_input(mock_http_session):
    """Test _fetch_page method with empty parameters."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
    
    result = await extractor._fetch_page({})
    
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.side_effect = Exception("Network error")
    
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session, sample_records):
    """Test _make_request method with valid parameters."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    
    result = await extractor._make_request({})
    
    assert result == sample_records

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.side_effect = Exception("Network error")
    
    with pytest.raises(Exception):
        await extractor._make_request({})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(mock.Mock(status=429))
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session, sample_records):
    """Test _retry_with_backoff method with successful request."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    
    result = await extractor._retry_with_backoff(extractor._make_request, {})
    
    assert result == sample_records

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    mock_http_session.get.side_effect = Exception("Network error")
    
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, {})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method when session is active."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    
    await extractor.close()
    
    mock_http_session.close.assert_called_once()

@pytest.mark.asyncio
async def test_start_happy_path(mock_http_session):
    """Test start method initializes session."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = None
    
    await extractor.start()
    
    assert extractor.session is not None

@pytest.mark.asyncio
async def test_start_already_started(mock_http_session):
    """Test start method when session is already initialized."""
    extractor = ExchangeRatesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = mock_http_session
    
    await extractor.start()
    
    assert extractor.session is mock_http_session