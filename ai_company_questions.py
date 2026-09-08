"""
Charvak AI Company Question Generator
AI generates unique questions for every topic across all companies
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.ai_company_questions")

class AICompanyQuestionGenerator:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.question_cache = {}
        logger.info(f"AI Company Question Generator - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def generate_topic_questions(self, company_name, topic, count=10, difficulty="medium"):
        """Generate AI questions for any topic."""
        cache_key = f"{company_name}_{topic}_{count}"
        
        # Check cache
        if cache_key in self.question_cache:
            return self.question_cache[cache_key]
        
        if self.openai_api_key:
            questions = self._call_openai(company_name, topic, count, difficulty)
            if questions:
                self.question_cache[cache_key] = questions
                return questions
        
        # Fallback
        return self._get_fallback_questions(topic, count)
    
    def _call_openai(self, company_name, topic, count, difficulty):
        """Call OpenAI to generate questions."""
        try:
            import requests
            
            prompt = f"""Generate {count} {difficulty} difficulty multiple-choice questions for {company_name} placement test on {topic}.
            Requirements:
            - Each question must be relevant to {topic}
            - 4 options with one correct answer
            - Professional, market-standard quality
            - No repetition
            Return JSON array with fields: q (question), options (array of 4), correct (index 0-3)
            """
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.95,
                    "max_tokens": 3000
                },
                timeout=15
            )
            
            data = response.json()
            content_text = data["choices"][0]["message"]["content"]
            
            import re
            match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if match:
                questions = json.loads(match.group())
                # Format questions
                formatted = []
                for i, q in enumerate(questions):
                    formatted.append({
                        "id": i + 1,
                        "question": q.get("q", q.get("question", "")),
                        "options": q.get("options", ["A", "B", "C", "D"]),
                        "correct": q.get("correct", 0),
                        "topic": topic,
                        "ai_generated": True
                    })
                return formatted
        except Exception as e:
            logger.error(f"OpenAI failed for {topic}: {e}")
        
        return []
    
    def _get_fallback_questions(self, topic, count):
        """Fallback questions if AI unavailable."""
        bank = {
            "Aptitude": [
                {"q": "What is 25% of 400?", "options": ["80", "100", "120", "150"], "correct": 1},
                {"q": "Train travels 360 km in 6 hours. Speed?", "options": ["50", "55", "60", "65"], "correct": 2},
                {"q": "LCM of 12 and 18?", "options": ["24", "36", "48", "72"], "correct": 1},
                {"q": "5 workers do job in 10 days. 10 workers?", "options": ["3", "5", "7", "10"], "correct": 1}
            ],
            "Quant": [
                {"q": "20% of 500?", "options": ["80", "100", "120", "150"], "correct": 1},
                {"q": "Car covers 240 km in 4 hrs. 7 hrs?", "options": ["360", "420", "480", "520"], "correct": 1}
            ],
            "Logical": [
                {"q": "A > B, B > C. Then?", "options": ["A > C", "A < C", "A = C", "Cannot say"], "correct": 0},
                {"q": "Next: 1, 4, 9, 16, ?", "options": ["20", "25", "30", "36"], "correct": 1}
            ],
            "DSA": [
                {"q": "LIFO data structure?", "options": ["Queue", "Stack", "Array", "Linked List"], "correct": 1},
                {"q": "Binary search complexity?", "options": ["O(1)", "O(log n)", "O(n)", "O(n²)"], "correct": 1}
            ],
            "SQL": [
                {"q": "Retrieve data command?", "options": ["INSERT", "UPDATE", "SELECT", "DELETE"], "correct": 2},
                {"q": "Primary key?", "options": ["Unique ID", "Foreign key", "Index", "None"], "correct": 0}
            ]
        }
        
        questions = bank.get(topic, [])
        while len(questions) < count:
            questions.append({
                "q": f"{topic} practice question {len(questions) + 1}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": len(questions) % 4
            })
        
        formatted = []
        for i, q in enumerate(questions[:count]):
            formatted.append({
                "id": i + 1,
                "question": q["q"],
                "options": q["options"],
                "correct": q["correct"],
                "topic": topic,
                "ai_generated": False
            })
        return formatted
    
    def generate_company_mock_questions(self, company_id):
        """Generate all questions for a company mock drive."""
        companies = {
            "tcs": {
                "name": "TCS",
                "sections": [
                    {"name": "Foundation", "topics": ["Aptitude", "Logical", "Verbal"], "count": 25},
                    {"name": "Advanced", "topics": ["Advanced Quant", "Advanced Logic"], "count": 10},
                    {"name": "Coding", "topics": ["DSA", "Problem Solving"], "count": 2}
                ]
            },
            "cognizant": {
                "name": "Cognizant",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quantitative", "Analytical", "Verbal"], "count": 20},
                    {"name": "Communication", "topics": ["Speaking", "Grammar"], "count": 10},
                    {"name": "Programming", "topics": ["SQL", "Debugging"], "count": 5}
                ]
            },
            "wipro": {
                "name": "Wipro",
                "sections": [
                    {"name": "Aptitude", "topics": ["Logical", "Quant"], "count": 20},
                    {"name": "Communication", "topics": ["Essay", "Email"], "count": 2},
                    {"name": "Coding", "topics": ["Basic", "Intermediate"], "count": 2}
                ]
            },
            "infosys": {
                "name": "Infosys",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Logical"], "count": 20},
                    {"name": "Technical", "topics": ["DSA", "DBMS", "OOPs"], "count": 15},
                    {"name": "Coding", "topics": ["DSA", "Algorithms"], "count": 3}
                ]
            },
            "accenture": {
                "name": "Accenture",
                "sections": [
                    {"name": "Cognitive", "topics": ["Aptitude", "Logical"], "count": 25},
                    {"name": "Technical", "topics": ["CS Fundamentals"], "count": 15},
                    {"name": "Communication", "topics": ["Grammar"], "count": 10}
                ]
            },
            "capgemini": {
                "name": "Capgemini",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Logical"], "count": 20},
                    {"name": "Technical", "topics": ["DSA", "DBMS"], "count": 15},
                    {"name": "Coding", "topics": ["Basic"], "count": 2}
                ]
            },
            "ibm": {
                "name": "IBM",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Logical"], "count": 20},
                    {"name": "Technical", "topics": ["DSA", "OOPs"], "count": 10},
                    {"name": "Coding", "topics": ["Basic", "DSA"], "count": 2}
                ]
            },
            "hcl": {
                "name": "HCLTech",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Verbal"], "count": 20},
                    {"name": "Technical", "topics": ["CS Fundamentals"], "count": 15},
                    {"name": "Coding", "topics": ["Basic"], "count": 2}
                ]
            },
            "tech_mahindra": {
                "name": "Tech Mahindra",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Logical"], "count": 20},
                    {"name": "Technical", "topics": ["DSA"], "count": 10},
                    {"name": "Coding", "topics": ["Basic"], "count": 2}
                ]
            },
            "lti": {
                "name": "LTI",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Logical"], "count": 20},
                    {"name": "Technical", "topics": ["DSA"], "count": 10},
                    {"name": "Coding", "topics": ["Basic"], "count": 2}
                ]
            },
            "mindtree": {
                "name": "Mindtree",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Logical"], "count": 20},
                    {"name": "Technical", "topics": ["DSA"], "count": 10},
                    {"name": "Coding", "topics": ["Basic"], "count": 2}
                ]
            },
            "deloitte": {
                "name": "Deloitte",
                "sections": [
                    {"name": "Aptitude", "topics": ["Quant", "Logical", "Verbal"], "count": 25},
                    {"name": "Technical", "topics": ["CS Fundamentals"], "count": 10},
                    {"name": "Communication", "topics": ["Grammar"], "count": 5}
                ]
            }
        }
        
        company = companies.get(company_id, companies["tcs"])
        
        sections_with_questions = []
        for section in company["sections"]:
            topics = section["topics"]
            questions_per_topic = max(1, section["count"] // len(topics))
            
            section_questions = []
            for topic in topics:
                questions = self.generate_topic_questions(company["name"], topic, questions_per_topic)
                section_questions.extend(questions)
            
            sections_with_questions.append({
                "name": section["name"],
                "questions_count": section["count"],
                "topics": topics,
                "questions": section_questions[:section["count"]]
            })
        
        return {
            "status": "success",
            "company": company["name"],
            "sections": sections_with_questions,
            "ai_generated": self.openai_api_key is not None
        }

ai_company_questions = AICompanyQuestionGenerator()
