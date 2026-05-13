import re
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    record_count: int

class DataValidator:
    REQUIRED_FIELDS = ['country_code', 'country_name', 'year', 'load_timestamp', 'base_currency', 'target_currency', 'exchange_rate', 'rate_date', 'rate_timestamp', 'last_updated']
    
    def __init__(self):
        self.business_rules = {
            "BR1": self._apply_rule_br1,
            "BR2": self._apply_rule_br2,
            "BR3": self._apply_rule_br3,
            "BR4": self._apply_rule_br4,
            "BR5": self._apply_rule_br5,
        }

    async def validate_batch(self, records: List[Dict]) -> ValidationResult:
        errors = []
        warnings = []
        for record in records:
            result = self.validate_record(record)
            if not result.is_valid:
                errors.extend(result.errors)
                warnings.extend(result.warnings)
        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, record_count=len(records))

    def validate_record(self, record: Dict) -> ValidationResult:
        errors = []
        warnings = []
        
        for field in self.REQUIRED_FIELDS:
            if field not in record or record[field] is None:
                errors.append(f"{field} is required.")
        
        if 'country_code' in record and not re.match(r'^[A-Z]{3}$', record['country_code']):
            errors.append("country_code must match regex ^[A-Z]{3}$.")
        
        if 'year' in record and (record['year'] < 1960 or record['year'] > 2030):
            errors.append("year must be between 1960 and 2030.")
        
        if 'gdp_usd' in record and record['gdp_usd'] < 0:
            errors.append("gdp_usd must be >= 0.")
        
        if 'population' in record and record['population'] < 0:
            errors.append("population must be >= 0.")
        
        for rule in self.business_rules.values():
            rule_result = rule(record)
            if rule_result:
                warnings.append(rule_result)

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, record_count=1)

    def _apply_rule_br1(self, record: Dict) -> Optional[str]:
        if 'gdp_usd' in record and 'previous_gdp_usd' in record:
            if record['previous_gdp_usd'] > 0:
                growth = ((record['gdp_usd'] - record['previous_gdp_usd']) / record['previous_gdp_usd']) * 100
                return f"gdp_growth_yoy: {growth:.2f}%"
        return None

    def _apply_rule_br2(self, record: Dict) -> Optional[str]:
        if 'population' in record and 'previous_population' in record:
            if record['previous_population'] > 0:
                growth = ((record['population'] - record['previous_population']) / record['previous_population']) * 100
                return f"population_growth_yoy: {growth:.2f}%"
        return None

    def _apply_rule_br3(self, record: Dict) -> Optional[str]:
        if 'gdp_billions' in record:
            if record['gdp_billions'] < 100:
                return "economic_size_category: Small"
            elif record['gdp_billions'] < 1000:
                return "economic_size_category: Medium"
            elif record['gdp_billions'] < 5000:
                return "economic_size_category: Large"
            else:
                return "economic_size_category: Major"
        return None

    def _apply_rule_br4(self, record: Dict) -> Optional[str]:
        if 'population' in record:
            if record['population'] < 10_000_000:
                return "population_category: Small"
            elif record['population'] < 50_000_000:
                return "population_category: Medium"
            elif record['population'] < 200_000_000:
                return "population_category: Large"
            else:
                return "population_category: Very Large"
        return None

    def _apply_rule_br5(self, record: Dict) -> Optional[str]:
        if 'gdp_per_capita' in record:
            if record['gdp_per_capita'] < 1045:
                return "development_indicator: Low"
            elif record['gdp_per_capita'] < 4095:
                return "development_indicator: Lower-Middle"
            elif record['gdp_per_capita'] < 12695:
                return "development_indicator: Upper-Middle"
            else:
                return "development_indicator: High"
        return None