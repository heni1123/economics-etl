import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class WorldBankPopulationApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.base_url = config["url"]
        self.params = config["params"]
        self.session = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/1.0"}
        )
        results = []
        page = 1
        while True:
            self.params["page"] = page
            response = await self._retry_with_backoff(self._fetch_page, self.params)
            if not response or 'data' not in response:
                break
            results.extend(response['data'])
            if len(response['data']) < self.params['per_page']:
                break
            page += 1
        await self.close()
        return results

    async def _fetch_page(self, params: Dict) -> Dict:
        async with self.session.get(self.base_url, params=params) as response:
            if response.status == 429:
                await self._handle_rate_limit(response)
            elif response.status >= 500:
                raise Exception(f"Server error: {response.status}")
            elif response.status in (401, 403, 404):
                raise Exception(f"Unrecoverable error: {response.status}")
            return await response.json()

    async def _handle_rate_limit(self, response) -> None:
        self.logger.warning("Rate limit exceeded, retrying...")
        await asyncio.sleep(2)  # Simple backoff strategy
        raise Exception("Rate limit exceeded")

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except Exception as e:
                if attempt < 2:
                    backoff_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    self.logger.error(f"All attempts failed: {e}")
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()