import pytest
from transformations import calculate_gdp_growth_yoy, calculate_population_growth_yoy, categorize_economic_size

def test_calculate_gdp_growth_yoy():
    row = {'gdp_usd': 2000, 'gdp_usd_prev': 1800}
    result = calculate_gdp_growth_yoy(row)
    assert result == 11.11111111111111

    row = {'gdp_usd': 0, 'gdp_usd_prev': 0}
    result = calculate_gdp_growth_yoy(row)
    assert result == 0.0

    row = {'gdp_usd': 1500, 'gdp_usd_prev': 0}
    result = calculate_gdp_growth_yoy(row)
    assert result == 0.0

def test_calculate_population_growth_yoy():
    row = {'population': 1000000, 'population_prev': 950000}
    result = calculate_population_growth_yoy(row)
    assert result == 5.2631578947368425

    row = {'population': 0, 'population_prev': 0}
    result = calculate_population_growth_yoy(row)
    assert result == 0.0

    row = {'population': 500000, 'population_prev': 0}
    result = calculate_population_growth_yoy(row)
    assert result == 0.0

def test_categorize_economic_size():
    row = {'gdp_billions': 50}
    result = categorize_economic_size(row)
    assert result == 'Small'

    row = {'gdp_billions': 500}
    result = categorize_economic_size(row)
    assert result == 'Medium'

    row = {'gdp_billions': 2000}
    result = categorize_economic_size(row)
    assert result == 'Large'

    row = {'gdp_billions': 6000}
    result = categorize_economic_size(row)
    assert result == 'Major'