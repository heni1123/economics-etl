try:
    from validators.data_validator import *
except ImportError:
    pytest.skip("module not available", allow_module_level=True)

import pytest
from unittest import mock

@pytest.mark.asyncio
async def test_validate_batch_happy_path(sample_records):
    """Test validate_batch with valid input, expect success."""
    validator = DataValidator()
    result = await validator.validate_batch(sample_records)
    assert result.is_valid
    assert result.errors == []
    assert result.record_count == len(sample_records)

@pytest.mark.asyncio
async def test_validate_batch_empty_input(empty_records):
    """Test validate_batch with empty input, expect valid result."""
    validator = DataValidator()
    result = await validator.validate_batch(empty_records)
    assert result.is_valid
    assert result.errors == []
    assert result.record_count == 0

@pytest.mark.asyncio
async def test_validate_batch_error_handling(invalid_records):
    """Test validate_batch with invalid records, expect errors."""
    validator = DataValidator()
    result = await validator.validate_batch(invalid_records)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.record_count == len(invalid_records)

def test_validate_record_happy_path(sample_records):
    """Test validate_record with valid input, expect success."""
    validator = DataValidator()
    for record in sample_records:
        result = validator.validate_record(record)
        assert result.is_valid
        assert result.errors == []
        assert result.record_count == 1

def test_validate_record_empty_input():
    """Test validate_record with empty input, expect valid result."""
    validator = DataValidator()
    result = validator.validate_record({})
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.record_count == 1

def test_validate_record_error_handling(invalid_records):
    """Test validate_record with invalid records, expect errors."""
    validator = DataValidator()
    for record in invalid_records:
        result = validator.validate_record(record)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert result.record_count == 1

def test_apply_rule_br1_happy_path():
    """Test _apply_rule_br1 with valid GDP values, expect no error."""
    validator = DataValidator()
    record = {'gdp_usd': 2000, 'gdp_usd_prev': 1000}
    result = validator._apply_rule_br1(record)
    assert result is None

def test_apply_rule_br1_empty_input():
    """Test _apply_rule_br1 with missing GDP values, expect error."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br1(record)
    assert result == "GDP or previous GDP value is missing."

def test_apply_rule_br1_error_handling():
    """Test _apply_rule_br1 with zero previous GDP, expect error."""
    validator = DataValidator()
    record = {'gdp_usd': 2000, 'gdp_usd_prev': 0}
    result = validator._apply_rule_br1(record)
    assert result == "Previous GDP value is zero or missing for growth calculation."

def test_apply_rule_br2_happy_path():
    """Test _apply_rule_br2 with valid population values, expect no error."""
    validator = DataValidator()
    record = {'population': 50000000, 'population_prev': 25000000}
    result = validator._apply_rule_br2(record)
    assert result is None

def test_apply_rule_br2_empty_input():
    """Test _apply_rule_br2 with missing population values, expect error."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br2(record)
    assert result == "Population or previous population value is missing."

def test_apply_rule_br2_error_handling():
    """Test _apply_rule_br2 with zero previous population, expect error."""
    validator = DataValidator()
    record = {'population': 50000000, 'population_prev': 0}
    result = validator._apply_rule_br2(record)
    assert result == "Previous population value is zero or missing for growth calculation."

def test_apply_rule_br3_happy_path():
    """Test _apply_rule_br3 with valid GDP in billions, expect no error."""
    validator = DataValidator()
    record = {'gdp_billions': 1500}
    result = validator._apply_rule_br3(record)
    assert result is None

def test_apply_rule_br3_empty_input():
    """Test _apply_rule_br3 with missing GDP in billions, expect error."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br3(record)
    assert result == "GDP in billions is missing."

def test_apply_rule_br4_happy_path():
    """Test _apply_rule_br4 with valid population, expect no error."""
    validator = DataValidator()
    record = {'population': 30000000}
    result = validator._apply_rule_br4(record)
    assert result is None

def test_apply_rule_br4_empty_input():
    """Test _apply_rule_br4 with missing population, expect error."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br4(record)
    assert result == "Population value is missing."

def test_apply_rule_br5_happy_path():
    """Test _apply_rule_br5 with valid GDP per capita, expect no error."""
    validator = DataValidator()
    record = {'gdp_per_capita': 5000}
    result = validator._apply_rule_br5(record)
    assert result is None

def test_apply_rule_br5_empty_input():
    """Test _apply_rule_br5 with missing GDP per capita, expect error."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br5(record)
    assert result == "GDP per capita value is missing."