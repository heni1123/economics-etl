import aiohttp
import asyncio
import logging
from typing import List, Dict, Any

class DataExtractor:
    BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"
    MAX_RETRIES = 3
    TIMEOUT = (10, 30)
    HEADERS = {"User-Agent": "ETL-Agent/1.0"}

    def __init__(self) -> None:
        self.session: aiohttp.ClientSession = None
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        if self.session is None:
            self.session = aiohttp.ClientSession()

        url = f"{self.BASE_URL}?format=json&per_page=1000&date=2020:2023"
        for attempt in range(self.MAX_RETRIES):
            try:
                async with self.session.get(url, headers=self.HEADERS, timeout=self.TIMEOUT) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data[1]  # The actual data is in the second element of the response
                    elif response.status in {401, 403, 404}:
                        logging.error(f"Unrecoverable error: {response.status} for URL: {url}")
                        raise Exception(f"Unrecoverable error: {response.status}")
                    elif response.status == 429:
                        logging.warning("Rate limit exceeded, retrying...")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    elif 500 <= response.status < 600:
                        logging.warning(f"Server error: {response.status}, retrying...")
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        logging.error(f"Unexpected error: {response.status}")
                        raise Exception(f"Unexpected error: {response.status}")
            except Exception as e:
                logging.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.MAX_RETRIES - 1:
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()