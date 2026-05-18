import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class WorldBankGdpApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.base_url = config['url']
        self.params = config['params']
        self.session = None
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={'User-Agent': 'ETL-Agent/1.0'}
        )
        results = []
        page = 1
        while True:
            self.params['page'] = page
            response = await self._fetch_page(self.params)
            if not response or 'data' not in response:
                break
            results.extend(response['data'])
            if len(response['data']) < self.params['per_page']:
                break
            page += 1
        await self.close()
        return results

    async def _fetch_page(self, params: Dict) -> Dict:
        url = f"{self.base_url}"
        try:
            response = await self._retry_with_backoff(self.session.get, url, params=params)
            response_data = await response.json()
            return response_data
        except aiohttp.ClientError as e:
            self.logger.error(f"Client error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise

    async def _handle_rate_limit(self, response) -> None:
        if response.status == 429:
            self.logger.warning("Rate limit exceeded, handling backoff.")
            await asyncio.sleep(2)  # Simple backoff strategy

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                response = await func(*args)
                await self._handle_rate_limit(response)
                if response.status in {200, 201}:
                    return response
                elif response.status in {401, 403, 404}:
                    self.logger.error(f"Unrecoverable error: {response.status}")
                    raise aiohttp.ClientError(f"Unrecoverable error: {response.status}")
                elif response.status >= 500:
                    self.logger.warning(f"Server error: {response.status}, retrying...")
                    await asyncio.sleep(2 ** attempt)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(2 ** attempt)
        raise aiohttp.ClientError("Max retries exceeded")

    async def close(self) -> None:
        if self.session:
            await self.session.close()