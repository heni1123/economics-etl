try:
    from pipeline.ingestion import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_fetch_data_happy_path(mock_http_session):
    """Test fetch_data with valid URL."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"data": "some_data"})
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, ingestion.worldbank_gdp_url)
    assert result == {"data": "some_data"}

@pytest.mark.asyncio
async def test_fetch_data_empty_input(mock_http_session):
    """Test fetch_data with empty response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, ingestion.worldbank_gdp_url)
    assert result == {}

@pytest.mark.asyncio
async def test_fetch_data_error_handling(mock_http_session):
    """Test fetch_data handles exceptions."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.fetch_data(mock_http_session, ingestion.worldbank_gdp_url)
    assert result == {}

@pytest.mark.asyncio
async def test_extract_gdp_happy_path(mock_http_session):
    """Test extract_gdp with valid data."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, [{"country": "A", "gdp": 1000}]])
    ingestion = DataIngestion()
    result = await ingestion.extract_gdp()
    assert result == [{"country": "A", "gdp": 1000}]

@pytest.mark.asyncio
async def test_extract_gdp_empty_input(mock_http_session):
    """Test extract_gdp with empty response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}])
    ingestion = DataIngestion()
    result = await ingestion.extract_gdp()
    assert result == []

@pytest.mark.asyncio
async def test_extract_gdp_error_handling(mock_http_session):
    """Test extract_gdp handles exceptions."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.extract_gdp()
    assert result == []

@pytest.mark.asyncio
async def test_extract_population_happy_path(mock_http_session):
    """Test extract_population with valid data."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}, [{"country": "A", "population": 1000000}]])
    ingestion = DataIngestion()
    result = await ingestion.extract_population()
    assert result == [{"country": "A", "population": 1000000}]

@pytest.mark.asyncio
async def test_extract_population_empty_input(mock_http_session):
    """Test extract_population with empty response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{}])
    ingestion = DataIngestion()
    result = await ingestion.extract_population()
    assert result == []

@pytest.mark.asyncio
async def test_extract_population_error_handling(mock_http_session):
    """Test extract_population handles exceptions."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.extract_population()
    assert result == []

@pytest.mark.asyncio
async def test_extract_exchange_rates_happy_path(mock_http_session):
    """Test extract_exchange_rates with valid data."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={"rates": {"EUR": 0.85}})
    ingestion = DataIngestion()
    result = await ingestion.extract_exchange_rates()
    assert result == {"rates": {"EUR": 0.85}}

@pytest.mark.asyncio
async def test_extract_exchange_rates_empty_input(mock_http_session):
    """Test extract_exchange_rates with empty response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={})
    ingestion = DataIngestion()
    result = await ingestion.extract_exchange_rates()
    assert result == {}

@pytest.mark.asyncio
async def test_extract_exchange_rates_error_handling(mock_http_session):
    """Test extract_exchange_rates handles exceptions."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.extract_exchange_rates()
    assert result == {}

@pytest.mark.asyncio
async def test_extract_countries_info_happy_path(mock_http_session):
    """Test extract_countries_info with valid data."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[{"name": "Country A"}])
    ingestion = DataIngestion()
    result = await ingestion.extract_countries_info()
    assert result == [{"name": "Country A"}]

@pytest.mark.asyncio
async def test_extract_countries_info_empty_input(mock_http_session):
    """Test extract_countries_info with empty response."""
    mock_http_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value=[])
    ingestion = DataIngestion()
    result = await ingestion.extract_countries_info()
    assert result == []

@pytest.mark.asyncio
async def test_extract_countries_info_error_handling(mock_http_session):
    """Test extract_countries_info handles exceptions."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    result = await ingestion.extract_countries_info()
    assert result == []

@pytest.mark.asyncio
async def test_run_extraction_happy_path(mock_http_session):
    """Test run_extraction with all valid data."""
    mock_http_session.get.side_effect = [
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value=[{}, [{"country": "A", "gdp": 1000}]])))),
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value=[{}, [{"country": "A", "population": 1000000}]])))),
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value={"rates": {"EUR": 0.85}})))),
        AsyncMock(__aenter__=AsyncMock(return_value=AsyncMock(json=AsyncMock(return_value=[{"name": "Country A"}]))))
    ]
    ingestion = DataIngestion()
    await ingestion.run_extraction()

@pytest.mark.asyncio
async def test_run_extraction_error_handling(mock_http_session):
    """Test run_extraction handles exceptions."""
    mock_http_session.get.side_effect = Exception("Network error")
    ingestion = DataIngestion()
    await ingestion.run_extraction()  # Should not raise an exception