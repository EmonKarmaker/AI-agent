"""
Developer Tools Research API
FastAPI application for researching developer tools using AI
"""
import os
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()

from src.workflow import ResearchWorkflow
from src.models import ResearchState


# Request/Response Models
class ResearchRequest(BaseModel):
    query: str = Field(
        ..., 
        min_length=3, 
        max_length=200,
        description="What developer tools to research",
        examples=["best database for startups", "React state management libraries"]
    )


class ToolInfo(BaseModel):
    name: str
    website: str
    description: str
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    language_support: list[str] = []
    integrations: list[str] = []


class ResearchResponse(BaseModel):
    id: str = Field(description="Unique research ID")
    query: str
    tools: list[ToolInfo]
    recommendations: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    version: str
    groq_configured: bool


# Cache
research_cache: dict[str, ResearchResponse] = {}


# App Setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Developer Tools Research API")
    if not os.getenv("GROQ_API_KEY"):
        print("⚠️ WARNING: GROQ_API_KEY not set!")
    else:
        print("✅ Groq API configured")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="Developer Tools Research API",
    description="""
## 🔍 AI-Powered Developer Tools Research

This API uses an agentic AI workflow to research and compare developer tools.

### Features
- **Automatic tool discovery** from tech articles
- **Deep analysis** of each tool (pricing, features, integrations)
- **AI recommendations** tailored to your needs

### Tech Stack (100% Free)
- **LLM**: Groq (Llama 3.3 70B)
- **Search**: DuckDuckGo
- **Orchestration**: LangGraph
    """,
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Endpoints
@app.get("/", tags=["Info"])
async def root():
    return {
        "message": "Developer Tools Research API",
        "docs": "/docs",
        "health": "/health",
        "research": "POST /research"
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        groq_configured=bool(os.getenv("GROQ_API_KEY"))
    )


@app.post("/research", response_model=ResearchResponse, tags=["Research"])
async def research_tools(request: ResearchRequest):
    try:
        workflow = ResearchWorkflow()
        result: ResearchState = workflow.run(request.query)
        
        tools = [
            ToolInfo(
                name=c.name,
                website=c.website,
                description=c.description,
                pricing_model=c.pricing_model,
                is_open_source=c.is_open_source,
                language_support=c.language_support,
                integrations=c.integration_capabilities
            )
            for c in result.companies
        ]
        
        response = ResearchResponse(
            id=str(uuid.uuid4()),
            query=request.query,
            tools=tools,
            recommendations=result.analysis or "No recommendations generated",
            timestamp=datetime.utcnow().isoformat()
        )
        
        research_cache[response.id] = response
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Research error: {e}")
        raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")


@app.get("/research/{research_id}", response_model=ResearchResponse, tags=["Research"])
async def get_research(research_id: str):
    if research_id not in research_cache:
        raise HTTPException(status_code=404, detail="Research not found")
    return research_cache[research_id]


@app.get("/examples", tags=["Info"])
async def get_examples():
    return {
        "examples": [
            {"query": "best database for startups", "description": "Compare Supabase, PlanetScale, Neon"},
            {"query": "React state management libraries", "description": "Compare Redux, Zustand, Jotai"},
            {"query": "Python web frameworks 2024", "description": "Compare FastAPI, Django, Flask"},
            {"query": "free backend as a service", "description": "Compare Firebase alternatives"},
            {"query": "best CI/CD tools for small teams", "description": "Compare GitHub Actions, GitLab CI"},
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)