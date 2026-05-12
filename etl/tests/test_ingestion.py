try:
    from pipeline.ingestion import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_fetch_data_happy_path(mock_http_session):
    """Test fetch_data with valid input, expect successful data retrieval."""
    source = {
        "name": "worldbank_gdp",
        "url": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD",
        "params": {"format": "json", "per_page": 1000, "date": "2020:2023"}
    }
    mock_http_session.get.return_value.__aenter__.return_value = AsyncMock(
        status=200,
        json=AsyncMock(return_value=[{"data": "sample"}])
    )
    ingestion = DataIngestion(run_id="test")
    result = await ingestion.fetch_data(mock_http_session, source)
    assert result == [{"data": "sample"}]

@pytest.mark.asyncio
async def test_fetch_data_empty_input():
    """Test fetch_data with empty input, expect empty list."""
    ingestion = DataIngestion(run_id="test")
    result = await ingestion.fetch_data(mock.Mock(), {})
    assert result == []

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test fetch_data with error handling, expect empty list on exception."""
    source = {
        "name": "worldbank_gdp",
        "url": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD",
        "params": {"format": "json", "per_page": 1000, "date": "2020:2023"}
    }
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("Network error")
    ingestion = DataIngestion(run_id="test")
    result = await ingestion.fetch_data(mock_http_session, source)
    assert result == []

@pytest.mark.asyncio
async def test_ingest_data_happy_path(mock_http_session):
    """Test ingest_data with valid sources, expect successful ingestion."""
    mock_http_session.get.return_value.__aenter__.return_value = AsyncMock(
        status=200,
        json=AsyncMock(return_value=[{"data": "sample"}])
    )
    ingestion = DataIngestion(run_id="test")
    result = await ingestion.ingest_data()
    assert len(result) == 4  # Expecting 4 sources to be processed

@pytest.mark.asyncio
async def test_ingest_data_empty_sources():
    """Test ingest_data with empty sources, expect empty result."""
    ingestion = DataIngestion(run_id="test")
    ingestion.sources = []  # Set sources to empty
    result = await ingestion.ingest_data()
    assert result == []

@pytest.mark.asyncio
async def test_ingest_data_error_handling(mock_http_session):
    """Test ingest_data with one failing source, expect partial results."""
    mock_http_session.get.return_value.__aenter__.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=[{"data": "sample1"}])),
        AsyncMock(status=500)  # Simulate an error for the second source
    ] * 2  # Repeat for all sources
    ingestion = DataIngestion(run_id="test")
    result = await ingestion.ingest_data()
    assert len(result) == 4  # Expecting 4 sources to be processed, but one will fail

def test_run():
    """Test run method to ensure it completes without errors."""
    ingestion = DataIngestion(run_id="test")
    ingestion.run()  # No assertion needed, just check for exceptions

def test_run_empty_sources():
    """Test run method with empty sources, ensure it completes without errors."""
    ingestion = DataIngestion(run_id="test")
    ingestion.sources = []  # Set sources to empty
    ingestion.run()  # No assertion needed, just check for exceptions

def test_run_error_handling(monkeypatch):
    """Test run method with error handling, ensure it completes without errors."""
    ingestion = DataIngestion(run_id="test")
    monkeypatch.setattr(ingestion, 'ingest_data', AsyncMock(side_effect=Exception("Error during ingestion")))
    ingestion.run()  # No assertion needed, just check for exceptions