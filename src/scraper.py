"""
Free web scraping using httpx + BeautifulSoup
No API keys required
"""
import httpx
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse
import re


class ScraperService:
    """Free web scraper using httpx and BeautifulSoup"""
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.timeout = 10.0
    
    def scrape_url(self, url: str) -> Optional[str]:
        """
        Scrape a URL and return clean text content
        
        Args:
            url: The URL to scrape
            
        Returns:
            Cleaned text content or None if failed
        """
        try:
            with httpx.Client(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                
                return self._extract_content(response.text, url)
                
        except httpx.TimeoutException:
            print(f"Timeout scraping: {url}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"HTTP error {e.response.status_code}: {url}")
            return None
        except Exception as e:
            print(f"Scrape error: {e}")
            return None
    
    def _extract_content(self, html: str, url: str) -> str:
        """Extract and clean text content from HTML"""
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", 
                           "aside", "form", "button", "iframe", "noscript"]):
            element.decompose()
        
        # Try to find main content area
        main_content = (
            soup.find("main") or 
            soup.find("article") or 
            soup.find(class_=re.compile(r"content|main|article", re.I)) or
            soup.find("body")
        )
        
        if main_content:
            text = main_content.get_text(separator="\n", strip=True)
        else:
            text = soup.get_text(separator="\n", strip=True)
        
        # Clean up the text
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = "\n".join(lines)
        
        # Limit length to avoid token limits
        return cleaned[:5000]
    
    def get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc