# app/dependencies.py
from app.interfaces import SearchProvider, WebCrawler, AIProvider, PDFGenerator
from app.services.search import SerperSearchProvider
from app.services.crawler import HttpxCrawler
from app.services.ai import OpenRouterAIProvider
from app.services.pdf import XhtmlPdfGenerator

# Instantiate services once at module level (Composition Root)
_search_service = SerperSearchProvider()
_crawler_service = HttpxCrawler(max_pages=4)
_ai_service = OpenRouterAIProvider()
_pdf_service = XhtmlPdfGenerator()

def get_search_provider() -> SearchProvider:
    return _search_service

def get_crawler() -> WebCrawler:
    return _crawler_service

def get_ai_provider() -> AIProvider:
    return _ai_service

def get_pdf_generator() -> PDFGenerator:
    return _pdf_service