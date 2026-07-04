import asyncio
import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

async def run_checkpoint():
    if not SERPER_API_KEY or not OPENROUTER_API_KEY:
        print("❌ ERROR: Missing API keys in .env")
        return

    print("Initiating Checkpoint 0...\n")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Test Serper.dev
        print("Testing Serper API...")
        try:
            serper_resp = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
                json={"q": "OpenAI", "num": 1}
            )
            if serper_resp.status_code == 200:
                print("✅ Serper API: Connected and authenticated!")
            else:
                print(f"❌ Serper API Failed: {serper_resp.status_code} - {serper_resp.text}")
        except Exception as e:
            print(f"❌ Serper API Exception: {str(e)}")

        # 2. Test OpenRouter
        print("\nTesting OpenRouter API...")
        try:
            or_resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "google/gemma-4-31b-it:free", # Fast/free ping
                    "messages": [{"role": "user", "content": "Ping. Reply with exactly 'Pong'."}]
                }
            )
            if or_resp.status_code == 200:
                print("✅ OpenRouter API: Connected and authenticated!")
                data = or_resp.json()
                print(f"   Response: {data['choices'][0]['message']['content']}")
            else:
                print(f"❌ OpenRouter API Failed: {or_resp.status_code} - {or_resp.text}")
        except Exception as e:
            print(f"❌ OpenRouter API Exception: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_checkpoint())