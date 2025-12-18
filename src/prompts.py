class DeveloperToolsPrompts:
    """Prompts optimized for developer tools research"""

    TOOL_EXTRACTION_SYSTEM = """You are a tech researcher specializing in developer tools.
Extract specific tool, library, platform, or service names from articles.
Focus on actual products developers can use, not general concepts."""

    @staticmethod
    def tool_extraction_user(query: str, content: str) -> str:
        return f"""Query: {query}

Article Content:
{content[:3000]}

Extract the most relevant tool/service names for "{query}".

Rules:
- Only actual product names (not generic terms)
- Tools developers can directly use
- Include open source and commercial options
- Maximum 5 tools
- Return ONLY tool names, one per line

Example output:
Supabase
PlanetScale
Railway"""

    TOOL_ANALYSIS_SYSTEM = """You are analyzing developer tools. Extract structured information.
Be concise and accurate. If information is not found, use appropriate defaults."""

    @staticmethod
    def tool_analysis_user(tool_name: str, content: str) -> str:
        return f"""Tool: {tool_name}

Content:
{content[:2500]}

Analyze and return a JSON object with:
{{
    "pricing_model": "Free" | "Freemium" | "Paid" | "Enterprise" | "Unknown",
    "is_open_source": true | false | null,
    "tech_stack": ["list of supported technologies"],
    "description": "One sentence about what it does",
    "api_available": true | false | null,
    "language_support": ["Python", "JavaScript", etc.],
    "integration_capabilities": ["GitHub", "Docker", etc.]
}}

Return ONLY valid JSON, no markdown formatting."""

    RECOMMENDATIONS_SYSTEM = """You are a senior developer giving concise tech recommendations.
Be direct and actionable. Format with markdown for readability."""

    @staticmethod
    def recommendations_user(query: str, tools_data: str) -> str:
        return f"""Query: {query}

Tools Analyzed:
{tools_data}

Provide recommendations in this format:

## 🏆 Top Pick
[Best tool and why in 2-3 sentences]

## 💰 Pricing Comparison
| Tool | Model | Best For |
|------|-------|----------|
[Fill table]

## ⚡ Quick Verdict
[2-3 sentences on which to choose based on use case]

Keep it brief and useful for developers."""