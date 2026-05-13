import pytest
from transformations import calculate_gdp_growth_yoy, calculate_population_growth_yoy, categorize_economic_size, categorize_population_size

def test_calculate_gdp_growth_yoy():
    previous_row = {'gdp_usd': 1000}
    current_row = {'gdp_usd': 1100}
    result = calculate_gdp_growth_yoy(current_row, previous_row)
    assert result == 10.0

def test_calculate_gdp_growth_yoy_no_previous():
    current_row = {'gdp_usd': 1100}
    previous_row = {'gdp_usd': 0}
    result = calculate_gdp_growth_yoy(current_row, previous_row)
    assert result is None

def test_calculate_population_growth_yoy():
    previous_row = {'population': 1000}
    current_row = {'population': 1100}
    result = calculate_population_growth_yoy(current_row, previous_row)
    assert result == 10.0

def test_calculate_population_growth_yoy_no_previous():
    current_row = {'population': 1100}
    previous_row = {'population': 0}
    result = calculate_population_growth_yoy(current_row, previous_row)
    assert result is None

def test_categorize_economic_size_small():
    row = {'gdp_billions': 50}
    result = categorize_economic_size(row)
    assert result == 'Small'

def test_categorize_economic_size_medium():
    row = {'gdp_billions': 500}
    result = categorize_economic_size(row)
    assert result == 'Medium'

def test_categorize_economic_size_large():
    row = {'gdp_billions': 1500}
    result = categorize_economic_size(row)
    assert result == 'Large'

def test_categorize_economic_size_major():
    row = {'gdp_billions': 6000}
    result = categorize_economic_size(row)
    assert result == 'Major'

def test_categorize_population_size_small():
    row = {'population': 50000}
    result = categorize_population_size(row)
    assert result == 'Small'

def test_categorize_population_size_medium():
    row = {'population': 500000}
    result = categorize_population_size(row)
    assert result == 'Medium'

def test_categorize_population_size_large():
    row = {'population': 5000000}
    result = categorize_population_size(row)
    assert result == 'Large'

def test_categorize_population_size_major():
    row = {'population': 50000000}
    result = categorize_population_size(row)
    assert result == 'Major'