import pytest
from transformations import calculate_gdp_growth_yoy, calculate_population_growth_yoy, categorize_economic_size

def test_calculate_gdp_growth_yoy():
    row_current = {'gdp_usd': 2000}
    row_previous = {'gdp_usd': 1500}
    result = calculate_gdp_growth_yoy(row_current, row_previous)
    assert result == 33.33

def test_calculate_gdp_growth_yoy_no_previous():
    row_current = {'gdp_usd': 2000}
    row_previous = {}
    result = calculate_gdp_growth_yoy(row_current, row_previous)
    assert result == 0.0

def test_calculate_population_growth_yoy():
    row_current = {'population': 1000000}
    row_previous = {'population': 900000}
    result = calculate_population_growth_yoy(row_current, row_previous)
    assert result == 11.11

def test_calculate_population_growth_yoy_no_previous():
    row_current = {'population': 1000000}
    row_previous = {}
    result = calculate_population_growth_yoy(row_current, row_previous)
    assert result == 0.0

def test_categorize_economic_size_small():
    row = {'gdp_billions': 50}
    result = categorize_economic_size(row)
    assert result == 'Small'

def test_categorize_economic_size_medium():
    row = {'gdp_billions': 500}
    result = categorize_economic_size(row)
    assert result == 'Medium'

def test_categorize_economic_size_large():
    row = {'gdp_billions': 2000}
    result = categorize_economic_size(row)
    assert result == 'Large'

def test_categorize_economic_size_major():
    row = {'gdp_billions': 6000}
    result = categorize_economic_size(row)
    assert result == 'Major'

def test_categorize_economic_size_zero():
    row = {'gdp_billions': 0}
    result = categorize_economic_size(row)
    assert result == 'Small'

def test_categorize_economic_size_negative():
    row = {'gdp_billions': -100}
    result = categorize_economic_size(row)
    assert result == 'Small'

def test_calculate_gdp_growth_yoy_negative_current():
    row_current = {'gdp_usd': -1000}
    row_previous = {'gdp_usd': 1500}
    result = calculate_gdp_growth_yoy(row_current, row_previous)
    assert result == -166.67

def test_calculate_population_growth_yoy_negative_current():
    row_current = {'population': -1000000}
    row_previous = {'population': 900000}
    result = calculate_population_growth_yoy(row_current, row_previous)
    assert result == -211.11

def test_calculate_population_growth_yoy_negative_previous():
    row_current = {'population': 1000000}
    row_previous = {'population': -900000}
    result = calculate_population_growth_yoy(row_current, row_previous)
    assert result == 311.11