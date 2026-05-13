import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class RestCountriesApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.session = None
        self.base_url = config["url"]
        self.params = config["params"]
        self.max_retries = 3
        self.timeout = aiohttp.ClientTimeout(total=10, connect=30)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    async def extract(self) -> List[Dict[str, Any]]:
        if not self.session:
            await self._init_session()
        try:
            response = await self._fetch_page(self.params)
            return response
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            return []

    async def _fetch_page(self, params: Dict) -> List[Dict[str, Any]]:
        url = self.base_url
        response = await self._retry_with_backoff(self._make_request, url, params)
        return response

    async def _make_request(self, url: str, params: Dict) -> List[Dict[str, Any]]:
        async with self.session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return self._parse_response(data)
            elif response.status == 429:
                await self._handle_rate_limit(response)
            else:
                response.raise_for_status()

    async def _handle_rate_limit(self, response) -> None:
        wait_time = 60
        self.logger.warning(f"Rate limit exceeded. Waiting for {wait_time} seconds.")
        await asyncio.sleep(wait_time)

    async def _retry_with_backoff(self, func, *args) -> Any:
        for attempt in range(self.max_retries):
            try:
                return await func(*args)
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time} seconds.")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"Max retries reached. Last error: {e}")
                    raise

    async def _init_session(self) -> None:
        self.session = aiohttp.ClientSession(
            timeout=self.timeout,
            headers={"User-Agent": "ETL-Agent/5.0"},
        )

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
                "languages": country.get("languages"),
                "currencies": country.get("currencies"),
            })
        return parsed_data

    async def close(self) -> None:
        if self.session:
            await self.session.close()