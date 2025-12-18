"""
Free web search using DuckDuckGo - no API key required
"""
from typing import List
from duckduckgo_search import DDGS
from .models import SearchResult


class SearchService:
    """DuckDuckGo search - completely free, no API key needed"""
    
    def __init__(self):
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search the web using DuckDuckGo
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of SearchResult objects
        """
        try:
            results = list(self.ddgs.text(
                query,
                max_results=max_results,
                region="wt-wt",
                safesearch="moderate"
            ))
            
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
        """Search specifically for developer tools articles"""
        enhanced_query = f"{query} developer tools comparison best 2024"
        return self.search(enhanced_query, max_results=3)
    
    def search_official_site(self, tool_name: str) -> List[SearchResult]:
        """Find the official site for a specific tool"""
        query = f"{tool_name} official site documentation"
        return self.search(query, max_results=1)