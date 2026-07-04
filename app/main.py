# app/main.py
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, Response
from app.models import CompanyInput, ResearchResult
from app.interfaces import SearchProvider, WebCrawler, AIProvider, PDFGenerator
from app.dependencies import get_search_provider, get_crawler, get_ai_provider, get_pdf_generator
from app.exceptions import register_exception_handlers, SearchFailedException, AISynthesisException

app = FastAPI(title="AI Company Research Assistant API", version="1.0.0")



# Load environment variables explicitly for local run / runtime safety
load_dotenv()



app = FastAPI(title="AI Company Research Assistant API", version="1.0.0")
# ... remainder of your file stays exactly the same

# Register custom global exception handlers
register_exception_handlers(app)

@app.post("/research", response_model=ResearchResult)
async def perform_research(
    payload: CompanyInput,
    search_svc: SearchProvider = Depends(get_search_provider),
    crawler_svc: WebCrawler = Depends(get_crawler),
    ai_svc: AIProvider = Depends(get_ai_provider)
):
    # Step 1: Resolve the official target URL if only a name is passed
    target_url = payload.website_url
    if not target_url:
        target_url = await search_svc.search_company_website(payload.company_name)
        if not target_url:
            raise SearchFailedException(
                f"Could not automatically resolve an official website for '{payload.company_name}'. Please explicitly provide a URL.", 
                status_code=404
            )

    # Step 2: Extract text via Crawler
    pages = await crawler_svc.crawl_website(target_url)

    # Step 3: Analyze extracted data via AI Router
    try:
        company_info = await ai_svc.extract_company_info(pages)
    except Exception as e:
        raise AISynthesisException(f"AI Deep Extraction Layer Failed: {str(e)}", status_code=502)

    # Force inputs into model synchronization if LLM changes returned details
    if not company_info.name or company_info.name.lower() == "company name":
        company_info.name = payload.company_name
    company_info.website = target_url

    # Step 4: Map strategic competitors
    competitors = await ai_svc.discover_competitors(company_info)

    return ResearchResult(
        company_info=company_info,
        competitors=competitors,
        crawled_pages=pages
    )

@app.post("/generate-pdf")
async def generate_pdf_report(
    result: ResearchResult,
    pdf_svc: PDFGenerator = Depends(get_pdf_generator)
):
    pdf_bytes = await pdf_svc.generate_report(result.company_info, result.competitors)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={result.company_info.name.replace(' ', '_')}_report.pdf"}
    )