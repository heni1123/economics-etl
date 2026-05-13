import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class WorldBankGdpApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.base_url = config["url"]
        self.params = config["params"]
        self.session = None
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/5.0"}
        )
        results = []
        page = 1
        while True:
            self.params["page"] = page
            try:
                response = await self._fetch_page(self.params)
                if not response or 'data' not in response:
                    break
                results.extend(response['data'])
                if len(response['data']) < self.params["per_page"]:
                    break
                page += 1
            except Exception as e:
                self.logger.error(f"Error during extraction: {e}")
                break
        await self.close()
        return results

    async def _fetch_page(self, params: Dict) -> Dict:
        return await self._retry_with_backoff(self._make_request, params)

    async def _make_request(self, params: Dict) -> Dict:
        async with self.session.get(self.base_url, params=params) as response:
            if response.status == 429:
                await self._handle_rate_limit(response)
            response.raise_for_status()
            return await response.json()

    async def _handle_rate_limit(self, response) -> None:
        wait_time = 60
        self.logger.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
        await asyncio.sleep(wait_time)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                if attempt < 2:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded: {e}")
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()