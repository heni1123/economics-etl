import aiohttp
import asyncio
import logging
from typing import Any, Dict, List

class RestCountriesApiExtractor:
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
            return response
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            return []

    async def _fetch_page(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        url = self.config["url"]
        response = await self._retry_with_backoff(self.session.get, url, params=params)
        data = await response.json()
        return self._parse_response(data)

    async def _handle_rate_limit(self, response) -> None:
        if response.status == 429:
            self.logger.warning("Rate limit exceeded, waiting for 60 seconds.")
            await asyncio.sleep(60)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(3):
            try:
                response = await func(*args)
                await self._handle_rate_limit(response)
                return response
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < 2:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries reached for {args[0]}: {e}")
                    raise

    async def close(self) -> None:
        await self.session.close()

    def _parse_response(self, List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed_data = []
        for country in data:
            parsed_data.append({
                "name_common": country.get("name", {}).get("common"),
                "name_official": country.get("name", {}).get("official"),
                "cca3": country.get("cca3"),
                "capital": country.get("capital"),
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population"),
                "area": country.get("area"),
            })
        return parsed_data