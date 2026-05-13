import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class ExchangeRatesApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.base_url = config["url"]
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30)
        )
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page({})
            return response
        except Exception as e:
            self.logger.error(f"Error during extraction: {str(e)}")
            raise

    async def _fetch_page(self, params: Dict) -> Dict[str, Any]:
        response = await self._retry_with_backoff(self.session.get, self.base_url, params=params)
        data = await response.json()
        if data.get("result") != "success":
            self.logger.error(f"Failed to fetch {data}")
            raise ValueError("Data fetch unsuccessful")
        return self._parse_response(data)

    async def _handle_rate_limit(self, response) -> None:
        if response.status == 429:
            self.logger.warning("Rate limit exceeded, handling...")
            await asyncio.sleep(1)  # Simple rate limit handling

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                response = await func(*args)
                await self._handle_rate_limit(response)
                if response.status in {200, 201}:
                    return response
                elif response.status in {401, 403, 404}:
                    self.logger.error(f"Unrecoverable error: {response.status}")
                    raise ValueError(f"Unrecoverable error: {response.status}")
                elif response.status >= 500:
                    self.logger.warning(f"Server error: {response.status}, retrying...")
            except Exception as e:
                self.logger.warning(f"Error occurred: {str(e)}, retrying...")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
        raise RuntimeError("Max retries exceeded")

    async def close(self) -> None:
        await self.session.close()

    def _parse_response(self, Dict[str, Any]) -> List[Dict[str, Any]]:
        rates = data.get("rates", {})
        return [
            {
                "result": data.get("result"),
                "provider": data.get("provider"),
                "time_last_update_unix": data.get("time_last_update_unix"),
                "time_last_update_utc": data.get("time_last_update_utc"),
                "time_next_update_unix": data.get("time_next_update_unix"),
                "time_next_update_utc": data.get("time_next_update_utc"),
                "base_code": data.get("base_code"),
                "EUR": rates.get("EUR"),
                "GBP": rates.get("GBP"),
                "JPY": rates.get("JPY"),
                "CHF": rates.get("CHF"),
            }
        ]