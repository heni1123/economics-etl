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
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(*self.TIMEOUT))
        
        params = {
            "format": "json",
            "per_page": "1000",
            "date": "2020:2023"
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                async with self.session.get(self.BASE_URL, params=params, headers={"User-Agent": "ETL-Agent/5.0"}) as response:
                    if response.status == 429:
                        self.logger.warning("Received 429 Too Many Requests. Retrying after 60 seconds.")
                        await asyncio.sleep(60)
                        continue
                    response.raise_for_status()
                    data = await response.json()
                    return data[1]  # Extract the actual data from the response
            except aiohttp.ClientError as e:
                self.logger.error(f"Client error: {e}. Attempt {attempt + 1} of {self.MAX_RETRIES}.")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}. Attempt {attempt + 1} of {self.MAX_RETRIES}.")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        self.logger.critical("Max retries exceeded. Unable to fetch data.")
        return []
    
    async def close(self) -> None:
        if self.session:
            await self.session.close()