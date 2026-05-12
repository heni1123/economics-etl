import logging
from dataclasses import dataclass
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    record_count: int

class DataValidator:
    def __init__(self):
        self.business_rules = {
            "BR1": self._apply_rule_br1,
            "BR2": self._apply_rule_br2,
            "BR3": self._apply_rule_br3,
            "BR4": self._apply_rule_br4,
            "BR5": self._apply_rule_br5,
        }

    async def validate_batch(self, records: List[Dict]) -> ValidationResult:
        total_errors = []
        total_warnings = []
        for record in records:
            result = self.validate_record(record)
            if not result.is_valid:
                total_errors.extend(result.errors)
                total_warnings.extend(result.warnings)
        return ValidationResult(
            is_valid=len(total_errors) == 0,
            errors=total_errors,
            warnings=total_warnings,
            record_count=len(records)
        )

    def validate_record(self, record: Dict) -> ValidationResult:
        errors = []
        warnings = []
        for rule_id, rule_func in self.business_rules.items():
            result = rule_func(record)
            if result:
                errors.append(result)
        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings, record_count=1)

    def _apply_rule_br1(self, record: Dict) -> Optional[str]:
        if 'gdp_usd' in record and 'gdp_usd_prev' in record:
            if record['gdp_usd_prev'] > 0:
                growth = ((record['gdp_usd'] - record['gdp_usd_prev']) / record['gdp_usd_prev']) * 100
                return None
            else:
                return "Previous GDP value is zero or missing for growth calculation."
        return "GDP or previous GDP value is missing."

    def _apply_rule_br2(self, record: Dict) -> Optional[str]:
        if 'population' in record and 'population_prev' in record:
            if record['population_prev'] > 0:
                growth = ((record['population'] - record['population_prev']) / record['population_prev']) * 100
                return None
            else:
                return "Previous population value is zero or missing for growth calculation."
        return "Population or previous population value is missing."

    def _apply_rule_br3(self, record: Dict) -> Optional[str]:
        if 'gdp_billions' in record:
            if record['gdp_billions'] < 100:
                return None
            elif record['gdp_billions'] < 1000:
                return None
            elif record['gdp_billions'] < 5000:
                return None
            else:
                return None
        return "GDP in billions is missing."

    def _apply_rule_br4(self, record: Dict) -> Optional[str]:
        if 'population' in record:
            if record['population'] < 10000000:
                return None
            elif record['population'] < 50000000:
                return None
            elif record['population'] < 200000000:
                return None
            else:
                return None
        return "Population value is missing."

    def _apply_rule_br5(self, record: Dict) -> Optional[str]:
        if 'gdp_per_capita' in record:
            if record['gdp_per_capita'] < 1045:
                return None
            elif record['gdp_per_capita'] < 4095:
                return None
            elif record['gdp_per_capita'] < 12695:
                return None
            else:
                return None
        return "GDP per capita value is missing."