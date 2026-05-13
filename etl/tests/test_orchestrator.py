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
        AsyncMock(json=AsyncMock(return_value=[{"country.id": "USA", "country.value": "United States", "date": "2020", "value": 21000000000, "population": 331000000}])),
        AsyncMock(json=AsyncMock(return_value=[{"country.id": "USA", "country.value": "United States", "date": "2020", "value": 331000000}])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"EUR": 0.85}})),
        AsyncMock(json=AsyncMock(return_value=[{"name": {"common": "United States"}}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    await orchestrator.run()
    assert orchestrator.status == 'success'
    assert orchestrator.rows_extracted > 0

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session, mock_db_connection):
    """Test the run method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[])),
        AsyncMock(json=AsyncMock(return_value=[])),
        AsyncMock(json=AsyncMock(return_value={"rates": {}})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    await orchestrator.run()
    assert orchestrator.status == 'partial'
    assert orchestrator.rows_extracted == 0

@pytest.mark.asyncio
async def test_run_error_handling(mock_http_session, mock_db_connection):
    """Test the run method with an error during extraction."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    await orchestrator.run()
    assert orchestrator.status == 'failed'
    assert orchestrator.error_message == "Network error"

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session):
    """Test the _extract_phase method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{"country.id": "USA", "country.value": "United States", "date": "2020", "value": 21000000000, "population": 331000000}])),
        AsyncMock(json=AsyncMock(return_value=[{"country.id": "USA", "country.value": "United States", "date": "2020", "value": 331000000}])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"EUR": 0.85}})),
        AsyncMock(json=AsyncMock(return_value=[{"name": {"common": "United States"}}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    records = await orchestrator._extract_phase()
    assert len(records) > 0
    assert orchestrator.rows_extracted > 0

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Test the _extract_phase method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[])),
        AsyncMock(json=AsyncMock(return_value=[])),
        AsyncMock(json=AsyncMock(return_value={"rates": {}})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    records = await orchestrator._extract_phase()
    assert len(records) == 0
    assert orchestrator.rows_extracted == 0

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Test the _extract_phase method with an error during extraction."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    records = await orchestrator._extract_phase()
    assert len(records) == 0
    assert orchestrator.status == 'partial'

@pytest.mark.asyncio
async def test_transform_phase_happy_path(sample_records):
    """Test the _transform_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = await orchestrator._transform_phase(sample_records)
    assert len(transformed_records) == len(sample_records)

@pytest.mark.asyncio
async def test_transform_phase_empty_input():
    """Test the _transform_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = await orchestrator._transform_phase([])
    assert len(transformed_records) == 0

@pytest.mark.asyncio
async def test_transform_phase_error_handling(invalid_records):
    """Test the _transform_phase method with invalid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(KeyError):
        await orchestrator._transform_phase(invalid_records)

@pytest.mark.asyncio
async def test_validate_phase_happy_path(sample_records):
    """Test the _validate_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._validate_phase(sample_records)

@pytest.mark.asyncio
async def test_validate_phase_empty_input():
    """Test the _validate_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._validate_phase([])

@pytest.mark.asyncio
async def test_validate_phase_error_handling(invalid_records):
    """Test the _validate_phase method with invalid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(ValueError):
        await orchestrator._validate_phase(invalid_records)

@pytest.mark.asyncio
async def test_load_phase_happy_path(mock_db_connection, sample_records):
    """Test the _load_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    await orchestrator._load_phase(sample_records)
    assert orchestrator.rows_loaded == len(sample_records)

@pytest.mark.asyncio
async def test_load_phase_empty_input(mock_db_connection):
    """Test the _load_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    await orchestrator._load_phase([])
    assert orchestrator.rows_loaded == 0

@pytest.mark.asyncio
async def test_load_phase_error_handling(mock_db_connection, invalid_records):
    """Test the _load_phase method with invalid data."""
    orchestrator = PipelineOrchestrator(db_config={"user": "user", "password": "password", "database": "db", "host": "localhost"})
    with pytest.raises(Exception):
        await orchestrator._load_phase(invalid_records)