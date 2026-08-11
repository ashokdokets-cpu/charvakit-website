"""
Charvak AI Chatbot Engine
Website widget + backend for AI-powered customer support
"""
import os
import logging
from datetime import datetime
from typing import Dict, List
import secrets

logger = logging.getLogger("charvakit.chatbot")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class ChatbotEngine:
    """AI-powered chatbot for customer support."""
    
    def __init__(self):
        self.sessions = {}
        self.faqs = self._load_faqs()
        logger.info(f"✅ Chatbot Engine ready with {len(self.faqs)} FAQs")
    
    def _load_faqs(self) -> List[Dict]:
        """Load FAQ knowledge base."""
        return [
            {"q": "What services does Charvak offer?", "a": "We offer IT staffing, web design, staff augmentation, AI-powered tools, and North America bench staffing with visa handling for 17 visa types."},
            {"q": "How does the NA module work?", "a": "Our North America module handles work authorization verification for 17 visa types (H-1B, OPT, CPT, L-1, etc.), connects you with US employers, and manages the entire hiring process."},
            {"q": "What is Dokets VouchAI?", "a": "Dokets VouchAI is our AI-powered escrow platform. It protects both clients and freelancers with just 1% transaction fee. Funds are held securely until work is delivered and approved."},
            {"q": "How much do your services cost?", "a": "Pricing varies by service. AI tools start at ₹99, background checks from ₹499, NA module subscriptions from $50/month. Visit /pricing for full details."},
            {"q": "How do I get a verified badge?", "a": "Take our Skill-Twin assessment at /skill-twin. Once you pass, you'll receive a verified badge you can share on LinkedIn and your resume."},
            {"q": "What payment methods do you accept?", "a": "We accept Razorpay (India), PayPal (Global), and UPI. All payments are secured through Dokets VouchAI escrow."},
            {"q": "How do I contact support?", "a": "Email hr@charvakit.com, call +91 799 7871 701, or WhatsApp us. Our team responds within 24 hours."},
            {"q": "Do you offer refunds?", "a": "Yes, we have a refund policy. Visit /refund for details. Escrow payments are protected — funds are only released when you approve the work."},
            {"q": "What is the Career Engine?", "a": "Our 7-step career pipeline: DoketsRB assessment → Job Board → Interview Prep → Micro-Internship → Training → Background Verification → Reverse Staffing placement."},
            {"q": "Which countries do you operate in?", "a": "We operate in 50+ countries with support for 34 languages and 13 currencies. Major markets: India, USA, Canada, UK, UAE, Singapore, Australia."},
        ]
    
    def start_session(self) -> Dict:
        """Start a new chat session."""
        session_id = f"CHAT-{secrets.token_hex(4)}"
        self.sessions[session_id] = {
            "session_id": session_id,
            "messages": [{"role": "bot", "text": "👋 Hi! I'm Charvak's AI assistant. How can I help you today?", "timestamp": datetime.now().isoformat()}],
            "created_at": datetime.now().isoformat()
        }
        return {"status": "success", "session": self.sessions[session_id]}
    
    def send_message(self, session_id: str, message: str) -> Dict:
        """Process a user message and return AI response."""
        if session_id not in self.sessions:
            return {"status": "error", "message": "Session not found. Start a new chat."}
        
        # Add user message
        self.sessions[session_id]["messages"].append({
            "role": "user",
            "text": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Try FAQ match first
        response = self._match_faq(message)
        
        # Fallback to AI if OpenAI is configured
        if not response and OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_key_here":
            response = self._ai_response(message, self.sessions[session_id]["messages"])
        
        # Ultimate fallback
        if not response:
            response = "Thanks for your question! For personalized help, email hr@charvakit.com or call +91 799 7871 701. Our team will get back to you within 24 hours."
        
        # Add bot response
        self.sessions[session_id]["messages"].append({
            "role": "bot",
            "text": response,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "response": response,
            "session": self.sessions[session_id]
        }
    
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
                for faq in self.faqs:
                    if key in faq["q"].lower().replace(" ", ""):
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
                    {"role": "user", "content": message}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"AI chatbot error: {e}")
            return None
    
    def get_faqs(self) -> Dict:
        """Get all FAQs."""
        return {"status": "success", "faqs": self.faqs, "count": len(self.faqs)}


chatbot_engine = ChatbotEngine()