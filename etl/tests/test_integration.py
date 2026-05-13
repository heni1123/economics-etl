import aiohttp
import asyncio
import logging
from typing import List, Dict, Any

class DataExtractor:
    BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD"
    MAX_RETRIES = 3
    TIMEOUT = (10, 30)
    USER_AGENT = "ETL-Agent/5.0"
    
    def __init__(self) -> None:
        self.session: aiohttp.ClientSession = None
        logging.basicConfig(level=logging.INFO)
    
    async def extract(self) -> List[Dict[str, Any]]:
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(*self.TIMEOUT), headers={"User-Agent": self.USER_AGENT})
        
        params = {
            "format": "json",
            "per_page": "1000",
            "date": "2020:2023"
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                async with self.session.get(self.BASE_URL, params=params) as response:
                    if response.status == 429:
                        logging.warning("Received 429 Too Many Requests. Retrying after 60 seconds.")
                        await asyncio.sleep(60)
                        continue
                    response.raise_for_status()
                    data = await response.json()
                    return data[1]  # Extracting the actual data from the response
            except aiohttp.ClientError as e:
                logging.error(f"Client error: {e}. Attempt {attempt + 1} of {self.MAX_RETRIES}.")
                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logging.error(f"Unexpected error: {e}. Attempt {attempt + 1} of {self.MAX_RETRIES}.")
                await asyncio.sleep(2 ** attempt)
        
        logging.error("Max retries exceeded. Unable to fetch data.")
        return []
    
    async def close(self) -> None:
        if self.session:
            await self.session.close()