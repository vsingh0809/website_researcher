from typing import Protocol, List
from app.models import CompanyInfo, CompetitorInfo, CrawlPage

class SearchProvider(Protocol):
    async def search_company_website(self, company_name: str) -> str | None:
        """Returns the most likely official website URL for a given company name."""
        ...

class WebCrawler(Protocol):
    async def crawl_website(self, url: str) -> List[CrawlPage]:
        """Crawls a given URL and returns extracted text from key pages."""
        ...

class AIProvider(Protocol):
    async def extract_company_info(self, crawled_pages: List[CrawlPage]) -> CompanyInfo:
        """Analyzes crawled text and returns structured company data."""
        ...
        
    async def discover_competitors(self, company_info: CompanyInfo) -> List[CompetitorInfo]:
        """Identifies top competitors based on the extracted company profile."""
        ...

class PDFGenerator(Protocol):
    async def generate_report(self, company_info: CompanyInfo, competitors: List[CompetitorInfo]) -> bytes:
        """Generates a PDF report and returns it as a byte stream."""
        ...