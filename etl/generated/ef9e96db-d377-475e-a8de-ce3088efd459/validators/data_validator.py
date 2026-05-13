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
    
    async def validate_batch(self, records: List[Dict]) -> Dict:
        total = len(records)
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
            'total': total,
            'valid': valid_count,
            'invalid': invalid_count,
            'failed_records': failed_records
        }

    def validate_record(self, record: Dict) -> ValidationResult:
        for field in self.REQUIRED_FIELDS:
            if field not in record or record[field] is None:
                return ValidationResult(False, 'REQUIRED_FIELD_MISSING', field, f"{field} is required.", 'critical')

        if not (1960 <= record['year'] <= 2030):
            return ValidationResult(False, 'YEAR_OUT_OF_BOUNDS', 'year', "Year must be between 1960 and 2030.", 'critical')

        if not self._validate_country_code(record['country_code']):
            return ValidationResult(False, 'INVALID_COUNTRY_CODE', 'country_code', "Country code must match ISO 3166-1 alpha-3 format.", 'critical')

        return self._apply_business_rules(record)

    def _apply_business_rules(self, record: Dict) -> ValidationResult:
        for rule_id in ['BR1', 'BR2', 'BR3', 'BR4', 'BR5']:
            result = self._apply_rule(record, rule_id)
            if not result.is_valid:
                return result
        return ValidationResult(True, '', '', '', '')

    def _apply_rule(self, record: Dict, rule_id: str) -> ValidationResult:
        if rule_id == 'BR1':
            return self._validate_gdp_growth_yoy(record)
        elif rule_id == 'BR2':
            return self._validate_population_growth_yoy(record)
        elif rule_id == 'BR3':
            return self._validate_economic_size_category(record)
        elif rule_id == 'BR4':
            return self._validate_population_category(record)
        elif rule_id == 'BR5':
            return self._validate_development_indicator(record)
        return ValidationResult(True, '', '', '', '')

    def _validate_gdp_growth_yoy(self, record: Dict) -> ValidationResult:
        # Implement logic to calculate and validate GDP growth YoY
        return ValidationResult(True, '', '', '', '')

    def _validate_population_growth_yoy(self, record: Dict) -> ValidationResult:
        # Implement logic to calculate and validate population growth YoY
        return ValidationResult(True, '', '', '', '')

    def _validate_economic_size_category(self, record: Dict) -> ValidationResult:
        gdp_billions = record.get('gdp_billions', 0)
        if gdp_billions < 100:
            category = 'Small'
        elif gdp_billions < 1000:
            category = 'Medium'
        elif gdp_billions < 5000:
            category = 'Large'
        else:
            category = 'Major'
        record['economic_size_category'] = category
        return ValidationResult(True, 'BR3', 'economic_size_category', f"Economic size category set to {category}.", 'warning')

    def _validate_population_category(self, record: Dict) -> ValidationResult:
        population = record.get('population', 0)
        if population < 10_000_000:
            category = 'Small'
        elif population < 50_000_000:
            category = 'Medium'
        elif population < 200_000_000:
            category = 'Large'
        else:
            category = 'Very Large'
        record['population_category'] = category
        return ValidationResult(True, 'BR4', 'population_category', f"Population category set to {category}.", 'warning')

    def _validate_development_indicator(self, record: Dict) -> ValidationResult:
        gdp_per_capita = record.get('gdp_per_capita', 0)
        if gdp_per_capita < 1045:
            indicator = 'Low'
        elif gdp_per_capita < 4095:
            indicator = 'Lower-Middle'
        elif gdp_per_capita < 12695:
            indicator = 'Upper-Middle'
        else:
            indicator = 'High'
        record['development_indicator'] = indicator
        return ValidationResult(True, 'BR5', 'development_indicator', f"Development indicator set to {indicator}.", 'warning')

    def _validate_country_code(self, country_code: str) -> bool:
        import re
        return bool(re.match(r'^[A-Z]{3}$', country_code))