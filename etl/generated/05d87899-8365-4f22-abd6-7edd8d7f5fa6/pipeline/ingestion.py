import asyncio
import aiohttp
import logging
import pandas as pd
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)

class DataIngestion:
    def __init__(self) -> None:
        self.worldbank_gdp_url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023"
        self.worldbank_population_url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023"
        self.exchangerate_api_url = "https://open.er-api.com/v6/latest/USD"
        self.restcountries_info_url = "https://restcountries.com/v3.1/all?fields=name,capital,region,population"

    async def fetch_data(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logging.error(f"Error fetching data from {url}: {e}")
            return {}

    async def extract_gdp(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            gdp_data = await self.fetch_data(session, self.worldbank_gdp_url)
            return gdp_data[1] if gdp_data and len(gdp_data) > 1 else []

    async def extract_population(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            population_data = await self.fetch_data(session, self.worldbank_population_url)
            return population_data[1] if population_data and len(population_data) > 1 else []

    async def extract_exchange_rates(self) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            exchange_data = await self.fetch_data(session, self.exchangerate_api_url)
            return exchange_data

    async def extract_countries_info(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            countries_data = await self.fetch_data(session, self.restcountries_info_url)
            return countries_data

    async def run_extraction(self) -> None:
        gdp_task = asyncio.create_task(self.extract_gdp())
        population_task = asyncio.create_task(self.extract_population())
        exchange_rates_task = asyncio.create_task(self.extract_exchange_rates())
        countries_info_task = asyncio.create_task(self.extract_countries_info())

        gdp, population, exchange_rates, countries_info = await asyncio.gather(
            gdp_task, population_task, exchange_rates_task, countries_info_task
        )

        logging.info(f"GDP Data: {len(gdp)} records extracted.")
        logging.info(f"Population Data: {len(population)} records extracted.")
        logging.info(f"Exchange Rates Data: {exchange_rates}")
        logging.info(f"Countries Info Data: {len(countries_info)} records extracted.")

if __name__ == "__main__":
    ingestion = DataIngestion()
    asyncio.run(ingestion.run_extraction())