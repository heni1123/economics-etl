import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class RestCountriesApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.base_url = config["url"]
        self.session = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10, connect=30))
        try:
            response = await self._fetch_page({})
            return response
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    async def _fetch_page(self, params: Dict) -> List[Dict[str, Any]]:
        url = self.base_url
        response = await self._retry_with_backoff(self.session.get, url, params=params)
        if response.status == 200:
            data = await response.json()
            return data
        elif response.status in {429, 500, 502, 503, 504}:
            await self._handle_rate_limit(response)
        else:
            self.logger.error(f"Unrecoverable error: {response.status}")
            response.raise_for_status()

    async def _handle_rate_limit(self, response) -> None:
        self.logger.warning(f"Rate limit exceeded, status: {response.status}. Retrying...")
        await asyncio.sleep(2)  # Simple backoff strategy
        await self.extract()

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < 2:
                    backoff_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {backoff_time} seconds...")
                    await asyncio.sleep(backoff_time)
                else:
                    self.logger.error(f"Max retries exceeded for {func.__name__}.")
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()