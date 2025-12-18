from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .models import ResearchState, CompanyInfo
from .search import SearchService
from .scraper import ScraperService
from .llm import LLMService


# Fallback data for common queries when search fails
FALLBACK_TOOLS = {
    "database": ["Supabase", "PlanetScale", "Neon", "Firebase"],
    "backend": ["Supabase", "Firebase", "Appwrite", "Convex"],
    "state": ["Redux", "Zustand", "Jotai", "Recoil"],
    "framework": ["Next.js", "Remix", "Astro", "SvelteKit"],
    "api": ["FastAPI", "Express", "Hono", "tRPC"],
    "auth": ["Auth0", "Clerk", "NextAuth", "Supabase Auth"],
    "default": ["GitHub", "Vercel", "Netlify", "Railway"]
}


def get_fallback_tools(query: str) -> list[str]:
    """Get fallback tools based on query keywords"""
    query_lower = query.lower()
    for keyword, tools in FALLBACK_TOOLS.items():
        if keyword in query_lower:
            return tools
    return FALLBACK_TOOLS["default"]


class ResearchWorkflow:
    
    def __init__(self):
        self.search = SearchService()
        self.scraper = ScraperService()
        self.llm = LLMService()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_node)
        graph.add_node("research", self._research_node)
        graph.add_node("analyze", self._analyze_node)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()
    
    def _extract_tools_node(self, state: ResearchState) -> Dict[str, Any]:
        print(f"🔍 Step 1: Finding tools for '{state.query}'")
        
        # Try search
        search_results = self.search.search_for_tools(state.query)
        
        tools = []
        
        if search_results:
            # Build content from snippets
            all_content = "\n".join([
                f"{r.title}: {r.snippet}" 
                for r in search_results
            ])
            
            # Try scraping first result for more content
            if search_results[0].url:
                scraped = self.scraper.scrape_url(search_results[0].url)
                if scraped:
                    all_content += f"\n\n{scraped}"
            
            # Extract tools with LLM
            if len(all_content) > 50:
                tools = self.llm.extract_tools(state.query, all_content)
        
        # Fallback if no tools found
        if not tools:
            print("⚠️ Using fallback tools")
            tools = get_fallback_tools(state.query)
        
        print(f"📦 Tools to research: {tools}")
        
        return {
            "extracted_tools": tools,
            "search_results": search_results
        }
    
    def _research_node(self, state: ResearchState) -> Dict[str, Any]:
        tools = state.extracted_tools[:4]
        print(f"🔬 Step 2: Researching {len(tools)} tools")
        
        companies = []
        
        for tool_name in tools:
            print(f"  → Researching: {tool_name}")
            
            # Search for tool
            results = self.search.search_official_site(tool_name)
            
            website = ""
            content = ""
            snippet = ""
            
            if results:
                website = results[0].url
                snippet = results[0].snippet
                content = self.scraper.scrape_url(website)
            
            # Analyze with LLM if we have content
            if content and len(content) > 100:
                analysis = self.llm.analyze_tool(tool_name, content)
                company = CompanyInfo(
                    name=tool_name,
                    description=analysis.description,
                    website=website,
                    pricing_model=analysis.pricing_model,
                    is_open_source=analysis.is_open_source,
                    tech_stack=analysis.tech_stack,
                    api_available=analysis.api_available,
                    language_support=analysis.language_support,
                    integration_capabilities=analysis.integration_capabilities
                )
            else:
                # Basic info without scraping
                company = CompanyInfo(
                    name=tool_name,
                    description=snippet or f"{tool_name} - developer tool",
                    website=website or f"https://www.google.com/search?q={tool_name}",
                    pricing_model="Unknown"
                )
            
            companies.append(company)
            print(f"  ✅ Added: {tool_name}")
        
        return {"companies": companies}
    
    def _analyze_node(self, state: ResearchState) -> Dict[str, Any]:
        print("📝 Step 3: Generating recommendations")
        
        if not state.companies:
            return {"analysis": "No tools found. Try queries like 'best database for startups' or 'React state management'."}
        
        tools_data = "\n\n".join([
            f"**{c.name}**\n"
            f"- Website: {c.website}\n"
            f"- Pricing: {c.pricing_model or 'Unknown'}\n"
            f"- Open Source: {c.is_open_source}\n"
            f"- Description: {c.description}\n"
            f"- Languages: {', '.join(c.language_support) if c.language_support else 'N/A'}\n"
            f"- Integrations: {', '.join(c.integration_capabilities) if c.integration_capabilities else 'N/A'}"
            for c in state.companies
        ])
        
        analysis = self.llm.generate_recommendations(state.query, tools_data)
        
        return {"analysis": analysis}
    
    def run(self, query: str) -> ResearchState:
        print(f"\n{'='*50}")
        print(f"🚀 Starting research: {query}")
        print(f"{'='*50}\n")
        
        initial_state = ResearchState(query=query)
        result = self.workflow.invoke(initial_state)
        
        print(f"\n{'='*50}")
        print(f"✅ Research complete!")
        print(f"{'='*50}\n")
        
        return ResearchState(**result)