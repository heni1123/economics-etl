import pytest
from unittest import mock

@pytest.fixture
def sample_records():
    """Provides a list of valid records matching the fact_economic_indicators schema."""
    return [
        {
            "country_code": "USA",
            "country_name": "United States",
            "year": "2022",
            "gdp_usd": "22675271",
            "gdp_billions": "22675.271",
            "population": "331002651",
            "gdp_per_capita": "68351",
            "gdp_growth_yoy": "5.7",
            "population_growth_yoy": "0.1",
            "economic_size_category": "High income",
            "population_category": "Large",
            "development_indicator": "Developed",
            "region": "North America",
            "subregion": "Northern America",
            "capital_city": "Washington, D.C."
        },
        {
            "country_code": "CAN",
            "country_name": "Canada",
            "year": "2022",
            "gdp_usd": "2000000",
            "gdp_billions": "2000",
            "population": "37742154",
            "gdp_per_capita": "52900",
            "gdp_growth_yoy": "4.6",
            "population_growth_yoy": "0.9",
            "economic_size_category": "High income",
            "population_category": "Medium",
            "development_indicator": "Developed",
            "region": "North America",
            "subregion": "Northern America",
            "capital_city": "Ottawa"
        }
    ]

@pytest.fixture
def empty_records():
    """Provides an empty list of records."""
    return []

@pytest.fixture
def invalid_records():
    """Provides a list of records with missing/null required fields."""
    return [
        {"country_code": None, "country_name": "Invalid Country"},
        {"country_code": "XYZ", "year": "2022"},
        {}
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
        mock_session_instance = mock.AsyncMock()
        mock_session_instance.get.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_session_instance.post.return_value.__aenter__.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_session.return_value = mock_session_instance
        yield mock_session_instance