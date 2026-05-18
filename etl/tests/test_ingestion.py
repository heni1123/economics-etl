try:
    from pipeline.ingestion import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_fetch_data_happy_path(mock_http_session, sample_records):
    """Test fetch_data with valid input, expect successful DataFrame return."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, ingestion.sources[0])
    assert not result.empty

@pytest.mark.asyncio
async def test_fetch_data_empty_input(mock_http_session):
    """Test fetch_data with empty input, expect empty DataFrame return."""
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, {})
    assert result.empty

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test fetch_data with error handling, expect empty DataFrame return on exception."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, ingestion.sources[0])
    assert result.empty

@pytest.mark.asyncio
async def test_ingest_data_happy_path(mock_http_session, sample_records):
    """Test ingest_data with valid sources, expect data loading to be called."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    ingestion = DataIngestion()
    with mock.patch.object(ingestion, 'load_data') as mock_load_data:
        await ingestion.ingest_data()
        mock_load_data.assert_called_once()

@pytest.mark.asyncio
async def test_ingest_data_empty_input(mock_http_session):
    """Test ingest_data with empty sources, expect load_data not to be called."""
    ingestion = DataIngestion()
    ingestion.sources = []
    with mock.patch.object(ingestion, 'load_data') as mock_load_data:
        await ingestion.ingest_data()
        mock_load_data.assert_not_called()

@pytest.mark.asyncio
async def test_ingest_data_error_handling(mock_http_session):
    """Test ingest_data with error handling, expect load_data to be called with empty DataFrame."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    with mock.patch.object(ingestion, 'load_data') as mock_load_data:
        await ingestion.ingest_data()
        mock_load_data.assert_called_once_with(pd.DataFrame())

def test_load_data_happy_path(mock_db_connection, sample_records):
    """Test load_data with valid DataFrame, expect logging to occur."""
    ingestion = DataIngestion()
    with mock.patch('logging.info') as mock_logging:
        ingestion.load_data(pd.DataFrame(sample_records))
        mock_logging.assert_called_with("Loading data to PostgreSQL...")

def test_load_data_empty_input(mock_db_connection):
    """Test load_data with empty DataFrame, expect logging to occur."""
    ingestion = DataIngestion()
    with mock.patch('logging.info') as mock_logging:
        ingestion.load_data(pd.DataFrame())
        mock_logging.assert_called_with("Loading data to PostgreSQL...")

def test_run_happy_path(mock_http_session, sample_records):
    """Test run method, expect ingestion process to complete without errors."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=sample_records)
    ingestion = DataIngestion()
    with mock.patch.object(ingestion, 'ingest_data', return_value=None) as mock_ingest_data:
        ingestion.run()
        mock_ingest_data.assert_called_once()

def test_run_error_handling(mock_http_session):
    """Test run method with error handling, expect logging to occur on exception."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    with mock.patch('logging.info') as mock_logging:
        ingestion.run()
        mock_logging.assert_any_call("Starting data ingestion...")
        mock_logging.assert_any_call("Data ingestion completed.")