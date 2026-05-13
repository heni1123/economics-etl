import asyncio
import logging
import aiohttp
import pandas as pd
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestion:
    def __init__(self) -> None:
        self.gdp_url = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&per_page=1000&date=2020:2023"
        self.population_url = "https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL?format=json&per_page=1000&date=2020:2023"
        self.exchange_rate_url = "https://open.er-api.com/v6/latest/USD"
        self.countries_url = "https://restcountries.com/v3.1/all"

    async def fetch_data(self, session: aiohttp.ClientSession, url: str) -> List[Dict[str, Any]]:
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                logger.info(f"Data fetched from {url}: {len(data)} records")
                return data
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return []

    async def extract_gdp(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            return await self.fetch_data(session, self.gdp_url)

    async def extract_population(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            return await self.fetch_data(session, self.population_url)

    async def extract_exchange_rates(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            return await self.fetch_data(session, self.exchange_rate_url)

    async def extract_countries(self) -> List[Dict[str, Any]]:
        async with aiohttp.ClientSession() as session:
            return await self.fetch_data(session, self.countries_url)

    async def run_extraction(self) -> pd.DataFrame:
        gdp_task = self.extract_gdp()
        population_task = self.extract_population()
        exchange_rates_task = self.extract_exchange_rates()
        countries_task = self.extract_countries()

        gdp_data, population_data, exchange_rates_data, countries_data = await asyncio.gather(
            gdp_task, population_task, exchange_rates_task, countries_task
        )

        gdp_df = pd.json_normalize(gdp_data[1])  # Assuming the second element contains the actual data
        population_df = pd.json_normalize(population_data[1])
        exchange_rates_df = pd.json_normalize(exchange_rates_data)
        countries_df = pd.json_normalize(countries_data)

        combined_df = pd.merge(gdp_df, population_df, on=["country.id", "date"], how="inner")
        logger.info(f"Combined GDP and Population {combined_df.shape[0]} records")

        return combined_df

async def main() -> None:
    ingestion = DataIngestion()
    combined_data = await ingestion.run_extraction()
    logger.info(f"Final combined data shape: {combined_data.shape}")

if __name__ == "__main__":
    asyncio.run(main())