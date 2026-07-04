import os
import json
import httpx
import asyncio
from typing import List
from app.interfaces import AIProvider
from app.models import CompanyInfo, CompetitorInfo, CrawlPage

class OpenRouterAIProvider(AIProvider):
    def __init__(self, model_name: str = "openrouter/free"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        # Overriding to use the dynamic free router to prevent single-provider rate locks
        self.model_name = "openrouter/free"

    async def _post_with_retry(self, client: httpx.AsyncClient, system_prompt: str, user_content: str, max_retries: int = 4) -> dict:
        """Helper to post to OpenRouter with automatic backoff parsing for 429 errors."""
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"}  # Forces compatible models to return structured JSON
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",  # OpenRouter ranking preference metrics
            "X-Title": "Hackathon Researcher"
        }

        base_delay = 2.0
        for attempt in range(max_retries):
            response = await client.post(self.url, headers=headers, json=payload)
            
            # Explicitly capture rate limit errors
            if response.status_code == 429:
                wait_time = base_delay * (2 ** attempt)  # Fallback exponential backoff
                try:
                    error_json = response.json()
                    # Pull exact upstream pause time if provided by OpenRouter
                    wait_time = error_json.get("error", {}).get("metadata", {}).get("retry_after_seconds", wait_time)
                except Exception:
                    pass
                
                print(f"[!] Rate limited (429). Retrying in {float(wait_time):.2f}s... (Attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(float(wait_time))
                continue
                
            if response.status_code != 200:
                raise RuntimeError(f"OpenRouter Extraction Failed Status {response.status_code}: {response.text}")
                
            return response.json()
            
        raise RuntimeError(f"OpenRouter operations failed after exceeding {max_retries} rate-limit retries.")

    def _clean_json_content(self, raw_content: str) -> str:
        """Strip markdown fences gracefully if the model returns them."""
        content = raw_content.strip()
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
        return content

    async def extract_company_info(self, crawled_pages: List[CrawlPage]) -> CompanyInfo:
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing.")
            
        context_text = "\n\n".join([f"Source ({p.url}):\n{p.text}" for p in crawled_pages])
        
        system_prompt = (
            "You are an elite corporate research analyst. Analyze the provided text context and return raw JSON matching this structure exactly:\n"
            "{\n"
            "  \"name\": \"Company Name\",\n"
            "  \"website\": \"Official URL\",\n"
            "  \"phone\": \"Phone number or null\",\n"
            "  \"address\": \"Physical headquarters or null\",\n"
            "  \"products_services\": [\"Product A\", \"Service B\"],\n"
            "  \"pain_points\": [\"Specific operational or market risk/pain point 1\", \"Pain point 2\"]\n"
            "}\n"
            "Return only the valid JSON block. No markdown wrappers, no introductory chat."
        )

        async with httpx.AsyncClient(timeout=45.0) as client:
            user_content = f"Analyze this crawled text content:\n{context_text[:15000]}"
            data = await self._post_with_retry(client, system_prompt, user_content)
            
            raw_text = data["choices"][0]["message"]["content"]
            cleaned_text = self._clean_json_content(raw_text)
            parsed = json.loads(cleaned_text)
            return CompanyInfo(**parsed)

    async def discover_competitors(self, company_info: CompanyInfo) -> List[CompetitorInfo]:
        if not self.api_key:
            return []

        system_prompt = (
            "You are an industry analysis engine. Identify 3 to 5 realistic market competitors for the given company profile.\n"
            "Return a raw JSON list matching this format exactly:\n"
            "[\n"
            "  {\"name\": \"Competitor 1 Name\", \"website\": \"https://competitor1.com\"},\n"
            "  {\"name\": \"Competitor 2 Name\", \"website\": \"https://competitor2.com\"}\n"
            "]\n"
            "Provide real, functional website domains. Return only raw JSON data."
        )

        async with httpx.AsyncClient(timeout=45.0) as client:
            user_content = f"Find competitors for this company:\nName: {company_info.name}\nWebsite: {company_info.website}\nServices: {', '.join(company_info.products_services)}"
            
            try:
                data = await self._post_with_retry(client, system_prompt, user_content)
                raw_text = data["choices"][0]["message"]["content"]
                cleaned_text = self._clean_json_content(raw_text)
                parsed = json.loads(cleaned_text)
                return [CompetitorInfo(**item) for item in parsed]
            except Exception as e:
                print(f"[-] Competitor discovery failed gracefully: {e}")
                return []
