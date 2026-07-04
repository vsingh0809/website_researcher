# app/models.py
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class CompanyInput(BaseModel):
    company_name: str = Field(..., description="Name of the company to research")
    website_url: Optional[str] = Field(None, description="Optional baseline website URL")

class CompanyInfo(BaseModel):
    name: str
    website: str
    phone: Optional[str] = None
    address: Optional[str] = None
    products_services: List[str] = Field(default_factory=list)
    pain_points: List[str] = Field(default_factory=list)

class CompetitorInfo(BaseModel):
    name: str
    website: str

class CrawlPage(BaseModel):
    url: str
    title: Optional[str] = None
    text: str

class ResearchResult(BaseModel):
    company_info: CompanyInfo
    competitors: List[CompetitorInfo] = Field(default_factory=list)
    crawled_pages: List[CrawlPage] = Field(default_factory=list)

class ChatMessage(BaseModel):
    role: str 
    content: str