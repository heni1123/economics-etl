import pytest
from transformations import calculate_gdp_growth_yoy, calculate_population_growth_yoy, categorize_economic_size

def test_calculate_gdp_growth_yoy():
    row_current = {'gdp_usd': 2000, 'gdp_usd_prev': 1500}
    result = calculate_gdp_growth_yoy(row_current)
    assert result == 33.33

    row_current = {'gdp_usd': 1500, 'gdp_usd_prev': 1500}
    result = calculate_gdp_growth_yoy(row_current)
    assert result == 0.0

    row_current = {'gdp_usd': 0, 'gdp_usd_prev': 1500}
    result = calculate_gdp_growth_yoy(row_current)
    assert result == -100.0

def test_calculate_population_growth_yoy():
    row_current = {'population': 1000000, 'population_prev': 900000}
    result = calculate_population_growth_yoy(row_current)
    assert result == 11.11

    row_current = {'population': 900000, 'population_prev': 900000}
    result = calculate_population_growth_yoy(row_current)
    assert result == 0.0

    row_current = {'population': 0, 'population_prev': 900000}
    result = calculate_population_growth_yoy(row_current)
    assert result == -100.0

def test_categorize_economic_size():
    row = {'gdp_billions': 50}
    result = categorize_economic_size(row)
    assert result == 'Small'

    row = {'gdp_billions': 500}
    result = categorize_economic_size(row)
    assert result == 'Medium'

    row = {'gdp_billions': 1500}
    result = categorize_economic_size(row)
    assert result == 'Large'

    row = {'gdp_billions': 6000}
    result = categorize_economic_size(row)
    assert result == 'Major'