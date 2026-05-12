import asyncio
import logging
import aiohttp
import asyncpg
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)

class PipelineOrchestrator:
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.start_ts = None
        self.end_ts = None
        self.rows_loaded = 0
        self.status = 'success'
        self.error_message = None

    async def run(self) -> None:
        self.start_ts = datetime.utcnow()
        try:
            records = await self._extract_phase()
            transformed_records = self._transform_phase(records)
            validated_records = self._validate_phase(transformed_records)
            await self._load_phase(validated_records)
        except Exception as e:
            self.status = 'failed'
            self.error_message = str(e)
            logging.error(f"Pipeline failed: {self.error_message}")
        finally:
            self.end_ts = datetime.utcnow()
            await self._log_audit()

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            gdp_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD")
            population_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL")
            exchange_rates = await self._fetch_data(session, "https://open.er-api.com/v6/latest/USD")
            countries_info = await self._fetch_data(session, "https://restcountries.com/v3.1/all")
            return self._merge_data(gdp_data, population_data, exchange_rates, countries_info)

    async def _fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        retries = 3
        for attempt in range(retries):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data[1]  # Assuming the data is in the second element
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logging.error(f"Failed to fetch data from {url}: {str(e)}")
                    raise

    def _merge_data(self, gdp_List[Dict[str, Any]], population_List[Dict[str, Any]], 
                    exchange_rates: List[Dict[str, Any]], countries_info: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Implement merging logic based on country codes and years
        merged_data = []
        # Merging logic goes here
        return merged_data

    def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed_records = []
        for record in records:
            # Implement transformation logic
            transformed_records.append(record)
        return transformed_records

    def _validate_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_records = []
        for record in records:
            if self._is_valid(record):
                validated_records.append(record)
        return validated_records

    def _is_valid(self, record: Dict[str, Any]) -> bool:
        # Implement validation logic
        return True

    async def _load_phase(self, records: List[Dict[str, Any]]) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            await conn.execute("TRUNCATE TABLE public.fact_economic_indicators")
            for record in records:
                await conn.execute("""
                    INSERT INTO public.fact_economic_indicators (country_code, year, gdp_usd, population)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (country_code, year) DO UPDATE SET gdp_usd = EXCLUDED.gdp_usd, population = EXCLUDED.population
                """, record['country_code'], record['year'], record['gdp_usd'], record['population'])
                self.rows_loaded += 1
        finally:
            await conn.close()

    async def _log_audit(self) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            await conn.execute("""
                INSERT INTO etl_pipeline_runs (start_ts, end_ts, status, rows_loaded, error_message)
                VALUES ($1, $2, $3, $4, $5)
            """, self.start_ts, self.end_ts, self.status, self.rows_loaded, self.error_message)
        finally:
            await conn.close()