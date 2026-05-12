import pytest
from unittest import mock

@pytest.fixture
def sample_records():
    """Provides a list of valid records matching the fact_economic_indicators schema."""
    return [
        {"id": 1, "name": "Country A", "gdp": 1000.0, "population": 5000000, "exchange_rate": 1.0},
        {"id": 2, "name": "Country B", "gdp": 2000.0, "population": 10000000, "exchange_rate": 1.5},
        {"id": 3, "name": "Country C", "gdp": 1500.0, "population": 7500000, "exchange_rate": 0.8},
    ]

@pytest.fixture
def empty_records():
    """Provides an empty list of records."""
    return []

@pytest.fixture
def invalid_records():
    """Provides a list of records with missing or null required fields."""
    return [
        {"id": None, "name": "Country D", "gdp": 3000.0, "population": 2000000, "exchange_rate": 1.2},
        {"id": "invalid_type", "name": None, "gdp": 2500.0, "population": 3000000, "exchange_rate": 1.1},
        {},
    ]

@pytest.fixture
async def mock_db_connection():
    """Mocks asyncpg.Connection or sqlalchemy Engine connection."""
    with mock.patch('asyncpg.connect', create=True) as mock_connect:
        mock_conn = mock.AsyncMock()
        mock_conn.fetch.return_value = []
        mock_conn.execute.return_value = None
        mock_conn.fetchrow.return_value = None
        mock_conn.fetchval.return_value = None
        mock_connect.return_value = mock_conn
        yield mock_conn

@pytest.fixture
async def mock_http_session():
    """Mocks aiohttp.ClientSession."""
    with mock.patch('aiohttp.ClientSession', create=True) as mock_session:
        mock_instance = mock.AsyncMock()
        mock_instance.get.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_instance.post.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_session.return_value = mock_instance
        yield mock_instance