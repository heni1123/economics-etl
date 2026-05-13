import asyncio
import logging
import psycopg2
import requests
from datetime import datetime
from typing import List, Dict, Any, Tuple

class PipelineOrchestrator:
    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("ETL Pipeline")
        return logger

    async def run(self) -> None:
        start_ts = datetime.utcnow()
        status = 'success'
        rows_loaded = 0

        try:
            records = await self._extract_phase()
            transformed_records = self._transform_phase(records)
            validated_records = self._validate_phase(transformed_records)
            rows_loaded = await self._load_phase(validated_records)
        except Exception as e:
            status = 'failed'
            self.logger.error(f"Pipeline failed: {e}")
        finally:
            end_ts = datetime.utcnow()
            self.log_audit(start_ts, end_ts, status, rows_loaded)

    async def _extract_phase(self) -> List[Dict[str, Any]]:
        self.logger.info("Starting extraction phase")
        tasks = [
            self.fetch_data("https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"),
            self.fetch_data("https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL"),
            self.fetch_data("https://open.er-api.com/v6/latest/USD"),
            self.fetch_data("https://restcountries.com/v3.1/all")
        ]
        results = await asyncio.gather(*tasks)
        self.logger.info("Extraction phase completed")
        return results

    async def fetch_data(self, url: str) -> List[Dict[str, Any]]:
        retries = 3
        for attempt in range(retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()[1]  # Assuming the data is in the second element
            except requests.RequestException as e:
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    self.logger.error(f"Failed to fetch data from {url}: {e}")
                    raise

    def _transform_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting transformation phase")
        transformed_records = []
        for record in records:
            for item in record:
                transformed_record = {
                    "country_code": item['country']['id'].upper(),
                    "country_name": item['country']['value'],
                    "year": int(item['date']),
                    "gdp_usd": item['value'],
                    "gdp_billions": item['value'] / 1_000_000_000 if item['value'] else None,
                    "population": None,  # Placeholder for population data
                    "gdp_per_capita": None  # Placeholder for GDP per capita
                }
                transformed_records.append(transformed_record)
        self.logger.info("Transformation phase completed")
        return transformed_records

    def _validate_phase(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        self.logger.info("Starting validation phase")
        validated_records = []
        for record in records:
            if (record['gdp_usd'] is not None and record['gdp_usd'] >= 0 and
                record['year'] >= 1960 and record['year'] <= 2030 and
                re.match(r'^[A-Z]{3}$', record['country_code'])):
                validated_records.append(record)
        self.logger.info(f"Validation phase completed with {len(validated_records)} valid records")
        return validated_records

    async def _load_phase(self, records: List[Dict[str, Any]]) -> int:
        self.logger.info("Starting load phase")
        connection = psycopg2.connect(self.db_connection_string)
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE public.fact_economic_indicators")
        insert_query = """
            INSERT INTO public.fact_economic_indicators (country_code, country_name, year, gdp_usd, gdp_billions, population, gdp_per_capita)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (country_code, year) DO UPDATE SET
            gdp_usd = EXCLUDED.gdp_usd,
            gdp_billions = EXCLUDED.gdp_billions,
            population = EXCLUDED.population,
            gdp_per_capita = EXCLUDED.gdp_per_capita
        """
        rows_loaded = 0
        for record in records:
            cursor.execute(insert_query, (
                record['country_code'],
                record['country_name'],
                record['year'],
                record['gdp_usd'],
                record['gdp_billions'],
                record.get('population'),
                record.get('gdp_per_capita')
            ))
            rows_loaded += 1
        connection.commit()
        cursor.close()
        connection.close()
        self.logger.info(f"Load phase completed with {rows_loaded} rows loaded")
        return rows_loaded

    def log_audit(self, start_ts: datetime, end_ts: datetime, status: str, rows_loaded: int) -> None:
        connection = psycopg2.connect(self.db_connection_string)
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO etl_pipeline_runs (start_ts, end_ts, status, rows_loaded)
            VALUES (%s, %s, %s, %s)
        """, (start_ts, end_ts, status, rows_loaded))
        connection.commit()
        cursor.close()
        connection.close()
        self.logger.info("Audit log recorded")