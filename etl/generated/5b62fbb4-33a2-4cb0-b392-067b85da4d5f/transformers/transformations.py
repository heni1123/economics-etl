import logging
from typing import List, Dict, Any

class DataTransformer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def transform_batch(self, records: List[Dict]) -> List[Dict]:
        transformed_records = []
        for record in records:
            transformed_record = self._apply_all(record)
            transformed_records.append(transformed_record)
        return transformed_records

    def _apply_all(self, record: Dict) -> Dict:
        return {
            "country_code": self._country_code(record),
            "country_name": self._country_name(record),
            "year": self._year(record),
            "gdp_usd": self._gdp_usd(record),
            "gdp_billions": self._gdp_billions(record),
            "population": self._population(record),
            "gdp_per_capita": self._gdp_per_capita(record),
            "gdp_growth_yoy": self._gdp_growth_yoy(record),
            "population_growth_yoy": self._population_growth_yoy(record),
            "economic_size_category": self._economic_size_category(record),
            "population_category": self._population_category(record),
            "development_indicator": self._development_indicator(record),
        }

    def _country_code(self, record: Dict) -> Any:
        return record['country']['id'].upper() if record.get('country') else None

    def _country_name(self, record: Dict) -> Any:
        return record['country']['value'] if record.get('country') else None

    def _year(self, record: Dict) -> Any:
        return int(record['date']) if record.get('date') else None

    def _gdp_usd(self, record: Dict) -> Any:
        return record['value'] if record.get('value') is not None else None

    def _gdp_billions(self, record: Dict) -> Any:
        gdp_usd = self._gdp_usd(record)
        return round(gdp_usd / 1_000_000_000, 2) if gdp_usd is not None else None

    def _population(self, record: Dict) -> Any:
        return record['value'] if record.get('value') is not None else None

    def _gdp_per_capita(self, record: Dict) -> Any:
        gdp_usd = self._gdp_usd(record)
        population = self._population(record)
        return round(gdp_usd / population, 2) if gdp_usd is not None and population else None

    def _gdp_growth_yoy(self, record: Dict) -> Any:
        # Placeholder for previous year's GDP value
        previous_gdp_usd = None  # This should be fetched from the previous record
        gdp_usd = self._gdp_usd(record)
        if previous_gdp_usd is not None and previous_gdp_usd > 0:
            return round(((gdp_usd - previous_gdp_usd) / previous_gdp_usd) * 100, 2)
        return None

    def _population_growth_yoy(self, record: Dict) -> Any:
        # Placeholder for previous year's population value
        previous_population = None  # This should be fetched from the previous record
        population = self._population(record)
        if previous_population is not None and previous_population > 0:
            return round(((population - previous_population) / previous_population) * 100, 2)
        return None

    def _economic_size_category(self, record: Dict) -> Any:
        gdp_billions = self._gdp_billions(record)
        if gdp_billions is not None:
            if gdp_billions < 100:
                return 'Small'
            elif gdp_billions < 1000:
                return 'Medium'
            elif gdp_billions < 5000:
                return 'Large'
            else:
                return 'Major'
        return None

    def _population_category(self, record: Dict) -> Any:
        population = self._population(record)
        if population is not None:
            if population < 1_000_000:
                return 'Small'
            elif population < 10_000_000:
                return 'Medium'
            elif population < 100_000_000:
                return 'Large'
            else:
                return 'Major'
        return None

    def _development_indicator(self, record: Dict) -> Any:
        gdp_per_capita = self._gdp_per_capita(record)
        if gdp_per_capita is not None:
            if gdp_per_capita < 1_045:
                return 'Low income'
            elif gdp_per_capita < 4_095:
                return 'Lower-middle income'
            elif gdp_per_capita < 12_695:
                return 'Upper-middle income'
            else:
                return 'High income'
        return None