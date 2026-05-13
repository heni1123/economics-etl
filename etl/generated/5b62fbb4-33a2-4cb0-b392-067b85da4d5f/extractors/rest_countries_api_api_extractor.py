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
            data = await self._fetch_page()
            return data
        finally:
            await self.close()

    async def _fetch_page(self) -> List[Dict[str, Any]]:
        response = await self._retry_with_backoff(self.session.get, self.base_url)
        if response.status != 200:
            self.logger.error(f"Failed to fetch {response.status}")
            return []
        json_response = await response.json()
        return self._parse_response(json_response)

    def _parse_response(self, json_response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        countries_data = []
        for country in json_response:
            country_info = {
                "name_common": country.get("name", {}).get("common"),
                "name_official": country.get("name", {}).get("official"),
                "cca3": country.get("cca3"),
                "capital": country.get("capital"),
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population"),
                "area": country.get("area"),
            }
            countries_data.append(country_info)
        return countries_data

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(self.max_retries):
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                wait_time = 2 ** attempt
                if "429" in str(e):
                    wait_time = 60
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        raise Exception("Max retries exceeded")

    async def close(self) -> None:
        if self.session:
            await self.session.close()