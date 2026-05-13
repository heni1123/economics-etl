import pytest
from your_module import validate_gdp, validate_population, categorize_economic_size, categorize_population, calculate_gdp_growth_yoy, calculate_population_growth_yoy

def test_validate_gdp():
    assert validate_gdp(1000) == True
    assert validate_gdp(0) == True
    assert validate_gdp(-1) == False
    assert validate_gdp(None) == False

def test_validate_population():
    assert validate_population(1000000) == True
    assert validate_population(0) == True
    assert validate_population(-1) == False
    assert validate_population(None) == False

def test_categorize_economic_size():
    assert categorize_economic_size(500) == 'Small'
    assert categorize_economic_size(1500) == 'Medium'
    assert categorize_economic_size(3000) == 'Large'
    assert categorize_economic_size(6000) == 'Major'

def test_categorize_population():
    assert categorize_population(500000) == 'Low'
    assert categorize_population(2000000) == 'Medium'
    assert categorize_population(10000000) == 'High'

def test_calculate_gdp_growth_yoy():
    assert calculate_gdp_growth_yoy(2000, 2500) == 25.0
    assert calculate_gdp_growth_yoy(2500, 2500) == 0.0
    assert calculate_gdp_growth_yoy(2500, 2000) == -20.0
    assert calculate_gdp_growth_yoy(0, 2500) == None

def test_calculate_population_growth_yoy():
    assert calculate_population_growth_yoy(1000000, 1100000) == 10.0
    assert calculate_population_growth_yoy(1100000, 1100000) == 0.0
    assert calculate_population_growth_yoy(1100000, 1000000) == -9.09
    assert calculate_population_growth_yoy(0, 1100000) == None