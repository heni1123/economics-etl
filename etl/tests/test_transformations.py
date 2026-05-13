import pytest
from transformations import calculate_gdp_growth_yoy, calculate_population_growth_yoy, categorize_economic_size, categorize_population

def test_calculate_gdp_growth_yoy():
    previous_gdp = 1000
    current_gdp = 1200
    expected_growth = 20.0
    result = calculate_gdp_growth_yoy(current_gdp, previous_gdp)
    assert result == expected_growth

def test_calculate_population_growth_yoy():
    previous_population = 1000000
    current_population = 1100000
    expected_growth = 10.0
    result = calculate_population_growth_yoy(current_population, previous_population)
    assert result == expected_growth

def test_categorize_economic_size_small():
    gdp_billions = 50
    expected_category = 'Small'
    result = categorize_economic_size(gdp_billions)
    assert result == expected_category

def test_categorize_economic_size_medium():
    gdp_billions = 500
    expected_category = 'Medium'
    result = categorize_economic_size(gdp_billions)
    assert result == expected_category

def test_categorize_economic_size_large():
    gdp_billions = 3000
    expected_category = 'Large'
    result = categorize_economic_size(gdp_billions)
    assert result == expected_category

def test_categorize_economic_size_major():
    gdp_billions = 6000
    expected_category = 'Major'
    result = categorize_economic_size(gdp_billions)
    assert result == expected_category

def test_categorize_population_small():
    population = 50000
    expected_category = 'Small'
    result = categorize_population(population)
    assert result == expected_category

def test_categorize_population_medium():
    population = 500000
    expected_category = 'Medium'
    result = categorize_population(population)
    assert result == expected_category

def test_categorize_population_large():
    population = 5000000
    expected_category = 'Large'
    result = categorize_population(population)
    assert result == expected_category

def test_categorize_population_major():
    population = 50000000
    expected_category = 'Major'
    result = categorize_population(population)
    assert result == expected_category

def test_invalid_gdp_growth_yoy():
    previous_gdp = 0
    current_gdp = 1200
    with pytest.raises(ZeroDivisionError):
        calculate_gdp_growth_yoy(current_gdp, previous_gdp)

def test_invalid_population_growth_yoy():
    previous_population = 0
    current_population = 1100000
    with pytest.raises(ZeroDivisionError):
        calculate_population_growth_yoy(current_population, previous_population)