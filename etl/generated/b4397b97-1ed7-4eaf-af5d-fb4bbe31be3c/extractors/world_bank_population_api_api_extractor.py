import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class WorldBankPopulationApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.session = None
        self.base_url = config["url"]
        self.params = config["params"]
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10, connect=30))
        results = []
        try:
            page = 1
            while True:
                self.params["page"] = page
                response = await self._retry_with_backoff(self._fetch_page, self.params)
                if not response or 'data' not in response or not response['data']:
                    break
                results.extend(response['data'])
                page += 1
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
        finally:
            await self.close()
        return results

    async def _fetch_page(self, params: Dict) -> Dict:
        async with self.session.get(self.base_url, params=params, headers={"User-Agent": "ETL-Agent/5.0"}) as response:
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
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                wait_time = 2 ** attempt
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        raise Exception("Max retries exceeded")

    async def close(self) -> None:
        if self.session:
            await self.session.close()