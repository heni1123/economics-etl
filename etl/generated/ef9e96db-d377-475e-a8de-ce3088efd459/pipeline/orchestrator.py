import asyncio
import logging
import aiohttp
import asyncpg
import time
from typing import List, Dict, Any, Tuple

class PipelineOrchestrator:
    def __init__(self, db_config: Dict[str, str], dry_run: bool = False):
        self.db_config = db_config
        self.dry_run = dry_run
        self.start_ts = None
        self.end_ts = None
        self.rows_extracted = 0
        self.rows_loaded = 0
        self.status = 'success'
        self.error_message = None
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(__name__)

    async def run(self) -> None:
        self.start_ts = time.time()
        try:
            records = await self._extract_phase()
            transformed_records = await self._transform_phase(records)
            await self._validate_phase(transformed_records)
            if not self.dry_run:
                await self._load_phase(transformed_records)
        except Exception as e:
            self.status = 'failed'
            self.error_message = str(e)
            self.logger.error(f"Pipeline failed: {self.error_message}")
        finally:
            self.end_ts = time.time()
            await self.audit_pipeline_run()

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        records = []
        async with aiohttp.ClientSession() as session:
            try:
                gdp_data = await self.fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD")
                population_data = await self.fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL")
                exchange_rates_data = await self.fetch_data(session, "https://open.er-api.com/v6/latest/USD")
                countries_data = await self.fetch_data(session, "https://restcountries.com/v3.1/all")

                records = self.merge_data(gdp_data, population_data, exchange_rates_data, countries_data)
                self.rows_extracted = len(records)
                self.logger.info(f"Extracted {self.rows_extracted} records.")
            except Exception as e:
                self.logger.error(f"Error during extraction: {str(e)}")
                self.status = 'partial'
        return records

    async def fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    def merge_data(self, gdp_List[Dict[str, Any]], population_List[Dict[str, Any]], 
                   exchange_rates_Dict[str, Any], countries_List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # Implement merging logic based on the provided data structure
        return []

    async def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed_records = []
        for record in records:
            transformed_record = {
                'country_code': record['country.id'].upper(),
                'country_name': record['country.value'],
                'year': int(record['date']),
                'gdp_usd': record['value'],
                'gdp_billions': record['value'] / 1000000000,
                'population': record['population'],
                # Add additional transformations as needed
            }
            transformed_records.append(transformed_record)
        self.logger.info(f"Transformed {len(transformed_records)} records.")
        return transformed_records

    async def _validate_phase(self, records: List[Dict[str, Any]]) -> None:
        for record in records:
            if not (0 <= record['gdp_usd'] and 0 <= record['population']):
                raise ValueError("GDP and Population must be non-negative.")
            if not (1960 <= record['year'] <= 2030):
                raise ValueError("Year must be between 1960 and 2030.")
            if not self.validate_country_code(record['country_code']):
                raise ValueError("Invalid country code format.")
        self.logger.info("Validation passed for all records.")

    def validate_country_code(self, country_code: str) -> bool:
        return bool(re.match(r'^[A-Z]{3}$', country_code))

    async def _load_phase(self, records: List[Dict[str, Any]]) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            if self.dry_run:
                self.logger.info("Dry run mode, skipping load.")
                return

            await conn.execute("TRUNCATE TABLE public.fact_economic_indicators")
            self.rows_loaded = await self.upsert_records(conn, records)
            self.logger.info(f"Loaded {self.rows_loaded} records.")
        finally:
            await conn.close()

    async def upsert_records(self, conn: asyncpg.Connection, records: List[Dict[str, Any]]) -> int:
        # Implement UPSERT logic here
        return len(records)

    async def audit_pipeline_run(self) -> None:
        conn = await asyncpg.connect(**self.db_config)
        try:
            await conn.execute("""
                INSERT INTO etl_pipeline_runs (start_ts, end_ts, status, rows_extracted, rows_loaded, error_message)
                VALUES (to_timestamp($1), to_timestamp($2), $3, $4, $5, $6)
            """, self.start_ts, self.end_ts, self.status, self.rows_extracted, self.rows_loaded, self.error_message)
        finally:
            await conn.close()