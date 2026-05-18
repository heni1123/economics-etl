import pytest
from your_module import calculate_gdp_growth_yoy, categorize_economy, classify_income_level

def test_calculate_gdp_growth_yoy():
    assert calculate_gdp_growth_yoy(2000, 2500) == 100.0
    assert calculate_gdp_growth_yoy(2500, 2500) == 0.0
    assert calculate_gdp_growth_yoy(0, 2500) == pytest.approx(-100.0, rel=1e-2)
    assert calculate_gdp_growth_yoy(2500, 0) == pytest.approx(100.0, rel=1e-2)

def test_categorize_economy():
    assert categorize_economy(50) == 'Small'
    assert categorize_economy(500) == 'Medium'
    assert categorize_economy(3000) == 'Large'
    assert categorize_economy(6000) == 'Major'

def test_classify_income_level():
    assert classify_income_level(1000) == 'Low Income'
    assert classify_income_level(2000) == 'Lower-Middle'
    assert classify_income_level(5000) == 'Upper-Middle'
    assert classify_income_level(13000) == 'High Income'

def test_invalid_gdp_growth_yoy():
    with pytest.raises(ZeroDivisionError):
        calculate_gdp_growth_yoy(0, 0)

def test_invalid_categorize_economy():
    with pytest.raises(ValueError):
        categorize_economy(-10)

def test_invalid_classify_income_level():
    with pytest.raises(ValueError):
        classify_income_level(-100)