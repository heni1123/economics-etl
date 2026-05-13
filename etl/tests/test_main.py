try:
    from main import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_run_happy_path():
    """Test run method with valid phase and expect success."""
    orchestrator = PipelineOrchestrator()
    result = await orchestrator.run("extract", False)
    assert result["status"] == "success"
    assert result["rows_extracted"] == 1000
    assert result["rows_loaded"] == 1000

@pytest.mark.asyncio
async def test_run_empty_input():
    """Test run method with empty phase and expect success with zero rows."""
    orchestrator = PipelineOrchestrator()
    result = await orchestrator.run("", False)
    assert result["status"] == "success"
    assert result["rows_extracted"] == 0
    assert result["rows_loaded"] == 0

@pytest.mark.asyncio
async def test_run_error_handling():
    """Test run method with an invalid phase and expect failure."""
    orchestrator = PipelineOrchestrator()
    with mock.patch('time.time', side_effect=Exception("Timeout")):
        result = await orchestrator.run("invalid_phase", False)
        assert result["status"] == "failed"
        assert "Timeout" in result["error_message"]

@pytest.mark.asyncio
async def test_main_happy_path():
    """Test main function with valid inputs and expect exit code 0."""
    with mock.patch('main.PipelineOrchestrator.run', return_value={"rows_extracted": 1000, "rows_loaded": 1000, "status": "success", "error_message": "", "duration": 1.0}):
        exit_code = await main("config_path", False, "all")
        assert exit_code == 0

@pytest.mark.asyncio
async def test_main_empty_input():
    """Test main function with no rows extracted or loaded and expect exit code 1."""
    with mock.patch('main.PipelineOrchestrator.run', return_value={"rows_extracted": 0, "rows_loaded": 0, "status": "success", "error_message": "", "duration": 1.0}):
        exit_code = await main("config_path", False, "all")
        assert exit_code == 1

@pytest.mark.asyncio
async def test_main_error_handling():
    """Test main function with failure in orchestrator and expect exit code 2."""
    with mock.patch('main.PipelineOrchestrator.run', return_value={"rows_extracted": 1000, "rows_loaded": 1000, "status": "failed", "error_message": "Error", "duration": 1.0}):
        exit_code = await main("config_path", False, "all")
        assert exit_code == 2

def test_signal_handler():
    """Test signal handler for graceful shutdown."""
    with mock.patch('sys.exit') as mock_exit:
        signal_handler(0, None)
        mock_exit.assert_called_once_with(0)