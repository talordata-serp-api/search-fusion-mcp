import os
import httpx
from typing import Any, Dict, List
from .base import SearchEngine, SearchResult  # 继承原作者的基类

class TalorDataSearch(SearchEngine):
    """TalorData SERP API 搜索引擎实现"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("TALORDATA_API_KEY")
        self.name = "talordata"
        # 设置与 Google/Serper 同等的最高优先级 (Priority 1)
        self.priority = 1.0 

    async def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        if not self.api_key:
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
            "json": "1"  # 返回结构化 JSON
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, headers=headers, json=payload, timeout=15.0)
                if response.status_code == 200:
                    data = response.json()
                    raw_results = data.get("organic_results", [])[:num_results]
                    
                    # 转化为原作者专案标准的 SearchResult 对象结构
                    results = []
                    for item in raw_results:
                        results.append(SearchResult(
                            title=item.get("title", "No Title"),
                            link=item.get("link", item.get("url", "")),
                            snippet=item.get("snippet", item.get("description", "")),
                            engine=self.name
                        ))
                    return results
            except Exception as e:
                print(f"TalorData search failed: {e}")
                
        return []
