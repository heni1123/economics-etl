try:
    from extractors.rest_countries_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session, sample_records):
    """Test extract method with valid input, expect successful extraction."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = await extractor.extract()
    assert result == extractor._parse_response(sample_records)

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty input, expect empty list."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling, expect empty list on exception."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid parameters, expect valid response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = await extractor._fetch_page({'param': 'value'})
    assert result == sample_records

@pytest.mark.asyncio
async def test_fetch_page_empty_input(mock_http_session):
    """Test _fetch_page method with empty parameters, expect valid response."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = await extractor._fetch_page({})
    assert result is not None

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling, expect exception."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    with pytest.raises(Exception):
        await extractor._fetch_page({'param': 'value'})

@pytest.mark.asyncio
async def test_handle_rate_limit_happy_path(mock_http_session):
    """Test _handle_rate_limit method with valid response, expect no action."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    response = AsyncMock(status=200)
    await extractor._handle_rate_limit(response)

@pytest.mark.asyncio
async def test_handle_rate_limit_exceeded(mock_http_session):
    """Test _handle_rate_limit method with rate limit exceeded, expect wait."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    response = AsyncMock(status=429)
    with mock.patch('asyncio.sleep', return_value=None) as sleep_mock:
        await extractor._handle_rate_limit(response)
        sleep_mock.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session, sample_records):
    """Test _retry_with_backoff method with valid call, expect valid response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = await extractor._retry_with_backoff(mock_http_session.get, 'http://example.com', params={})
    assert result == sample_records

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling, expect exception after retries."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(mock_http_session.get, 'http://example.com', params={})

def test_parse_response_happy_path(sample_records):
    """Test _parse_response method with valid input, expect parsed output."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = extractor._parse_response(sample_records)
    assert result == [
        {
            "common_name": country.get("name", {}).get("common"),
            "official_name": country.get("name", {}).get("official"),
            "country_code": country.get("cca3"),
            "capital": country.get("capital", [None])[0],
            "region": country.get("region"),
            "subregion": country.get("subregion"),
            "population": country.get("population"),
            "area": country.get("area"),
            "languages": country.get("languages"),
            "currencies": country.get("currencies"),
        } for country in sample_records
    ]

def test_parse_response_empty_input():
    """Test _parse_response method with empty input, expect empty list."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = extractor._parse_response([])
    assert result == []

def test_parse_response_invalid_input(invalid_records):
    """Test _parse_response method with invalid input, expect handled output."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    result = extractor._parse_response(invalid_records)
    assert result == []

@pytest.mark.asyncio
async def test_close_happy_path():
    """Test close method, expect session to close without errors."""
    extractor = RestCountriesApiExtractor({'url': 'http://example.com', 'params': {}})
    await extractor.close()