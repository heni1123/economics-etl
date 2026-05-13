import logging
from typing import List, Dict, Any

class DataTransformer:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
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
        return record.get('country', {}).get('id', '').upper() if record.get('country') else None

    def _country_name(self, record: Dict) -> Any:
        return record.get('country', {}).get('value', None)

    def _year(self, record: Dict) -> Any:
        return int(record.get('date', 0))

    def _gdp_usd(self, record: Dict) -> Any:
        return record.get('value', None)

    def _gdp_billions(self, record: Dict) -> Any:
        gdp_usd = self._gdp_usd(record)
        return round(gdp_usd / 1_000_000_000, 2) if gdp_usd is not None else None

    def _population(self, record: Dict) -> Any:
        return record.get('population', {}).get('value', None)

    def _gdp_per_capita(self, record: Dict) -> Any:
        gdp_usd = self._gdp_usd(record)
        population = self._population(record)
        return round(gdp_usd / population, 2) if gdp_usd is not None and population else None

    def _gdp_growth_yoy(self, record: Dict) -> Any:
        current_gdp = self._gdp_usd(record)
        previous_gdp = record.get('gdp_usd_prev', 0)
        if previous_gdp and current_gdp is not None:
            return round(((current_gdp - previous_gdp) / previous_gdp) * 100, 2)
        return None

    def _population_growth_yoy(self, record: Dict) -> Any:
        current_population = self._population(record)
        previous_population = record.get('population_prev', 0)
        if previous_population and current_population is not None:
            return round(((current_population - previous_population) / previous_population) * 100, 2)
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
        gdp_usd = self._gdp_usd(record)
        if gdp_usd is not None:
            if gdp_usd < 1045:
                return 'Low income'
            elif gdp_usd < 4095:
                return 'Lower-middle income'
            elif gdp_usd < 12695:
                return 'Upper-middle income'
            else:
                return 'High income'
        return None