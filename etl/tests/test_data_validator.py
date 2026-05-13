try:
    from validators.data_validator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_validate_batch_happy_path(sample_records):
    """Test validate_batch with valid input."""
    validator = DataValidator()
    result = await validator.validate_batch(sample_records)
    assert result.is_valid
    assert result.record_count == len(sample_records)
    assert not result.errors
    assert not result.warnings

@pytest.mark.asyncio
async def test_validate_batch_empty_input(empty_records):
    """Test validate_batch with empty input."""
    validator = DataValidator()
    result = await validator.validate_batch(empty_records)
    assert not result.is_valid
    assert result.record_count == 0
    assert result.errors == []
    assert result.warnings == []

@pytest.mark.asyncio
async def test_validate_batch_error_handling(invalid_records):
    """Test validate_batch with invalid records."""
    validator = DataValidator()
    result = await validator.validate_batch(invalid_records)
    assert not result.is_valid
    assert result.record_count == 0
    assert len(result.errors) > 0
    assert len(result.warnings) == 0

def test_validate_record_happy_path():
    """Test validate_record with valid input."""
    validator = DataValidator()
    record = {
        'country_code': 'USA',
        'country_name': 'United States',
        'year': 2020,
        'load_timestamp': '2020-01-01T00:00:00Z',
        'base_currency': 'USD',
        'target_currency': 'EUR',
        'exchange_rate': 0.85,
        'rate_date': '2020-01-01',
        'rate_timestamp': '2020-01-01T00:00:00Z'
    }
    result = validator.validate_record(record)
    assert result.is_valid
    assert result.record_count == 1
    assert not result.errors
    assert not result.warnings

def test_validate_record_empty_input():
    """Test validate_record with empty input."""
    validator = DataValidator()
    record = {}
    result = validator.validate_record(record)
    assert not result.is_valid
    assert result.record_count == 1
    assert len(result.errors) > 0
    assert len(result.warnings) == 0

def test_validate_record_error_handling():
    """Test validate_record with invalid fields."""
    validator = DataValidator()
    record = {
        'country_code': 'US',
        'year': 2050,
        'gdp_usd': -100,
        'population': -1
    }
    result = validator.validate_record(record)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.record_count == 1

def test_apply_rule_happy_path():
    """Test _apply_rule with valid input."""
    validator = DataValidator()
    record = {
        'gdp_usd': 1000,
        'gdp_usd_prev': 900
    }
    result = validator._apply_rule(record)
    assert result is None
    assert record['gdp_growth_yoy'] == 11.11111111111111

def test_apply_rule_1_happy_path():
    """Test _apply_rule_1 with valid input."""
    validator = DataValidator()
    record = {
        'gdp_usd': 1000,
        'gdp_usd_prev': 900
    }
    result = validator._apply_rule_1(record)
    assert result is None
    assert record['gdp_growth_yoy'] == 11.11111111111111

def test_apply_rule_1_error_handling():
    """Test _apply_rule_1 with missing previous GDP value."""
    validator = DataValidator()
    record = {
        'gdp_usd': 1000
    }
    result = validator._apply_rule_1(record)
    assert result == "Previous GDP value is missing."

def test_apply_rule_2_happy_path():
    """Test _apply_rule_2 with valid input."""
    validator = DataValidator()
    record = {
        'population': 2000000,
        'population_prev': 1800000
    }
    result = validator._apply_rule_2(record)
    assert result is None
    assert record['population_growth_yoy'] == 11.11111111111111

def test_apply_rule_2_error_handling():
    """Test _apply_rule_2 with missing previous population value."""
    validator = DataValidator()
    record = {
        'population': 2000000
    }
    result = validator._apply_rule_2(record)
    assert result == "Previous population value is missing."

def test_apply_rule_3_happy_path():
    """Test _apply_rule_3 with valid input."""
    validator = DataValidator()
    record = {
        'gdp_billions': 500
    }
    result = validator._apply_rule_3(record)
    assert result is None
    assert record['economic_size_category'] == 'Medium'

def test_apply_rule_3_error_handling():
    """Test _apply_rule_3 with missing GDP in billions."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_3(record)
    assert result == "GDP in billions is missing."

def test_apply_rule_4_happy_path():
    """Test _apply_rule_4 with valid input."""
    validator = DataValidator()
    record = {
        'population': 30000000
    }
    result = validator._apply_rule_4(record)
    assert result is None
    assert record['population_category'] == 'Medium'

def test_apply_rule_4_error_handling():
    """Test _apply_rule_4 with missing population value."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_4(record)
    assert result == "Population value is missing."

def test_apply_rule_5_happy_path():
    """Test _apply_rule_5 with valid input."""
    validator = DataValidator()
    record = {
        'gdp_per_capita': 5000
    }
    result = validator._apply_rule_5(record)
    assert result is None
    assert record['development_indicator'] == 'Upper-Middle'

def test_apply_rule_5_error_handling():
    """Test _apply_rule_5 with missing GDP per capita value."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_5(record)
    assert result == "GDP per capita value is missing."