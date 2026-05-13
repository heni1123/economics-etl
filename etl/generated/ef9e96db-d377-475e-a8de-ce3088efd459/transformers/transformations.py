import logging
from typing import List, Dict, Any

class DataTransformer:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def transform_batch(self, records: List[Dict]) -> List[Dict]:
        transformed_records = []
        for record in records:
            try:
                transformed_record = self._apply_all(record)
                transformed_records.append(transformed_record)
            except ValueError as e:
                self.logger.error(f"ValueError: {e} for record: {record}")
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
            "load_timestamp": self._get_current_timestamp(),
            # Add other fields as necessary
        }

    def _country_code(self, record: Dict) -> str:
        country_id = record.get('country', {}).get('id')
        if country_id is None:
            raise ValueError("country_code cannot be None")
        return country_id.upper()

    def _country_name(self, record: Dict) -> str:
        country_name = record.get('country', {}).get('value')
        if country_name is None:
            raise ValueError("country_name cannot be None")
        return country_name

    def _year(self, record: Dict) -> int:
        year = record.get('date')
        if year is None:
            raise ValueError("year cannot be None")
        return int(year)

    def _gdp_usd(self, record: Dict) -> float:
        gdp_usd = record.get('value')
        return gdp_usd if gdp_usd is not None else None

    def _gdp_billions(self, record: Dict) -> float:
        gdp_usd = self._gdp_usd(record)
        return gdp_usd / 1_000_000_000 if gdp_usd is not None else None

    def _population(self, record: Dict) -> int:
        population = record.get('value')
        return population if population is not None else None

    def _gdp_per_capita(self, record: Dict) -> float:
        gdp_usd = self._gdp_usd(record)
        population = self._population(record)
        if gdp_usd is not None and population is not None and population > 0:
            return gdp_usd / population
        return None

    def _gdp_growth_yoy(self, record: Dict) -> float:
        # Placeholder for previous year's GDP, to be implemented with actual data
        previous_gdp_usd = 0  # This should be fetched from the previous record
        current_gdp_usd = self._gdp_usd(record)
        if previous_gdp_usd is None or current_gdp_usd is None or previous_gdp_usd <= 0:
            return None
        return ((current_gdp_usd - previous_gdp_usd) / previous_gdp_usd) * 100

    def _population_growth_yoy(self, record: Dict) -> float:
        # Placeholder for previous year's population, to be implemented with actual data
        previous_population = 0  # This should be fetched from the previous record
        current_population = self._population(record)
        if previous_population is None or current_population is None or previous_population <= 0:
            return None
        return ((current_population - previous_population) / previous_population) * 100

    def _economic_size_category(self, record: Dict) -> str:
        gdp_billions = self._gdp_billions(record)
        if gdp_billions is None:
            return None
        if gdp_billions < 100:
            return 'Small'
        elif gdp_billions < 1000:
            return 'Medium'
        elif gdp_billions < 5000:
            return 'Large'
        else:
            return 'Major'

    def _population_category(self, record: Dict) -> str:
        population = self._population(record)
        if population is None:
            return None
        if population < 10_000_000:
            return 'Small'
        elif population < 50_000_000:
            return 'Medium'
        elif population < 200_000_000:
            return 'Large'
        else:
            return 'Very Large'

    def _development_indicator(self, record: Dict) -> str:
        gdp_usd = self._gdp_usd(record)
        if gdp_usd is None:
            return None
        if gdp_usd < 1_045:
            return 'Low income'
        elif gdp_usd < 4_095:
            return 'Lower-middle income'
        elif gdp_usd < 12_695:
            return 'Upper-middle income'
        else:
            return 'High income'

    def _get_current_timestamp(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'