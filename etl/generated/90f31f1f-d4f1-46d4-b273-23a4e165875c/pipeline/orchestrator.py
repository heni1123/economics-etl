import asyncio
import logging
import aiohttp
import asyncpg
from typing import List, Dict, Any, Tuple
from datetime import datetime

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
            transformed_records = await self._transform_phase(records)
            validated_records = await self._validate_phase(transformed_records)
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
            gdp_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023")
            population_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023")
            exchange_rate_data = await self._fetch_data(session, "https://open.er-api.com/v6/latest/USD")
            country_data = await self._fetch_data(session, "https://restcountries.com/v3.1/all")

            logging.info(f"Extracted {len(gdp_data)} GDP records, {len(population_data)} population records")
            return self._combine_data(gdp_data, population_data, exchange_rate_data, country_data)

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
                    logging.error(f"Failed to fetch data from {url}: {str(e)}")
                    raise

    def _combine_data(self, gdp_List[Dict[str, Any]], population_List[Dict[str, Any]], exchange_rate_Dict[str, Any], country_List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        combined_records = []
        for gdp_record in gdp_data[1]:
            for population_record in population_data[1]:
                if gdp_record['country']['id'] == population_record['country']['id'] and gdp_record['date'] == population_record['date']:
                    combined_record = {
                        'country_code': gdp_record['country']['id'].upper(),
                        'country_name': gdp_record['country']['value'],
                        'year': gdp_record['date'],
                        'gdp_usd': gdp_record['value'],
                        'population': population_record['value'],
                    }
                    combined_records.append(combined_record)
        return combined_records

    async def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for record in records:
            record['gdp_billions'] = record['gdp_usd'] / 1_000_000_000 if record['gdp_usd'] is not None else None
            record['gdp_per_capita'] = record['gdp_usd'] / record['population'] if record['population'] else None
        return records

    async def _validate_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_records = []
        for record in records:
            if (record['gdp_usd'] is not None and record['gdp_usd'] >= 0 and
                record['population'] is not None and record['population'] >= 0 and
                1960 <= record['year'] <= 2030 and
                re.match(r'^[A-Z]{3}$', record['country_code'])):
                validated_records.append(record)
        logging.info(f"Validated {len(validated_records)} records")
        return validated_records

    async def _load_phase(self, records: List[Dict[str, Any]]) -> None:
        conn = await asyncpg.connect(**self.db_config)
        await conn.execute("TRUNCATE TABLE public.fact_economic_indicators")
        for record in records:
            await conn.execute("""
                INSERT INTO public.fact_economic_indicators (country_code, country_name, year, gdp_usd, gdp_billions, population, gdp_per_capita)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (country_code, year) DO UPDATE SET
                gdp_usd = EXCLUDED.gdp_usd,
                gdp_billions = EXCLUDED.gdp_billions,
                population = EXCLUDED.population,
                gdp_per_capita = EXCLUDED.gdp_per_capita
            """, record['country_code'], record['country_name'], record['year'], record['gdp_usd'], record['gdp_billions'], record['population'], record['gdp_per_capita'])
            self.rows_loaded += 1
        await conn.close()
        logging.info(f"Loaded {self.rows_loaded} records into the database")

    async def _log_audit(self) -> None:
        conn = await asyncpg.connect(**self.db_config)
        await conn.execute("""
            INSERT INTO etl_pipeline_runs (start_ts, end_ts, status, rows_loaded, error_message)
            VALUES ($1, $2, $3, $4, $5)
        """, self.start_ts, self.end_ts, self.status, self.rows_loaded, self.error_message)
        await conn.close()
        logging.info("Audit log written")