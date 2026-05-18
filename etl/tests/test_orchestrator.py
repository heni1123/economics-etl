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
        AsyncMock(json=AsyncMock(return_value=[{}, {}])),
        AsyncMock(json=AsyncMock(return_value=[{}, {}])),
        AsyncMock(json=AsyncMock(return_value=[{}])),
        AsyncMock(json=AsyncMock(return_value=[{}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.metrics['rows_extracted'] > 0
    assert orchestrator.metrics['rows_loaded'] == 0  # Dry run by default

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session, mock_db_connection):
    """Test run method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[[], []])),
        AsyncMock(json=AsyncMock(return_value=[[], []])),
        AsyncMock(json=AsyncMock(return_value=[[]])),
        AsyncMock(json=AsyncMock(return_value=[[]])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.metrics['rows_extracted'] == 0
    assert orchestrator.metrics['rows_loaded'] == 0

@pytest.mark.asyncio
async def test_run_error_handling(mock_http_session, mock_db_connection):
    """Test run method error handling."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.metrics['errors'] == ["Network error"]

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session):
    """Test extract_phase method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, {}])),
        AsyncMock(json=AsyncMock(return_value=[{}, {}])),
        AsyncMock(json=AsyncMock(return_value=[{}])),
        AsyncMock(json=AsyncMock(return_value=[{}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) == 4  # Expecting 4 datasets

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Test extract_phase method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[[], []])),
        AsyncMock(json=AsyncMock(return_value=[[], []])),
        AsyncMock(json=AsyncMock(return_value=[[]])),
        AsyncMock(json=AsyncMock(return_value=[[]])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert all(len(record) == 0 for record in records)

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Test extract_phase method error handling."""
    mock_http_session.get.side_effect = Exception("Fetch error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._extract_phase()

@pytest.mark.asyncio
async def test_transform_phase_happy_path(sample_records):
    """Test transform_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed = await orchestrator._transform_phase(sample_records)
    assert isinstance(transformed, list)
    assert len(transformed) > 0

@pytest.mark.asyncio
async def test_transform_phase_empty_input(empty_records):
    """Test transform_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed = await orchestrator._transform_phase(empty_records)
    assert transformed == []

@pytest.mark.asyncio
async def test_transform_phase_error_handling(invalid_records):
    """Test transform_phase method error handling."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(KeyError):
        await orchestrator._transform_phase(invalid_records)

@pytest.mark.asyncio
async def test_validate_phase_happy_path(sample_records):
    """Test validate_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._validate_phase(sample_records)

@pytest.mark.asyncio
async def test_validate_phase_empty_input(empty_records):
    """Test validate_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._validate_phase(empty_records)

@pytest.mark.asyncio
async def test_validate_phase_error_handling(invalid_records):
    """Test validate_phase method error handling."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(ValueError):
        await orchestrator._validate_phase(invalid_records)

@pytest.mark.asyncio
async def test_load_phase_happy_path(sample_records, mock_db_connection):
    """Test load_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase(sample_records)
    assert orchestrator.metrics['rows_loaded'] == len(sample_records)

@pytest.mark.asyncio
async def test_load_phase_empty_input(empty_records, mock_db_connection):
    """Test load_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase(empty_records)
    assert orchestrator.metrics['rows_loaded'] == 0

@pytest.mark.asyncio
async def test_load_phase_error_handling(invalid_records, mock_db_connection):
    """Test load_phase method error handling."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._load_phase(invalid_records)

@pytest.mark.asyncio
async def test_audit_pipeline_run_happy_path(mock_db_connection):
    """Test audit_pipeline_run method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._audit_pipeline_run(datetime.utcnow(), datetime.utcnow(), 'success')

@pytest.mark.asyncio
async def test_audit_pipeline_run_error_handling(mock_db_connection):
    """Test audit_pipeline_run method error handling."""
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._audit_pipeline_run(datetime.utcnow(), datetime.utcnow(), 'success')