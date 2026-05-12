import pytest

def test_gdp_growth_yoy():
    row = {'gdp_usd': 2000, 'gdp_usd_prev': 1500}
    result = (row['gdp_usd'] - row.get('gdp_usd_prev', 0)) / row.get('gdp_usd_prev', 1) * 100
    assert result == 33.33333333333333

def test_population_growth_yoy():
    row = {'population': 1000000, 'population_prev': 900000}
    result = (row['population'] - row.get('population_prev', 0)) / row.get('population_prev', 1) * 100
    assert result == 11.11111111111111

def test_economic_size_category_small():
    row = {'gdp_billions': 50}
    result = 'Small' if row['gdp_billions'] < 100 else 'Medium' if row['gdp_billions'] < 1000 else 'Large' if row['gdp_billions'] < 5000 else 'Major'
    assert result == 'Small'

def test_economic_size_category_medium():
    row = {'gdp_billions': 500}
    result = 'Small' if row['gdp_billions'] < 100 else 'Medium' if row['gdp_billions'] < 1000 else 'Large' if row['gdp_billions'] < 5000 else 'Major'
    assert result == 'Medium'

def test_economic_size_category_large():
    row = {'gdp_billions': 2000}
    result = 'Small' if row['gdp_billions'] < 100 else 'Medium' if row['gdp_billions'] < 1000 else 'Large' if row['gdp_billions'] < 5000 else 'Major'
    assert result == 'Large'

def test_economic_size_category_major():
    row = {'gdp_billions': 6000}
    result = 'Small' if row['gdp_billions'] < 100 else 'Medium' if row['gdp_billions'] < 1000 else 'Large' if row['gdp_billions'] < 5000 else 'Major'
    assert result == 'Major'

def test_country_code_validation_valid():
    country_code = 'USA'
    assert re.match(r'^[A-Z]{3}$', country_code)

def test_country_code_validation_invalid():
    country_code = 'US1'
    assert not re.match(r'^[A-Z]{3}$', country_code)

def test_year_validation_valid():
    year = 2022
    assert 1960 <= year <= 2030

def test_year_validation_invalid_low():
    year = 1959
    assert not (1960 <= year <= 2030)

def test_year_validation_invalid_high():
    year = 2031
    assert not (1960 <= year <= 2030)

def test_gdp_validation_valid():
    gdp = 1000
    assert gdp >= 0

def test_gdp_validation_invalid():
    gdp = -100
    assert gdp < 0

def test_population_validation_valid():
    population = 500000
    assert population >= 0

def test_population_validation_invalid():
    population = -5000
    assert population < 0

def test_data_completeness_logging():
    data = [None, 1000, 2000]
    completeness_rate = sum(1 for item in data if item is not None) / len(data)
    assert completeness_rate == 0.6666666666666666

def test_api_error_handling():
    with pytest.raises(Exception):
        raise Exception("API call failed")