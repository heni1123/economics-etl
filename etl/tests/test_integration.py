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
    
    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(*self.TIMEOUT))
        url = f"{self.BASE_URL}?format=json&per_page=1000&date=2020:2023"
        attempt = 0
        
        while attempt < self.MAX_RETRIES:
            try:
                async with self.session.get(url, headers={"User-Agent": "ETL-Agent/5.0"}) as response:
                    if response.status == 429:
                        self.logger.warning("Received 429 Too Many Requests. Retrying after 60 seconds.")
                        await asyncio.sleep(60)
                        attempt += 1
                        continue
                    response.raise_for_status()
                    data = await response.json()
                    return data[1]  # Extract the actual data from the response
            except aiohttp.ClientError as e:
                attempt += 1
                wait_time = 2 ** attempt
                self.logger.error(f"Error fetching {e}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        
        self.logger.critical("Max retries exceeded. Unable to fetch data.")
        return []
    
    async def close(self) -> None:
        if self.session:
            await self.session.close()