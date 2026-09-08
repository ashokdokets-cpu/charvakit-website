"""
Charvak Universal Company System
Any company, user content requests, admin communication
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.universal_company")

class UniversalCompanySystem:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.custom_companies = {}
        self.content_requests = []
        self.admin_messages = []
        logger.info("Universal Company System ready")
    
    def add_custom_company(self, company_name, pattern_name, sections, cutoff=65, difficulty="Moderate"):
        """Add any company to the system."""
        company_id = company_name.lower().replace(" ", "_")
        
        self.custom_companies[company_id] = {
            "id": company_id,
            "name": company_name,
            "pattern": pattern_name,
            "sections": sections,
            "cutoff": cutoff,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        return {"status": "success", "company": self.custom_companies[company_id]}
    
    def request_content(self, email, company_name, content_type, topic, description):
        """User requests content that's missing."""
        request_id = f"REQ-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        request = {
            "request_id": request_id,
            "email": email,
            "company_name": company_name,
            "content_type": content_type,
            "topic": topic,
            "description": description,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        self.content_requests.append(request)
        
        # Notify admin
        self._notify_admin(request)
        
        return {
            "status": "success",
            "request_id": request_id,
            "message": "Content request submitted. Our team will add it within 24 hours."
        }
    
    def _notify_admin(self, request):
        """Notify admin about content request."""
        from email_engine import email_engine
        
        subject = f"New Content Request: {request['company_name']} - {request['topic']}"
        body = f"""
        New content request received:
        - Request ID: {request['request_id']}
        - User: {request['email']}
        - Company: {request['company_name']}
        - Content Type: {request['content_type']}
        - Topic: {request['topic']}
        - Description: {request['description']}
        """
        
        email_engine.send_email("hr@charvakit.com", subject, body)
    
    def contact_admin(self, email, subject, message):
        """User contacts admin directly."""
        message_id = f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        admin_message = {
            "message_id": message_id,
            "email": email,
            "subject": subject,
            "message": message,
            "status": "unread",
            "created_at": datetime.now().isoformat()
        }
        
        self.admin_messages.append(admin_message)
        
        # Send email to admin
        from email_engine import email_engine
        email_engine.send_email(
            "hr@charvakit.com",
            f"User Message: {subject}",
            f"From: {email}\n\n{message}"
        )
        
        return {"status": "success", "message_id": message_id, "message": "Message sent to admin."}
    
    def get_content_requests(self, status="pending"):
        """Get content requests (admin only)."""
        requests = [r for r in self.content_requests if r["status"] == status]
        return {"status": "success", "total": len(requests), "requests": requests}
    
    def update_content_request(self, request_id, status, admin_note=None):
        """Admin updates content request status."""
        for request in self.content_requests:
            if request["request_id"] == request_id:
                request["status"] = status
                if admin_note:
                    request["admin_note"] = admin_note
                request["updated_at"] = datetime.now().isoformat()
                return {"status": "success", "request": request}
        
        return {"status": "error", "message": "Request not found"}
    
    def get_custom_companies(self):
        """Get all custom companies added."""
        companies = list(self.custom_companies.values())
        return {"status": "success", "total": len(companies), "companies": companies}
    
    def generate_content_for_any_company(self, company_name, topic, count=5):
        """Generate content for any company using AI."""
        if self.openai_api_key:
            try:
                import requests
                
                prompt = f"Generate {count} practice questions for {company_name} placement test on {topic}. Return JSON array with question, options (4), correct_index, explanation."
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.9
                    }
                )
                
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                import re
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    return {"status": "success", "questions": json.loads(match.group()), "ai_generated": True}
            except Exception as e:
                logger.error(f"AI generation failed: {e}")
        
        # Fallback
        return {
            "status": "success",
            "questions": [
                {"id": i+1, "question": f"Practice question {i+1} on {topic} for {company_name}", "options": ["A", "B", "C", "D"], "correct": 0}
                for i in range(count)
            ],
            "ai_generated": False
        }
    
    def get_all_companies_combined(self):
        """Get all companies (standard + custom)."""
        from enhanced_assessment_engine import enhanced_assessment_engine
        standard = enhanced_assessment_engine.get_supported_companies()
        
        all_companies = standard["companies"] if "companies" in standard else []
        
        for company in self.custom_companies.values():
            all_companies.append({
                "id": company["id"],
                "name": company["name"],
                "patterns": [company["pattern"]],
                "custom": True
            })
        
        return {"status": "success", "total": len(all_companies), "companies": all_companies}

universal_company = UniversalCompanySystem()
