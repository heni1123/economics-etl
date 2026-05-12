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
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country_code": "USA", "year": 2020, "gdp_usd": 21000000, "population": 331000000}]])),
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country_code": "USA", "year": 2020, "population": 331000000}]])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"USD": 1}})),
        AsyncMock(json=AsyncMock(return_value=[{"alpha3Code": "USA"}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'success'
    assert orchestrator.rows_loaded > 0

@pytest.mark.asyncio
async def test_run_empty_input(mock_http_session, mock_db_connection):
    """Test run method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value={"rates": {}})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    assert orchestrator.status == 'success'
    assert orchestrator.rows_loaded == 0

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
    """Test _extract_phase method with valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country_code": "USA", "year": 2020, "gdp_usd": 21000000}]])),
        AsyncMock(json=AsyncMock(return_value=[{}, [{"country_code": "USA", "year": 2020, "population": 331000000}]])),
        AsyncMock(json=AsyncMock(return_value={"rates": {"USD": 1}})),
        AsyncMock(json=AsyncMock(return_value=[{"alpha3Code": "USA"}])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) > 0

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session):
    """Test _extract_phase method with empty data."""
    mock_http_session.get.side_effect = [
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value=[{}, []])),
        AsyncMock(json=AsyncMock(return_value={"rates": {}})),
        AsyncMock(json=AsyncMock(return_value=[])),
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) == 0

@pytest.mark.asyncio
async def test_extract_phase_error_handling(mock_http_session):
    """Test _extract_phase method with an error during extraction."""
    mock_http_session.get.side_effect = Exception("Network error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._extract_phase()

def test_merge_data_happy_path(sample_records):
    """Test _merge_data method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    merged_data = orchestrator._merge_data(sample_records, sample_records, sample_records, sample_records)
    assert len(merged_data) > 0

def test_merge_data_empty_input():
    """Test _merge_data method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    merged_data = orchestrator._merge_data([], [], [], [])
    assert len(merged_data) == 0

def test_transform_phase_happy_path(sample_records):
    """Test _transform_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = orchestrator._transform_phase(sample_records)
    assert len(transformed_records) == len(sample_records)

def test_transform_phase_empty_input():
    """Test _transform_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed_records = orchestrator._transform_phase([])
    assert len(transformed_records) == 0

def test_validate_phase_happy_path(sample_records):
    """Test _validate_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated_records = orchestrator._validate_phase(sample_records)
    assert len(validated_records) == len(sample_records)

def test_validate_phase_empty_input():
    """Test _validate_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated_records = orchestrator._validate_phase([])
    assert len(validated_records) == 0

def test_is_valid_happy_path():
    """Test _is_valid method with valid record."""
    orchestrator = PipelineOrchestrator(db_config={})
    valid_record = {"country_code": "USA", "year": 2020, "gdp_usd": 21000000, "population": 331000000}
    assert orchestrator._is_valid(valid_record) is True

def test_is_valid_invalid_record():
    """Test _is_valid method with invalid record."""
    orchestrator = PipelineOrchestrator(db_config={})
    invalid_record = {"country_code": "USA", "year": None, "gdp_usd": 21000000, "population": 331000000}
    assert orchestrator._is_valid(invalid_record) is False

@pytest.mark.asyncio
async def test_load_phase_happy_path(mock_db_connection, sample_records):
    """Test _load_phase method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase(sample_records)
    assert orchestrator.rows_loaded == len(sample_records)

@pytest.mark.asyncio
async def test_load_phase_empty_input(mock_db_connection):
    """Test _load_phase method with empty data."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._load_phase([])
    assert orchestrator.rows_loaded == 0

@pytest.mark.asyncio
async def test_load_phase_error_handling(mock_db_connection):
    """Test _load_phase method with an error during loading."""
    mock_db_connection.execute.side_effect = Exception("DB error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._load_phase([{"country_code": "USA", "year": 2020, "gdp_usd": 21000000, "population": 331000000}])

@pytest.mark.asyncio
async def test_log_audit_happy_path(mock_db_connection):
    """Test _log_audit method with valid data."""
    orchestrator = PipelineOrchestrator(db_config={})
    orchestrator.start_ts = datetime.utcnow()
    orchestrator.end_ts = datetime.utcnow()
    orchestrator.rows_loaded = 1
    orchestrator.status = 'success'
    await orchestrator._log_audit()
    # Check if the audit log was called
    mock_db_connection.execute.assert_called_once()

@pytest.mark.asyncio
async def test_log_audit_error_handling(mock_db_connection):
    """Test _log_audit method with an error during logging."""
    mock_db_connection.execute.side_effect = Exception("DB error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._log_audit()