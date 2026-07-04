# checkpoint_4.py
import time
from fastapi.testclient import TestClient
from app.main import app

from dotenv import load_dotenv

# Ensure environment variables are loaded for the test harness
load_dotenv()


client = TestClient(app)

def test_api_orchestration():
    print("Executing Checkpoint 4: Verifying FastAPI Orchestration Routing...\n")
    
    start_time = time.time()
    
    # 1. Test POST /research endpoint
    payload = {"company_name": "Tesla", "website_url": None}
    print("Sending research request to POST /research for 'Tesla'...")
    
    response = client.post("/research", json=payload)
    print(f"Response status received: {response.status_code}")
    
    if response.status_code != 200:
        print(f"❌ API Flow Errored: {response.text}")
        return
        
    data = response.json()
    print("✅ /research integrated core execution chain cleanly!")
    print(f"   Company Found: {data['company_info']['name']}")
    print(f"   Competitors Discovered: {len(data['competitors'])}")
    
    # 2. Test POST /generate-pdf payload transmission
    print("\nForwarding synthesis schema to POST /generate-pdf...")
    pdf_response = client.post("/generate-pdf", json=data)
    
    if pdf_response.status_code == 200 and b"%PDF" in pdf_response.content:
        print("✅ /generate-pdf processed schema and returned binary application/pdf response!")
    else:
        print(f"❌ PDF Engine Routing Failed: {pdf_response.status_code}")
        return

    print(f"\n🎉 CHECKPOINT 4 PASSED: FastAPI routing and DI are fully complete. Duration: {time.time() - start_time:.2f}s")

if __name__ == "__main__":
    test_api_orchestration()