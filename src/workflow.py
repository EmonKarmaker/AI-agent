from typing import Dict, Any
from langgraph.graph import StateGraph, END

from .models import ResearchState, CompanyInfo
from .search import SearchService
from .scraper import ScraperService
from .llm import LLMService


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
        print(f"🔍 Searching for tools: {state.query}")
        
        search_results = self.search.search_for_tools(state.query)
        print(f"📄 Found {len(search_results)} articles")
        
        if not search_results:
            # Fallback: use the query words as potential tools
            print("⚠️ No search results, using query as tool name")
            return {
                "extracted_tools": [state.query],
                "search_results": []
            }
        
        # Collect content from search snippets + scraped pages
        all_content = ""
        
        # First, use snippets (always available)
        for result in search_results:
            all_content += f"\n{result.title}: {result.snippet}"
        
        # Then try to scrape for more content
        for result in search_results[:2]:  # Only scrape top 2
            print(f"📥 Scraping: {result.url[:50]}...")
            content = self.scraper.scrape_url(result.url)
            if content:
                all_content += f"\n\n{content[:1500]}"
                print(f"✅ Got {len(content)} chars")
            else:
                print(f"⚠️ Scrape failed, using snippet")
        
        if len(all_content) < 100:
            print("⚠️ Not enough content, using query as tool")
            return {
                "extracted_tools": [state.query],
                "search_results": search_results
            }
        
        # Extract tools using LLM
        tools = self.llm.extract_tools(state.query, all_content)
        print(f"📦 Extracted tools: {tools}")
        
        if not tools:
            # Fallback: extract from search titles
            tools = [state.query]
        
        return {
            "extracted_tools": tools[:5],
            "search_results": search_results
        }
    
    def _research_node(self, state: ResearchState) -> Dict[str, Any]:
        tools = state.extracted_tools[:4]
        
        if not tools:
            tools = [state.query]
        
        print(f"🔬 Researching: {', '.join(tools)}")
        
        companies = []
        for tool_name in tools:
            print(f"  🔎 Looking up: {tool_name}")
            
            # Search for official site
            results = self.search.search_official_site(tool_name)
            
            if not results:
                print(f"  ⚠️ No results for {tool_name}")
                continue
            
            result = results[0]
            print(f"  🌐 Found: {result.url[:50]}")
            
            # Try to scrape
            content = self.scraper.scrape_url(result.url)
            
            if content and len(content) > 100:
                print(f"  📄 Scraped {len(content)} chars, analyzing...")
                analysis = self.llm.analyze_tool(tool_name, content)
                
                company = CompanyInfo(
                    name=tool_name,
                    description=analysis.description or result.snippet,
                    website=result.url,
                    pricing_model=analysis.pricing_model,
                    is_open_source=analysis.is_open_source,
                    tech_stack=analysis.tech_stack,
                    api_available=analysis.api_available,
                    language_support=analysis.language_support,
                    integration_capabilities=analysis.integration_capabilities
                )
            else:
                print(f"  ⚠️ Using snippet for {tool_name}")
                company = CompanyInfo(
                    name=tool_name,
                    description=result.snippet,
                    website=result.url,
                    pricing_model="Unknown"
                )
            
            companies.append(company)
            print(f"  ✅ Added: {tool_name}")
        
        return {"companies": companies}
    
    def _analyze_node(self, state: ResearchState) -> Dict[str, Any]:
        print("📝 Generating recommendations...")
        
        if not state.companies:
            return {"analysis": "No tools found to analyze. Try a different query."}
        
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
        print("✅ Recommendations generated")
        
        return {"analysis": analysis}
    
    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        result = self.workflow.invoke(initial_state)
        return ResearchState(**result)