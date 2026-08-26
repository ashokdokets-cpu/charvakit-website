"""
Charvak Final Year Project Assistant — AI-Powered
Personalized project support using GPT-4o-mini
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, List
import secrets

logger = logging.getLogger("charvakit.fyp")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")


class FinalYearProjectEngine:
    """AI-powered final year project support."""
    
    PLANS = {
        "free": {"name": "Free", "price": 0, "features": ["Topic suggestions (5)", "Basic outline"]},
        "pro": {"name": "Pro", "price": 299, "features": ["AI personalized topics (20+)", "AI proposal generation", "Tech stack suggestion"]},
        "premium": {"name": "Premium", "price": 999, "features": ["Everything in Pro", "Full AI documentation", "Viva preparation", "Code starter templates", "Priority support"]},
    }
    
    def __init__(self):
        self.projects = []
        self.subscriptions = []
        self.revenue = 0
        logger.info(f"FYP Engine ready | AI: {'Enabled' if OPENAI_API_KEY else 'Fallback mode'}")
    
    # ============================================================
    # AI-POWERED TOPIC SUGGESTIONS
    # ============================================================
    
    def suggest_topics_ai(self, data: Dict) -> Dict:
        """
        AI-powered topic suggestions.
        data = {branch, domain, skills, interests, plan}
        """
        branch = data.get("branch", "Computer Science")
        domain = data.get("domain", "AI/ML")
        skills = data.get("skills", [])
        interests = data.get("interests", [])
        plan = data.get("plan", "free")
        
        # Try AI
        if OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                
                prompt = f"""Generate 10 unique final year project topics for a {branch} student.
                Domain: {domain}
                Skills: {', '.join(skills) if skills else 'General programming'}
                Interests: {', '.join(interests) if interests else 'Open to suggestions'}
                
                Return JSON: {{"topics": [{{"title": "...", "domain": "...", "difficulty": "...", "description": "..."}}]}}"""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.8
                )
                
                topics_data = json.loads(response.choices[0].message.content)
                return {"status": "success", "ai_generated": True, **topics_data}
            except Exception as e:
                logger.warning(f"AI failed, using fallback: {e}")
        
        # Fallback predefined
        return self._fallback_topics(branch, domain)
    
    def _fallback_topics(self, branch: str, domain: str) -> Dict:
        """Fallback predefined topics."""
        topics = [
            {"title": "Chatbot for College Enquiry", "domain": domain, "difficulty": "Intermediate", "description": "AI chatbot answering college queries"},
            {"title": "Disease Prediction using ML", "domain": domain, "difficulty": "Advanced", "description": "Predict diseases from symptoms"},
            {"title": "Face Recognition Attendance", "domain": domain, "difficulty": "Intermediate", "description": "Automated attendance using face recognition"},
            {"title": "Sentiment Analysis Platform", "domain": domain, "difficulty": "Beginner", "description": "Analyze sentiment from reviews"},
            {"title": "Stock Price Predictor", "domain": domain, "difficulty": "Advanced", "description": "LSTM-based stock prediction"},
        ]
        return {"status": "success", "ai_generated": False, "topics": topics}
    
    # ============================================================
    # AI-POWERED PROPOSAL GENERATION
    # ============================================================
    
    def generate_proposal_ai(self, data: Dict) -> Dict:
        """
        AI-powered proposal generation.
        data = {topic, branch, domain, student_name, college}
        """
        topic = data.get("topic", "Project")
        student = data.get("student_name", "Student")
        college = data.get("college", "College")
        
        if OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                
                prompt = f"""Generate a professional final year project proposal for:
                Student: {student}
                College: {college}
                Topic: {topic}
                
                Return JSON: {{"title": "...", "abstract": "...", "objectives": [...], "scope": "...", "tech_stack": [...], "modules": [...], "timeline": [...]}}"""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.7
                )
                
                proposal = json.loads(response.choices[0].message.content)
                return {"status": "success", "ai_generated": True, "proposal": proposal}
            except Exception as e:
                logger.warning(f"AI proposal failed: {e}")
        
        return {"status": "success", "ai_generated": False, "proposal": self._fallback_proposal(topic)}
    
    def _fallback_proposal(self, topic: str) -> Dict:
        return {
            "title": topic,
            "abstract": f"This project focuses on {topic}.",
            "objectives": [f"Study {topic}", f"Design {topic}", f"Implement {topic}"],
            "scope": f"End-to-end development of {topic}",
            "tech_stack": ["Python", "React", "PostgreSQL"],
            "modules": ["Authentication", "Core Module", "Admin", "Reports"],
            "timeline": ["Week 1-2: Research", "Week 3-8: Development", "Week 9-12: Testing"]
        }
    
    # ============================================================
    # AI-POWERED DOCUMENTATION
    # ============================================================
    
    def generate_documentation_ai(self, data: Dict) -> Dict:
        """
        AI-powered documentation.
        data = {topic, proposal}
        """
        topic = data.get("topic", "Project")
        
        if OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                
                prompt = f"""Generate complete documentation outline for final year project: {topic}
                Return JSON: {{"chapters": [{{"chapter": 1, "title": "...", "content_outline": "..."}}], "diagrams": [...], "documents": [...]}}"""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=800,
                    temperature=0.5
                )
                
                docs = json.loads(response.choices[0].message.content)
                return {"status": "success", "ai_generated": True, "documentation": docs}
            except Exception as e:
                logger.warning(f"AI docs failed: {e}")
        
        return {"status": "success", "ai_generated": False, "documentation": self._fallback_docs(topic)}
    
    def _fallback_docs(self, topic: str) -> Dict:
        return {
            "chapters": [
                {"chapter": 1, "title": "Introduction", "content_outline": f"Background of {topic}"},
                {"chapter": 2, "title": "Literature Review", "content_outline": "Existing systems"},
                {"chapter": 3, "title": "System Design", "content_outline": "Architecture"},
                {"chapter": 4, "title": "Implementation", "content_outline": "Code structure"},
                {"chapter": 5, "title": "Testing", "content_outline": "Test cases"},
                {"chapter": 6, "title": "Conclusion", "content_outline": "Summary"}
            ],
            "diagrams": ["Use Case", "ER Diagram", "Class Diagram"],
            "documents": ["SRS", "SDD", "User Manual"]
        }
    
    # ============================================================
    # AI-POWERED VIVA PREP
    # ============================================================
    
    def generate_viva_ai(self, data: Dict) -> Dict:
        """
        AI-powered viva questions specific to project.
        """
        topic = data.get("topic", "Project")
        
        if OPENAI_API_KEY:
            try:
                import openai
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                
                prompt = f"""Generate 15 viva questions specific to final year project: {topic}
                Include technical, architectural, and general questions.
                Return JSON: {{"questions": [...], "tips": [...]}}"""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=600,
                    temperature=0.6
                )
                
                viva = json.loads(response.choices[0].message.content)
                return {"status": "success", "ai_generated": True, **viva}
            except Exception as e:
                logger.warning(f"AI viva failed: {e}")
        
        return {"status": "success", "ai_generated": False, "questions": self._fallback_questions(topic)}
    
    def _fallback_questions(self, topic: str) -> List[str]:
        return [
            f"Why did you choose {topic}?",
            "What technologies did you use?",
            "What challenges did you face?",
            "How does your project differ from existing solutions?",
            "What future enhancements would you suggest?"
        ]
    
    # ============================================================
    # MONETIZATION
    # ============================================================
    
    def subscribe(self, data: Dict) -> Dict:
        """
        Subscribe to FYP plan.
        data = {email, plan}
        """
        plan_key = data.get("plan", "free")
        plan = self.PLANS.get(plan_key, self.PLANS["free"])
        
        subscription = {
            "subscription_id": f"FYP-SUB-{secrets.token_hex(4).upper()}",
            "email": data.get("email"),
            "plan": plan_key,
            "price": plan["price"],
            "subscribed_at": datetime.now().isoformat()
        }
        
        self.subscriptions.append(subscription)
        self.revenue += plan["price"]
        
        return {
            "status": "success",
            "plan": plan["name"],
            "price": plan["price"],
            "features": plan["features"],
            "message": f"Subscribed to {plan['name']}!"
        }
    
    def get_plans(self) -> Dict:
        return {"status": "success", "plans": self.PLANS}
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_projects": len(self.projects),
                "total_subscriptions": len(self.subscriptions),
                "total_revenue": self.revenue,
                "ai_enabled": bool(OPENAI_API_KEY)
            }
        }


final_year_project_engine = FinalYearProjectEngine()