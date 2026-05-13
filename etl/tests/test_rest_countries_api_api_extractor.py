try:
    from extractors.rest_countries_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000, "languages": {"lang1": "Language 1"}, "currencies": {"curr1": {"name": "Currency 1"}}}]))
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling."""
    mock_http_session.get.side_effect = Exception("Network error")
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid input."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A"}, "cca3": "CTA"}]))
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({})
    
    assert len(result) == 1
    assert result[0]["cca3"] == "CTA"

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty input."""
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({})
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling."""
    mock_http_session.get.side_effect = Exception("Network error")
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session):
    """Test _make_request method with valid input."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A"}, "cca3": "CTA"}]))
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._make_request("http://example.com", {})
    
    assert len(result) == 1
    assert result[0]["cca3"] == "CTA"

@pytest.mark.asyncio
async def test_make_request_rate_limit_handling(mock_http_session):
    """Test _make_request method handling rate limit."""
    mock_http_session.get.side_effect = AsyncMock(status=429)
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    await extractor._make_request("http://example.com", {})
    
    # Check if the logger was called for rate limit
    with mock.patch('extractors.rest_countries_api_api_extractor.logging.getLogger') as mock_logger:
        await extractor._make_request("http://example.com", {})
        mock_logger().warning.assert_called_with("Rate limit exceeded. Waiting for 60 seconds.")

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method error handling."""
    mock_http_session.get.side_effect = Exception("Network error")
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor._make_request("http://example.com", {})

@pytest.mark.asyncio
async def test_handle_rate_limit():
    """Test _handle_rate_limit method."""
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(AsyncMock())
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful retry."""
    mock_http_session.get.side_effect = [AsyncMock(status=500), AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A"}, "cca3": "CTA"}]))]
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._retry_with_backoff(extractor._make_request, "http://example.com", {})
    
    assert len(result) == 1
    assert result[0]["cca3"] == "CTA"

@pytest.mark.asyncio
async def test_retry_with_backoff_max_retries(mock_http_session):
    """Test _retry_with_backoff method reaching max retries."""
    mock_http_session.get.side_effect = AsyncMock(status=500)
    
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, "http://example.com", {})

@pytest.mark.asyncio
async def test_init_session():
    """Test _init_session method."""
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    await extractor._init_session()
    
    assert extractor.session is not None

@pytest.mark.asyncio
async def test_close():
    """Test close method."""
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    await extractor._init_session()
    await extractor.close()
    
    assert extractor.session is None

def test_parse_response_happy_path():
    """Test _parse_response method with valid input."""
    extractor = RestCountriesApiExtractor(config={"url": "http://example.com", "params": {}})
    data = [{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000, "languages": {"lang1": "Language 1"}, "currencies": {"curr1": {"name": "Currency 1"}}}]
    
    result = extractor._parse_response(data)
    
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"