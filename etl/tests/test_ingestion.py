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
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"data": "sample"}])
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, url)
    assert result == [{"data": "sample"}]

@pytest.mark.asyncio
async def test_fetch_data_empty_input(mock_http_session):
    """Test fetch_data with empty URL."""
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, "")
    assert result == []

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test fetch_data handles exceptions properly."""
    url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023"
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, url)
    assert result == []

@pytest.mark.asyncio
async def test_gather_data_happy_path(mock_http_session):
    """Test gather_data with all valid responses."""
    mock_http_session.get.side_effect = [
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value=[{"gdp": "sample"}])))),
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value=[{"population": "sample"}])))),
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value=[{"exchange": "sample"}])))),
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value=[{"country": "sample"}]))))
    ]
    ingestion = DataIngestion()
    result = await ingestion.gather_data()
    assert result == {
        "gdp_data": [{"gdp": "sample"}],
        "population_data": [{"population": "sample"}],
        "exchange_rates": [{"exchange": "sample"}],
        "countries_info": [{"country": "sample"}]
    }

@pytest.mark.asyncio
async def test_gather_data_error_handling(mock_http_session):
    """Test gather_data handles errors from fetch_data."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.gather_data()
    assert result == {
        "gdp_data": [],
        "population_data": [],
        "exchange_rates": [],
        "countries_info": []
    }

def test_run_logs_info(mocker):
    """Test run method logs start and completion messages."""
    mock_logger = mocker.patch('logging.info')
    ingestion = DataIngestion()
    ingestion.run()
    mock_logger.assert_any_call("Starting data ingestion...")
    mock_logger.assert_any_call("Data ingestion completed.")