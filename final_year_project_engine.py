"""
Charvak Final Year Project Assistant - AI-Powered
Personalized project support using GPT-4o-mini
(DB-backed - Session E/4)
"""
import logging
import json
import os
import secrets
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger("charvakit.fyp")



def _runtime_key_present() -> bool:
    """Return True if an OpenAI key is available right now."""
    import os as _os
    return bool(_os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY)

# Session 43-D fix: load .env before reading OPENAI_API_KEY.
# Without this, the module-level constant is empty because the
# shell env only populates after load_dotenv() runs.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class FinalYearProjectEngine:
    """AI-powered final year project support (subscriptions DB-backed)."""

    PLANS = {
        "free":    {"name": "Free",    "price": 0,   "features": ["Topic suggestions (5)", "Basic outline"]},
        "pro":     {"name": "Pro",     "price": 299, "features": ["AI personalized topics (20+)", "AI proposal generation", "Tech stack suggestion"]},
        "premium": {"name": "Premium", "price": 999, "features": ["Everything in Pro", "Full AI documentation", "Viva preparation", "Code starter templates", "Priority support"]},
    }

    def __init__(self):
        self._ensure_tables()
        logger.info(f"FYP Engine ready (DB-backed) | AI: {'Enabled' if OPENAI_API_KEY else 'Fallback mode'}")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_fyp_subscriptions (
                    subscription_id  TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    plan             TEXT NOT NULL DEFAULT 'free',
                    price            INTEGER DEFAULT 0,
                    status           TEXT NOT NULL DEFAULT 'active',
                    subscribed_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_fyp_subs_email  ON charvak_fyp_subscriptions(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_fyp_subs_plan   ON charvak_fyp_subscriptions(plan)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_fyp_subs_status ON charvak_fyp_subscriptions(status)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"fyp tables init failed: {e}")

    # ============================================================
    # AI HELPER (JSON-only response)
    # ============================================================

    def _ai_json(self, prompt: str, max_tokens: int, temperature: float):
        """Call OpenAI in JSON mode and return parsed dict, or None on failure."""
        try:
            import openai
            # Session 43-D: Runtime env re-read. The module-level
            # OPENAI_API_KEY can be empty if the module was imported
            # before load_dotenv() ran in some code paths. Re-read
            # at call time as a safety net.
            import os as _os
            _key = _os.getenv("OPENAI_API_KEY") or OPENAI_API_KEY
            if not _key:
                print("[FYP] OpenAI key missing at call time — falling back")
                return None
            client = openai.OpenAI(api_key=_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            # Defensive: strip accidental markdown fences even in JSON mode
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            return json.loads(content)
        except Exception as e:
            logger.warning(f"AI call failed: {e}")
            return None

    # ============================================================
    # AI-POWERED TOPIC SUGGESTIONS (stateless)
    # ============================================================

    def suggest_topics_ai(self, data: Dict) -> Dict:
        branch = data.get("branch", "Computer Science")
        domain = data.get("domain", "AI/ML")
        skills = data.get("skills", [])
        interests = data.get("interests", [])
        if OPENAI_API_KEY:
            prompt = f"""Generate 10 unique final year project topics for a {branch} student.

Domain: {domain}
Skills: {', '.join(skills) if skills else 'Not specified'}
Interests: {', '.join(interests) if interests else 'Open to suggestions'}

CRITICAL: Infer the correct discipline from the DOMAIN name and generate
projects appropriate to that discipline. Do NOT default to software
engineering projects.

Discipline rules:
- Engineering domains (CS, IT, AI/ML, Cybersecurity, IoT, Data Science,
  Electronics, Mechanical, Civil): produce software/hardware/system
  projects that involve building, coding, or prototyping.
- Business domains (MBA, Marketing, Finance, HR, Operations, Strategy,
  Consulting, Management): produce RESEARCH-BASED analytical projects
  using surveys, case studies, secondary data, or mixed methods.
  NOT software projects. NOT "build a chatbot". Instead: "A study of X",
  "An analysis of Y", "A comparative study of Z".
- Commerce domains (MCom, BCom, Accounting, Taxation): produce research
  or analytical projects on financial/accounting topics.
- Design domains (UX, Graphic, Product Design): produce portfolio-based
  or user-research projects.
- Other domains: infer the appropriate project shape from the domain.

Each project should include:
- "title": the project title (natural, discipline-appropriate)
- "domain": the domain
- "difficulty": Beginner / Intermediate / Advanced
- "description": 1-2 sentences describing the project AND its methodology
  (e.g., "Primary survey of N respondents" for MBA, "Python + TensorFlow
  implementation" for engineering)

Return JSON: {{"topics": [{{"title": "...", "domain": "...", "difficulty": "...", "description": "..."}}]}}"""
            topics_data = self._ai_json(prompt, max_tokens=1400, temperature=0.8)
            if topics_data is not None:
                return {"status": "success", "ai_generated": True, **topics_data}
        return self._fallback_topics(branch, domain)

    def _fallback_topics(self, branch: str, domain: str) -> Dict:
        topics = [
            {"title": "Chatbot for College Enquiry", "domain": domain, "difficulty": "Intermediate", "description": "AI chatbot answering college queries"},
            {"title": "Disease Prediction using ML", "domain": domain, "difficulty": "Advanced", "description": "Predict diseases from symptoms"},
            {"title": "Face Recognition Attendance", "domain": domain, "difficulty": "Intermediate", "description": "Automated attendance using face recognition"},
            {"title": "Sentiment Analysis Platform", "domain": domain, "difficulty": "Beginner", "description": "Analyze sentiment from reviews"},
            {"title": "Stock Price Predictor", "domain": domain, "difficulty": "Advanced", "description": "LSTM-based stock prediction"},
        ]
        return {"status": "success", "ai_generated": False, "topics": topics}

    # ============================================================
    # AI-POWERED PROPOSAL GENERATION (stateless)
    # ============================================================

    def generate_proposal_ai(self, data: Dict) -> Dict:
        topic = data.get("topic", "Project")
        student = data.get("student_name", "Student")
        college = data.get("college", "College")
        if OPENAI_API_KEY:
            prompt = f"""Generate a professional final year project proposal for:
            Student: {student}
            College: {college}
            Topic: {topic}

            Return JSON: {{"title": "...", "abstract": "...", "objectives": [...], "scope": "...", "tech_stack": [...], "modules": [...], "timeline": [...]}}"""
            proposal = self._ai_json(prompt, max_tokens=1000, temperature=0.7)
            if proposal is not None:
                return {"status": "success", "ai_generated": True, "proposal": proposal}
        return {"status": "success", "ai_generated": False, "proposal": self._fallback_proposal(topic)}

    def _fallback_proposal(self, topic: str) -> Dict:
        return {
            "title": topic,
            "abstract": f"This project focuses on {topic}.",
            "objectives": [f"Study {topic}", f"Design {topic}", f"Implement {topic}"],
            "scope": f"End-to-end development of {topic}",
            "tech_stack": ["Python", "React", "PostgreSQL"],
            "modules": ["Authentication", "Core Module", "Admin", "Reports"],
            "timeline": ["Week 1-2: Research", "Week 3-8: Development", "Week 9-12: Testing"],
        }

    # ============================================================
    # AI-POWERED DOCUMENTATION (stateless)
    # ============================================================

    def generate_documentation_ai(self, data: Dict) -> Dict:
        topic = data.get("topic", "Project")
        if OPENAI_API_KEY:
            prompt = f"""Generate complete documentation outline for final year project: {topic}
            Return JSON: {{"chapters": [{{"chapter": 1, "title": "...", "content_outline": "..."}}], "diagrams": [...], "documents": [...]}}"""
            docs = self._ai_json(prompt, max_tokens=800, temperature=0.5)
            if docs is not None:
                return {"status": "success", "ai_generated": True, "documentation": docs}
        return {"status": "success", "ai_generated": False, "documentation": self._fallback_docs(topic)}

    def _fallback_docs(self, topic: str) -> Dict:
        return {
            "chapters": [
                {"chapter": 1, "title": "Introduction", "content_outline": f"Background of {topic}"},
                {"chapter": 2, "title": "Literature Review", "content_outline": "Existing systems"},
                {"chapter": 3, "title": "System Design", "content_outline": "Architecture"},
                {"chapter": 4, "title": "Implementation", "content_outline": "Code structure"},
                {"chapter": 5, "title": "Testing", "content_outline": "Test cases"},
                {"chapter": 6, "title": "Conclusion", "content_outline": "Summary"},
            ],
            "diagrams": ["Use Case", "ER Diagram", "Class Diagram"],
            "documents": ["SRS", "SDD", "User Manual"],
        }

    def expand_chapter_ai(self, data: Dict) -> Dict:
        """Expand a documentation chapter outline into full prose. Stateless."""
        topic = data.get("topic", "Project")
        chapter_title = data.get("chapter_title", "").strip()
        chapter_outline = data.get("chapter_outline", "").strip()
        chapter_num = data.get("chapter_number", 0)

        if not chapter_title:
            return {"status": "error", "message": "chapter_title required."}

        if OPENAI_API_KEY:
            prompt = (
                f"You are writing one chapter of a final year project report.\n"
                f"Project topic: {topic}\n"
                f"Chapter {chapter_num}: {chapter_title}\n"
                f"Outline: {chapter_outline}\n\n"
                "Write the full chapter content in academic prose (600-900 words). "
                "Use 3-5 subsections with markdown-style headers (## Subsection). "
                "Be specific to the project topic — no generic filler.\n"
                "Return JSON: {\"chapter_content\": \"...\"}"
            )
            result = self._ai_json(prompt, max_tokens=2000, temperature=0.5)
            if result is not None and result.get("chapter_content"):
                return {
                    "status": "success",
                    "ai_generated": True,
                    "chapter": {
                        "chapter": chapter_num,
                        "title": chapter_title,
                        "content": result["chapter_content"],
                    },
                }

        return {
            "status": "success",
            "ai_generated": False,
            "chapter": self._fallback_expand(chapter_num, chapter_title, chapter_outline),
        }

    def _fallback_expand(self, chapter_num: int, chapter_title: str, chapter_outline: str) -> Dict:
        """Offline fallback — structured prose derived from the outline."""
        body = (
            f"## Overview\n\n"
            f"This chapter covers {chapter_title.lower()}. {chapter_outline or 'Details to be expanded.'}\n\n"
            f"## Key Points\n\n"
            f"- {chapter_outline or 'Chapter scope'}\n"
            f"- Detailed discussion to be added\n\n"
            f"## Summary\n\n"
            f"The chapter establishes the foundation for {chapter_title.lower()} "
            f"within the overall project structure."
        )
        return {"chapter": chapter_num, "title": chapter_title, "content": body}

    # ============================================================
    # AI-POWERED VIVA PREP (stateless)
    # ============================================================

    def generate_viva_ai(self, data: Dict) -> Dict:
        """Generate viva questions with model answers.

        Returns questions as list of {"q": ..., "a": ...} objects so the
        frontend can show a "Show answer" toggle per question. Legacy
        string-only questions are normalized to this shape for compat.
        """
        topic = data.get("topic", "Project")
        if OPENAI_API_KEY:
            prompt = (
                f"Generate 15 viva questions with model answers for a final year project on: {topic}\n\n"
                "Include technical, architectural, and general questions a real examiner would ask.\n\n"
                "Return STRICT JSON only with this exact shape:\n"
                "{\n"
                '  "questions": [\n'
                '    {"q": "<question text>", "a": "<2-4 sentence model answer a strong student would give>"},\n'
                "    ...\n"
                "  ],\n"
                '  "tips": ["<tip 1>", "<tip 2>", "<tip 3>"]\n'
                "}"
            )
            viva = self._ai_json(prompt, max_tokens=1800, temperature=0.6)
            if viva is not None and isinstance(viva.get("questions"), list):
                normalized = []
                for item in viva["questions"]:
                    if isinstance(item, str):
                        normalized.append({"q": item, "a": ""})
                    elif isinstance(item, dict):
                        q_text = str(item.get("q") or item.get("question") or "").strip()
                        a_text = str(item.get("a") or item.get("answer") or "").strip()
                        if q_text:
                            normalized.append({"q": q_text, "a": a_text})
                if normalized:
                    viva["questions"] = normalized
                    return {"status": "success", "ai_generated": True, **viva}
        return {
            "status": "success",
            "ai_generated": False,
            "questions": [
                {"q": f"Why did you choose {topic}?", "a": ""},
                {"q": "What technologies did you use?", "a": ""},
                {"q": "What challenges did you face?", "a": ""},
                {"q": "How does your project differ from existing solutions?", "a": ""},
                {"q": "What future enhancements would you suggest?", "a": ""},
            ],
            "tips": [
                "Be specific with numbers and examples",
                "Know your architecture diagram cold",
                "Prepare a 30-second demo pitch",
            ],
        }

    # ============================================================
    # MONETIZATION (DB-backed)
    # ============================================================

    def generate_citations_ai(self, data: Dict) -> Dict:
        """
        Generate proper citations for a chapter or topic.

        Body: {topic, chapter_title?, content?}
        Returns: {"citations": {"ieee": [...], "apa": [...], "mla": [...]}, "notes": "..."}

        Each citation is a full formatted string ready to paste into the
        references section. AI-generated; the student should verify the
        actual source exists before submitting.
        """
        topic = (data.get("topic") or "").strip()
        chapter_title = (data.get("chapter_title") or "").strip()
        chapter_content = (data.get("content") or "").strip()

        if not topic:
            return {"status": "error", "message": "topic required."}

        # Cap the pasted content to keep tokens bounded
        if len(chapter_content) > 4000:
            chapter_content = chapter_content[:4000]

        if _runtime_key_present():
            prompt = (
                "You are helping a final year engineering student write the References "
                "section of their project report.\n\n"
                f"Project topic: {topic}\n"
                f"Chapter: {chapter_title or 'General'}\n"
            )
            if chapter_content:
                prompt += f"Chapter content (for context):\n{chapter_content}\n\n"
            prompt += (
                "Generate 6 real, plausible academic or industry references "
                "that a project on this topic would cite. For each reference, "
                "give the full formatted string in THREE citation styles.\n\n"
                "Rules:\n"
                "- Include a mix: 3-4 academic papers, 1-2 books, 1-2 industry/standard sources.\n"
                "- Author names, years, titles, journals/publishers must look plausible for the topic.\n"
                "- IEEE format: [N] A. Author, \"Title,\" Journal, vol. X, no. Y, pp. Z, Year.\n"
                "- APA format: Author, A. A. (Year). Title. Journal, Volume(Issue), Pages.\n"
                "- MLA format: Author. \"Title.\" Journal, vol. X, no. Y, Year, pp. Z.\n"
                "- Add a short 'note' field per reference explaining what it supports.\n\n"
                "Return STRICT JSON only with this exact shape:\n"
                "{\n"
                '  "citations": [\n'
                '    {\n'
                '      "ieee": "<IEEE formatted string>",\n'
                '      "apa": "<APA formatted string>",\n'
                '      "mla": "<MLA formatted string>",\n'
                '      "note": "<what this reference supports in the report>"\n'
                '    }\n'
                "  ],\n"
                '  "notes": "<one-line advice about verifying real sources before submission>"\n'
                "}"
            )
            result = self._ai_json(prompt, max_tokens=3000, temperature=0.4)
            if result and result.get("citations"):
                return {"status": "success", **result}

        # Fallback — generic templates
        return self._fallback_citations(topic, chapter_title)

    def _fallback_citations(self, topic: str, chapter_title: str) -> Dict:
        """Generic fallback when AI is unavailable. Clearly placeholder citations."""
        return {
            "status": "success",
            "citations": [
                {
                    "ieee": f"[1] A. Author, \"Foundations of {topic},\" Journal of {topic}, vol. 1, no. 1, pp. 1-10, 2024.",
                    "apa": f"Author, A. (2024). Foundations of {topic}. Journal of {topic}, 1(1), 1-10.",
                    "mla": f"Author, A. \"Foundations of {topic}.\" Journal of {topic}, vol. 1, no. 1, 2024, pp. 1-10.",
                    "note": f"Placeholder for {chapter_title or topic}. Replace with a real source."
                }
            ],
            "notes": "AI was unavailable. Please search Google Scholar, IEEE Xplore, or the ACM Digital Library for real references on this topic and format them manually."
        }

    def generate_roadmap_ai(self, data: Dict) -> Dict:
        """
        Generate a week-by-week milestone roadmap for a final year project.

        Body: {topic, duration_weeks (default 16)}
        Returns: {"roadmap": [{"week": N, "title": "...", "goal": "...",
                               "deliverables": [...], "tools": [...]}], "tips": [...]}
        """
        topic = (data.get("topic") or "").strip()
        try:
            duration = int(data.get("duration_weeks") or 16)
        except Exception:
            duration = 16
        # Sanity clamp
        duration = max(4, min(24, duration))

        if not topic:
            return {"status": "error", "message": "topic required."}

        if _runtime_key_present():
            prompt = (
                f"You are planning a final year engineering project on: {topic}\n"
                f"Duration: {duration} weeks\n\n"
                "Produce a phase-based milestone roadmap.\n\n"
                "Rules:\n"
                "- Return between 4 and 7 phases total (ONE entry per phase, not per deliverable)\n"
                "- Each phase covers a range of weeks, in order: research → design → implementation → testing → report\n"
                "- Each phase must have: 1 clear goal, 2-4 deliverables, 2-4 tools\n"
                "- Week ranges must cover the full duration without overlap or gaps\n"
                "- Be specific to the project topic, not generic\n"
                "- DO NOT return multiple entries for the same phase or the same week range\n"
                "- DO NOT repeat a phase title\n\n"
                "Return STRICT JSON only with this exact shape:\n"
                "{\n"
                '  "roadmap": [\n'
                '    {\n'
                '      "week": 1,\n'
                '      "week_range": "1-2",\n'
                '      "title": "<phase title>",\n'
                '      "goal": "<what the student must accomplish>",\n'
                '      "deliverables": ["<item>", "<item>"],\n'
                '      "tools": ["<tool>", "<tool>"]\n'
                '    }\n'
                "  ],\n"
                '  "tips": ["<3-5 short tips to stay on track>"]\n'
                "}"
            )
            result = self._ai_json(prompt, max_tokens=3500, temperature=0.4)
            if result and result.get("roadmap"):
                return {"status": "success", **result}

        # Fallback
        return self._fallback_roadmap(topic, duration)

    def _fallback_roadmap(self, topic: str, duration: int) -> Dict:
        """Generic fallback roadmap when AI is unavailable."""
        phases = [
            ("Research & Literature Review", "Survey existing work and define scope"),
            ("Design & Architecture", "Finalise system design and component choices"),
            ("Implementation", "Build the core system iteratively"),
            ("Testing & Validation", "Unit test, integration test, and validate against requirements"),
            ("Report Writing & Viva Prep", "Write the final report and prepare for viva"),
        ]
        roadmap = []
        for i, (title, goal) in enumerate(phases):
            start = 1 + (i * duration) // len(phases)
            end = ((i + 1) * duration) // len(phases)
            roadmap.append({
                "week": start,
                "week_range": f"{start}-{end}" if start != end else str(start),
                "title": title,
                "goal": f"{goal} for {topic}",
                "deliverables": [f"{title} section in the report"],
                "tools": ["(define per your project)"],
            })
        return {
            "status": "success",
            "roadmap": roadmap,
            "tips": [
                "AI was unavailable — this is a generic roadmap. Refine it manually.",
                "Set a weekly check-in with your guide.",
                "Keep an evidence log (screenshots, notes) as you go.",
            ],
        }

    def subscribe(self, data: Dict) -> Dict:
        """
        Subscribe to FYP plan.
        data = {email, plan}
        """
        plan_key = data.get("plan", "free")
        plan = self.PLANS.get(plan_key, self.PLANS["free"])
        subscription_id = f"FYP-SUB-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_fyp_subscriptions
                    (subscription_id, email, plan, price, status)
                VALUES (%s, %s, %s, %s, 'active')
            ''', (subscription_id, data.get("email"), plan_key, plan["price"]))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"subscribe failed: {e}")
            return {"status": "error", "message": "Could not subscribe"}

        return {
            "status": "success",
            "plan": plan["name"],
            "price": plan["price"],
            "features": plan["features"],
            "message": f"Subscribed to {plan['name']}!",
        }

    def get_plans(self) -> Dict:
        return {"status": "success", "plans": self.PLANS}

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*), COALESCE(SUM(price), 0) FROM charvak_fyp_subscriptions')
            row = cur.fetchone()
            total_subscriptions = row[0] or 0
            total_revenue = row[1] or 0
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                # total_projects removed - was hardcoded 0 with no live consumers
                "total_subscriptions": total_subscriptions,
                "total_revenue": total_revenue,
                "ai_enabled": bool(OPENAI_API_KEY),
            },
        }


final_year_project_engine = FinalYearProjectEngine()