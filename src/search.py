from typing import List
from duckduckgo_search import DDGS
from .models import SearchResult


class SearchService:
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
            
            return [
                SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", "")
                )
                for r in results
            ]
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_for_tools(self, query: str) -> List[SearchResult]:
        enhanced_query = f"{query} developer tools comparison best 2024"
        return self.search(enhanced_query, max_results=3)
    
    def search_official_site(self, tool_name: str) -> List[SearchResult]:
        query = f"{tool_name} official site"
        return self.search(query, max_results=1)