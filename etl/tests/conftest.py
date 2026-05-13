import pytest
from unittest import mock

@pytest.fixture
def sample_records():
    """Provides a list of valid records matching the fact_economic_indicators schema."""
    return [
        {
            "country_code": "USA",
            "country_name": "United States",
            "year": "2021",
            "gdp_usd": "22 trillion",
            "gdp_billions": "22000",
            "population": "331 million",
            "gdp_per_capita": "67000",
            "gdp_growth_yoy": "5.7%",
            "population_growth_yoy": "0.7%",
            "economic_size_category": "Large",
            "population_category": "High",
            "development_indicator": "Developed",
            "region": "Americas",
            "subregion": "North America",
            "capital_city": "Washington, D.C."
        },
        {
            "country_code": "CAN",
            "country_name": "Canada",
            "year": "2021",
            "gdp_usd": "2 trillion",
            "gdp_billions": "2000",
            "population": "38 million",
            "gdp_per_capita": "52000",
            "gdp_growth_yoy": "4.5%",
            "population_growth_yoy": "1.1%",
            "economic_size_category": "Large",
            "population_category": "High",
            "development_indicator": "Developed",
            "region": "Americas",
            "subregion": "North America",
            "capital_city": "Ottawa"
        },
        {
            "country_code": "IND",
            "country_name": "India",
            "year": "2021",
            "gdp_usd": "3 trillion",
            "gdp_billions": "3000",
            "population": "1.366 billion",
            "gdp_per_capita": "2200",
            "gdp_growth_yoy": "9.5%",
            "population_growth_yoy": "1.0%",
            "economic_size_category": "Emerging",
            "population_category": "Medium",
            "development_indicator": "Developing",
            "region": "Asia",
            "subregion": "South Asia",
            "capital_city": "New Delhi"
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
        {"country_code": "XYZ", "country_name": None, "year": "2021"},
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
        mock_instance = mock.AsyncMock()
        mock_instance.get.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_instance.post.return_value = mock.AsyncMock(json=mock.AsyncMock(return_value={}))
        mock_session.return_value = mock_instance
        yield mock_instance

pytest_plugins = ["pytest_asyncio"]
asyncio_mode = "auto"