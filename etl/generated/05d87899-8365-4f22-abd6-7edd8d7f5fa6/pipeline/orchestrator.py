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
        self.connection = None

    async def run(self) -> None:
        start_ts = datetime.utcnow()
        status = 'success'
        rows_loaded = 0

        try:
            await self._connect_db()
            records = await self._extract_phase()
            transformed_records = await self._transform_phase(records)
            validated_records = await self._validate_phase(transformed_records)
            rows_loaded = await self._load_phase(validated_records)
        except Exception as e:
            logging.error(f"Pipeline failed: {e}")
            status = 'failed'
        finally:
            await self._log_run(start_ts, status, rows_loaded)
            await self._disconnect_db()

    async def _connect_db(self) -> None:
        self.connection = await asyncpg.connect(**self.db_config)

    async def _disconnect_db(self) -> None:
        if self.connection:
            await self.connection.close()

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            gdp_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023")
            population_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023")
            return gdp_data + population_data

    async def _fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        retries = 3
        for attempt in range(retries):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logging.error(f"Failed to fetch data from {url}: {e}")
                    raise

    async def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for record in records:
            # Transformation logic here
            transformed.append(record)  # Placeholder for actual transformation
        return transformed

    async def _validate_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated = []
        for record in records:
            if self._is_valid(record):
                validated.append(record)
            else:
                logging.warning(f"Invalid record: {record}")
        return validated

    def _is_valid(self, record: Dict[str, Any]) -> bool:
        # Validation logic here
        return True  # Placeholder for actual validation

    async def _load_phase(self, records: List[Dict[str, Any]]) -> int:
        await self.connection.execute("TRUNCATE TABLE public.fact_economic_indicators")
        rows_loaded = 0
        for record in records:
            await self.connection.execute("""
                INSERT INTO public.fact_economic_indicators (country_code, year, gdp_usd, population)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (country_code, year) DO UPDATE SET gdp_usd = EXCLUDED.gdp_usd, population = EXCLUDED.population
            """, record['country_code'], record['year'], record['gdp_usd'], record['population'])
            rows_loaded += 1
        return rows_loaded

    async def _log_run(self, start_ts: datetime, status: str, rows_loaded: int) -> None:
        end_ts = datetime.utcnow()
        await self.connection.execute("""
            INSERT INTO etl_pipeline_runs (start_ts, end_ts, status, rows_loaded)
            VALUES ($1, $2, $3, $4)
        """, start_ts, end_ts, status, rows_loaded)