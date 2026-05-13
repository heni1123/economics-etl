import aiohttp
import asyncio
import logging
from typing import Any, Dict, List

class ExchangeRatesApiExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/5.0"}
        )
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page({})
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            return []

    async def _fetch_page(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return await self._retry_with_backoff(self.session.get, self.config['url'], params=params)

    async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> None:
        if response.status == 429:
            wait_time = 60
            self.logger.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
            await asyncio.sleep(wait_time)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                async with func(*args) as response:
                    await self._handle_rate_limit(response)
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientError as e:
                if attempt < 2:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries exceeded: {e}")
                    raise

    async def close(self) -> None:
        await self.session.close()

    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        rates = response.get('rates', {})
        return [
            {
                "result": response.get("result"),
                "provider": response.get("provider"),
                "time_last_update_unix": response.get("time_last_update_unix"),
                "time_last_update_utc": response.get("time_last_update_utc"),
                "time_next_update_unix": response.get("time_next_update_unix"),
                "base_code": response.get("base_code"),
                "EUR": rates.get("EUR"),
                "GBP": rates.get("GBP"),
                "JPY": rates.get("JPY"),
                "CHF": rates.get("CHF"),
            }
        ]