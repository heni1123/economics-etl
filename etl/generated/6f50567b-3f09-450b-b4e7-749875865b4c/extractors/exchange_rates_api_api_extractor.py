import aiohttp
import asyncio
import logging
from typing import Any, Dict, List

class ExchangeRatesApiExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.base_url = config["url"]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30)
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized {self.config['name']} extractor")

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._retry_with_backoff(self._fetch_page)
            return response
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    async def _fetch_page(self, params: Dict[str, Any] = {}) -> Dict[str, Any]:
        async with self.session.get(self.base_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                self.logger.info(f"Fetched {data}")
                return data
            elif response.status == 429:
                await self._handle_rate_limit(response)
            elif response.status >= 500:
                await self._retry_with_backoff(self._fetch_page, params)
            else:
                self.logger.error(f"Unrecoverable error: {response.status}")
                raise Exception(f"HTTP Error: {response.status}")

    async def _handle_rate_limit(self, response) -> None:
        self.logger.warning("Rate limit exceeded, handling...")
        await asyncio.sleep(60)  # Wait for a minute before retrying

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except Exception as e:
                if attempt < 2:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded: {e}")
                    raise

    async def close(self) -> None:
        await self.session.close()
        self.logger.info("Closed session")