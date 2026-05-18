import asyncio
import aiohttp
import logging
import pandas as pd
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)

class DataIngestion:
    def __init__(self) -> None:
        self.sources = [
            {
                "name": "worldbank_gdp",
                "url": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD",
                "params": {"format": "json", "per_page": "1000", "date": "2020:2023"}
            },
            {
                "name": "worldbank_population",
                "url": "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL",
                "params": {"format": "json", "per_page": "1000", "date": "2020:2023"}
            },
            {
                "name": "exchangerate_api",
                "url": "https://open.er-api.com/v6/latest/USD",
                "params": {}
            },
            {
                "name": "restcountries_info",
                "url": "https://restcountries.com/v3.1/all",
                "params": {}
            }
        ]

    async def fetch_data(self, session: aiohttp.ClientSession, source: Dict[str, Any]) -> pd.DataFrame:
        try:
            async with session.get(source["url"], params=source["params"]) as response:
                response.raise_for_status()
                data = await response.json()
                return pd.json_normalize(data)
        except Exception as e:
            logging.error(f"Error fetching data from {source['name']}: {e}")
            return pd.DataFrame()

    async def ingest_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_data(session, source) for source in self.sources]
            results = await asyncio.gather(*tasks)
            combined_data = pd.concat(results, ignore_index=True)
            self.load_data(combined_data)

    def load_data(self, pd.DataFrame) -> None:
        # Placeholder for loading data to PostgreSQL
        logging.info("Loading data to PostgreSQL...")
        # Implement the actual loading logic here

    def run(self) -> None:
        logging.info("Starting data ingestion...")
        asyncio.run(self.ingest_data())
        logging.info("Data ingestion completed.")

if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run()