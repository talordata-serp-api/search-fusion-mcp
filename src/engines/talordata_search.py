import os
import httpx
from typing import List
from loguru import logger
from .base import SearchEngine, SearchResult


class TalorDataSearch(SearchEngine):
    """TalorData SERP API search engine implementation"""
    
    def __init__(self, api_key: str = None):
        super().__init__()
        self.api_key = api_key or os.getenv("TALORDATA_API_KEY")
        self.priority = 1.0
        self.name = "talordata"
        
        if self.api_key:
            logger.info("✅ TalorData search engine initialized successfully")
        else:
            logger.warning("⚠️ TalorData API key not found, engine disabled")
    
    def is_available(self) -> bool:
        """Check if TalorData search is available"""
        return bool(self.api_key) and not self.is_in_cooldown()
    
    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Execute search using TalorData SERP API"""
        if not self.is_available():
            return []
        
        url = "https://api.talordata.com/accounts/v1/serp/get_serp_data"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "engine": "google",
            "num": num_results,
            "json": "1"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=15.0)
                
                if response.status_code == 200:
                    data = response.json()
                    raw_results = data.get("organic_results", [])[:num_results]
                    
                    results = []
                    for item in raw_results:
                        results.append(SearchResult(
                            title=item.get("title", "No Title"),
                            link=item.get("link", item.get("url", "")),
                            snippet=item.get("snippet", item.get("description", "")),
                            source="talordata",
                            metadata={
                                'engine': self.name,
                                'display_link': item.get("display_link", item.get("displayLink", ""))
                            }
                        ))
                    
                    await self.record_success()
                    return results
                    
            except Exception as e:
                await self.record_error()
                logger.error(f"TalorData search failed: {e}")
                
        return []
