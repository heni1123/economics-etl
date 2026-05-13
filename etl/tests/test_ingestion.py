try:
    from pipeline.ingestion import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_fetch_data_happy_path(mock_http_session, sample_records):
    """Test fetch_data with valid input, expect successful data retrieval."""
    source = {
        "name": "worldbank_gdp",
        "url": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD",
        "params": {"format": "json", "per_page": "1000", "date": "2020:2023"},
    }
    mock_http_session.get.return_value.__aenter__.return_value = AsyncMock(
        status=200, json=AsyncMock(return_value=sample_records)
    )
    ingestion = DataIngestion(run_id="2023-10-01")
    result = await ingestion.fetch_data(mock_http_session, source)
    assert result == sample_records

@pytest.mark.asyncio
async def test_fetch_data_empty_input(mock_http_session):
    """Test fetch_data with empty input, expect empty list."""
    source = {
        "name": "empty_source",
        "url": "https://api.example.com/data",
        "params": {},
    }
    mock_http_session.get.return_value.__aenter__.return_value = AsyncMock(
        status=200, json=AsyncMock(return_value=[])
    )
    ingestion = DataIngestion(run_id="2023-10-01")
    result = await ingestion.fetch_data(mock_http_session, source)
    assert result == []

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test fetch_data with error response, expect empty list."""
    source = {
        "name": "error_source",
        "url": "https://api.example.com/data",
        "params": {},
    }
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("Network error")
    ingestion = DataIngestion(run_id="2023-10-01")
    result = await ingestion.fetch_data(mock_http_session, source)
    assert result == []

@pytest.mark.asyncio
async def test_ingest_data_happy_path(mock_http_session, sample_records):
    """Test ingest_data with valid sources, expect successful ingestion."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
    ]
    ingestion = DataIngestion(run_id="2023-10-01")
    result = await ingestion.ingest_data()
    assert len(result) == 4  # Expecting 4 sources

@pytest.mark.asyncio
async def test_ingest_data_empty_sources(mock_http_session):
    """Test ingest_data with empty sources, expect empty results."""
    ingestion = DataIngestion(run_id="2023-10-01")
    ingestion.sources = []  # Set sources to empty
    result = await ingestion.ingest_data()
    assert result == []

@pytest.mark.asyncio
async def test_ingest_data_error_handling(mock_http_session):
    """Test ingest_data with one failing source, expect partial results."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
        AsyncMock(status=500),  # Simulate an error for the second source
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
    ]
    ingestion = DataIngestion(run_id="2023-10-01")
    result = await ingestion.ingest_data()
    assert len(result) == 4  # Expecting 4 results, but one source failed

def test_run():
    """Test run method to ensure it executes without error."""
    ingestion = DataIngestion(run_id="2023-10-01")
    try:
        ingestion.run()  # This should not raise any exceptions
    except Exception as e:
        pytest.fail(f"run() raised an exception: {e}")