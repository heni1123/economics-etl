try:
    from pipeline.orchestrator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_run_happy_path(mock_http_session, mock_db_connection, sample_records):
    """Test run method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{"country": {"id": "USA", "value": "United States"}, "date": "2020", "value": 21000000}])) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator("mock_db_url")
    await orchestrator.run()
    assert orchestrator.status == 'success'
    assert orchestrator.rows_loaded > 0

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session, mock_db_connection, empty_records):
    """Test run method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[])) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator("mock_db_url")
    await orchestrator.run()
    assert orchestrator.status == 'success'
    assert orchestrator.rows_loaded == 0

@pytest.mark.asyncio
async def test_run_error_handling(mock_http_session, mock_db_connection):
    """Test run method error handling."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator("mock_db_url")
    await orchestrator.run()
    assert orchestrator.status == 'failed'
    assert orchestrator.error_message == "Network error"

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session, sample_records):
    """Test _extract_phase method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{"country": {"id": "USA", "value": "United States"}, "date": "2020", "value": 21000000}])),
        AsyncMock(json=AsyncMock(return_value=[{"country": {"id": "USA", "value": "United States"}, "date": "2020", "value": 331000000}])),
        AsyncMock(json=AsyncMock(return_value=[{"rate": 1.0}])),
        AsyncMock(json=AsyncMock(return_value=[{"id": "USA", "name": "United States"}]))
    ]
    orchestrator = PipelineOrchestrator("mock_db_url")
    records = await orchestrator._extract_phase()
    assert len(records) > 0

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Test _extract_phase method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[])) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator("mock_db_url")
    records = await orchestrator._extract_phase()
    assert len(records) == 0

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Test _extract_phase method error handling."""
    mock_http_session.get.side_effect = Exception("Fetch error")
    orchestrator = PipelineOrchestrator("mock_db_url")
    with pytest.raises(Exception):
        await orchestrator._extract_phase()

def test_combine_data_happy_path(sample_records):
    """Test _combine_data method with valid data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    combined = orchestrator._combine_data(sample_records['gdp'], sample_records['population'])
    assert len(combined) > 0

def test_combine_data_empty_input():
    """Test _combine_data method with empty data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    combined = orchestrator._combine_data([], [])
    assert len(combined) == 0

@pytest.mark.asyncio
async def test_transform_phase_happy_path(sample_records):
    """Test _transform_phase method with valid data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    transformed = await orchestrator._transform_phase(sample_records['valid'])
    assert all('gdp_billions' in record for record in transformed)

@pytest.mark.asyncio
async def test_transform_phase_empty_input():
    """Test _transform_phase method with empty data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    transformed = await orchestrator._transform_phase([])
    assert len(transformed) == 0

@pytest.mark.asyncio
async def test_validate_phase_happy_path(sample_records):
    """Test _validate_phase method with valid data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    validated = await orchestrator._validate_phase(sample_records['valid'])
    assert len(validated) == len(sample_records['valid'])

@pytest.mark.asyncio
async def test_validate_phase_empty_input():
    """Test _validate_phase method with empty data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    validated = await orchestrator._validate_phase([])
    assert len(validated) == 0

@pytest.mark.asyncio
async def test_load_phase_happy_path(mock_db_connection, sample_records):
    """Test _load_phase method with valid data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    await orchestrator._load_phase(sample_records['valid'])
    # Check if the mock DB connection was called
    mock_db_connection.execute.assert_called()

@pytest.mark.asyncio
async def test_load_phase_empty_input(mock_db_connection):
    """Test _load_phase method with empty data."""
    orchestrator = PipelineOrchestrator("mock_db_url")
    await orchestrator._load_phase([])
    # Check if the mock DB connection was not called
    mock_db_connection.execute.assert_not_called()