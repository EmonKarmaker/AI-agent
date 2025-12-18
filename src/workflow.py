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
        print(f"🔍 Step 1: Searching for '{state.query}'")
        
        search_results = self.search.search_for_tools(state.query)
        
        if not search_results:
            return {
                "extracted_tools": [],
                "search_results": [],
                "error": "No search results found"
            }
        
        all_content = "\n\n".join([
            f"Title: {r.title}\nURL: {r.url}\nContent: {r.snippet}" 
            for r in search_results
        ])
        
        if search_results[0].url:
            print(f"📥 Scraping: {search_results[0].url[:50]}...")
            scraped = self.scraper.scrape_url(search_results[0].url)
            if scraped:
                all_content += f"\n\nFull page content:\n{scraped[:2000]}"
                print(f"✅ Scraped {len(scraped)} chars")
        
        print(f"🤖 Extracting tools from {len(all_content)} chars...")
        tools = self.llm.extract_tools(state.query, all_content)
        
        print(f"📦 Found tools: {tools}")
        
        return {
            "extracted_tools": tools[:5],
            "search_results": search_results
        }
    
    def _research_node(self, state: ResearchState) -> Dict[str, Any]:
        tools = state.extracted_tools[:4]
        
        if not tools:
            print("⚠️ No tools found")
            return {"companies": []}
        
        print(f"🔬 Step 2: Researching {len(tools)} tools")
        
        companies = []
        
        for tool_name in tools:
            print(f"  → {tool_name}")
            
            results = self.search.search_official_site(tool_name)
            
            if not results:
                print(f"    ⚠️ No results for {tool_name}")
                continue
            
            result = results[0]
            content = self.scraper.scrape_url(result.url)
            
            if content and len(content) > 100:
                print(f"    🤖 Analyzing {len(content)} chars...")
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
                print(f"    ✅ Analyzed")
            else:
                company = CompanyInfo(
                    name=tool_name,
                    description=result.snippet,
                    website=result.url,
                    pricing_model="Unknown"
                )
                print(f"    ⚠️ Using snippet only")
            
            companies.append(company)
        
        return {"companies": companies}
    
    def _analyze_node(self, state: ResearchState) -> Dict[str, Any]:
        print("📝 Step 3: Generating recommendations")
        
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
        
        return {"analysis": analysis}
    
    def run(self, query: str) -> ResearchState:
        print(f"\n{'='*50}")
        print(f"🚀 LIVE RESEARCH: {query}")
        print(f"{'='*50}\n")
        
        initial_state = ResearchState(query=query)
        result = self.workflow.invoke(initial_state)
        
        print(f"\n✅ Research complete!\n")
        
        return ResearchState(**result)