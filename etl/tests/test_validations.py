import pytest
from your_module import validate_gdp_growth_yoy, validate_population_growth_yoy, categorize_economy

def test_validate_gdp_growth_yoy():
    assert validate_gdp_growth_yoy({'gdp_usd': 2000, 'gdp_usd_prev': 1000}) == 100.0
    assert validate_gdp_growth_yoy({'gdp_usd': 1500, 'gdp_usd_prev': 2000}) == -25.0
    assert validate_gdp_growth_yoy({'gdp_usd': 1000, 'gdp_usd_prev': 0}) == 0.0
    assert validate_gdp_growth_yoy({'gdp_usd': 0, 'gdp_usd_prev': 0}) == 0.0
    assert validate_gdp_growth_yoy({'gdp_usd': 5000, 'gdp_usd_prev': 5000}) == 0.0

def test_validate_population_growth_yoy():
    assert validate_population_growth_yoy({'population': 1000000, 'population_prev': 900000}) == 11.11
    assert validate_population_growth_yoy({'population': 800000, 'population_prev': 1000000}) == -20.0
    assert validate_population_growth_yoy({'population': 0, 'population_prev': 0}) == 0.0
    assert validate_population_growth_yoy({'population': 500000, 'population_prev': 500000}) == 0.0
    assert validate_population_growth_yoy({'population': 2000000, 'population_prev': 1000000}) == 100.0

def test_categorize_economy():
    assert categorize_economy({'gdp_billions': 500}) == 'Small'
    assert categorize_economy({'gdp_billions': 1500}) == 'Medium'
    assert categorize_economy({'gdp_billions': 3000}) == 'Large'
    assert categorize_economy({'gdp_billions': 6000}) == 'Major'
    assert categorize_economy({'gdp_billions': 100}) == 'Small'