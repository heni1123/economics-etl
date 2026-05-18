import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class ExchangeRatesApiExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.base_url = config["url"]
        self.session = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page({})
            return response
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            raise

    async def _fetch_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self._retry_with_backoff(self._make_request, params)

    async def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10, connect=30)) as session:
            headers = {"User-Agent": "ETL-Agent/1.0"}
            async with session.get(self.base_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429 or 500 <= response.status < 600:
                    await self._handle_rate_limit(response)
                else:
                    self.logger.error(f"Unrecoverable error: {response.status}")
                    raise Exception(f"HTTP Error: {response.status}")

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
                    self.logger.error("Max retries exceeded")
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()