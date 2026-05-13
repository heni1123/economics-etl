import aiohttp
import asyncio
import logging
from typing import Any, Dict, List

class ExchangeRatesApiExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.session = None
        self.base_url = config["url"]
        self.max_retries = 3
        self.timeout = aiohttp.ClientTimeout(total=10, connect=30)
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page({})
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return []

    async def _fetch_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self._retry_with_backoff(self._make_request, params)

    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
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
        for attempt in range(self.max_retries):
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Request failed: {e}. Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded: {e}")
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    async def start(self) -> None:
        self.session = aiohttp.ClientSession(timeout=self.timeout, headers={"User-Agent": "ETL-Agent/5.0"})