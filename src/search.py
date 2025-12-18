from typing import List
from .models import SearchResult


class SearchService:
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        try:
            from duckduckgo_search import DDGS
            
            ddgs = DDGS()
            results = ddgs.text(query, max_results=max_results)
            
            search_results = []
            for r in results:
                search_results.append(SearchResult(
                    title=r.get("title", ""),
                    url=r.get("href", ""),
                    snippet=r.get("body", "")
                ))
            
            print(f"✅ Search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def search_for_tools(self, query: str) -> List[SearchResult]:
        enhanced_query = f"{query} tools comparison best 2024"
        return self.search(enhanced_query, max_results=3)
    
    def search_official_site(self, tool_name: str) -> List[SearchResult]:
        query = f"{tool_name} official website"
        return self.search(query, max_results=1)