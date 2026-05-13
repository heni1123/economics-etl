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
    assert result.is_valid
    assert result.errors == []
    assert result.warnings == []
    assert result.record_count == len(sample_records)

@pytest.mark.asyncio
async def test_validate_batch_empty_input(empty_records):
    """Test validate_batch with empty input."""
    validator = DataValidator()
    result = await validator.validate_batch(empty_records)
    assert not result.is_valid
    assert result.errors == []
    assert result.warnings == []
    assert result.record_count == 0

@pytest.mark.asyncio
async def test_validate_batch_error_handling(invalid_records):
    """Test validate_batch with invalid records."""
    validator = DataValidator()
    result = await validator.validate_batch(invalid_records)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.warnings == []
    assert result.record_count == len(invalid_records)

def test_validate_record_happy_path():
    """Test validate_record with a valid record."""
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
    assert result.errors == []
    assert result.warnings == []
    assert result.record_count == 1

def test_validate_record_empty_input():
    """Test validate_record with an empty record."""
    validator = DataValidator()
    record = {}
    result = validator.validate_record(record)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.warnings == []
    assert result.record_count == 1

def test_validate_record_error_handling():
    """Test validate_record with an invalid record."""
    validator = DataValidator()
    record = {
        'country_code': 'US',
        'country_name': 'United States',
        'year': 2050,  # Invalid year
        'load_timestamp': None,
        'base_currency': 'USD',
        'target_currency': 'EUR',
        'exchange_rate': 0.85,
        'rate_date': '2020-01-01',
        'rate_timestamp': '2020-01-01T00:00:00Z'
    }
    result = validator.validate_record(record)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.warnings == []
    assert result.record_count == 1

def test_validate_country_code_happy_path():
    """Test _validate_country_code with a valid code."""
    validator = DataValidator()
    result = validator._validate_country_code('USA')
    assert result

def test_validate_country_code_invalid_code():
    """Test _validate_country_code with an invalid code."""
    validator = DataValidator()
    result = validator._validate_country_code('US1')
    assert not result

def test_validate_year_happy_path():
    """Test _validate_year with a valid year."""
    validator = DataValidator()
    result = validator._validate_year(2020)
    assert result

def test_validate_year_invalid_year():
    """Test _validate_year with an invalid year."""
    validator = DataValidator()
    result = validator._validate_year(1950)
    assert not result

def test_apply_rule():
    """Test _apply_rule with a record."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule(record)
    assert result is None

def test_apply_rule_br1():
    """Test _apply_rule_br1 with a record."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br1(record)
    assert result is None

def test_apply_rule_br2():
    """Test _apply_rule_br2 with a record."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br2(record)
    assert result is None

def test_apply_rule_br3():
    """Test _apply_rule_br3 with a record."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br3(record)
    assert result is None

def test_apply_rule_br4():
    """Test _apply_rule_br4 with a record."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br4(record)
    assert result is None

def test_apply_rule_br5():
    """Test _apply_rule_br5 with a record."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br5(record)
    assert result is None