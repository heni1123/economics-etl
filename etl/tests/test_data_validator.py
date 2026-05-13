try:
    from validators.data_validator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock

@pytest.mark.asyncio
async def test_validate_batch_happy_path(sample_records):
    """Test validate_batch with valid input."""
    validator = DataValidator()
    result = await validator.validate_batch(sample_records)
    assert result.is_valid
    assert result.errors == []
    assert result.record_count == len(sample_records)

@pytest.mark.asyncio
async def test_validate_batch_empty_input(empty_records):
    """Test validate_batch with empty input."""
    validator = DataValidator()
    result = await validator.validate_batch(empty_records)
    assert not result.is_valid
    assert result.errors == []
    assert result.record_count == 0

@pytest.mark.asyncio
async def test_validate_batch_error_handling(invalid_records):
    """Test validate_batch with invalid records."""
    validator = DataValidator()
    result = await validator.validate_batch(invalid_records)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.record_count == len(invalid_records)

def test_validate_record_happy_path():
    """Test validate_record with valid input."""
    validator = DataValidator()
    valid_record = {
        'country_code': 'USA',
        'country_name': 'United States',
        'year': 2020,
        'load_timestamp': '2020-01-01T00:00:00Z',
        'base_currency': 'USD',
        'target_currency': 'EUR',
        'exchange_rate': 0.85,
        'rate_date': '2020-01-01',
        'rate_timestamp': '2020-01-01T00:00:00Z',
        'last_updated': '2020-01-01T00:00:00Z'
    }
    result = validator.validate_record(valid_record)
    assert result.is_valid
    assert result.errors == []

def test_validate_record_empty_input():
    """Test validate_record with empty input."""
    validator = DataValidator()
    result = validator.validate_record({})
    assert not result.is_valid
    assert "country_code is required." in result.errors

def test_validate_record_error_handling():
    """Test validate_record with invalid input."""
    validator = DataValidator()
    invalid_record = {
        'country_code': 'US',
        'country_name': None,
        'year': 2050,
        'load_timestamp': None,
        'base_currency': 'USD',
        'target_currency': 'EUR',
        'exchange_rate': -1,
        'rate_date': None,
        'rate_timestamp': None,
        'last_updated': None
    }
    result = validator.validate_record(invalid_record)
    assert not result.is_valid
    assert "country_name is required." in result.errors
    assert "year must be between 1960 and 2030." in result.errors
    assert "exchange_rate must be >= 0." in result.errors

def test_apply_rule_br1_happy_path():
    """Test _apply_rule_br1 with valid GDP data."""
    validator = DataValidator()
    record = {
        'gdp_usd': 2000,
        'previous_gdp_usd': 1000
    }
    result = validator._apply_rule_br1(record)
    assert result == "gdp_growth_yoy: 100.00%"

def test_apply_rule_br1_no_growth():
    """Test _apply_rule_br1 with no previous GDP data."""
    validator = DataValidator()
    record = {
        'gdp_usd': 2000
    }
    result = validator._apply_rule_br1(record)
    assert result is None

def test_apply_rule_br2_happy_path():
    """Test _apply_rule_br2 with valid population data."""
    validator = DataValidator()
    record = {
        'population': 2000000,
        'previous_population': 1000000
    }
    result = validator._apply_rule_br2(record)
    assert result == "population_growth_yoy: 100.00%"

def test_apply_rule_br2_no_growth():
    """Test _apply_rule_br2 with no previous population data."""
    validator = DataValidator()
    record = {
        'population': 2000000
    }
    result = validator._apply_rule_br2(record)
    assert result is None

def test_apply_rule_br3_happy_path():
    """Test _apply_rule_br3 with valid GDP billions data."""
    validator = DataValidator()
    record = {
        'gdp_billions': 500
    }
    result = validator._apply_rule_br3(record)
    assert result == "economic_size_category: Medium"

def test_apply_rule_br3_small_economy():
    """Test _apply_rule_br3 with small GDP billions data."""
    validator = DataValidator()
    record = {
        'gdp_billions': 50
    }
    result = validator._apply_rule_br3(record)
    assert result == "economic_size_category: Small"

def test_apply_rule_br4_happy_path():
    """Test _apply_rule_br4 with valid population data."""
    validator = DataValidator()
    record = {
        'population': 30000000
    }
    result = validator._apply_rule_br4(record)
    assert result == "population_category: Medium"

def test_apply_rule_br4_small_population():
    """Test _apply_rule_br4 with small population data."""
    validator = DataValidator()
    record = {
        'population': 5000000
    }
    result = validator._apply_rule_br4(record)
    assert result == "population_category: Small"

def test_apply_rule_br5_happy_path():
    """Test _apply_rule_br5 with valid GDP per capita data."""
    validator = DataValidator()
    record = {
        'gdp_per_capita': 5000
    }
    result = validator._apply_rule_br5(record)
    assert result == "development_indicator: Upper-Middle"

def test_apply_rule_br5_low_development():
    """Test _apply_rule_br5 with low GDP per capita data."""
    validator = DataValidator()
    record = {
        'gdp_per_capita': 500
    }
    result = validator._apply_rule_br5(record)
    assert result == "development_indicator: Low"