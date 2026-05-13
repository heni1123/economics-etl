import asyncio
import logging
import aiohttp
import pandas as pd
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self) -> None:
        self.sources = [
            {
                "name": "worldbank_gdp",
                "url": "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD",
                "params": {"format": "json", "per_page": "1000", "date": "2020:2023"},
            },
            {
                "name": "worldbank_population",
                "url": "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL",
                "params": {"format": "json", "per_page": "1000", "date": "2020:2023"},
            },
            {
                "name": "exchangerate_api",
                "url": "https://open.er-api.com/v6/latest/USD",
                "params": {},
            },
            {
                "name": "restcountries_info",
                "url": "https://restcountries.com/v3.1/all",
                "params": {},
            },
        ]

    async def fetch_data(self, session: aiohttp.ClientSession, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            async with session.get(source["url"], params=source["params"]) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Fetched data from {source['name']}")
                return data[1]  # Assuming the data is in the second element of the response
        except Exception as e:
            logger.error(f"Error fetching data from {source['name']}: {e}")
            return []

    async def ingest_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_data(session, source) for source in self.sources]
            results = await asyncio.gather(*tasks)
            logger.info("Data ingestion completed.")
            return results

    def run(self) -> None:
        loop = asyncio.get_event_loop()
        data = loop.run_until_complete(self.ingest_data())
        logger.info("Ingestion results: %s", data)

if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run()