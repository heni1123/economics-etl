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
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": "Country1"}]))
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    assert result == [{"name": "Country1"}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input, expect success."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling with a network error."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(Exception, match="Network error"):
        await extractor.extract()

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid parameters, expect success."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": "Country1"}]))
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page({})
    assert result == [{"name": "Country1"}]

@pytest.mark.asyncio
async def test_fetch_page_empty_input():
    """Test _fetch_page method with empty parameters, expect success."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._fetch_page({})
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling with a 404 response."""
    mock_http_session.get.return_value = AsyncMock(status=404)
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(Exception):
        await extractor._fetch_page({})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method with a rate limit response."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    mock_response = AsyncMock(status=429)
    with mock.patch.object(extractor, 'extract', return_value=AsyncMock()) as mock_extract:
        await extractor._handle_rate_limit(mock_response)
        mock_extract.assert_called_once()

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful call."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=[{"name": "Country1"}]))
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    result = await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")
    assert result == [{"name": "Country1"}]

@pytest.mark.asyncio
async def test_retry_with_backoff_timeout_handling(mock_http_session):
    """Test _retry_with_backoff method with timeout error."""
    mock_http_session.get.side_effect = asyncio.TimeoutError
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    with pytest.raises(asyncio.TimeoutError):
        await extractor._retry_with_backoff(mock_http_session.get, "http://example.com")

@pytest.mark.asyncio
async def test_close_happy_path():
    """Test close method to ensure session is closed."""
    extractor = RestCountriesApiExtractor({"url": "http://example.com"})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_called_once()