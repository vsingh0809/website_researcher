# AI-Powered Company Research Assistant

An AI-powered corporate intelligence platform that automates company research from a company name or website URL. The system discovers the official company website, crawls important business pages, enriches the collected information using Google Knowledge Graph, generates structured insights with an LLM, identifies competitors, and produces a professional PDF report.

---

## 🚀 Live Demo

**Frontend:** https://hackathon-frontend-fp1a.onrender.com/

---

# Features

- Search using either:
  - Company Name
  - Company Website URL
- Automatically discovers the official company website
- Intelligent web crawling of important pages
- Google Knowledge Graph integration via Serper.dev
- AI-powered structured company analysis
- Automatic competitor discovery
- Professional PDF report generation
- Fault-tolerant pipeline with graceful degradation
- Clean Streamlit interface
- FastAPI backend with asynchronous architecture

---

# Project Architecture

```
hackathon-researcher/
│
├── .env
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── interfaces.py
│   ├── exceptions.py
│   ├── dependencies.py
│   │
│   └── services/
│       ├── __init__.py
│       ├── search.py
│       ├── crawler.py
│       ├── ai.py
│       └── pdf.py
│
└── frontend/
    └── app.py
```

---

# Workflow

```text
User Input
     │
     ▼
Company Name / Website
     │
     ▼
Resolve Official Website
     │
     ▼
Web Crawling
(Home, About, Products,
Services, Pricing, Contact)
     │
     ▼
Google Knowledge Graph
(Serper.dev)
     │
     ▼
Context Merging
     │
     ▼
OpenRouter AI
     │
     ▼
Structured Company Profile
     │
     ▼
Competitor Discovery
     │
     ▼
PDF Report Generation
```

---

# Technology Stack

| Category | Technology |
|----------|------------|
| Backend | FastAPI |
| Frontend | Streamlit |
| AI | OpenRouter API |
| Search | Serper.dev |
| Web Crawling | HTTPX + BeautifulSoup4 |
| PDF Generation | xhtml2pdf |
| Data Validation | Pydantic |
| Dependency Management | uv |
| Language | Python 3.12 |

---

# Key Architectural Features

## 1. Fault-Tolerant AI Pipeline

The application is designed to handle failures gracefully.

- Automatic exponential backoff
- Retry using `retry_after_seconds`
- Handles HTTP 429 rate limits
- Dynamic model fallback when required
- Prevents pipeline failures

---

## 2. Dual-Source Data Validation

Information is merged using a strict priority hierarchy:

```
Google Knowledge Graph
        ↓
Website Crawl
        ↓
Unknown
```

Critical business information such as:

- Headquarters
- Phone Number
- Website
- Business Description

is always taken from the most authoritative available source.

---

## 3. Robust JSON Parsing

LLM responses often vary in structure.

The application automatically supports formats like:

```json
{
  "company_info": { ... }
}
```

and

```json
{
  ...
}
```

before validating with Pydantic models.

---

## 4. Graceful Degradation

If one stage fails, the system continues whenever possible.

Examples:

- Cloudflare blocks crawling
- Missing company pages
- Competitor search failure
- Partial Knowledge Graph data

The report is still generated instead of terminating the request.

---

# Installation

## 1. Clone Repository

```bash
git clone <repository-url>
cd hackathon-researcher
```

---

## 2. Create Virtual Environment

```bash
uv venv --python 3.12
```

Activate the environment.

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Install Dependencies

```bash
uv pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create a `.env` file.

```env
SERPER_API_KEY=your_serper_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

---

# Running Locally

## Backend

```bash
uvicorn app.main:app --reload --port 8000
```

Swagger Documentation:

```
http://localhost:8000/docs
```

---

## Frontend

```bash
streamlit run frontend/app.py --server.port 8501
```

Application:

```
http://localhost:8501
```

---

# Production Deployment (Render)

## Backend Service

Create a Render **Web Service**.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables

```text
SERPER_API_KEY
OPENROUTER_API_KEY
```

---

## Frontend Service

Create another Render **Web Service**.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
```

### Environment Variable

```text
API_URL=https://your-backend-service.onrender.com
```

> **Note:** Do not include a trailing slash (`/`) in the `API_URL`.

---

# API Flow

```
Client
   │
   ▼
FastAPI
   │
   ├── Search Service
   │
   ├── Website Crawler
   │
   ├── Knowledge Graph
   │
   ├── OpenRouter AI
   │
   ├── Competitor Discovery
   │
   └── PDF Generator
           │
           ▼
Structured Company Report
```

---


# License

This project was developed as part of a hackathon submission and is intended for educational and demonstration purposes.