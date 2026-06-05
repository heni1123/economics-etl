try:
    from extractors.exchange_rates_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"rate": 1.0}])
    
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    result = await extractor.extract()
    
    assert result == [{"rate": 1.0}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    
    with pytest.raises(Exception):
        await extractor.extract()

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling on fetch failure."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 500
    
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    
    with pytest.raises(Exception):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"rate": 1.0})
    
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    result = await extractor._fetch_page()
    
    assert result == {"rate": 1.0}

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty parameters."""
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling on HTTP error."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 404
    
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    
    with pytest.raises(Exception):
        await extractor._fetch_page()

@pytest.mark.asyncio
async def test_handle_rate_limit():
    """Test _handle_rate_limit method."""
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(None)
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful fetch."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"rate": 1.0})
    
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    result = await extractor._retry_with_backoff(extractor._fetch_page)
    
    assert result == {"rate": 1.0}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling on all retries failing."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 500
    
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._fetch_page)

@pytest.mark.asyncio
async def test_close():
    """Test close method."""
    extractor = ExchangeRatesApiExtractor({"url": "http://example.com", "name": "Test Extractor"})
    
    with mock.patch.object(extractor.session, 'close', return_value=None) as mock_close:
        await extractor.close()
        mock_close.assert_called_once()