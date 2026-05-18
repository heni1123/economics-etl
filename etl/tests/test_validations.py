import pytest
from your_module import calculate_gdp_growth_yoy, categorize_economic_size, classify_development

def test_calculate_gdp_growth_yoy():
    assert calculate_gdp_growth_yoy(2000, 2500) == 25.0
    assert calculate_gdp_growth_yoy(2500, 2500) == 0.0
    assert calculate_gdp_growth_yoy(0, 2500) == 0.0
    assert calculate_gdp_growth_yoy(2500, 0) == -100.0

def test_categorize_economic_size():
    assert categorize_economic_size(50) == 'Small'
    assert categorize_economic_size(500) == 'Medium'
    assert categorize_economic_size(3000) == 'Large'
    assert categorize_economic_size(6000) == 'Major'

def test_classify_development():
    assert classify_development(1000) == 'Low Income'
    assert classify_development(2000) == 'Lower-Middle'
    assert classify_development(5000) == 'Upper-Middle'
    assert classify_development(13000) == 'High Income'

def test_invalid_gdp_growth_yoy():
    with pytest.raises(ZeroDivisionError):
        calculate_gdp_growth_yoy(0, 0)

def test_invalid_categorize_economic_size():
    with pytest.raises(ValueError):
        categorize_economic_size(-100)

def test_invalid_classify_development():
    with pytest.raises(ValueError):
        classify_development(-500)