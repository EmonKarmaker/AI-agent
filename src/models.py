from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class CompanyAnalysis(BaseModel):
    """Structured output for LLM company analysis"""
    pricing_model: str = Field(description="One of: Free, Freemium, Paid, Enterprise, Unknown")
    is_open_source: Optional[bool] = Field(default=None, description="True if open source")
    tech_stack: List[str] = Field(default_factory=list, description="Supported technologies")
    description: str = Field(default="", description="One-sentence description")
    api_available: Optional[bool] = Field(default=None, description="Has API/SDK access")
    language_support: List[str] = Field(default_factory=list, description="Supported languages")
    integration_capabilities: List[str] = Field(default_factory=list, description="Integrations")


class CompanyInfo(BaseModel):
    name: str
    description: str = ""
    website: str = ""
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    competitors: List[str] = []
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class ResearchState(BaseModel):
    query: str
    extracted_tools: List[str] = []
    companies: List[CompanyInfo] = []
    search_results: List[SearchResult] = []
    analysis: Optional[str] = None
    error: Optional[str] = None