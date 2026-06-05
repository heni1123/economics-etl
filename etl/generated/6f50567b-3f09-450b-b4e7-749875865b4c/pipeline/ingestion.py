import asyncio
import aiohttp
import logging
import pandas as pd
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)

class DataIngestion:
    def __init__(self) -> None:
        self.worldbank_gdp_url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023"
        self.worldbank_population_url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023"
        self.exchangerate_api_url = "https://open.er-api.com/v6/latest/USD"
        self.restcountries_info_url = "https://restcountries.com/v3.1/all"

    async def fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return []

    async def gather_data(self) -> Dict[str, List[Dict[str, Any]]]:
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_data(session, self.worldbank_gdp_url),
                self.fetch_data(session, self.worldbank_population_url),
                self.fetch_data(session, self.exchangerate_api_url),
                self.fetch_data(session, self.restcountries_info_url)
            ]
            results = await asyncio.gather(*tasks)
            return {
                "gdp_data": results[0],
                "population_data": results[1],
                "exchange_rates": results[2],
                "countries_info": results[3]
            }

    def run(self) -> None:
        logging.info("Starting data ingestion...")
        data = asyncio.run(self.gather_data())
        logging.info("Data ingestion completed.")
        # Further processing of data can be done here

if __name__ == "__main__":
    ingestion = DataIngestion()
    ingestion.run()