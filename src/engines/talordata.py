import os
import httpx
from typing import Dict, Any, List
from .base import BaseSearchEngine

class TalorDataSearch(BaseSearchEngine):
    """TalorData SERP API Implementation optimized for LLM workflow."""
    
    def __init__(self, client: httpx.AsyncClient):
        super().__init__(client)
        self.api_key = os.getenv("TALORDATA_API_KEY")
        self.name = "talordata"

    async def search(self, query: str, num_results: int = 10, **kwargs) -> List[Dict[str, Any]]:
        if not self.api_key:
            return []

        url = "https://talordata.com"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "q": query,
            "engine": "google"
        }

        try:
            response = await self.client.post(url, headers=headers, json=payload, timeout=15.0)
            if response.status_code == 200:
                data = response.json()
                raw_results = data.get("organic_results", [])[:num_results]
                
                # 转换为项目统一的规范输出格式
                return [
                    {
                        "title": item.get("title", "No Title"),
                        "link": item.get("link", item.get("url", "")),
                        "snippet": item.get("snippet", item.get("description", ""))
                    }
                    for item in raw_results
                ]
        except Exception as e:
            print(f"[{self.name.upper()}] Search failed: {e}")
        return []
