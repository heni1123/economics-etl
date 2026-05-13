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
        self.logger = logging.getLogger("WorldBankPopulationApiExtractor")
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/1.0"}
        )
        data = []
        try:
            page_data = await self._fetch_page(self.params)
            data.extend(page_data)
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            raise
        finally:
            await self.close()
        return data

    async def _fetch_page(self, params: Dict) -> List[Dict[str, Any]]:
        url = f"{self.base_url}"
        response = await self._retry_with_backoff(self.session.get, url, params=params)
        if response.status == 200:
            json_response = await response.json()
            return json_response[1]  # The actual data is in the second element
        elif response.status == 429:
            await self._handle_rate_limit(response)
        else:
            response.raise_for_status()

    async def _handle_rate_limit(self, response) -> None:
        self.logger.warning("Rate limit exceeded, retrying...")
        await asyncio.sleep(2)  # Simple backoff strategy
        return await self._fetch_page(self.params)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                return await func(*args)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < 2:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error("Max retries exceeded.")
                    raise

    async def close(self) -> None:
        if self.session:
            await self.session.close()