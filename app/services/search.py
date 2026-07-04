import os
import httpx
from typing import Optional
from app.interfaces import SearchProvider
from dotenv import load_dotenv

# Load environment variables explicitly for local run / runtime safety
load_dotenv()

class SerperSearchProvider(SearchProvider):
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.url = "https://google.serper.dev/search"

    async def search_company_website(self, company_name: str) -> Optional[str]:
        if not self.api_key:
            raise ValueError("SERPER_API_KEY environment variable is not set.")
            
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "q": f"{company_name} official website home",
            "num": 3
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(self.url, headers=headers, json=payload)
            if response.status_code != 200:
                return None
                
            data = response.json()
            organic_results = data.get("organic", [])
            
            if not organic_results:
                return None
                
            # Return the link of the top organic search result
            return organic_results[0].get("link")