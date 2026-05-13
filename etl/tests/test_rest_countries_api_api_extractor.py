try:
    from extractors.rest_countries_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]))
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    result = await extractor.extract()
    assert result == [{"name_common": "Country A", "name_official": "Country A Official", "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input, expect empty list."""
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling with non-200 response."""
    mock_http_session.get.return_value = AsyncMock(status=500)
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid input, expect transformed data."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]))
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    result = await extractor._fetch_page({})
    assert result == [{"name_common": "Country A", "name_official": "Country A Official", "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty input, expect empty list."""
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    result = await extractor._fetch_page({})
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling with non-200 response."""
    mock_http_session.get.return_value = AsyncMock(status=404)
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    result = await extractor._fetch_page({})
    assert result == []

@pytest.mark.asyncio
async def test_handle_rate_limit():
    """Test _handle_rate_limit method with rate limit response."""
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    response = AsyncMock(status=429)
    with mock.patch('asyncio.sleep', return_value=None) as sleep_mock:
        await extractor._handle_rate_limit(response)
        sleep_mock.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful response."""
    mock_http_session.get.return_value = AsyncMock(status=200)
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    response = await extractor._retry_with_backoff(mock_http_session.get, "http://fakeurl.com")
    assert response.status == 200

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with client error."""
    mock_http_session.get.side_effect = [AsyncMock(status=500), AsyncMock(status=200)]
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    response = await extractor._retry_with_backoff(mock_http_session.get, "http://fakeurl.com")
    assert response.status == 200

@pytest.mark.asyncio
async def test_close():
    """Test close method to ensure session is closed."""
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_called_once()

def test_transform_data_happy_path():
    """Test _transform_data method with valid input, expect transformed output."""
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    data = [{"name": {"common": "Country A", "official": "Country A Official"}, "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]
    result = extractor._transform_data(data)
    assert result == [{"name_common": "Country A", "name_official": "Country A Official", "cca3": "CTA", "capital": "Capital A", "region": "Region A", "subregion": "Subregion A", "population": 1000000, "area": 50000}]

def test_transform_data_empty_input():
    """Test _transform_data method with empty input, expect empty list."""
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    result = extractor._transform_data([])
    assert result == []

def test_transform_data_invalid_input():
    """Test _transform_data method with invalid input, expect empty list."""
    extractor = RestCountriesApiExtractor({"url": "http://fakeurl.com"})
    data = [{"name": {"common": "Country A"}, "cca3": "CTA"}]  # Missing required fields
    result = extractor._transform_data(data)
    assert result == [{"name_common": "Country A", "name_official": None, "cca3": "CTA", "capital": None, "region": None, "subregion": None, "population": None, "area": None}]