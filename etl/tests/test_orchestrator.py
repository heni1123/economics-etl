try:
    from pipeline.orchestrator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_run_happy_path(mock_http_session, mock_db_connection):
    """Test run method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2021, "value": 21000000}]])),
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2021, "value": 331000000}]])),
        AsyncMock(json=AsyncMock(return_value={"USD": 1})),
        AsyncMock(json=AsyncMock(return_value=[{"cca3": "USA", "name": {"common": "United States"}}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'success'

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session, mock_db_connection):
    """Test run method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value={"USD": 1})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'success'

@pytest.mark.asyncio
async def test_run_error_handling(mock_http_session, mock_db_connection):
    """Test run method with an error during execution."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'failed'
    assert orchestrator.error_message == "Network error"

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session):
    """Test extract_phase method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2021, "value": 21000000}]])),
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country": {"id": "USA", "value": "United States"}, "date": 2021, "value": 331000000}]])),
        AsyncMock(json=AsyncMock(return_value={"USD": 1})),
        AsyncMock(json=AsyncMock(return_value=[{"cca3": "USA", "name": {"common": "United States"}}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) > 0

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Test extract_phase method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value={"USD": 1})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) == 0

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Test extract_phase method with an error during extraction."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._extract_phase()

def test_combine_data_happy_path(sample_records):
    """Test combine_data method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    combined = orchestrator._combine_data(sample_records['gdp_data'], sample_records['population_data'], {}, {})
    assert len(combined) > 0

def test_combine_data_empty_input():
    """Test combine_data method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    combined = orchestrator._combine_data([], [], {}, {})
    assert len(combined) == 0

@pytest.mark.asyncio
async def test_transform_phase_happy_path(sample_records):
    """Test transform_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed = await orchestrator._transform_phase(sample_records['valid_records'])
    assert all('gdp_billions' in record for record in transformed)

@pytest.mark.asyncio
async def test_transform_phase_empty_input():
    """Test transform_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed = await orchestrator._transform_phase([])
    assert len(transformed) == 0

@pytest.mark.asyncio
async def test_validate_phase_happy_path(sample_records):
    """Test validate_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated = await orchestrator._validate_phase(sample_records['valid_records'])
    assert len(validated) == len(sample_records['valid_records'])

@pytest.mark.asyncio
async def test_validate_phase_empty_input():
    """Test validate_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated = await orchestrator._validate_phase([])
    assert len(validated) == 0

@pytest.mark.asyncio
async def test_load_phase_happy_path(mock_db_connection, sample_records):
    """Test load_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase(sample_records['valid_records'])
    mock_db_connection.execute.assert_called()

@pytest.mark.asyncio
async def test_load_phase_empty_input(mock_db_connection):
    """Test load_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase([])
    mock_db_connection.execute.assert_called_once_with("TRUNCATE TABLE public.fact_economic_indicators")

@pytest.mark.asyncio
async def test_load_phase_error_handling(mock_db_connection, sample_records):
    """Test load_phase method with an error during loading."""
    mock_db_connection.execute.side_effect = Exception("DB error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._load_phase(sample_records['valid_records'])