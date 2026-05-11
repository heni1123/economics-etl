try:
    from pipeline.orchestrator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_run_happy_path(mock_db_connection, mock_http_session, sample_records):
    """Test run method with valid input, expect success."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records))
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    # Add assertions to verify the expected behavior

@pytest.mark.asyncio
async def test_run_empty_input(mock_db_connection, mock_http_session, empty_records):
    """Test run method with empty input, expect success."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=empty_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=empty_records))
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    # Add assertions to verify the expected behavior

@pytest.mark.asyncio
async def test_run_error_handling(mock_db_connection, mock_http_session):
    """Test run method error handling, expect failure."""
    mock_http_session.get.side_effect = AsyncMock(side_effect=Exception("Network error"))
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator.run()
    # Add assertions to verify the expected behavior

@pytest.mark.asyncio
async def test_connect_db_happy_path(mock_db_connection):
    """Test _connect_db method, expect successful connection."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._connect_db()
    assert orchestrator.connection is not None

@pytest.mark.asyncio
async def test_disconnect_db_happy_path(mock_db_connection):
    """Test _disconnect_db method, expect successful disconnection."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._connect_db()
    await orchestrator._disconnect_db()
    assert orchestrator.connection is None

@pytest.mark.asyncio
async def test_extract_phase_happy_path(mock_http_session, sample_records):
    """Test _extract_phase method with valid input, expect records."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=sample_records))
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) > 0

@pytest.mark.asyncio
async def test_extract_phase_empty_input(mock_http_session, empty_records):
    """Test _extract_phase method with empty input, expect empty records."""
    mock_http_session.get.side_effect = [
        AsyncMock(status=200, json=AsyncMock(return_value=empty_records)),
        AsyncMock(status=200, json=AsyncMock(return_value=empty_records))
    ]
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._extract_phase()
    assert len(records) == 0

@pytest.mark.asyncio
async def test_fetch_data_happy_path(mock_http_session, sample_records):
    """Test _fetch_data method with valid URL, expect records."""
    mock_http_session.get.return_value = AsyncMock(status=200, json=AsyncMock(return_value=sample_records))
    orchestrator = PipelineOrchestrator(db_config={})
    records = await orchestrator._fetch_data(mock_http_session, "http://test.url")
    assert len(records) > 0

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test _fetch_data method error handling, expect exception."""
    mock_http_session.get.side_effect = Exception("Fetch error")
    orchestrator = PipelineOrchestrator(db_config={})
    with pytest.raises(Exception):
        await orchestrator._fetch_data(mock_http_session, "http://test.url")

@pytest.mark.asyncio
async def test_transform_phase_happy_path(sample_records):
    """Test _transform_phase method with valid records, expect transformed records."""
    orchestrator = PipelineOrchestrator(db_config={})
    transformed = await orchestrator._transform_phase(sample_records)
    assert len(transformed) == len(sample_records)

@pytest.mark.asyncio
async def test_validate_phase_happy_path(sample_records):
    """Test _validate_phase method with valid records, expect all records validated."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated = await orchestrator._validate_phase(sample_records)
    assert len(validated) == len(sample_records)

@pytest.mark.asyncio
async def test_validate_phase_invalid_records(invalid_records):
    """Test _validate_phase method with invalid records, expect no records validated."""
    orchestrator = PipelineOrchestrator(db_config={})
    validated = await orchestrator._validate_phase(invalid_records)
    assert len(validated) == 0

@pytest.mark.asyncio
async def test_load_phase_happy_path(mock_db_connection, sample_records):
    """Test _load_phase method with valid records, expect rows loaded."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._connect_db()
    rows_loaded = await orchestrator._load_phase(sample_records)
    assert rows_loaded == len(sample_records)

@pytest.mark.asyncio
async def test_log_run_happy_path(mock_db_connection):
    """Test _log_run method, expect successful logging."""
    orchestrator = PipelineOrchestrator(db_config={})
    await orchestrator._connect_db()
    await orchestrator._log_run(datetime.utcnow(), 'success', 10)
    # Add assertions to verify the expected behavior