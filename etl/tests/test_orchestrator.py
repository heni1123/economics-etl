try:
    from pipeline.orchestrator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_run_happy_path(mock_http_session, mock_db_connection):
    """Test the run method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2020, "value": 21000000}]])),
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2020, "value": 331000000}]])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"USD": 1}})),
        AsyncMock(json=AsyncMock(return_value=[{"cca3": "USA", "name": {"common": "United States"}}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'success'
    assert orchestrator.rows_loaded > 0

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session, mock_db_connection):
    """Test the run method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"USD": 1}})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'success'
    assert orchestrator.rows_loaded == 0

@pytest.mark.asyncio
async def test_run_error_handling(mock_http_session, mock_db_connection):
    """Test the run method with an error in the extraction phase."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'failed'
    assert orchestrator.error_message == "Network error"

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session):
    """Test the _extract_phase method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2020, "value": 21000000}]])),
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2020, "value": 331000000}]])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"USD": 1}})),
        AsyncMock(json=AsyncMock(return_value=[{"cca3": "USA", "name": {"common": "United States"}}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) > 0

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Test the _extract_phase method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"USD": 1}})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) == 0

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Test the _extract_phase method with an error in fetching data."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception, match="Network error"):
        await orchestrator._extract_phase()

def test_merge_data_happy_path(sample_records):
    """Test the _merge_data method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    gdp_data = [{"country": {"id": "USA", "value": "United States"}, "date": 2020, "value": 21000000}]
    population_data = [{"country": {"id": "USA", "value": "United States"}, "date": 2020, "value": 331000000}]
    exchange_rate_data = {"rates": {"USD": 1}}
    country_data = [{"cca3": "USA", "name": {"common": "United States"}}]
    merged_records = orchestrator._merge_data(gdp_data, population_data, exchange_rate_data, country_data)
    assert len(merged_records) == 1
    assert merged_records[0]['country_code'] == 'USA'

def test_merge_data_empty_input():
    """Test the _merge_data method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    merged_records = orchestrator._merge_data([], [], {}, [])
    assert len(merged_records) == 0

def test_transform_phase_happy_path(sample_records):
    """Test the _transform_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = orchestrator._transform_phase(sample_records)
    assert all('gdp_billions' in record and 'gdp_per_capita' in record for record in transformed_records)

def test_transform_phase_empty_input():
    """Test the _transform_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = orchestrator._transform_phase([])
    assert len(transformed_records) == 0

def test_validate_phase_happy_path(sample_records):
    """Test the _validate_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated_records = orchestrator._validate_phase(sample_records)
    assert len(validated_records) == len(sample_records)

def test_validate_phase_empty_input():
    """Test the _validate_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated_records = orchestrator._validate_phase([])
    assert len(validated_records) == 0

def test_validate_phase_error_handling(invalid_records):
    """Test the _validate_phase method with invalid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated_records = orchestrator._validate_phase(invalid_records)
    assert len(validated_records) == 0

@pytest.mark.asyncio
async def test_load_phase_happy_path(mock_db_connection, sample_records):
    """Test the _load_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase(sample_records)
    mock_db_connection.execute.assert_called()

@pytest.mark.asyncio
async def test_load_phase_empty_input(mock_db_connection):
    """Test the _load_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase([])
    mock_db_connection.execute.assert_called_once_with("TRUNCATE TABLE public.fact_economic_indicators")

@pytest.mark.asyncio
async def test_load_phase_error_handling(mock_db_connection):
    """Test the _load_phase method with an error during DB operation."""
    mock_db_connection.execute.side_effect = Exception("DB error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception, match="DB error"):
        await orchestrator._load_phase([{"country_code": "USA", "year": 2020}])