"""
LangGraph Workflow - Orchestrates the research agent
"""
from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .models import ResearchState, CompanyInfo
from .search import SearchService
from .scraper import ScraperService
from .llm import LLMService


class ResearchWorkflow:
    """
    Agentic workflow for researching developer tools
    
    Flow:
    1. extract_tools - Find relevant tools from articles
    2. research - Gather detailed info on each tool
    3. analyze - Generate recommendations
    """
    
    def __init__(self):
        self.search = SearchService()
        self.scraper = ScraperService()
        self.llm = LLMService()
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        graph = StateGraph(ResearchState)
        
        # Add nodes
        graph.add_node("extract_tools", self._extract_tools_node)
        graph.add_node("research", self._research_node)
        graph.add_node("analyze", self._analyze_node)
        
        # Define flow
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        
        return graph.compile()
    
    def _extract_tools_node(self, state: ResearchState) -> Dict[str, Any]:
        """Step 1: Find and extract tool names from articles"""
        print(f"🔍 Searching for tools: {state.query}")
        
        # Search for comparison articles
        search_results = self.search.search_for_tools(state.query)
        
        if not search_results:
            return {
                "extracted_tools": [],
                "error": "No search results found"
            }
        
        # Scrape articles and extract content
        all_content = ""
        for result in search_results[:3]:
            content = self.scraper.scrape_url(result.url)
            if content:
                all_content += f"\n\n--- From {result.title} ---\n{content[:1500]}"
        
        if not all_content:
            return {
                "extracted_tools": [],
                "search_results": search_results
            }
        
        # Extract tool names using LLM
        tools = self.llm.extract_tools(state.query, all_content)
        print(f"📦 Found tools: {', '.join(tools)}")
        
        return {
            "extracted_tools": tools,
            "search_results": search_results
        }
    
    def _research_node(self, state: ResearchState) -> Dict[str, Any]:
        """Step 2: Research each tool in detail"""
        tools = state.extracted_tools[:4]
        
        if not tools:
            print("⚠️ No tools extracted, using search results")
            tools = [r.title.split()[0] for r in state.search_results[:3]]
        
        print(f"🔬 Researching: {', '.join(tools)}")
        
        companies = []
        for tool_name in tools:
            # Find official site
            results = self.search.search_official_site(tool_name)
            
            if not results:
                continue
            
            result = results[0]
            
            # Scrape the official site
            content = self.scraper.scrape_url(result.url)
            
            if content:
                # Analyze with LLM
                analysis = self.llm.analyze_tool(tool_name, content)
                
                company = CompanyInfo(
                    name=tool_name,
                    description=analysis.description,
                    website=result.url,
                    pricing_model=analysis.pricing_model,
                    is_open_source=analysis.is_open_source,
                    tech_stack=analysis.tech_stack,
                    api_available=analysis.api_available,
                    language_support=analysis.language_support,
                    integration_capabilities=analysis.integration_capabilities
                )
                companies.append(company)
                print(f"  ✅ Analyzed: {tool_name}")
            else:
                companies.append(CompanyInfo(
                    name=tool_name,
                    description=result.snippet,
                    website=result.url
                ))
                print(f"  ⚠️ Limited data: {tool_name}")
        
        return {"companies": companies}
    
    def _analyze_node(self, state: ResearchState) -> Dict[str, Any]:
        """Step 3: Generate recommendations"""
        print("📝 Generating recommendations...")
        
        if not state.companies:
            return {"analysis": "No tools found to analyze. Try a different query."}
        
        # Format tool data for LLM
        tools_data = "\n\n".join([
            f"**{c.name}**\n"
            f"- Website: {c.website}\n"
            f"- Pricing: {c.pricing_model or 'Unknown'}\n"
            f"- Open Source: {c.is_open_source}\n"
            f"- Description: {c.description}\n"
            f"- Languages: {', '.join(c.language_support) or 'N/A'}\n"
            f"- Integrations: {', '.join(c.integration_capabilities) or 'N/A'}"
            for c in state.companies
        ])
        
        analysis = self.llm.generate_recommendations(state.query, tools_data)
        
        return {"analysis": analysis}
    
    def run(self, query: str) -> ResearchState:
        """Execute the research workflow"""
        initial_state = ResearchState(query=query)
        result = self.workflow.invoke(initial_state)
        return ResearchState(**result)