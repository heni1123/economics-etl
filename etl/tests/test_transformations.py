import pytest
from transformations import calculate_gdp_growth_yoy, calculate_population_growth_yoy, categorize_economic_size

def test_calculate_gdp_growth_yoy():
    row = {
        'gdp_usd': 20000,
        'gdp_usd_prev': 18000
    }
    result = calculate_gdp_growth_yoy(row)
    assert result == 11.1111

def test_calculate_gdp_growth_yoy_no_previous():
    row = {
        'gdp_usd': 20000,
        'gdp_usd_prev': 0
    }
    result = calculate_gdp_growth_yoy(row)
    assert result == 0

def test_calculate_population_growth_yoy():
    row = {
        'population': 1000000,
        'population_prev': 950000
    }
    result = calculate_population_growth_yoy(row)
    assert result == 5.2632

def test_calculate_population_growth_yoy_no_previous():
    row = {
        'population': 1000000,
        'population_prev': 0
    }
    result = calculate_population_growth_yoy(row)
    assert result == 0

def test_categorize_economic_size_small():
    row = {
        'gdp_billions': 50
    }
    result = categorize_economic_size(row)
    assert result == 'Small'

def test_categorize_economic_size_medium():
    row = {
        'gdp_billions': 500
    }
    result = categorize_economic_size(row)
    assert result == 'Medium'

def test_categorize_economic_size_large():
    row = {
        'gdp_billions': 3000
    }
    result = categorize_economic_size(row)
    assert result == 'Large'

def test_categorize_economic_size_major():
    row = {
        'gdp_billions': 6000
    }
    result = categorize_economic_size(row)
    assert result == 'Major'

def test_categorize_economic_size_edge_case():
    row = {
        'gdp_billions': 100
    }
    result = categorize_economic_size(row)
    assert result == 'Small'

def test_categorize_economic_size_edge_case_large():
    row = {
        'gdp_billions': 5000
    }
    result = categorize_economic_size(row)
    assert result == 'Large'