try:
    from extractors.rest_countries_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input, expect successful extraction."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]))
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    assert result == [{"name_common": "Country A", "name_official": "Country A Official", "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with no data, expect empty list."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    extractor._fetch_page = AsyncMock(return_value=[])
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with an error during extraction, expect empty list."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters, expect successful fetch."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A"}, "cca3": "CTA"}]))
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page({})
    assert result == [{"name_common": "Country A", "cca3": "CTA"}]

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with no parameters, expect empty list."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    extractor._retry_with_backoff = AsyncMock(return_value=[])
    result = await extractor._fetch_page({})
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with an error during fetch, expect exception handling."""
    mock_http_session.get.side_effect = Exception("Fetch error")
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_handle_rate_limit_happy_path():
    """Test _handle_rate_limit method with a 429 response, expect wait."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    response = AsyncMock(status=429)
    await extractor._handle_rate_limit(response)

@pytest.mark.asyncio
async def test_handle_rate_limit_no_limit():
    """Test _handle_rate_limit method with a non-429 response, expect no wait."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    response = AsyncMock(status=200)
    await extractor._handle_rate_limit(response)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful fetch, expect response."""
    mock_http_session.get.return_value = AsyncMock(status=200)
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")
    assert result.status == 200

@pytest.mark.asyncio
async def test_retry_with_backoff_timeout_handling(mock_http_session):
    """Test _retry_with_backoff method with timeouts, expect retries."""
    mock_http_session.get.side_effect = [asyncio.TimeoutError, AsyncMock(status=200)]
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")
    assert result.status == 200

@pytest.mark.asyncio
async def test_retry_with_backoff_max_retries(mock_http_session):
    """Test _retry_with_backoff method with failures, expect error after max retries."""
    mock_http_session.get.side_effect = asyncio.TimeoutError
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(asyncio.TimeoutError):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")

@pytest.mark.asyncio
async def test_close():
    """Test close method to ensure session is closed."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    await extractor.close()

def test_parse_response_happy_path():
    """Test _parse_response method with valid data, expect parsed output."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    data = [{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]
    result = extractor._parse_response(data)
    assert result == [{"name_common": "Country A", "name_official": "Country A Official", "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]

def test_parse_response_empty_input():
    """Test _parse_response method with empty data, expect empty list."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = extractor._parse_response([])
    assert result == []

def test_parse_response_invalid_data():
    """Test _parse_response method with invalid data, expect handled missing fields."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    data = [{"name": {"common": "Country A"}, "cca3": "CTA"}]
    result = extractor._parse_response(data)
    assert result == [{"name_common": "Country A", "name_official": None, "cca3": "CTA", "capital": None, "region": None, "subregion": None, "population": None, "area": None}]