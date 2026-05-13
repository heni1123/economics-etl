import pytest
from your_module import validate_gdp_growth_yoy, validate_population_growth_yoy, categorize_economic_size, categorize_population_size

def test_validate_gdp_growth_yoy():
    previous_row = {'gdp_usd': 1000}
    current_row = {'gdp_usd': 1100}
    result = validate_gdp_growth_yoy(current_row, previous_row)
    assert result == 10.0

    previous_row = {'gdp_usd': 0}
    current_row = {'gdp_usd': 1000}
    result = validate_gdp_growth_yoy(current_row, previous_row)
    assert result is None

def test_validate_population_growth_yoy():
    previous_row = {'population': 1000}
    current_row = {'population': 1100}
    result = validate_population_growth_yoy(current_row, previous_row)
    assert result == 10.0

    previous_row = {'population': 0}
    current_row = {'population': 1000}
    result = validate_population_growth_yoy(current_row, previous_row)
    assert result is None

def test_categorize_economic_size():
    assert categorize_economic_size({'gdp_billions': 50}) == 'Small'
    assert categorize_economic_size({'gdp_billions': 500}) == 'Medium'
    assert categorize_economic_size({'gdp_billions': 2000}) == 'Large'
    assert categorize_economic_size({'gdp_billions': 6000}) == 'Major'

def test_categorize_population_size():
    assert categorize_population_size({'population': 50000}) == 'Small'
    assert categorize_population_size({'population': 500000}) == 'Medium'
    assert categorize_population_size({'population': 5000000}) == 'Large'
    assert categorize_population_size({'population': 50000000}) == 'Major'