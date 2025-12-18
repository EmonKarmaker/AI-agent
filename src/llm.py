import os
import json
import re
from groq import Groq
from .models import CompanyAnalysis
from .prompts import DeveloperToolsPrompts


class LLMService:
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("Missing GROQ_API_KEY")
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"
        self.prompts = DeveloperToolsPrompts()
    
    def extract_tools(self, query: str, content: str) -> list[str]:
        try:
            print(f"🤖 Extracting tools from {len(content)} chars...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompts.TOOL_EXTRACTION_SYSTEM},
                    {"role": "user", "content": self.prompts.tool_extraction_user(query, content)}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            text = response.choices[0].message.content.strip()
            print(f"🤖 LLM response: {text[:100]}")
            
            # Parse tool names
            tools = []
            for line in text.split("\n"):
                line = line.strip()
                # Remove numbering, bullets, dashes
                line = re.sub(r'^[\d\.\-\*\•]+\s*', '', line)
                if line and len(line) < 50 and not line.startswith("Example"):
                    tools.append(line)
            
            print(f"✅ Extracted tools: {tools}")
            return tools[:5]
            
        except Exception as e:
            print(f"❌ Tool extraction error: {e}")
            return []
    
    def analyze_tool(self, tool_name: str, content: str) -> CompanyAnalysis:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompts.TOOL_ANALYSIS_SYSTEM},
                    {"role": "user", "content": self.prompts.tool_analysis_user(tool_name, content)}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            text = response.choices[0].message.content.strip()
            json_data = self._extract_json(text)
            
            return CompanyAnalysis(
                pricing_model=json_data.get("pricing_model", "Unknown"),
                is_open_source=json_data.get("is_open_source"),
                tech_stack=json_data.get("tech_stack", []),
                description=json_data.get("description", f"{tool_name} - developer tool"),
                api_available=json_data.get("api_available"),
                language_support=json_data.get("language_support", []),
                integration_capabilities=json_data.get("integration_capabilities", [])
            )
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return CompanyAnalysis(
                pricing_model="Unknown",
                description=f"{tool_name} - developer tool"
            )
    
    def generate_recommendations(self, query: str, tools_data: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.prompts.RECOMMENDATIONS_SYSTEM},
                    {"role": "user", "content": self.prompts.recommendations_user(query, tools_data)}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Recommendations error: {e}")
            return "Unable to generate recommendations."
    
    def _extract_json(self, text: str) -> dict:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        
        try:
            return json.loads(text)
        except:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {}