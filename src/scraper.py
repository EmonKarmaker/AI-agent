import httpx
from bs4 import BeautifulSoup
from typing import Optional
import re
import warnings

warnings.filterwarnings("ignore")


class ScraperService:
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
    
    def scrape_url(self, url: str) -> Optional[str]:
        try:
            with httpx.Client(
                headers=self.headers,
                timeout=10.0,
                follow_redirects=True,
                verify=False
            ) as client:
                response = client.get(url)
                
                if response.status_code == 200:
                    content = self._extract_content(response.text)
                    print(f"✅ Scraped {len(content)} chars from {url[:40]}")
                    return content
                else:
                    print(f"❌ HTTP {response.status_code}: {url[:40]}")
                    return None
                    
        except Exception as e:
            print(f"❌ Scrape failed: {e}")
            return None
    
    def _extract_content(self, html: str) -> str:
        try:
            soup = BeautifulSoup(html, "html.parser")
            
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r'\s+', ' ', text)
            
            return text[:5000]
        except:
            return ""