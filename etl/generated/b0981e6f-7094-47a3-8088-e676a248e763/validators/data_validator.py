import re
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    record_count: int

class DataValidator:
    REQUIRED_FIELDS = ['country_code', 'country_name', 'year', 'load_timestamp', 'base_currency', 'target_currency', 'exchange_rate', 'rate_date', 'rate_timestamp']
    
    async def validate_batch(self, records: List[Dict]) -> ValidationResult:
        total_errors = []
        total_warnings = []
        valid_count = 0
        
        for record in records:
            result = self.validate_record(record)
            if result.is_valid:
                valid_count += 1
            total_errors.extend(result.errors)
            total_warnings.extend(result.warnings)
        
        is_valid = len(total_errors) == 0
        return ValidationResult(is_valid=is_valid, errors=total_errors, warnings=total_warnings, record_count=valid_count)

    def validate_record(self, record: Dict) -> ValidationResult:
        errors = []
        warnings = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in record or record[field] is None:
                errors.append(f"{field} is required.")
        
        if 'country_code' in record and not re.match(r'^[A-Z]{3}$', record['country_code']):
            errors.append("country_code must be in ISO 3166-1 alpha-3 format.")
        
        if 'year' in record:
            if not (1960 <= record['year'] <= 2030):
                errors.append("year must be between 1960 and 2030.")
        
        if 'gdp_usd' in record and record['gdp_usd'] is not None and record['gdp_usd'] < 0:
            errors.append("gdp_usd must be greater than or equal to 0.")
        
        if 'population' in record and record['population'] is not None and record['population'] < 0:
            errors.append("population must be greater than or equal to 0.")
        
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, record_count=1)

    def _apply_rule(self, record: Dict) -> Optional[str]:
        return self._apply_rule_1(record)

    def _apply_rule_1(self, record: Dict) -> Optional[str]:
        if 'gdp_usd' in record and 'gdp_usd_prev' in record:
            gdp_growth = ((record['gdp_usd'] - record['gdp_usd_prev']) / record['gdp_usd_prev']) * 100
            record['gdp_growth_yoy'] = gdp_growth
            return None
        return "Previous GDP value is missing."

    def _apply_rule_2(self, record: Dict) -> Optional[str]:
        if 'population' in record and 'population_prev' in record:
            population_growth = ((record['population'] - record['population_prev']) / record['population_prev']) * 100
            record['population_growth_yoy'] = population_growth
            return None
        return "Previous population value is missing."

    def _apply_rule_3(self, record: Dict) -> Optional[str]:
        if 'gdp_billions' in record:
            if record['gdp_billions'] < 100:
                record['economic_size_category'] = 'Small'
            elif record['gdp_billions'] < 1000:
                record['economic_size_category'] = 'Medium'
            elif record['gdp_billions'] < 5000:
                record['economic_size_category'] = 'Large'
            else:
                record['economic_size_category'] = 'Major'
            return None
        return "GDP in billions is missing."

    def _apply_rule_4(self, record: Dict) -> Optional[str]:
        if 'population' in record:
            if record['population'] < 10000000:
                record['population_category'] = 'Small'
            elif record['population'] < 50000000:
                record['population_category'] = 'Medium'
            elif record['population'] < 200000000:
                record['population_category'] = 'Large'
            else:
                record['population_category'] = 'Very Large'
            return None
        return "Population value is missing."

    def _apply_rule_5(self, record: Dict) -> Optional[str]:
        if 'gdp_per_capita' in record:
            if record['gdp_per_capita'] < 1045:
                record['development_indicator'] = 'Low'
            elif record['gdp_per_capita'] < 4095:
                record['development_indicator'] = 'Lower-Middle'
            elif record['gdp_per_capita'] < 12695:
                record['development_indicator'] = 'Upper-Middle'
            else:
                record['development_indicator'] = 'High'
            return None
        return "GDP per capita value is missing."