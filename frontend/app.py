# frontend/app.py
import streamlit as st
import httpx
import asyncio
import os
import re

# Set page config first
st.set_page_config(page_title="AI Research Assistant", page_icon="🕵️‍♂️", layout="centered")

# Backend API Configuration
# Defaults to localhost for Checkpoint 5; Render will inject the real URL later
API_URL = os.getenv("API_URL", "http://localhost:8000")

# --- Async Networking Functions ---

async def cycle_status_stages(status_placeholder, stop_event):
    """Client-side estimated progress tracking to provide UI feedback during blocking API calls."""
    stages = [
        "🔍 Searching Serper.dev to verify official domain...",
        "🕷️ Crawling website targets and extracting text payload...",
        "🧠 Synthesizing data through OpenRouter AI...",
        "⚔️ Mapping market landscape and competitors...",
        "📄 Compiling final data structures..."
    ]
    
    # Cycle through estimated stages (approx 6-8 seconds each for standard crawling/AI)
    for stage in stages:
        if stop_event.is_set():
            return
        status_placeholder.markdown(stage)
        # We wait in small chunks so we can break out immediately if the API returns early
        for _ in range(80): 
            if stop_event.is_set():
                return
            await asyncio.sleep(0.1)
            
    # If the API takes longer (e.g., rate limit retries), show a final holding message
    while not stop_event.is_set():
        status_placeholder.markdown("⏳ Handling upstream rate limits. Deep analysis continuing...")
        await asyncio.sleep(1)

async def fetch_research_data(company_name: str, website_url: str = None):
    """Calls the Phase 4 FastAPI backend to perform the research workflow."""
    payload = {"company_name": company_name, "website_url": website_url}
    
    # We use a long timeout because the AI fallback retry loop can take over a minute
    async with httpx.AsyncClient(timeout=300.0) as client:
        response = await client.post(f"{API_URL}/research", json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Backend API Error: {response.text}")
        return response.json()

async def fetch_pdf_report(research_result: dict):
    """Calls the FastAPI backend to compile the JSON into a binary PDF."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(f"{API_URL}/generate-pdf", json=research_result)
        if response.status_code != 200:
            raise RuntimeError(f"PDF Engine Error: {response.text}")
        return response.content

async def process_user_request(user_prompt: str):
    """Orchestrates the UI updates and API calls concurrently."""
    # Basic heuristic to check if the user provided a URL or just a name
    url_pattern = re.compile(r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+")
    urls = url_pattern.findall(user_prompt)
    website_url = urls[0] if urls else None
    
    # Clean up company name if a URL was provided alongside it
    company_name = user_prompt.replace(website_url, "").strip() if website_url else user_prompt
    if not company_name:
        company_name = "Target Company" # Fallback if they ONLY paste a URL

    with st.status("Initializing Research Protocol...", expanded=True) as status_box:
        status_text = st.empty()
        stop_event = asyncio.Event()
        
        # Run the UI cycler and the API call concurrently
        progress_task = asyncio.create_task(cycle_status_stages(status_text, stop_event))
        api_task = asyncio.create_task(fetch_research_data(company_name, website_url))
        
        try:
            research_data = await api_task
            stop_event.set() # Stop the UI cycler
            status_box.update(label="✅ Research Complete!", state="complete", expanded=False)
            return research_data
        except Exception as e:
            stop_event.set()
            status_box.update(label="❌ Research Failed", state="error", expanded=True)
            st.error(str(e))
            return None

# --- UI Layout & Logic ---

st.title("Corporate Research AI")
st.markdown("Enter a company name or paste a website URL to generate a comprehensive intelligence report.")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            # Render the cached JSON result beautifully
            data = msg["content"]
            info = data["company_info"]
            
            st.subheader(f"🏢 {info['name']}")
            st.markdown(f"**Domain:** [{info['website']}]({info['website']}) | **Location:** {info.get('address', 'N/A')} | **Phone:** {info.get('phone', 'N/A')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Core Products & Services:**")
                for p in info.get("products_services", []):
                    st.write(f"- {p}")
            with col2:
                st.write("**Identified Pain Points:**")
                for pp in info.get("pain_points", []):
                    st.write(f"- {pp}")
            
            st.write("**Strategic Competitors:**")
            comps = data.get("competitors", [])
            if comps:
                for c in comps:
                    st.write(f"- {c['name']} ({c['website']})")
            else:
                st.write("*No competitor data available (Upstream limits applied).*")
            
            # Show cached PDF download button
            if "pdf_bytes" in msg:
                st.download_button(
                    label="📄 Download PDF Report",
                    data=msg["pdf_bytes"],
                    file_name=f"{info['name'].replace(' ', '_')}_report.pdf",
                    mime="application/pdf",
                    key=f"dl_{info['name']}"
                )

# Input handling
if prompt := st.chat_input("E.g., 'Stripe' or 'https://stripe.com'"):
    # 1. Add and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 2. Add assistant response placeholder
    with st.chat_message("assistant"):
        # Execute the async data fetching
        result = asyncio.run(process_user_request(prompt))
        
        if result:
            info = result["company_info"]
            st.subheader(f"🏢 {info['name']}")
            st.markdown(f"**Domain:** [{info['website']}]({info['website']}) | **Location:** {info.get('address', 'N/A')} | **Phone:** {info.get('phone', 'N/A')}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("**Core Products & Services:**")
                for p in info.get("products_services", []):
                    st.write(f"- {p}")
            with col2:
                st.write("**Identified Pain Points:**")
                for pp in info.get("pain_points", []):
                    st.write(f"- {pp}")
            
            st.write("**Strategic Competitors:**")
            comps = result.get("competitors", [])
            if comps:
                for c in comps:
                    st.write(f"- {c['name']} ({c['website']})")
            else:
                st.write("*No competitor data available (Upstream limits applied).*")

            # 3. Fetch PDF silently in the background now that data is on screen
            with st.spinner("Compiling PDF layout..."):
                try:
                    pdf_bytes = asyncio.run(fetch_pdf_report(result))
                    st.download_button(
                        label="📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"{info['name'].replace(' ', '_')}_report.pdf",
                        mime="application/pdf"
                    )
                    # Cache the result and the binary PDF in session state so it persists on scroll/rerender
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": result,
                        "pdf_bytes": pdf_bytes
                    })
                except Exception as e:
                    st.error(f"Failed to compile PDF: {str(e)}")
                    st.session_state.messages.append({"role": "assistant", "content": result})