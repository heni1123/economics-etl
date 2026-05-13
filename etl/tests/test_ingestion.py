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
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, sample_records])
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, ingestion.sources[0])
    assert result == sample_records

@pytest.mark.asyncio
async def test_fetch_data_empty_input(mock_http_session):
    """Test fetch_data with empty input, expect empty list."""
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, {})
    assert result == []

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test fetch_data error handling with a simulated HTTP error."""
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("HTTP error")
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, ingestion.sources[0])
    assert result == []

@pytest.mark.asyncio
async def test_ingest_data_happy_path(mock_http_session, sample_records):
    """Test ingest_data with valid sources, expect successful ingestion."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, sample_records])
    ingestion = DataIngestion()
    result = await ingestion.ingest_data()
    assert len(result) == len(ingestion.sources)

@pytest.mark.asyncio
async def test_ingest_data_empty_sources(mock_http_session):
    """Test ingest_data with empty sources, expect empty results."""
    ingestion = DataIngestion()
    ingestion.sources = []
    result = await ingestion.ingest_data()
    assert result == []

@pytest.mark.asyncio
async def test_ingest_data_error_handling(mock_http_session):
    """Test ingest_data error handling with a simulated HTTP error."""
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("HTTP error")
    ingestion = DataIngestion()
    result = await ingestion.ingest_data()
    assert len(result) == len(ingestion.sources)

def test_run_happy_path(monkeypatch, mock_http_session, sample_records):
    """Test run method, expect successful execution."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, sample_records])
    ingestion = DataIngestion()
    monkeypatch.setattr(ingestion, 'ingest_data', AsyncMock(return_value=[sample_records] * len(ingestion.sources)))
    ingestion.run()

def test_run_empty_sources(monkeypatch):
    """Test run method with empty sources, expect no errors."""
    ingestion = DataIngestion()
    ingestion.sources = []
    monkeypatch.setattr(ingestion, 'ingest_data', AsyncMock(return_value=[]))
    ingestion.run()

def test_run_error_handling(monkeypatch, mock_http_session):
    """Test run method error handling with simulated HTTP error."""
    mock_http_session.get.return_value.__aenter__.side_effect = Exception("HTTP error")
    ingestion = DataIngestion()
    monkeypatch.setattr(ingestion, 'ingest_data', AsyncMock(side_effect=Exception("HTTP error")))
    ingestion.run()