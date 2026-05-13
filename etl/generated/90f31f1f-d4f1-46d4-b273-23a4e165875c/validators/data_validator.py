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
                errors.append(f"Missing required field: {field}")

        if 'country_code' in record and not re.match(r'^[A-Z]{3}$', record['country_code']):
            errors.append("Invalid country_code format")
        
        if 'year' in record and (record['year'] < 1960 or record['year'] > 2030):
            errors.append("Year must be between 1960 and 2030")
        
        if 'gdp_usd' in record and record['gdp_usd'] < 0:
            errors.append("GDP must be >= 0")
        
        if 'population' in record and record['population'] < 0:
            errors.append("Population must be >= 0")

        for rule_id, rule_func in self.business_rules.items():
            warning = rule_func(record)
            if warning:
                warnings.append(warning)

        return ValidationResult(is_valid=len(errors) == 0, errors=errors, warnings=warnings, record_count=1)

    def _apply_rule_br1(self, record: Dict) -> Optional[str]:
        if 'gdp_usd' in record and 'gdp_usd_prev' in record:
            if record['gdp_usd_prev'] == 0:
                return "Previous GDP is zero, cannot calculate growth"
            growth = ((record['gdp_usd'] - record['gdp_usd_prev']) / record['gdp_usd_prev']) * 100
            return None if growth >= 0 else "GDP growth is negative"
        return "Missing GDP data for growth calculation"

    def _apply_rule_br2(self, record: Dict) -> Optional[str]:
        if 'population' in record and 'population_prev' in record:
            if record['population_prev'] == 0:
                return "Previous population is zero, cannot calculate growth"
            growth = ((record['population'] - record['population_prev']) / record['population_prev']) * 100
            return None if growth >= 0 else "Population growth is negative"
        return "Missing population data for growth calculation"

    def _apply_rule_br3(self, record: Dict) -> Optional[str]:
        if 'gdp_billions' in record:
            if record['gdp_billions'] < 100:
                return "Economic size category: Small"
            elif record['gdp_billions'] < 1000:
                return "Economic size category: Medium"
            elif record['gdp_billions'] < 5000:
                return "Economic size category: Large"
            else:
                return "Economic size category: Major"
        return "Missing GDP data for size categorization"

    def _apply_rule_br4(self, record: Dict) -> Optional[str]:
        if 'population' in record:
            if record['population'] < 10000000:
                return "Population category: Small"
            elif record['population'] < 50000000:
                return "Population category: Medium"
            elif record['population'] < 200000000:
                return "Population category: Large"
            else:
                return "Population category: Very Large"
        return "Missing population data for category determination"

    def _apply_rule_br5(self, record: Dict) -> Optional[str]:
        if 'gdp_per_capita' in record:
            if record['gdp_per_capita'] < 1045:
                return "Development indicator: Low"
            elif record['gdp_per_capita'] < 4095:
                return "Development indicator: Lower-Middle"
            elif record['gdp_per_capita'] < 12695:
                return "Development indicator: Upper-Middle"
            else:
                return "Development indicator: High"
        return "Missing GDP per capita data for development indicator"