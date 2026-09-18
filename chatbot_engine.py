"""
Charvak AI Chatbot Engine
Website widget + backend for AI-powered customer support
(DB-backed - Session H/3)
"""
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.chatbot")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class ChatbotEngine:
    """AI-powered chatbot for customer support (DB-backed)."""

    def __init__(self):
        self.faqs = self._load_faqs()
        self._ensure_tables()
        logger.info("Chatbot Engine ready (DB-backed) with %d FAQs", len(self.faqs))

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_chatbot_sessions (
                    session_id   TEXT PRIMARY KEY,
                    data         JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_chatbot_created ON charvak_chatbot_sessions(created_at)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_chatbot_updated ON charvak_chatbot_sessions(updated_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"chatbot tables init failed: {e}")

    def _load_faqs(self) -> List[Dict]:
        """Load FAQ knowledge base (static)."""
        return [
            {"q": "What services does Charvak offer?", "a": "We offer IT staffing, web design, staff augmentation, AI-powered tools, and North America bench staffing with visa handling for 17 visa types."},
            {"q": "How does the NA module work?", "a": "Our North America module handles work authorization verification for 17 visa types (H-1B, OPT, CPT, L-1, etc.), connects you with US employers, and manages the entire hiring process."},
            {"q": "What is Dokets VouchAI?", "a": "Dokets VouchAI is our AI-powered escrow platform. It protects both clients and freelancers with just 1% transaction fee. Funds are held securely until work is delivered and approved."},
            {"q": "How much do your services cost?", "a": "Pricing varies by service. AI tools start at Rs.99, background checks from Rs.499, NA module subscriptions from $50/month. Visit /pricing for full details."},
            {"q": "How do I get a verified badge?", "a": "Take our Skill-Twin assessment at /skill-twin. Once you pass, you'll receive a verified badge you can share on LinkedIn and your resume."},
            {"q": "What payment methods do you accept?", "a": "We accept Razorpay (India), PayPal (Global), and UPI. All payments are secured through Dokets VouchAI escrow."},
            {"q": "How do I contact support?", "a": "Email hr@charvakit.com, call +91 799 7871 701, or WhatsApp us. Our team responds within 24 hours."},
            {"q": "Do you offer refunds?", "a": "Yes, we have a refund policy. Visit /refund for details. Escrow payments are protected - funds are only released when you approve the work."},
            {"q": "What is the Career Engine?", "a": "Our 7-step career pipeline: DoketsRB assessment -> Job Board -> Interview Prep -> Micro-Internship -> Training -> Background Verification -> Reverse Staffing placement."},
            {"q": "Which countries do you operate in?", "a": "We operate in 50+ countries with support for 34 languages and 13 currencies. Major markets: India, USA, Canada, UK, UAE, Singapore, Australia."},
        ]

    # ============================================================
    # SESSION
    # ============================================================

    def start_session(self) -> Dict:
        """Start a new chat session."""
        session_id = f"CHAT-{secrets.token_hex(4)}"
        now_iso = datetime.now().isoformat()

        session = {
            "session_id": session_id,
            "messages": [
                {
                    "role": "bot",
                    "text": "\U0001F44B Hi! I'm Charvak's AI assistant. How can I help you today?",
                    "timestamp": now_iso,
                }
            ],
            "created_at": now_iso,
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_chatbot_sessions (session_id, data)
                VALUES (%s, %s::jsonb)
            ''', (session_id, json.dumps(session)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_session failed: {e}")
            return {"status": "error", "message": "Could not start session"}

        return {"status": "success", "session": session}

    def _get_session(self, session_id: str) -> Optional[Dict]:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT data FROM charvak_chatbot_sessions WHERE session_id = %s', (session_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_get_session failed: {e}")
            return None

        if not row:
            return None
        return row[0] if isinstance(row[0], dict) else json.loads(row[0] or "{}")

    def _save_session(self, session: Dict) -> bool:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_chatbot_sessions
                SET data = %s::jsonb, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            ''', (json.dumps(session), session["session_id"]))
            conn.commit()
            cur.close(); conn.close()
            return True
        except Exception as e:
            logger.error(f"_save_session failed: {e}")
            return False

    def send_message(self, session_id: str, message: str) -> Dict:
        """Process a user message and return AI response."""
        session = self._get_session(session_id)
        if not session:
            return {"status": "error", "message": "Session not found. Start a new chat."}

        # Add user message
        session["messages"].append({
            "role": "user",
            "text": message,
            "timestamp": datetime.now().isoformat(),
        })

        # Try FAQ match first
        response = self._match_faq(message)

        # Fallback to AI if OpenAI is configured
        if not response and OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_key_here":
            response = self._ai_response(message, session["messages"])

        # Ultimate fallback
        if not response:
            response = "Thanks for your question! For personalized help, email hr@charvakit.com or call +91 799 7871 701. Our team will get back to you within 24 hours."

        # Add bot response
        session["messages"].append({
            "role": "bot",
            "text": response,
            "timestamp": datetime.now().isoformat(),
        })

        # Persist
        self._save_session(session)

        return {
            "status": "success",
            "response": response,
            "session": session,
        }

    # ============================================================
    # MATCHING / AI
    # ============================================================

    def _match_faq(self, message: str) -> Optional[str]:
        """Simple keyword-based FAQ matching."""
        message_lower = message.lower()
        keywords_map = {
            "service": ["service", "offer", "provide", "what do you"],
            "na module": ["na ", "north america", "us ", "usa", "visa", "h-1b", "opt"],
            "escrow": ["escrow", "vouchai", "payment protect", "secure"],
            "pricing": ["price", "cost", "pricing", "how much", "fee", "charge"],
            "badge": ["badge", "verified", "skill-twin", "certification"],
            "payment": ["payment", "pay", "razorpay", "paypal", "upi"],
            "contact": ["contact", "email", "phone", "call", "reach"],
            "refund": ["refund", "cancel", "money back"],
            "career": ["career", "job", "placement", "hire"],
            "countries": ["country", "countries", "location", "where", "global"],
        }

        for key, keywords in keywords_map.items():
            if any(kw in message_lower for kw in keywords):
                normalized_key = key.replace(" ", "")
                for faq in self.faqs:
                    if normalized_key in faq["q"].lower().replace(" ", ""):
                        return faq["a"]

        return None

    def _ai_response(self, message: str, history: List) -> Optional[str]:
        """Fallback to OpenAI for complex questions."""
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are Charvak's AI assistant. Keep responses under 3 sentences. Be helpful and friendly. If you don't know, suggest contacting hr@charvakit.com."},
                    {"role": "user", "content": message},
                ],
                max_tokens=150,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI chatbot error: {e}")
            return None

    # ============================================================
    # FAQS
    # ============================================================

    def get_faqs(self) -> Dict:
        """Get all FAQs."""
        return {"status": "success", "faqs": self.faqs, "count": len(self.faqs)}


chatbot_engine = ChatbotEngine()