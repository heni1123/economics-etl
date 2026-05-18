import re
import logging
from typing import List, Dict, Optional, Tuple

class ValidationResult:
    def __init__(self, is_valid: bool, rule_id: str, column: str, message: str, severity: str):
        self.is_valid = is_valid
        self.rule_id = rule_id
        self.column = column
        self.message = message
        self.severity = severity

class DataValidator:
    REQUIRED_FIELDS = ['country_code', 'country_name', 'year', 'load_timestamp', 'base_currency', 'target_currency', 'exchange_rate', 'rate_date', 'rate_timestamp', 'last_updated']
    NULLABLE_FIELDS = ['gdp_usd', 'gdp_billions', 'population', 'gdp_per_capita', 'gdp_growth_yoy', 'population_growth_yoy', 'economic_size_category', 'population_category', 'development_indicator', 'region', 'subregion', 'capital_city', 'area_km2', 'population_density', 'next_update_timestamp', 'provider', 'country_name_common', 'country_name_official', 'primary_language', 'primary_currency']

    def __init__(self):
        logging.basicConfig(level=logging.INFO)

    async def validate_batch(self, records: List[Dict]) -> Dict[str, Optional[List[Dict]]]:
        total_records = len(records)
        valid_count = 0
        invalid_count = 0
        failed_records = []

        for record in records:
            result = self.validate_record(record)
            if result.is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                failed_records.append(record)
                if result.severity == 'critical':
                    logging.error(f"Critical validation error: {result.message}")

        return {
            'total': total_records,
            'valid': valid_count,
            'invalid': invalid_count,
            'failed_records': failed_records
        }

    def validate_record(self, record: Dict) -> ValidationResult:
        for field in self.REQUIRED_FIELDS:
            if field not in record or record[field] is None:
                return ValidationResult(False, 'REQUIRED_FIELD_MISSING', field, f"{field} is required.", 'critical')

        if not re.match(r'^[A-Z]{3}$', record['country_code']):
            return ValidationResult(False, 'INVALID_COUNTRY_CODE', 'country_code', "country_code must match regex [A-Z]{3}.", 'critical')

        if not (1960 <= record['year'] <= 2030):
            return ValidationResult(False, 'INVALID_YEAR', 'year', "year must be between 1960 and 2030.", 'critical')

        if not (0 <= record.get('gdp_usd', 0) <= 200000):
            return ValidationResult(False, 'INVALID_GDP_USD', 'gdp_usd', "gdp_usd must be between 0 and 200000.", 'warning')

        self._apply_rule(record)
        return ValidationResult(True, '', '', '', '')

    def _apply_rule(self, record: Dict) -> None:
        self._validate_br1(record)
        self._validate_br2(record)
        self._validate_br3(record)
        self._validate_br4(record)
        self._validate_br5(record)

    def _validate_br1(self, record: Dict) -> None:
        if 'gdp_usd_previous' in record and record['gdp_usd_previous'] is not None:
            if record['gdp_usd_previous'] == 0:
                record['gdp_growth_yoy'] = None
            else:
                record['gdp_growth_yoy'] = ((record['gdp_usd'] - record['gdp_usd_previous']) / record['gdp_usd_previous']) * 100

    def _validate_br2(self, record: Dict) -> None:
        if 'population_previous' in record and record['population_previous'] is not None:
            if record['population_previous'] == 0:
                record['population_growth_yoy'] = None
            else:
                record['population_growth_yoy'] = ((record['population'] - record['population_previous']) / record['population_previous']) * 100

    def _validate_br3(self, record: Dict) -> None:
        if 'gdp_billions' in record:
            if record['gdp_billions'] < 100:
                record['economic_size_category'] = 'Small'
            elif record['gdp_billions'] < 1000:
                record['economic_size_category'] = 'Medium'
            elif record['gdp_billions'] < 5000:
                record['economic_size_category'] = 'Large'
            else:
                record['economic_size_category'] = 'Major'

    def _validate_br4(self, record: Dict) -> None:
        if 'population' in record:
            if record['population'] < 10000000:
                record['population_category'] = 'Small'
            elif record['population'] < 50000000:
                record['population_category'] = 'Medium'
            elif record['population'] < 200000000:
                record['population_category'] = 'Large'
            else:
                record['population_category'] = 'Very Large'

    def _validate_br5(self, record: Dict) -> None:
        if 'gdp_per_capita' in record:
            if record['gdp_per_capita'] < 1045:
                record['development_indicator'] = 'Low'
            elif record['gdp_per_capita'] < 4095:
                record['development_indicator'] = 'Lower-Middle'
            elif record['gdp_per_capita'] < 12695:
                record['development_indicator'] = 'Upper-Middle'
            else:
                record['development_indicator'] = 'High'