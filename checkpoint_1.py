# checkpoint_1.py
from app.models import CompanyInput, CompanyInfo, CompetitorInfo, CrawlPage, ResearchResult, ChatMessage

def test_models():
    print("Executing Checkpoint 1: Validating Pydantic Data Models...")

    # 1. Test CompanyInput
    input_data = {"company_name": "Stripe", "website_url": "https://stripe.com"}
    CompanyInput(**input_data)
    print("✅ CompanyInput validated successfully.")

    # 2. Test CompanyInfo
    info_data = {
        "name": "Stripe",
        "website": "https://stripe.com",
        "phone": "+1 800 555 0199",
        "address": "San Francisco, CA",
        "products_services": ["Payments API", "Billing", "Radar"],
        "pain_points": ["High international cross-border fees", "Complex onboarding for legacy enterprise"]
    }
    company_info = CompanyInfo(**info_data)
    print("✅ CompanyInfo validated successfully.")

    # 3. Test CompetitorInfo
    comp_data = {"name": "Adyen", "website": "https://adyen.com"}
    competitor = CompetitorInfo(**comp_data)
    print("✅ CompetitorInfo validated successfully.")

    # 4. Test CrawlPage
    page_data = {"url": "https://stripe.com/about", "title": "About Stripe", "text": "Stripe is a financial infrastructure platform..."}
    crawl_page = CrawlPage(**page_data)
    print("✅ CrawlPage validated successfully.")

    # 5. Test ResearchResult
    result_data = {
        "company_info": info_data,
        "competitors": [comp_data],
        "crawled_pages": [page_data]
    }
    ResearchResult(**result_data)
    print("✅ ResearchResult composite model validated successfully.")

    # 6. Test ChatMessage
    msg_data = {"role": "user", "content": "Analyze Stripe's competitors."}
    ChatMessage(**msg_data)
    print("✅ ChatMessage validated successfully.")

    print("\n🎉 CHECKPOINT 1 PASSED: All structural definitions are bulletproof.")

if __name__ == "__main__":
    test_models()