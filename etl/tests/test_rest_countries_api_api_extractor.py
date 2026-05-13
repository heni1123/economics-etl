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
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 10000, "languages": {"lang": "Language A"}, "currencies": {"currency": "Currency A"}}])
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling."""
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("Network error")
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid input."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"name": {"common": "Country A"}, "cca3": "CTA"}])
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page({})
    
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty input."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page({})
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling."""
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("Network error")
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session):
    """Test _make_request method with valid input."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"name": {"common": "Country A"}, "cca3": "CTA"}])
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._make_request({})
    
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method error handling."""
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("Network error")
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(Exception):
        await extractor._make_request({})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(None)
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful retry."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"name": {"common": "Country A"}, "cca3": "CTA"}])
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._retry_with_backoff(extractor._make_request, {})
    
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling."""
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("Network error")
    
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, {})

@pytest.mark.asyncio
async def test_init_session():
    """Test _init_session method."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    await extractor._init_session()
    
    assert extractor.session is not None

@pytest.mark.asyncio
async def test_close():
    """Test close method."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    await extractor._init_session()
    await extractor.close()
    
    assert extractor.session is None

def test_parse_response_happy_path():
    """Test _parse_response method with valid input."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    data = [{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 10000, "languages": {"lang": "Language A"}, "currencies": {"currency": "Currency A"}}]
    result = extractor._parse_response(data)
    
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"

def test_parse_response_empty_input():
    """Test _parse_response method with empty input."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = extractor._parse_response([])
    
    assert result == []

def test_parse_response_invalid_input():
    """Test _parse_response method with invalid input."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    data = [{"name": {"common": "Country A"}, "cca3": "CTA"}]  # Missing required fields
    result = extractor._parse_response(data)
    
    assert len(result) == 1
    assert "name_official" not in result[0]  # Check for missing field