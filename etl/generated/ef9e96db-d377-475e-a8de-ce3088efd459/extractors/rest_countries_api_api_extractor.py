import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class RestCountriesApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.base_url = config["url"]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/1.0"}
        )
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page({})
            return response
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            raise

    async def _fetch_page(self, params: Dict) -> List[Dict[str, Any]]:
        response = await self._retry_with_backoff(self.session.get, self.base_url, params=params)
        if response.status == 200:
            data = await response.json()
            return data
        elif response.status == 429:
            await self._handle_rate_limit(response)
        else:
            response.raise_for_status()

    async def _handle_rate_limit(self, response) -> None:
        self.logger.warning("Rate limit exceeded, retrying...")
        await asyncio.sleep(1)  # Simple backoff for demonstration
        return await self._fetch_page({})

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < 2:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded for {args[0]}")
                    raise

    async def close(self) -> None:
        await self.session.close()