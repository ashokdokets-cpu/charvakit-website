"""
Charvakit AI Service - Centralized OpenAI Integration
Powers all 8 AI-dependent models using GPT-4o-mini
"""
import os
import json
import httpx
from typing import Optional, Dict, List

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE = "https://api.openai.com/v1"

async def call_openai(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 2000, temperature: float = 0.7, json_mode: bool = False) -> Optional[str]:
    """Generic OpenAI API call. Set json_mode=True to force valid JSON output."""
    if not OPENAI_API_KEY:
        return None

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OPENAI_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json=payload,
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenAI API error: {type(e).__name__}: {e}")
        return None

# --- Model-Specific Functions ---

async def generate_assessment_questions(stack: str, difficulty: str, count: int) -> List[Dict]:
    """AI Stack Generator - Generate assessment questions"""
    prompt = f"""Generate {count} multiple-choice assessment questions about {stack} at {difficulty} level.
    Return ONLY valid JSON array: [{{"q":"question","o":["A","B","C","D"],"a":0}}]
    Correct answer index (a) must be 0-3. Make questions practical and test real understanding of {stack}."""
    
    result = await call_openai(prompt, temperature=0.7, max_tokens=2000)
    if result:
        try:
            return json.loads(result)
        except:
            pass
    return []

async def voice_to_website(transcript: str, language: str) -> Dict:
    """Voice-to-Web - Generate website from voice transcript"""
    prompt = f"""Parse this business description and generate a complete HTML website.
Description ({language}): {transcript}

Return ONLY a JSON object (no prose, no markdown, no code fences) with:
- business_name: string
- category: string
- description: string
- services: list of objects with keys "name" and "price" (prices in Indian Rupees, format as "₹1,500")
- contact: object with keys "phone", "email", "address"
- html: a complete, valid, mobile-optimized HTML document (including <!DOCTYPE html>, <html>, <head>, <body>) with inline Tailwind CSS via CDN
"""
    result = await call_openai(prompt, temperature=0.5, max_tokens=4000, json_mode=True)
    if not result:
        return {}
    # Defensive: strip code fences if present
    cleaned = result.strip()
    if cleaned.startswith("```"):
        # Remove leading ```json or ``` and trailing ```
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    try:
        return json.loads(cleaned)
    except Exception as e:
        print(f"voice_to_website parse error: {type(e).__name__}: {e}")
        print(f"  first 200 chars: {cleaned[:200]!r}")
        return {}

async def neural_wireframe_to_code(sketch_description: str) -> str:
    """Neural Wireframe - Convert sketch description to code"""
    prompt = f"""Generate production-ready React + Tailwind CSS component based on this description:
    {sketch_description}
    Return complete JSX code with responsive design."""
    return await call_openai(prompt, temperature=0.3, max_tokens=3000) or ""

async def localize_website(url: str, target_language: str) -> Dict:
    """Globalize.ai - Localize website content"""
    prompt = f"""Generate localization recommendations for {url} in {target_language}.
    Include: translated content, cultural adaptations, compliance notes.
    Return JSON."""
    result = await call_openai(prompt, temperature=0.5, max_tokens=2000)
    if result:
        try:
            return json.loads(result)
        except:
            pass
    return {}

async def generate_legal_contract(company: str, contractor_country: str, service: str) -> str:
    """Geo-Compliance - Generate compliant contract"""
    prompt = f"""Draft a jurisdiction-aware contractor agreement for:
    Company: {company}
    Contractor Country: {contractor_country}
    Service: {service}
    Include IP assignment, payment terms, termination clauses.
    Ensure compliance with local labor laws."""
    return await call_openai(prompt, temperature=0.3, max_tokens=3000) or ""

async def analyze_legacy_code(code: str) -> Dict:
    """Legacy-Shift - Analyze and modernize legacy code"""
    prompt = f"""Analyze this legacy code and provide modernization plan:
    {code[:3000]}
    Return JSON with: vulnerabilities, dependencies, recommended_stack, migration_steps"""
    result = await call_openai(prompt, temperature=0.3, max_tokens=2000)
    if result:
        try:
            return json.loads(result)
        except:
            pass
    return {}

async def generate_agent_schema(url: str) -> Dict:
    """Agent-Ready - Generate JSON-LD and micro-APIs"""
    prompt = f"""Analyze {url} and generate AI-agent-ready schema.
    Return JSON with: json_ld_schema, micro_apis, product_catalog_structure"""
    result = await call_openai(prompt, temperature=0.3, max_tokens=2000)
    if result:
        try:
            return json.loads(result)
        except:
            pass
    return {}

# Health check
def is_ai_ready() -> bool:
    return bool(OPENAI_API_KEY)