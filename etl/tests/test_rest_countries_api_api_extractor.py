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
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]))
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
    """Test extract method error handling on API failure."""
    mock_http_session.get.return_value = AsyncMock(status=500)
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid response."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]))
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page()
    assert len(result) == 1
    assert result[0]["name_common"] == "Country A"

@pytest.mark.asyncio
async def test_fetch_page_empty_response(mock_http_session):
    """Test _fetch_page method with empty response."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[]))
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling on API failure."""
    mock_http_session.get.return_value = AsyncMock(status=500)
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page()
    assert result == []

def test_parse_response_happy_path():
    """Test _parse_response method with valid input."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    json_response = [{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]
    result = extractor._parse_response(json_response)
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
    json_response = [{"name": {"common": None, "official": "Country A Official"}, "cca3": None, "capital": None, "region": None, "subregion": None, "population": None, "area": None}]
    result = extractor._parse_response(json_response)
    assert len(result) == 1
    assert result[0]["name_common"] is None

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful call."""
    mock_http_session.get.return_value = AsyncMock(status=200)
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")
    assert result.status == 200

@pytest.mark.asyncio
async def test_retry_with_backoff_timeout(mock_http_session):
    """Test _retry_with_backoff method with timeout error."""
    mock_http_session.get.side_effect = aiohttp.ClientError("Timeout")
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(Exception, match="Max retries exceeded"):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")

@pytest.mark.asyncio
async def test_close_happy_path():
    """Test close method to ensure session is closed."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    await extractor.extract()  # This will create a session
    await extractor.close()
    assert extractor.session is None

@pytest.mark.asyncio
async def test_close_no_session():
    """Test close method when no session exists."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    await extractor.close()  # Should not raise an error
    assert extractor.session is None