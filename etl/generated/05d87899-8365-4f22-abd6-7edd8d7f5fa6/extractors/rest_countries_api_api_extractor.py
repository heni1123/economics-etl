import aiohttp
import asyncio
import logging
from typing import Dict, List, Any

class RestCountriesApiExtractor:
    def __init__(self, config: Dict) -> None:
        self.config = config
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10, connect=30),
            headers={"User-Agent": "ETL-Agent/5.0"}
        )
        self.logger = logging.getLogger(__name__)

    async def extract(self) -> List[Dict[str, Any]]:
        try:
            response = await self._fetch_page(self.config['params'])
            return self._parse_response(response)
        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            return []

    async def _fetch_page(self, params: Dict) -> Dict:
        url = self.config['url']
        return await self._retry_with_backoff(self.session.get, url, params=params)

    async def _handle_rate_limit(self, response) -> None:
        if response.status == 429:
            self.logger.warning("Rate limit exceeded, waiting for 60 seconds.")
            await asyncio.sleep(60)

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
                    self.logger.error(f"Max retries reached: {e}")
                    raise

    def _parse_response(self, response: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed_data = []
        for country in response:
            parsed_data.append({
                "common_name": country.get("name", {}).get("common"),
                "official_name": country.get("name", {}).get("official"),
                "country_code": country.get("cca3"),
                "capital": country.get("capital", [None])[0],
                "region": country.get("region"),
                "subregion": country.get("subregion"),
                "population": country.get("population"),
                "area": country.get("area"),
                "languages": country.get("languages"),
                "currencies": country.get("currencies"),
            })
        return parsed_data

    async def close(self) -> None:
        await self.session.close()