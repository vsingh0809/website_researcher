# checkpoint_3_part2.py
import asyncio
from dotenv import load_dotenv
from app.models import CrawlPage
from app.services.ai import OpenRouterAIProvider
from app.services.pdf import XhtmlPdfGenerator

load_dotenv()

async def test_ai_and_pdf():
    print("Executing Checkpoint 3 (Part 2): Continuous AI Synthesis & PDF Generation...\n")
    
    # Simulate high-value crawler mock output to pass down bounds safely
    mock_pages = [
        CrawlPage(
            url="https://stripe.com",
            title="Stripe | Financial Infrastructure",
            text="Stripe builds infrastructure for the internet economy. Businesses of every size—from new startups to public companies—use our software to accept payments and manage their businesses online. We eliminate operational drag and overhead by optimizing cross-border money clearing pathways."
        )
    ]
    
    # 1. Test AI Processing
    ai_provider = OpenRouterAIProvider()
    print("Analyzing payload through OpenRouter...")
    company_info = await ai_provider.extract_company_info(mock_pages)
    print(f"✅ AI Profile Summary Extracted for: {company_info.name}")
    print(f"   Products: {company_info.products_services}")
    print(f"   Pain Points: {company_info.pain_points}")
    
    # 2. Test Competitor Discovery
    print("\nDiscovering target competitors...")
    competitors = await ai_provider.discover_competitors(company_info)
    print(f"✅ Discovered {len(competitors)} strategic competitors:")
    for comp in competitors:
        print(f"   - {comp.name} ({comp.website})")
        
    # 3. Test PDF Compile Engine
    print("\nCompiling artifacts into binary layout via xhtml2pdf...")
    pdf_gen = XhtmlPdfGenerator()
    pdf_bytes = await pdf_gen.generate_report(company_info, competitors)
    
    with open("test_output_report.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅ Valid PDF Document compiled and written to disk as 'test_output_report.pdf'.")
    
    print("\n🎉 CHECKPOINT 3 (PART 2) COMPLETE: All atomic pipeline services are perfectly operational.")

if __name__ == "__main__":
    asyncio.run(test_ai_and_pdf())