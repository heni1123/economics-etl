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
    assert result.is_valid
    assert result.rule_id == ''
    assert result.message == ''

def test_validate_record_empty_input():
    """Test validate_record with empty record."""
    validator = DataValidator()
    record = {}
    result = validator.validate_record(record)
    assert not result.is_valid
    assert result.rule_id == 'REQUIRED_FIELD_MISSING'
    assert result.message == 'country_code is required.'

def test_validate_record_error_handling(invalid_records):
    """Test validate_record with invalid record."""
    validator = DataValidator()
    for record in invalid_records:
        result = validator.validate_record(record)
        assert not result.is_valid

def test_apply_rule_happy_path():
    """Test _apply_rule with valid record."""
    validator = DataValidator()
    record = {
        'gdp_usd': 50000,
        'gdp_usd_prev': 40000,
        'population': 30000000,
        'gdp_billions': 500,
        'population_prev': 29000000,
        'gdp_per_capita': 1666
    }
    validator._apply_rule(record)
    assert 'gdp_growth_yoy' in record
    assert 'population_growth_yoy' in record
    assert 'economic_size_category' in record
    assert 'population_category' in record
    assert 'development_indicator' in record

def test_validate_br1_happy_path():
    """Test _validate_br1 with valid record."""
    validator = DataValidator()
    record = {'gdp_usd': 50000, 'gdp_usd_prev': 40000}
    validator._validate_br1(record)
    assert record['gdp_growth_yoy'] == 25.0

def test_validate_br2_happy_path():
    """Test _validate_br2 with valid record."""
    validator = DataValidator()
    record = {'population': 30000000, 'population_prev': 29000000}
    validator._validate_br2(record)
    assert record['population_growth_yoy'] == 3.4482758620689653

def test_validate_br3_happy_path():
    """Test _validate_br3 with valid record."""
    validator = DataValidator()
    record = {'gdp_billions': 500}
    validator._validate_br3(record)
    assert record['economic_size_category'] == 'Large'

def test_validate_br4_happy_path():
    """Test _validate_br4 with valid record."""
    validator = DataValidator()
    record = {'population': 30000000}
    validator._validate_br4(record)
    assert record['population_category'] == 'Medium'

def test_validate_br5_happy_path():
    """Test _validate_br5 with valid record."""
    validator = DataValidator()
    record = {'gdp_per_capita': 2000}
    validator._validate_br5(record)
    assert record['development_indicator'] == 'Lower-Middle'