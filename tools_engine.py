"""
Charvak AI Tools Engine
Shared backend for all 12 viral revenue tools
"""
import os
import json
import httpx
from typing import Dict, List, Optional
from datetime import datetime

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE = "https://api.openai.com/v1"

class ToolsEngine:
    """Unified engine for all 12 viral tools"""
    
    def __init__(self):
        self.tool_usage = {}
        self.revenue_tracker = {}
    
    async def call_ai(self, prompt: str, max_tokens: int = 1000) -> Optional[str]:
        """Generic AI call for all tools"""
        if not OPENAI_API_KEY:
            return None
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{OPENAI_BASE}/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens, "temperature": 0.7}
                )
                return response.json()["choices"][0]["message"]["content"]
        except:
            return None
    
    def track_usage(self, tool_name: str, revenue: float = 0):
        """Track tool usage and revenue"""
        if tool_name not in self.tool_usage:
            self.tool_usage[tool_name] = {"uses": 0, "revenue": 0}
        self.tool_usage[tool_name]["uses"] += 1
        self.tool_usage[tool_name]["revenue"] += revenue
    
    def get_stats(self) -> Dict:
        return {
            "total_tools": len(self.tool_usage),
            "total_uses": sum(t["uses"] for t in self.tool_usage.values()),
            "total_revenue": sum(t["revenue"] for t in self.tool_usage.values()),
            "tools": self.tool_usage
        }

# Initialize
tools_engine = ToolsEngine()
print("✅ Tools Engine ready - 12 products supported")