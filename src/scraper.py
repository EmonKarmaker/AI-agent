import httpx
from bs4 import BeautifulSoup
from typing import Optional
import re


class ScraperService:
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
        self.timeout = 15.0
    
    def scrape_url(self, url: str) -> Optional[str]:
        try:
            with httpx.Client(
                headers=self.headers,
                timeout=self.timeout,
                follow_redirects=True,
                verify=False  # Some sites have SSL issues
            ) as client:
                response = client.get(url)
                response.raise_for_status()
                return self._extract_content(response.text)
        except httpx.TimeoutException:
            print(f"⏱️ Timeout: {url}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP {e.response.status_code}: {url}")
            return None
        except Exception as e:
            print(f"❌ Scrape error ({url}): {e}")
            return None
    
    def _extract_content(self, html: str) -> str:
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove unwanted elements
        for element in soup(["script", "style", "nav", "footer", "header", 
                           "aside", "form", "button", "iframe", "noscript",
                           "svg", "img", "video", "audio"]):
            element.decompose()
        
        # Try to find main content
        main_content = (
            soup.find("main") or 
            soup.find("article") or 
            soup.find(class_=re.compile(r"content|main|article|post", re.I)) or
            soup.find("body")
        )
        
        if main_content:
            text = main_content.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text[:5000] if text else ""