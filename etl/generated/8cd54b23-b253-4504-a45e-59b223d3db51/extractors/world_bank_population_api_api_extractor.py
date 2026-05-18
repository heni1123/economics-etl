import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class WorldBankPopulationApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.base_url = config["url"]
        self.params = config["params"]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/1.0"}
        )
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        results = []
        page = 1
        while True:
            self.params["page"] = page
            response = await self._fetch_page(self.params)
            if not response.get('data'):
                break
            results.extend(response['data'])
            page += 1
        return results

    async def _fetch_page(self, params: Dict) -> Dict:
        url = f"{self.base_url}"
        try:
            response = await self._retry_with_backoff(self.session.get, url, params=params)
            response_data = await response.json()
            if response.status == 200:
                return response_data[1]  # The actual data is in the second element
            else:
                self.logger.error(f"Unexpected status code: {response.status}")
                raise Exception(f"HTTP error: {response.status}")
        except Exception as e:
            self.logger.error(f"Error fetching page: {e}")
            raise

    async def _handle_rate_limit(self, response) -> None:
        if response.status == 429:
            self.logger.warning("Rate limit exceeded, handling backoff.")
            await asyncio.sleep(2)  # Simple backoff strategy

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                response = await func(*args)
                await self._handle_rate_limit(response)
                return response
            except aiohttp.ClientError as e:
                if attempt < 2:
                    backoff_time = 2 ** attempt
                    self.logger.warning(f"Retrying in {backoff_time} seconds due to {e}")
                    await asyncio.sleep(backoff_time)
                else:
                    self.logger.error("Max retries exceeded.")
                    raise

    async def close(self) -> None:
        await self.session.close()