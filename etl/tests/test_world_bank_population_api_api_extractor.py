try:
    from extractors.world_bank_population_api_api_extractor import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_http_session):
    """Test extract method with valid input."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'data': [{'population': 1000}]})
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    
    assert result == [{'population': 1000}]

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_extract_error_handling(mock_http_session):
    """Test extract method error handling."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 500
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(side_effect=Exception("Server error"))
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor.extract()
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_page_happy_path(mock_http_session):
    """Test _fetch_page method with valid input."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'data': [{'population': 1000}]})
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._fetch_page({"page": 1})
    
    assert result == {'data': [{'population': 1000}]}

@pytest.mark.asyncio
async def test_fetch_page_error_handling(mock_http_session):
    """Test _fetch_page method error handling."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 500
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(side_effect=Exception("Server error"))
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor._fetch_page({"page": 1})

@pytest.mark.asyncio
async def test_make_request_happy_path(mock_http_session):
    """Test _make_request method with valid input."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'data': [{'population': 1000}]})
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._make_request({"page": 1})
    
    assert result == {'data': [{'population': 1000}]}

@pytest.mark.asyncio
async def test_make_request_error_handling(mock_http_session):
    """Test _make_request method error handling."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 500
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(side_effect=Exception("Server error"))
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor._make_request({"page": 1})

@pytest.mark.asyncio
async def test_handle_rate_limit(mock_http_session):
    """Test _handle_rate_limit method."""
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    with mock.patch('asyncio.sleep', return_value=None) as mock_sleep:
        await extractor._handle_rate_limit(mock.Mock())
        mock_sleep.assert_called_once_with(60)

@pytest.mark.asyncio
async def test_retry_with_backoff_happy_path(mock_http_session):
    """Test _retry_with_backoff method with successful request."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 200
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'data': [{'population': 1000}]})
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    result = await extractor._retry_with_backoff(extractor._make_request, {"page": 1})
    
    assert result == {'data': [{'population': 1000}]}

@pytest.mark.asyncio
async def test_retry_with_backoff_error_handling(mock_http_session):
    """Test _retry_with_backoff method error handling."""
    mock_http_session.get.return_value.__aenter__.return_value.status = 500
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(side_effect=Exception("Server error"))
    
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    with pytest.raises(Exception):
        await extractor._retry_with_backoff(extractor._make_request, {"page": 1})

@pytest.mark.asyncio
async def test_close_happy_path():
    """Test close method."""
    extractor = WorldBankPopulationApiExtractor(config={"url": "http://example.com", "params": {}})
    extractor.session = AsyncMock()
    await extractor.close()
    extractor.session.close.assert_awaited_once()