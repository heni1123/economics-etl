import asyncio
import logging
import aiohttp
import asyncpg
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            logger.error(f"Pipeline failed: {e}")
            self.status = 'failed'
            self.error_message = str(e)
        finally:
            self.end_ts = datetime.utcnow()
            await self._log_audit()

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            gdp_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD")
            population_data = await self._fetch_data(session, "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL")
            exchange_rate_data = await self._fetch_data(session, "https://open.er-api.com/v6/latest/USD")
            country_data = await self._fetch_data(session, "https://restcountries.com/v3.1/all")
            return self._merge_data(gdp_data, population_data, exchange_rate_data, country_data)

    async def _fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        retries = 3
        for attempt in range(retries):
            try:
                async with session.get(url) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data[1]  # Assuming the data is in the second element of the response
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch data from {url}: {e}")
                    raise

    def _merge_data(self, gdp_List[Dict[str, Any]], population_List[Dict[str, Any]], 
                    exchange_rate_Dict[str, Any], country_List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        merged_records = []
        for gdp in gdp_data:
            for population in population_data:
                if gdp['country']['id'] == population['country']['id'] and gdp['date'] == population['date']:
                    merged_record = {
                        'country_code': gdp['country']['id'].upper(),
                        'country_name': gdp['country']['value'],
                        'year': gdp['date'],
                        'gdp_usd': gdp['value'],
                        'population': population['value'],
                        'exchange_rate': exchange_rate_data['rates'].get('USD', None),
                    }
                    merged_records.append(merged_record)
        return merged_records

    def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for record in records:
            record['gdp_billions'] = record['gdp_usd'] / 1_000_000_000 if record['gdp_usd'] else None
            record['gdp_per_capita'] = record['gdp_usd'] / record['population'] if record['population'] else None
        return records

    def _validate_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        validated_records = []
        for record in records:
            if (record['gdp_usd'] is not None and record['gdp_usd'] >= 0 and
                record['population'] is not None and record['population'] >= 0 and
                1960 <= record['year'] <= 2030 and
                re.match(r'^[A-Z]{3}$', record['country_code'])):
                validated_records.append(record)
        self.rows_loaded = len(validated_records)
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
            """, record['country_code'], record['country_name'], record['year'], record['gdp_usd'], 
               record['gdp_billions'], record['population'], record['gdp_per_capita'])
        await conn.close()

    async def _log_audit(self) -> None:
        conn = await asyncpg.connect(**self.db_config)
        await conn.execute("""
            INSERT INTO etl_pipeline_runs (start_ts, end_ts, status, rows_loaded, error_message)
            VALUES ($1, $2, $3, $4, $5)
        """, self.start_ts, self.end_ts, self.status, self.rows_loaded, self.error_message)
        await conn.close()