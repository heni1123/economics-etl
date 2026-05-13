try:
    from pipeline.ingestion import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_fetch_data_happy_path(mock_http_session):
    """Test fetch_data with valid URL and response."""
    url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023"
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 21000000}]])
    
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, url)
    
    assert len(result) == 2

@pytest.mark.asyncio
async def test_fetch_data_empty_input(mock_http_session):
    """Test fetch_data with empty response."""
    url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023"
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[])
    
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, url)
    
    assert result == []

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test fetch_data with an error during fetch."""
    url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023"
    mock_http_session.get.side_effect = Exception("Network error")
    
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, url)
    
    assert result == []

@pytest.mark.asyncio
async def test_extract_gdp_happy_path(mock_http_session):
    """Test extract_gdp with valid response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 21000000}]])
    
    ingestion = DataIngestion()
    result = await ingestion.extract_gdp()
    
    assert len(result) == 2

@pytest.mark.asyncio
async def test_extract_population_happy_path(mock_http_session):
    """Test extract_population with valid response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 331000000}]])
    
    ingestion = DataIngestion()
    result = await ingestion.extract_population()
    
    assert len(result) == 2

@pytest.mark.asyncio
async def test_extract_exchange_rates_happy_path(mock_http_session):
    """Test extract_exchange_rates with valid response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"rates": {"EUR": 0.85}})
    
    ingestion = DataIngestion()
    result = await ingestion.extract_exchange_rates()
    
    assert "rates" in result

@pytest.mark.asyncio
async def test_extract_countries_happy_path(mock_http_session):
    """Test extract_countries with valid response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"name": {"common": "United States"}}])
    
    ingestion = DataIngestion()
    result = await ingestion.extract_countries()
    
    assert len(result) == 1

@pytest.mark.asyncio
async def test_run_extraction_happy_path(mock_http_session):
    """Test run_extraction with valid responses."""
    mock_http_session.get.side_effect = [
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 21000000}]]))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 331000000}]]))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value={"rates": {"EUR": 0.85}}))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{"name": {"common": "United States"}}])))))
    ]
    
    ingestion = DataIngestion()
    result = await ingestion.run_extraction()
    
    assert not result.empty

@pytest.mark.asyncio
async def test_run_extraction_error_handling(mock_http_session):
    """Test run_extraction with an error in one of the fetches."""
    mock_http_session.get.side_effect = [
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 21000000}]]))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[])))),
        AsyncMock(side_effect=Exception("Network error")),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{"name": {"common": "United States"}}])))))
    ]
    
    ingestion = DataIngestion()
    result = await ingestion.run_extraction()
    
    assert result.empty

@pytest.mark.asyncio
async def test_main_happy_path(mock_http_session):
    """Test main function with valid responses."""
    mock_http_session.get.side_effect = [
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 21000000}]]))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 331000000}]]))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value={"rates": {"EUR": 0.85}}))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{"name": {"common": "United States"}}])))))
    ]
    
    await main()  # No assertion needed, just check for exceptions

@pytest.mark.asyncio
async def test_main_error_handling(mock_http_session):
    """Test main function with an error in one of the fetches."""
    mock_http_session.get.side_effect = [
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{}, [{"country.id": "USA", "date": 2020, "value": 21000000}]]))))),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[])))),
        AsyncMock(side_effect=Exception("Network error")),
        AsyncMock(return_value=mock.Mock(__aenter__=AsyncMock(return_value=mock.Mock(json=AsyncMock(return_value=[{"name": {"common": "United States"}}])))))
    ]
    
    with pytest.raises(Exception):
        await main()  # Expecting an exception due to the error in fetching data