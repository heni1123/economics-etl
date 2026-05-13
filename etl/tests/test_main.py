try:
    from main import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock

@pytest.mark.asyncio
async def test_extract_happy_path(mock_db_connection):
    """Test extract method with valid input."""
    pipeline = ETLPipeline("config_path", False, "extract")
    await pipeline.extract()
    assert pipeline.execution_summary["total_rows_extracted"] == 1000

@pytest.mark.asyncio
async def test_extract_empty_input():
    """Test extract method with empty input."""
    pipeline = ETLPipeline("", False, "extract")
    await pipeline.extract()
    assert pipeline.execution_summary["total_rows_extracted"] == 1000

@pytest.mark.asyncio
async def test_extract_error_handling(mock_db_connection):
    """Test extract method error handling."""
    pipeline = ETLPipeline("config_path", False, "extract")
    with mock.patch('asyncio.sleep', side_effect=Exception("Simulated error")):
        await pipeline.extract()
        assert pipeline.execution_summary["total_rows_extracted"] == 0

@pytest.mark.asyncio
async def test_transform_happy_path(mock_db_connection):
    """Test transform method with valid input."""
    pipeline = ETLPipeline("config_path", False, "transform")
    await pipeline.transform()
    assert "transform" in pipeline.execution_summary["phase_durations"]

@pytest.mark.asyncio
async def test_transform_empty_input():
    """Test transform method with empty input."""
    pipeline = ETLPipeline("", False, "transform")
    await pipeline.transform()
    assert "transform" in pipeline.execution_summary["phase_durations"]

@pytest.mark.asyncio
async def test_transform_error_handling(mock_db_connection):
    """Test transform method error handling."""
    pipeline = ETLPipeline("config_path", False, "transform")
    with mock.patch('asyncio.sleep', side_effect=Exception("Simulated error")):
        await pipeline.transform()
        assert "transform" not in pipeline.execution_summary["phase_durations"]

@pytest.mark.asyncio
async def test_load_happy_path(mock_db_connection):
    """Test load method with valid input."""
    pipeline = ETLPipeline("config_path", False, "load")
    await pipeline.load()
    assert pipeline.execution_summary["total_rows_loaded"] == 1000

@pytest.mark.asyncio
async def test_load_empty_input():
    """Test load method with empty input."""
    pipeline = ETLPipeline("", False, "load")
    await pipeline.load()
    assert pipeline.execution_summary["total_rows_loaded"] == 1000

@pytest.mark.asyncio
async def test_load_error_handling(mock_db_connection):
    """Test load method error handling."""
    pipeline = ETLPipeline("config_path", False, "load")
    with mock.patch('asyncio.sleep', side_effect=Exception("Simulated error")):
        await pipeline.load()
        assert pipeline.execution_summary["total_rows_loaded"] == 0

@pytest.mark.asyncio
async def test_run_happy_path(mock_db_connection):
    """Test run method with valid input."""
    pipeline = ETLPipeline("config_path", False, "full")
    await pipeline.run()
    assert pipeline.execution_summary["total_rows_extracted"] == 1000
    assert pipeline.execution_summary["total_rows_loaded"] == 1000

@pytest.mark.asyncio
async def test_run_empty_input():
    """Test run method with empty input."""
    pipeline = ETLPipeline("", False, "full")
    await pipeline.run()
    assert pipeline.execution_summary["total_rows_extracted"] == 1000
    assert pipeline.execution_summary["total_rows_loaded"] == 1000

@pytest.mark.asyncio
async def test_run_error_handling(mock_db_connection):
    """Test run method error handling."""
    pipeline = ETLPipeline("config_path", False, "full")
    with mock.patch('asyncio.sleep', side_effect=Exception("Simulated error")):
        await pipeline.run()
        assert pipeline.execution_summary["total_rows_extracted"] == 0
        assert pipeline.execution_summary["total_rows_loaded"] == 0

@pytest.mark.asyncio
async def test_main_happy_path(mock_db_connection):
    """Test main function with valid input."""
    result = await main("config_path", False, "full")
    assert result == 0

@pytest.mark.asyncio
async def test_main_empty_input():
    """Test main function with empty input."""
    result = await main("", False, "full")
    assert result == 0

@pytest.mark.asyncio
async def test_main_error_handling(mock_db_connection):
    """Test main function error handling."""
    with mock.patch('main.ETLPipeline.run', side_effect=Exception("Simulated error")):
        result = await main("config_path", False, "full")
        assert result == 2

def test_signal_handler():
    """Test signal handler for graceful shutdown."""
    with mock.patch('main.exit') as mock_exit:
        signal_handler(None, None)
        mock_exit.assert_called_once()