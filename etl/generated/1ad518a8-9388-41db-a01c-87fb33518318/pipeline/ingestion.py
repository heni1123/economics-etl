import asyncio
import logging
import aiohttp
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self, run_id: str):
        self.run_id = run_id
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
                logger.info(f"Extracted {len(data)} records from {source['name']}")
                return data
        except Exception as e:
            logger.error(f"Error fetching data from {source['name']}: {e}")
            return []

    async def ingest_data(self) -> None:
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_data(session, source) for source in self.sources]
            results = await asyncio.gather(*tasks)
            logger.info("Data ingestion completed successfully.")
            return results

    def run(self) -> None:
        asyncio.run(self.ingest_data())

if __name__ == "__main__":
    ingestion = DataIngestion(run_id="2023-10-01")
    ingestion.run()