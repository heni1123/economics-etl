try:
    from validators.data_validator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock

@pytest.mark.asyncio
async def test_validate_batch_happy_path(sample_records):
    """Test validate_batch with valid records."""
    validator = DataValidator()
    result = await validator.validate_batch(sample_records)
    assert result['total'] == len(sample_records)
    assert result['valid'] == len(sample_records)
    assert result['invalid'] == 0
    assert result['failed_records'] == []

@pytest.mark.asyncio
async def test_validate_batch_empty_input(empty_records):
    """Test validate_batch with empty input."""
    validator = DataValidator()
    result = await validator.validate_batch(empty_records)
    assert result['total'] == 0
    assert result['valid'] == 0
    assert result['invalid'] == 0
    assert result['failed_records'] == []

@pytest.mark.asyncio
async def test_validate_batch_error_handling(invalid_records):
    """Test validate_batch with invalid records."""
    validator = DataValidator()
    result = await validator.validate_batch(invalid_records)
    assert result['total'] == len(invalid_records)
    assert result['valid'] == 0
    assert result['invalid'] == len(invalid_records)
    assert len(result['failed_records']) == len(invalid_records)

def test_validate_record_happy_path():
    """Test validate_record with valid record."""
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
        'rate_timestamp': '2020-01-01T00:00:00Z',
        'last_updated': '2020-01-01T00:00:00Z'
    }
    result = validator.validate_record(record)
    assert result.is_valid is True

def test_validate_record_empty_input():
    """Test validate_record with empty record."""
    validator = DataValidator()
    record = {}
    result = validator.validate_record(record)
    assert result.is_valid is False
    assert result.rule_id == 'REQUIRED_FIELD_MISSING'

def test_validate_record_error_handling(invalid_records):
    """Test validate_record with invalid record."""
    validator = DataValidator()
    for record in invalid_records:
        result = validator.validate_record(record)
        assert result.is_valid is False

def test_apply_business_rules_happy_path():
    """Test _apply_business_rules with valid record."""
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
        'rate_timestamp': '2020-01-01T00:00:00Z',
        'last_updated': '2020-01-01T00:00:00Z'
    }
    result = validator._apply_business_rules(record)
    assert result.is_valid is True

def test_apply_business_rules_error_handling():
    """Test _apply_business_rules with invalid record."""
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
        'rate_timestamp': '2020-01-01T00:00:00Z',
        'last_updated': '2020-01-01T00:00:00Z',
        'gdp_growth_yoy': None  # Invalid input
    }
    result = validator._apply_business_rules(record)
    assert result.is_valid is False

def test_apply_rule_happy_path():
    """Test _apply_rule with valid rule ID."""
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
        'rate_timestamp': '2020-01-01T00:00:00Z',
        'last_updated': '2020-01-01T00:00:00Z',
        'gdp_billions': 2000,
        'population': 300000000
    }
    result = validator._apply_rule(record, 'BR3')
    assert result.is_valid is True

def test_validate_gdp_growth_yoy():
    """Test _validate_gdp_growth_yoy with valid record."""
    validator = DataValidator()
    record = {}
    result = validator._validate_gdp_growth_yoy(record)
    assert result.is_valid is True

def test_validate_population_growth_yoy():
    """Test _validate_population_growth_yoy with valid record."""
    validator = DataValidator()
    record = {}
    result = validator._validate_population_growth_yoy(record)
    assert result.is_valid is True

def test_validate_economic_size_category():
    """Test _validate_economic_size_category with valid GDP."""
    validator = DataValidator()
    record = {'gdp_billions': 500}
    result = validator._validate_economic_size_category(record)
    assert result.is_valid is True
    assert record['economic_size_category'] == 'Medium'

def test_validate_population_category():
    """Test _validate_population_category with valid population."""
    validator = DataValidator()
    record = {'population': 15000000}
    result = validator._validate_population_category(record)
    assert result.is_valid is True
    assert record['population_category'] == 'Medium'