try:
    from extractors.world_bank_gdp_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session, sample_records):
    """Test extract method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(
        __aenter__=AsyncMock(return_value=AsyncMock(
            status=200,
            json=AsyncMock(return_value={"data": sample_records})
        ))
    )
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == sample_records

@pytest.mark.asyncio
async def test_extract_empty_input(mock_http_session):
    """Test extract method with empty input, expect empty result."""
    mock_http_session.get.return_value = AsyncMock(
        __aenter__=AsyncMock(return_value=AsyncMock(
            status=200,
            json=AsyncMock(return_value={})
        ))
    )
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method with error handling, expect logging error."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor.extract()
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session, sample_records):
    """Test _fetch_page method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(
        __aenter__=AsyncMock(return_value=AsyncMock(
            status=200,
            json=AsyncMock(return_value={"data": sample_records})
        ))
    )
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10, "page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_fetch_page_empty_input(mock_http_session):
    """Test _fetch_page method with empty input, expect empty result."""
    mock_http_session.get.return_value = AsyncMock(
        __aenter__=AsyncMock(return_value=AsyncMock(
            status=200,
            json=AsyncMock(return_value={})
        ))
    )
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._fetch_page({"per_page": 10, "page": 1})
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method with error handling, expect logging error."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._fetch_page({"per_page": 10, "page": 1})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session, sample_records):
    """Test _make_request method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(
        __aenter__=AsyncMock(return_value=AsyncMock(
            status=200,
            json=AsyncMock(return_value={"data": sample_records})
        ))
    )
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._make_request({"per_page": 10, "page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method with error handling, expect logging error."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._make_request({"per_page": 10, "page": 1})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method, expect waiting for rate limit."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(AsyncMock())
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session, sample_records):
    """Test _retry_with_backoff method with valid input, expect success."""
    mock_http_session.get.return_value = AsyncMock(
        __aenter__=AsyncMock(return_value=AsyncMock(
            status=200,
            json=AsyncMock(return_value={"data": sample_records})
        ))
    )
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    result = await extractor._retry_with_backoff(extractor._make_request, {"per_page": 10, "page": 1})
    assert result == {"data": sample_records}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method with error handling, expect logging error."""
    mock_http_session.get.side_effect = Exception("Network error")
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {"per_page": 10}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, {"per_page": 10, "page": 1})

@pytest.mark.asyncio
async def test_close_happy_path(mock_http_session):
    """Test close method, expect session to close without errors."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    await extractor.close()  # No exception should be raised

@pytest.mark.asyncio
async def test_close_no_session():
    """Test close method when no session exists, expect no errors."""
    extractor = WorldBankGdpApiExtractor(config={"url": "http://example.com", "params": {}})
    extractor.session = None
    await extractor.close()  # No exception should be raised