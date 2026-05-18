import asyncio
import logging
import time
from typing import List, Dict, Any, Tuple
import aiohttp
import pandas as pd
import asyncpg

class PipelineOrchestrator:
    def __init__(self, db_config: Dict[str, str], dry_run: bool = False):
        self.db_config = db_config
        self.dry_run = dry_run
        self.sources = {
            'worldbank_gdp': 'https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023',
            'worldbank_population': 'https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023',
            'exchangerate_api': 'https://open.er-api.com/v6/latest/USD',
            'restcountries_info': 'https://restcountries.com/v3.1/all'
        }
        self.metrics = {
            'rows_extracted': 0,
            'rows_loaded': 0,
            'errors': []
        }
        logging.basicConfig(level=logging.INFO)

    async def run(self) -> None:
        start_ts = time.time()
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
            end_ts = time.time()
            await self._audit_pipeline_run(start_ts, end_ts, status)

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_data(session, url) for url in self.sources.values()]
            results = await asyncio.gather(*tasks)
            records = [item for sublist in results for item in sublist]
            self.metrics['rows_extracted'] = len(records)
            return records

    async def _fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        async with session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch data from {url}, status: {response.status}")
            return await response.json()

    async def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        df = pd.json_normalize(records)
        df['country_code'] = df['country.id'].str.upper()
        df['gdp_billions'] = df['value'] / 1_000_000_000
        df['gdp_per_capita'] = df['gdp_usd'] / df['population']
        transformed_records = df.to_dict(orient='records')
        return transformed_records

    async def _validate_phase(self, records: List[Dict[str, Any]]) -> None:
        for record in records:
            if not isinstance(record['country_code'], str) or len(record['country_code']) != 3:
                raise ValueError(f"Invalid country_code: {record['country_code']}")
            if not (1960 <= record['year'] <= 2030):
                raise ValueError(f"Year out of range: {record['year']}")
            if not (0 <= record['gdp_per_capita'] <= 200000):
                raise ValueError(f"Outlier detected in gdp_per_capita: {record['gdp_per_capita']}")

    async def _load_phase(self, records: List[Dict[str, Any]]) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            await conn.execute("TRUNCATE TABLE public.fact_exchange_rates")
            await conn.execute("TRUNCATE TABLE public.dim_country")
            for record in records:
                await conn.execute("""
                    INSERT INTO public.fact_economic_indicators (country_code, year, gdp_usd, gdp_billions, population, gdp_per_capita)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (country_code, year) DO UPDATE SET
                    gdp_usd = EXCLUDED.gdp_usd,
                    gdp_billions = EXCLUDED.gdp_billions,
                    population = EXCLUDED.population,
                    gdp_per_capita = EXCLUDED.gdp_per_capita
                """, record['country_code'], record['year'], record['gdp_usd'], record['gdp_billions'], record['population'], record['gdp_per_capita'])
            self.metrics['rows_loaded'] = len(records)
        finally:
            await conn.close()

    async def _audit_pipeline_run(self, start_ts: float, end_ts: float, status: str) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            await conn.execute("""
                INSERT INTO etl_pipeline_runs (start_ts, end_ts, status, rows_extracted, rows_loaded)
                VALUES ($1, $2, $3, $4, $5)
            """, start_ts, end_ts, status, self.metrics['rows_extracted'], self.metrics['rows_loaded'])
        finally:
            await conn.close()