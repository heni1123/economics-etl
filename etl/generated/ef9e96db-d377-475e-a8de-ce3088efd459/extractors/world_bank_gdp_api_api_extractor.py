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
        self.logger = logging.getLogger("WorldBankGdpApiExtractor")
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30, connect=10),
            headers={"User-Agent": "ETL-Agent/1.0"}
        )
        results = []
        try:
            page_data = await self._fetch_page(self.params)
            results.extend(page_data)
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            raise
        finally:
            await self.close()
        return results

    async def _fetch_page(self, params: Dict) -> List[Dict[str, Any]]:
        response = await self._retry_with_backoff(self.session.get, self.base_url, params=params)
        if response.status == 200:
            data = await response.json()
            return data[1]  # The actual data is in the second element of the response
        elif response.status == 429:
            await self._handle_rate_limit(response)
        else:
            response.raise_for_status()

    async def _handle_rate_limit(self, response) -> None:
        self.logger.warning("Rate limit exceeded, retrying...")
        await asyncio.sleep(2)  # Simple backoff for rate limit
        return await self._fetch_page(self.params)

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
                    self.logger.error(f"Max retries exceeded for {func.__name__}.")
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()