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

def test_validate_record_happy_path(sample_records):
    """Test validate_record with valid input."""
    validator = DataValidator()
    for record in sample_records:
        result = validator.validate_record(record)
        assert result.is_valid
        assert result.errors == []
        assert result.record_count == 1

def test_validate_record_empty_input():
    """Test validate_record with empty input."""
    validator = DataValidator()
    result = validator.validate_record({})
    assert not result.is_valid
    assert len(result.errors) > 0
    assert result.record_count == 1

def test_validate_record_error_handling(invalid_records):
    """Test validate_record with invalid records."""
    validator = DataValidator()
    for record in invalid_records:
        result = validator.validate_record(record)
        assert not result.is_valid
        assert len(result.errors) > 0
        assert result.record_count == 1

def test_apply_rule_br1_happy_path():
    """Test _apply_rule_br1 with valid GDP data."""
    validator = DataValidator()
    record = {'gdp_usd': 2000, 'gdp_usd_prev': 1000}
    result = validator._apply_rule_br1(record)
    assert result is None

def test_apply_rule_br1_zero_previous_gdp():
    """Test _apply_rule_br1 with zero previous GDP."""
    validator = DataValidator()
    record = {'gdp_usd': 2000, 'gdp_usd_prev': 0}
    result = validator._apply_rule_br1(record)
    assert result == "Previous GDP cannot be zero for YoY calculation."

def test_apply_rule_br1_missing_fields():
    """Test _apply_rule_br1 with missing GDP fields."""
    validator = DataValidator()
    record = {'gdp_usd': 2000}
    result = validator._apply_rule_br1(record)
    assert result == "GDP or previous GDP value is missing."

def test_apply_rule_br2_happy_path():
    """Test _apply_rule_br2 with valid population data."""
    validator = DataValidator()
    record = {'population': 20000000, 'population_prev': 15000000}
    result = validator._apply_rule_br2(record)
    assert result is None

def test_apply_rule_br2_zero_previous_population():
    """Test _apply_rule_br2 with zero previous population."""
    validator = DataValidator()
    record = {'population': 20000000, 'population_prev': 0}
    result = validator._apply_rule_br2(record)
    assert result == "Previous population cannot be zero for YoY calculation."

def test_apply_rule_br2_missing_fields():
    """Test _apply_rule_br2 with missing population fields."""
    validator = DataValidator()
    record = {'population': 20000000}
    result = validator._apply_rule_br2(record)
    assert result == "Population or previous population value is missing."

def test_apply_rule_br3_happy_path():
    """Test _apply_rule_br3 with valid GDP billions data."""
    validator = DataValidator()
    record = {'gdp_billions': 500}
    result = validator._apply_rule_br3(record)
    assert result is None

def test_apply_rule_br3_invalid_gdp():
    """Test _apply_rule_br3 with invalid GDP billions data."""
    validator = DataValidator()
    record = {'gdp_billions': 10000}
    result = validator._apply_rule_br3(record)
    assert result is None

def test_apply_rule_br3_missing_field():
    """Test _apply_rule_br3 with missing GDP field."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br3(record)
    assert result == "GDP size category cannot be determined."

def test_apply_rule_br4_happy_path():
    """Test _apply_rule_br4 with valid population data."""
    validator = DataValidator()
    record = {'population': 30000000}
    result = validator._apply_rule_br4(record)
    assert result is None

def test_apply_rule_br4_invalid_population():
    """Test _apply_rule_br4 with invalid population data."""
    validator = DataValidator()
    record = {'population': 100000000}
    result = validator._apply_rule_br4(record)
    assert result is None

def test_apply_rule_br4_missing_field():
    """Test _apply_rule_br4 with missing population field."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br4(record)
    assert result == "Population category cannot be determined."

def test_apply_rule_br5_happy_path():
    """Test _apply_rule_br5 with valid GDP per capita data."""
    validator = DataValidator()
    record = {'gdp_per_capita': 5000}
    result = validator._apply_rule_br5(record)
    assert result is None

def test_apply_rule_br5_invalid_gdp_per_capita():
    """Test _apply_rule_br5 with invalid GDP per capita data."""
    validator = DataValidator()
    record = {'gdp_per_capita': 15000}
    result = validator._apply_rule_br5(record)
    assert result is None

def test_apply_rule_br5_missing_field():
    """Test _apply_rule_br5 with missing GDP per capita field."""
    validator = DataValidator()
    record = {}
    result = validator._apply_rule_br5(record)
    assert result == "GDP per capita category cannot be determined."