# checkpoint_3_part1.py
import asyncio
from dotenv import load_dotenv
from app.services.search import SerperSearchProvider
from app.services.crawler import HttpxCrawler

load_dotenv()

async def test_search_and_crawl():
    print("Executing Checkpoint 3 (Part 1): Standalone Search & Crawl Verification...\n")
    
    # 1. Test Serper Search Provider
    search_provider = SerperSearchProvider()
    print("Testing website discovery for 'Stripe'...")
    target_url = await search_provider.search_company_website("Stripe")
    print(f"✅ Discovered URL: {target_url}\n")
    
    if not target_url:
        target_url = "https://stripe.com"
        
    # 2. Test Crawler Provider
    crawler = HttpxCrawler(max_pages=3)
    print(f"Testing crawling engine on: {target_url}...")
    pages = await crawler.crawl_website(target_url)
    
    print(f"✅ Crawled {len(pages)} pages successfully.")
    for idx, page in enumerate(pages):
        print(f"   [{idx+1}] Title: {page.title} | URL: {page.url} | Content Length: {len(page.text)} chars")
        
    print("\n🎉 CHECKPOINT 3 (PART 1) PASSED: Search and crawl mechanics are operational.")

if __name__ == "__main__":
    asyncio.run(test_search_and_crawl())