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

        params = {
            "format": "json",
            "per_page": "1000",
            "date": "2020:2023"
        }
        
        for attempt in range(self.MAX_RETRIES):
            try:
                async with self.session.get(self.BASE_URL, params=params, headers=self.HEADERS, timeout=self.TIMEOUT) as response:
                    response.raise_for_status()
                    data = await response.json()
                    return data[1]  # The actual data is in the second element of the response
            except aiohttp.ClientResponseError as e:
                if e.status in {401, 403, 404}:
                    logging.error(f"Unrecoverable error: {e.status} - {e.message}")
                    raise
                elif e.status in {429, 500, 502, 503, 504}:
                    logging.warning(f"Retrying due to error {e.status}: {e.message}")
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logging.error(f"Unexpected error: {e.status} - {e.message}")
                    raise
            except Exception as e:
                logging.error(f"An error occurred: {str(e)}")
                raise

        logging.error("Max retries exceeded")
        raise Exception("Max retries exceeded")

    async def close(self) -> None:
        if self.session:
            await self.session.close()