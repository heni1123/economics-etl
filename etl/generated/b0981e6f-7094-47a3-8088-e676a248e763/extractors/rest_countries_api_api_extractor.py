import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class RestCountriesApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.session = None
        self.base_url = config["url"]
        self.max_retries = 3
        self.timeout = aiohttp.ClientTimeout(total=10, connect=30)
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        self.session = aiohttp.ClientSession(timeout=self.timeout, headers={"User-Agent": "ETL-Agent/5.0"})
        try:
            countries_data = await self._fetch_page({})
            return countries_data
        finally:
            await self.close()

    async def _fetch_page(self, params: Dict) -> List[Dict[str, Any]]:
        url = self.base_url
        response = await self._retry_with_backoff(self.session.get, url, params=params)
        if response.status == 200:
            data = await response.json()
            return self._transform_data(data)
        else:
            self.logger.error(f"Failed to fetch {response.status}")
            return []

    async def _handle_rate_limit(self, response) -> None:
        if response.status == 429:
            self.logger.warning("Rate limit exceeded, waiting for 60 seconds.")
            await asyncio.sleep(60)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(self.max_retries):
            try:
                response = await func(*args)
                await self._handle_rate_limit(response)
                return response
            except aiohttp.ClientError as e:
                self.logger.error(f"Client error: {e}, attempt {attempt + 1}")
                await asyncio.sleep(2 ** attempt)
        raise Exception("Max retries exceeded")

    async def close(self) -> None:
        if self.session:
            await self.session.close()

    def _transform_data(self, List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        transformed = []
        for country in data:
            transformed.append({
                "name_common": country.get("name", {}).get("common"),
                "name_official": country.get("name", {}).get("official"),
                "cca3": country.get("cca3"),
                "capital": country.get("capital"),
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population"),
                "area": country.get("area"),
            })
        return transformed