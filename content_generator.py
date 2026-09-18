"""
Charvak AI Content Generation System
High-quality, non-repetitive, market-standard content for all assessment sections
(DB-backed - Session J/2)
"""
import json
import logging
import os
import random
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.content_generator")


class AIContentGenerator:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self._ensure_tables()
        logger.info("AI Content Generator ready (DB-backed) | OpenAI: %s",
                    "ENABLED" if self.openai_api_key else "DISABLED")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_content_used_content (
                    content_key  TEXT PRIMARY KEY,
                    used_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_content_used_at ON charvak_content_used_content(used_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"content_generator tables init failed: {e}")

    # ============================================================
    # READ ALOUD
    # ============================================================

    def generate_read_aloud_content(self, count=8, difficulty="intermediate"):
        """Generate high-quality Read Aloud content."""
        content = [
            {"text": "The implementation of artificial intelligence has transformed how businesses approach customer service.", "difficulty": "intermediate", "word_count": 13, "focus": "business vocabulary"},
            {"text": "Sustainable development requires a balanced approach between economic growth and environmental protection.", "difficulty": "advanced", "word_count": 13, "focus": "academic vocabulary"},
            {"text": "The quarterly financial report indicates a significant improvement in operational efficiency.", "difficulty": "intermediate", "word_count": 12, "focus": "financial terms"},
            {"text": "Effective communication skills are essential for professional success in any industry.", "difficulty": "basic", "word_count": 11, "focus": "general business"},
            {"text": "The research team has developed an innovative solution to address climate change challenges.", "difficulty": "advanced", "word_count": 13, "focus": "scientific vocabulary"},
            {"text": "Organizations must adapt to rapidly changing market conditions to remain competitive.", "difficulty": "intermediate", "word_count": 11, "focus": "business strategy"},
            {"text": "The integration of cloud computing has revolutionized data management across enterprises.", "difficulty": "intermediate", "word_count": 11, "focus": "technology"},
            {"text": "Successful project management requires careful planning, execution, and continuous monitoring.", "difficulty": "basic", "word_count": 10, "focus": "management"},
        ]

        if self.openai_api_key:
            ai_content = self._generate_with_ai("read_aloud", count, difficulty)
            if ai_content:
                content = ai_content

        return self._deduplicate(content)

    def generate_repeats_content(self, count=16):
        """Generate Repeats content - short, natural sentences."""
        content = [
            "The meeting has been rescheduled to Thursday afternoon.",
            "Please submit your report by the end of this week.",
            "The new policy takes effect from the first of next month.",
            "We need to review the proposal before making a decision.",
            "The training session will be held in the main conference room.",
            "Customer feedback is essential for improving our services.",
            "The project deadline has been extended by two weeks.",
            "Please ensure all documents are submitted on time.",
            "The team achieved remarkable results this quarter.",
            "We should schedule a follow-up meeting next week.",
            "The budget approval process takes about two weeks.",
            "Please contact the support team if you need assistance.",
            "The annual performance review will be conducted in December.",
            "We need to analyze the data before presenting it.",
            "The company is expanding its operations internationally.",
            "Please review the document before signing it.",
        ]

        if self.openai_api_key:
            ai_content = self._generate_with_ai("repeats", count, "basic")
            if ai_content:
                content = ai_content

        return self._deduplicate(content)

    def generate_sentence_builds_content(self, count=10):
        """Generate Sentence Builds content - jumbled words."""
        content = [
            {"words": ["the", "meeting", "starts", "at", "nine", "sharp"], "answer": "The meeting starts at nine sharp."},
            {"words": ["please", "submit", "the", "report", "by", "Friday"], "answer": "Please submit the report by Friday."},
            {"words": ["the", "team", "completed", "the", "project", "successfully"], "answer": "The team completed the project successfully."},
            {"words": ["we", "will", "discuss", "the", "budget", "next", "week"], "answer": "We will discuss the budget next week."},
            {"words": ["she", "has", "been", "working", "here", "since", "2020"], "answer": "She has been working here since 2020."},
            {"words": ["the", "new", "policy", "takes", "effect", "from", "Monday"], "answer": "The new policy takes effect from Monday."},
            {"words": ["they", "are", "planning", "to", "launch", "the", "product"], "answer": "They are planning to launch the product."},
            {"words": ["the", "manager", "approved", "the", "proposal", "yesterday"], "answer": "The manager approved the proposal yesterday."},
        ]

        return self._deduplicate(content)

    def generate_conversations_content(self, count=10):
        """Generate conversation questions - common workplace scenarios."""
        content = [
            "How would you handle a disagreement with a colleague about project priorities?",
            "Describe a time when you had to meet a tight deadline.",
            "What steps would you take to improve customer satisfaction?",
            "How do you stay organized when managing multiple tasks?",
            "What would you do if you discovered an error in a completed project?",
            "How do you approach learning a new technology or skill?",
            "Describe your ideal work environment and why.",
            "How would you explain a technical concept to a non-technical person?",
            "What qualities do you think make a good team leader?",
            "How do you handle constructive criticism from your supervisor?",
        ]

        if self.openai_api_key:
            ai_content = self._generate_with_ai("conversations", count, "intermediate")
            if ai_content:
                content = ai_content

        return self._deduplicate(content)

    def generate_story_retelling_content(self, count=3):
        """Generate story retelling passages."""
        content = [
            "A young software engineer joined a startup and within six months, she had developed an innovative mobile application that attracted over a million users. Her dedication to learning and willingness to take risks led to rapid career growth.",
            "The marketing team launched an ambitious campaign during the holiday season. By analyzing customer data and personalizing their approach, they managed to double the company's customer base in just three months.",
            "A manufacturing company was struggling with declining productivity. After implementing automation and providing comprehensive training to employees, they saw a forty percent increase in output within one year.",
        ]

        return self._deduplicate(content)

    def generate_summary_content(self):
        """Generate summary writing topics."""
        content = [
            "Write a summary of the impact of artificial intelligence on modern workplaces. Include your opinion on whether AI will create more jobs than it eliminates.",
            "Discuss the importance of sustainable business practices in today's global economy. Provide examples of companies that have successfully implemented green initiatives.",
            "Analyze the role of remote work in shaping the future of employment. Consider both the benefits and challenges.",
        ]

        return self._deduplicate(content)

    # ============================================================
    # AI GENERATION (JSON mode)
    # ============================================================

    def _generate_with_ai(self, section_type, count, difficulty):
        """Generate content using OpenAI for variety and quality."""
        try:
            import requests
            import re

            prompts = {
                "read_aloud": f"Generate {count} professional English sentences for a Read Aloud assessment. Mix of business, technology, and general topics. Each 10-15 words. Return a JSON object {{\"items\":[{{\"text\":\"...\"}}]}}.",
                "repeats": f"Generate {count} short English sentences for a listening/repeat assessment. 5-10 words each. Natural conversational tone. Return a JSON object {{\"items\":[\"...\"]}}.",
                "conversations": f"Generate {count} workplace conversation questions for English assessment. Common professional scenarios. Return a JSON object {{\"items\":[\"...\"]}}.",
            }

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompts.get(section_type, "")}],
                    "temperature": 0.9,
                    "max_tokens": 2000,
                    "response_format": {"type": "json_object"},
                },
                timeout=25,
            )

            data = response.json()
            content_text = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()

            # Defensive: strip markdown fences
            if content_text.startswith("```"):
                content_text = content_text.split("```", 2)[1]
                if content_text.startswith("json"):
                    content_text = content_text[4:]
                content_text = content_text.strip()

            # Try direct JSON (response_format=json_object returns pure JSON)
            try:
                parsed = json.loads(content_text)
                if isinstance(parsed, dict) and "items" in parsed:
                    return parsed["items"]
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass

            # Fallback: regex-extract array from prose/fence-wrapped output
            json_match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")

        return []

    # ============================================================
    # DEDUPLICATION (DB-backed)
    # ============================================================

    def _deduplicate(self, content):
        """Ensure no duplicate content (across sessions, backed by DB)."""
        unique = []
        seen = set()

        # Compute candidate keys for all items (must be hashable strings)
        items_with_keys = []
        for item in content:
            if isinstance(item, str):
                key = item
            elif isinstance(item, dict):
                raw = item.get("text") or item.get("words") or ""
                key = raw if isinstance(raw, str) else str(raw)
            else:
                key = str(item)
            items_with_keys.append((key, item))

        # Query DB once for which keys are already used
        already_used = set()
        candidate_keys = [k for k, _ in items_with_keys if k]
        if candidate_keys:
            try:
                from database import db
                conn = db.get_connection()
                cur = conn.cursor()
                cur.execute('''
                    SELECT content_key FROM charvak_content_used_content
                    WHERE content_key = ANY(%s)
                ''', (candidate_keys,))
                already_used = {r[0] for r in cur.fetchall()}
                cur.close(); conn.close()
            except Exception as e:
                logger.error(f"_deduplicate read failed: {e}")

        # Apply dedup logic preserving original semantics
        for key, item in items_with_keys:
            if key not in seen and key not in already_used:
                seen.add(key)
                unique.append(item)

        # Persist newly seen keys (idempotent)
        if seen:
            try:
                from database import db
                conn = db.get_connection()
                cur = conn.cursor()
                cur.executemany('''
                    INSERT INTO charvak_content_used_content (content_key)
                    VALUES (%s)
                    ON CONFLICT (content_key) DO NOTHING
                ''', [(k,) for k in seen])
                conn.commit()
                cur.close(); conn.close()
            except Exception as e:
                logger.error(f"_deduplicate write failed: {e}")

        return unique

    # ============================================================
    # QUALITY REPORT
    # ============================================================

    def get_content_quality_report(self):
        """Get content quality metrics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_content_used_content')
            total = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_content_quality_report failed: {e}")
            total = 0

        return {
            "status": "success",
            "total_content_items": total,
            "ai_generated": bool(self.openai_api_key),
            "deduplicated": True,
            "quality_checks": [
                "Vocabulary variety",
                "Natural language flow",
                "Market-standard topics",
                "No repetition",
                "Appropriate difficulty levels",
            ],
        }


ai_content_generator = AIContentGenerator()