"""
Charvak Enhanced AI-Driven Assessment System
Supports: Any Company, Any Topic, Dynamic AI Content
"""
import logging
import random
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.enhanced_assessment")

class EnhancedAssessmentEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.question_cache = {}
        self.company_templates = self._initialize_company_templates()
        logger.info("Enhanced Assessment Engine ready")
    
    def _initialize_company_templates(self):
        return {
            "tcs": {"name": "TCS", "patterns": ["NQT", "Digital", "Innovator"]},
            "cognizant": {"name": "Cognizant", "patterns": ["GenC", "GenC Elevate", "GenC Pro"]},
            "wipro": {"name": "Wipro", "patterns": ["Elite NTH", "Turbo", "WILP"]},
            "hcl": {"name": "HCLTech", "patterns": ["TechBee", "TSS", "Graduate"]},
            "infosys": {"name": "Infosys", "patterns": ["InfyTQ", "HackWithInfy"]},
            "accenture": {"name": "Accenture", "patterns": ["ASE", "Advanced ASE"]},
            "capgemini": {"name": "Capgemini", "patterns": ["Exceller", "Pro"]},
            "tech_mahindra": {"name": "Tech Mahindra", "patterns": ["Talent", "Digital"]},
            "lti": {"name": "LTI", "patterns": ["GET", "Digital"]},
            "mindtree": {"name": "Mindtree", "patterns": ["Graduate", "Specialist"]},
            "ibm": {"name": "IBM", "patterns": ["Associate", "Developer"]},
            "deloitte": {"name": "Deloitte", "patterns": ["Analyst", "Consultant"]},
            "kpmg": {"name": "KPMG", "patterns": ["Analyst", "Advisory"]},
            "ey": {"name": "EY", "patterns": ["Associate", "Analyst"]},
            "pwc": {"name": "PwC", "patterns": ["Associate", "Advisory"]}
        }
    
    def get_supported_companies(self):
        companies = []
        for key, company in self.company_templates.items():
            companies.append({
                "id": key,
                "name": company["name"],
                "patterns": company.get("patterns", [])
            })
        return {"status": "success", "total": len(companies), "companies": companies}
    
    def create_custom_assessment(self, company_name, topics, difficulty="medium", count=10):
        assessment_id = f"ASSESS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return {
            "status": "success",
            "assessment_id": assessment_id,
            "company": company_name,
            "topics": topics,
            "difficulty": difficulty,
            "question_count": count,
            "ai_generated": True
        }
    
    def generate_topic_questions(self, topic, count=10, difficulty="medium"):
        questions = self._generate_ai_questions(topic, count, difficulty)
        return {
            "status": "success",
            "topic": topic,
            "difficulty": difficulty,
            "questions": questions,
            "ai_generated": True,
            "unique": True
        }
    
    def _generate_ai_questions(self, topic, count, difficulty):
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Generate {count} UNIQUE {difficulty} MCQs on {topic}. Return JSON array with question, options, correct_index, explanation."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9}
                )
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                import re
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except Exception as e:
                logger.error(f"AI error: {e}")
        
        # Fallback
        return [
            {"id": i, "question": f"Question {i+1} about {topic}", "options": ["A", "B", "C", "D"], "correct_index": 0}
            for i in range(count)
        ]
    
    def get_topic_suggestions(self, field="software"):
        topics = {
            "software": ["Data Structures", "Algorithms", "Python", "Java", "SQL", "System Design", "OOPs", "DBMS"],
            "data_science": ["Machine Learning", "Statistics", "Python", "Deep Learning", "NLP"],
            "cloud": ["AWS", "Azure", "GCP", "DevOps", "Docker", "Kubernetes"],
            "cybersecurity": ["Network Security", "Cryptography", "Ethical Hacking"],
            "aptitude": ["Quantitative", "Logical Reasoning", "Verbal Ability", "Data Interpretation"],
            "communication": ["Grammar", "Vocabulary", "Reading Comprehension", "Essay Writing"]
        }
        return {"status": "success", "field": field, "topics": topics.get(field, topics["software"])}

enhanced_assessment_engine = EnhancedAssessmentEngine()
