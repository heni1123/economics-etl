import aiohttp
import asyncio
import logging
from typing import List, Dict, Any

class DataExtractor:
    BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"
    MAX_RETRIES = 3
    TIMEOUT = (10, 30)

    def __init__(self) -> None:
        self.session: aiohttp.ClientSession = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        if self.session is None:
            self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=5), timeout=aiohttp.ClientTimeout(total=self.TIMEOUT[0], connect=self.TIMEOUT[1]))

        url = f"{self.BASE_URL}?format=json&per_page=1000&date=2020:2023"
        for attempt in range(self.MAX_RETRIES):
            try:
                async with self.session.get(url, headers={"User-Agent": "ETL-Agent/5.0"}) as response:
                    if response.status == 429:
                        self.logger.warning("Received HTTP 429, waiting for 60 seconds.")
                        await asyncio.sleep(60)
                        continue
                    response.raise_for_status()
                    data = await response.json()
                    self.logger.info("Data extracted successfully.")
                    return data[1]  # Assuming the second element contains the actual data
            except aiohttp.ClientError as e:
                self.logger.error(f"Client error: {e}, attempt {attempt + 1} of {self.MAX_RETRIES}")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                break
        return []

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None
            self.logger.info("Session closed.")