try:
    from pipeline.orchestrator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_run_happy_path(mock_http_session, mock_db_connection):
    """Tests the run method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=[{"country": {"id": "USA"}, "value": 21000000000, "year": 2020, "population": 331000000}])) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    await orchestrator.run()
    assert orchestrator.metrics['rows_extracted'] == 4
    assert orchestrator.metrics['rows_loaded'] == 4
    assert len(orchestrator.metrics['errors']) == 0

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session, mock_db_connection):
    """Tests the run method with no data."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=[])) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    await orchestrator.run()
    assert orchestrator.metrics['rows_extracted'] == 0
    assert orchestrator.metrics['rows_loaded'] == 0
    assert len(orchestrator.metrics['errors']) == 0

@pytest.mark.asyncio
async def test_run_error_handling(mock_http_session, mock_db_connection):
    """Tests the run method with an error during execution."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=500) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    await orchestrator.run()
    assert orchestrator.metrics['rows_extracted'] == 0
    assert orchestrator.metrics['rows_loaded'] == 0
    assert len(orchestrator.metrics['errors']) == 1

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session):
    """Tests the _extract_phase method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=[{"country": {"id": "USA"}, "value": 21000000000, "year": 2020, "population": 331000000}])) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) == 4

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Tests the _extract_phase method with no data."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=[])) for _ in range(4)
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) == 0

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Tests the _extract_phase method with an error during fetching."""
    mock_http_session.get.side_effect = AsyncMock(status=500)
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._extract_phase()

@pytest.mark.asyncio
async def test_transform_phase_happy_path(sample_records):
    """Tests the _transform_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = await orchestrator._transform_phase(sample_records)
    assert len(transformed_records) == len(sample_records)

@pytest.mark.asyncio
async def test_transform_phase_empty_input(empty_records):
    """Tests the _transform_phase method with no data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = await orchestrator._transform_phase(empty_records)
    assert len(transformed_records) == 0

@pytest.mark.asyncio
async def test_transform_phase_error_handling(invalid_records):
    """Tests the _transform_phase method with invalid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(KeyError):
        await orchestrator._transform_phase(invalid_records)

@pytest.mark.asyncio
async def test_validate_phase_happy_path(sample_records):
    """Tests the _validate_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._validate_phase(sample_records)

@pytest.mark.asyncio
async def test_validate_phase_empty_input(empty_records):
    """Tests the _validate_phase method with no data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._validate_phase(empty_records)

@pytest.mark.asyncio
async def test_validate_phase_error_handling(invalid_records):
    """Tests the _validate_phase method with invalid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(ValueError):
        await orchestrator._validate_phase(invalid_records)

@pytest.mark.asyncio
async def test_load_phase_happy_path(sample_records, mock_db_connection):
    """Tests the _load_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    await orchestrator._load_phase(sample_records)
    assert orchestrator.metrics['rows_loaded'] == len(sample_records)

@pytest.mark.asyncio
async def test_load_phase_empty_input(empty_records, mock_db_connection):
    """Tests the _load_phase method with no data."""
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    await orchestrator._load_phase(empty_records)
    assert orchestrator.metrics['rows_loaded'] == 0

@pytest.mark.asyncio
async def test_load_phase_error_handling(sample_records, mock_db_connection):
    """Tests the _load_phase method with an error during loading."""
    mock_db_connection.execute.side_effect = Exception("DB error")
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    with pytest.raises(Exception):
        await orchestrator._load_phase(sample_records)

@pytest.mark.asyncio
async def test_audit_pipeline_run_happy_path(mock_db_connection):
    """Tests the _audit_pipeline_run method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    await orchestrator._audit_pipeline_run(0.0, 1.0, 'success')
    mock_db_connection.execute.assert_called_once()

@pytest.mark.asyncio
async def test_audit_pipeline_run_error_handling(mock_db_connection):
    """Tests the _audit_pipeline_run method with an error during auditing."""
    mock_db_connection.execute.side_effect = Exception("DB error")
    orchestrator = PipelineOrchestrator(db_config={"host": "localhost", "database": "test", "user": "user", "password": "password"})
    with pytest.raises(Exception):
        await orchestrator._audit_pipeline_run(0.0, 1.0, 'success')