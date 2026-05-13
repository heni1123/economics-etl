import aiohttp
import asyncio
import logging
from typing import Any, Dict, List

class ExchangeRatesApiExtractor:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.session = None
        self.base_url = config["url"]
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

    async def start(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/5.0"},
        )

    def _parse_response(self, response: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "result": response.get("result"),
                "provider": response.get("provider"),
                "time_last_update_unix": response.get("time_last_update_unix"),
                "time_last_update_utc": response.get("time_last_update_utc"),
                "time_next_update_unix": response.get("time_next_update_unix"),
                "base_code": response.get("base_code"),
                "rates.EUR": response.get("rates", {}).get("EUR"),
                "rates.GBP": response.get("rates", {}).get("GBP"),
                "rates.JPY": response.get("rates", {}).get("JPY"),
                "rates.CHF": response.get("rates", {}).get("CHF"),
            }
        ]