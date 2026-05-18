import asyncio
import logging
from typing import List, Dict, Any
import pandas as pd

class DataTransformer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def transform_batch(self, records: List[Dict]) -> List[Dict]:
        transformed_records = []
        for record in records:
            try:
                transformed_record = self._apply_all(record)
                transformed_records.append(transformed_record)
            except ValueError as e:
                self.logger.error(f"Error transforming record {record}: {e}")
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
            # Add other fields as necessary
        }

    def _country_code(self, record: Dict) -> str:
        country_code = record.get('country', {}).get('id')
        if not country_code or not isinstance(country_code, str) or len(country_code) != 3:
            raise ValueError("country_code must be a 3-letter string")
        return country_code.upper()

    def _country_name(self, record: Dict) -> str:
        country_name = record.get('country', {}).get('value')
        if not country_name:
            raise ValueError("country_name cannot be null")
        return country_name

    def _year(self, record: Dict) -> int:
        year = record.get('date')
        if not year or not isinstance(year, str):
            raise ValueError("year must be a valid string")
        return int(year)

    def _gdp_usd(self, record: Dict) -> float:
        gdp_usd = record.get('value')
        return gdp_usd if gdp_usd is not None else None

    def _gdp_billions(self, record: Dict) -> float:
        gdp_usd = self._gdp_usd(record)
        return gdp_usd / 1_000_000_000 if gdp_usd is not None else None

    def _population(self, record: Dict) -> int:
        population = record.get('population', {}).get('value')
        return population if population is not None else None

    def _gdp_per_capita(self, record: Dict) -> float:
        gdp_usd = self._gdp_usd(record)
        population = self._population(record)
        if gdp_usd is not None and population is not None and population > 0:
            return gdp_usd / population
        return None

    def _gdp_growth_yoy(self, record: Dict) -> float:
        # Placeholder for previous year's GDP, should be fetched from the context
        previous_gdp_usd = record.get('previous_gdp_usd')
        current_gdp_usd = self._gdp_usd(record)
        if previous_gdp_usd is None or current_gdp_usd is None:
            return None
        return ((current_gdp_usd - previous_gdp_usd) / previous_gdp_usd) * 100

    def _population_growth_yoy(self, record: Dict) -> float:
        # Placeholder for previous year's population, should be fetched from the context
        previous_population = record.get('previous_population')
        current_population = self._population(record)
        if previous_population is None or current_population is None:
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
        if gdp_usd < 1045:
            return 'Low Income'
        elif gdp_usd < 4095:
            return 'Lower-Middle'
        elif gdp_usd < 12695:
            return 'Upper-Middle'
        else:
            return 'High Income'