import os
from typing import List
from tavily import TavilyClient
from .models import SearchResult


class SearchService:
    
    def __init__(self):
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("Missing TAVILY_API_KEY. Get free key at: https://app.tavily.com")
        self.client = TavilyClient(api_key=api_key)
        print("✅ Tavily Search ready")
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="basic"
            )
            
            results = []
            for r in response.get("results", []):
                results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", "")[:500]
                ))
            
            print(f"✅ Found {len(results)} results for: {query[:30]}...")
            return results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def search_for_tools(self, query: str) -> List[SearchResult]:
        enhanced_query = f"{query} tools comparison best 2024"
        return self.search(enhanced_query, max_results=5)
    
    def search_official_site(self, tool_name: str) -> List[SearchResult]:
        query = f"{tool_name} official website"
        return self.search(query, max_results=1)