import asyncio
import logging
import aiohttp
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any, Tuple
import asyncpg

class PipelineOrchestrator:
    def __init__(self, db_config: Dict[str, str], dry_run: bool = False):
        self.db_config = db_config
        self.dry_run = dry_run
        self.metrics = {
            'rows_extracted': 0,
            'rows_loaded': 0,
            'errors': []
        }
        logging.basicConfig(level=logging.INFO)

    async def run(self) -> None:
        start_ts = datetime.utcnow()
        try:
            records = await self._extract_phase()
            transformed_records = await self._transform_phase(records)
            await self._validate_phase(transformed_records)
            if not self.dry_run:
                await self._load_phase(transformed_records)
            status = 'success'
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            status = 'failed'
            self.metrics['errors'].append(str(e))
        finally:
            end_ts = datetime.utcnow()
            await self._audit_pipeline_run(start_ts, end_ts, status)

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            gdp_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023")
            population_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023")
            exchange_rates = await self._fetch_data(session, "https://open.er-api.com/v6/latest/USD")
            countries_info = await self._fetch_data(session, "https://restcountries.com/v3.1/all")

            self.metrics['rows_extracted'] = len(gdp_data) + len(population_data) + len(exchange_rates) + len(countries_info)
            return gdp_data, population_data, exchange_rates, countries_info

    async def _fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    async def _transform_phase(self, records: Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        gdp_data, population_data, exchange_rates, countries_info = records
        df_gdp = pd.json_normalize(gdp_data[1])
        df_population = pd.json_normalize(population_data[1])
        df_exchange = pd.json_normalize(exchange_rates)
        df_countries = pd.json_normalize(countries_info)

        # Merge and transform data
        merged_df = pd.merge(df_gdp, df_population, on=['country.id', 'date'], suffixes=('_gdp', '_pop'))
        merged_df['gdp_billions'] = merged_df['value_gdp'] / 1_000_000_000
        merged_df['gdp_per_capita'] = merged_df['value_gdp'] / merged_df['value_pop']
        merged_df['country_code'] = merged_df['country.id'].str.upper()

        # Additional transformations and calculations
        # ...

        return merged_df.to_dict(orient='records')

    async def _validate_phase(self, records: List[Dict[str, Any]]) -> None:
        for record in records:
            if not re.match(r'^[A-Z]{3}$', record['country_code']):
                raise ValueError(f"Invalid country_code: {record['country_code']}")
            if not (1960 <= record['year'] <= 2030):
                raise ValueError(f"Year out of range: {record['year']}")
            if not (0 <= record['gdp_per_capita'] <= 200000):
                raise ValueError(f"Outlier detected in gdp_per_capita: {record['gdp_per_capita']}")

    async def _load_phase(self, records: List[Dict[str, Any]]) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            if not self.dry_run:
                await conn.execute("TRUNCATE TABLE public.fact_exchange_rates")
                await conn.executemany("INSERT INTO public.fact_exchange_rates (country_code, rate) VALUES ($1, $2) ON CONFLICT (country_code) DO UPDATE SET rate = EXCLUDED.rate", records)
                self.metrics['rows_loaded'] += len(records)
        finally:
            await conn.close()

    async def _audit_pipeline_run(self, start_ts: datetime, end_ts: datetime, status: str) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            await conn.execute(
                "INSERT INTO public.etl_pipeline_runs (start_ts, end_ts, status, rows_extracted, rows_loaded) VALUES ($1, $2, $3, $4, $5)",
                start_ts, end_ts, status, self.metrics['rows_extracted'], self.metrics['rows_loaded']
            )
        finally:
            await conn.close()