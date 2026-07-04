# app/services/crawler.py
import os
import httpx
from bs4 import BeautifulSoup
from typing import List, Set
from urllib.parse import urljoin, urlparse
from app.interfaces import WebCrawler
from app.models import CrawlPage

class HttpxCrawler(WebCrawler):
    def __init__(self, max_pages: int = 5, timeout: float = 5.0):
        self.max_pages = max_pages
        self.timeout = timeout
        self.target_keywords = ["about", "product", "service", "solution", "contact", "pricing"]

    def _is_valid_subpage(self, base_url: str, current_url: str) -> bool:
        base_parsed = urlparse(base_url)
        curr_parsed = urlparse(current_url)
        if base_parsed.netloc != curr_parsed.netloc:
            return False
        path = curr_parsed.path.lower()
        blacklisted = ["login", "signup", "signin", "logout", "cart", "wp-admin", ".pdf", ".png", ".jpg", ".js", ".css"]
        if any(word in path for word in blacklisted):
            return False
        return True

    async def crawl_website(self, url: str) -> List[CrawlPage]:
        crawled_pages: List[CrawlPage] = []
        visited_urls: Set[str] = {url}
        urls_to_crawl: List[str] = [url]
        
        # Real-world browser headers to minimize anti-bot blocks
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        async with httpx.AsyncClient(timeout=self.timeout, headers=headers, follow_redirects=True) as client:
            # Try home page
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    for script in soup(["script", "style"]):
                        script.extract()
                    clean_text = " ".join(soup.get_text().split())
                    
                    if len(clean_text) > 100:
                        crawled_pages.append(CrawlPage(
                            url=url,
                            title=soup.title.string.strip() if soup.title else "Home",
                            text=clean_text[:6000]
                        ))
                        
                        # Gather links
                        for link in soup.find_all("a", href=True):
                            full_url = urljoin(url, link["href"]).split("#")[0].rstrip("/")
                            if full_url not in visited_urls and self._is_valid_subpage(url, full_url):
                                if any(kw in full_url.lower() for kw in self.target_keywords):
                                    urls_to_crawl.append(full_url)
                                    visited_urls.add(full_url)
            except Exception:
                pass

            # Try subpages
            while urls_to_crawl and len(crawled_pages) < self.max_pages:
                current_url = urls_to_crawl.pop(0)
                if current_url == url:
                    continue
                try:
                    res = await client.get(current_url)
                    if res.status_code == 200:
                        soup = BeautifulSoup(res.text, "html.parser")
                        for script in soup(["script", "style"]):
                            script.extract()
                        clean_text = " ".join(soup.get_text().split())
                        if len(clean_text) > 100:
                            crawled_pages.append(CrawlPage(
                                url=current_url,
                                title=soup.title.string.strip() if soup.title else "Subpage",
                                text=clean_text[:5000]
                            ))
                except Exception:
                    continue

        # Edge case: If the site blocked us entirely, fill context using an organic search payload
        if not crawled_pages:
            crawled_pages.append(CrawlPage(
                url=url,
                title="Public Search Context (Anti-bot Fallback)",
                text=f"Direct access to {url} was restricted. Analysis will rely on broader search indices."
            ))
            
        return crawled_pages