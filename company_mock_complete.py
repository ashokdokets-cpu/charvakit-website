"""
Charvak Complete Company Mock Drive
Questions per section, answer tracking, AI results
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.company_mock_complete")

class CompanyMockDrive:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.mock_sessions = {}
        self.mock_results = {}
        logger.info("Company Mock Drive ready")
    
    def get_company_sections(self, company_id):
        """Get complete section details with questions."""
        companies = {
            "tcs": {
                "name": "TCS",
                "pattern": "NQT",
                "sections": [
                    {
                        "name": "Foundation",
                        "questions_count": 25,
                        "time": "75 min",
                        "topics": ["Aptitude", "Logical", "Verbal"],
                        "questions": self._generate_section_questions("Foundation", ["Aptitude", "Logical", "Verbal"], 10)
                    },
                    {
                        "name": "Advanced",
                        "questions_count": 10,
                        "time": "25 min",
                        "topics": ["Advanced Quant", "Advanced Logic"],
                        "questions": self._generate_section_questions("Advanced", ["Advanced Quant", "Logic"], 5)
                    },
                    {
                        "name": "Coding",
                        "questions_count": 2,
                        "time": "55 min",
                        "topics": ["DSA", "Problem Solving"],
                        "questions": self._generate_section_questions("Coding", ["DSA", "Algorithms"], 2)
                    }
                ]
            },
            "infosys": {
                "name": "Infosys",
                "pattern": "InfyTQ",
                "sections": [
                    {"name": "Aptitude", "questions_count": 20, "time": "60 min", "topics": ["Quant", "Logical"], "questions": self._generate_section_questions("Aptitude", ["Quant", "Logical"], 5)},
                    {"name": "Technical", "questions_count": 15, "time": "30 min", "topics": ["DSA", "DBMS", "OOPs"], "questions": self._generate_section_questions("Technical", ["DSA", "DBMS"], 3)},
                    {"name": "Coding", "questions_count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"], "questions": self._generate_section_questions("Coding", ["DSA"], 2)}
                ]
            },
            "wipro": {
                "name": "Wipro",
                "pattern": "Elite NTH",
                "sections": [
                    {"name": "Aptitude", "questions_count": 20, "time": "48 min", "topics": ["Logical", "Quant"], "questions": self._generate_section_questions("Aptitude", ["Logical", "Quant"], 5)},
                    {"name": "Communication", "questions_count": 2, "time": "20 min", "topics": ["Essay", "Email"], "questions": self._generate_section_questions("Communication", ["Essay"], 2)},
                    {"name": "Coding", "questions_count": 2, "time": "45 min", "topics": ["Basic", "Intermediate"], "questions": self._generate_section_questions("Coding", ["Basic"], 2)}
                ]
            },
            "accenture": {
                "name": "Accenture",
                "pattern": "ASE",
                "sections": [
                    {"name": "Cognitive", "questions_count": 25, "time": "60 min", "topics": ["Aptitude", "Logical"], "questions": self._generate_section_questions("Cognitive", ["Aptitude"], 5)},
                    {"name": "Technical", "questions_count": 15, "time": "30 min", "topics": ["CS Fundamentals"], "questions": self._generate_section_questions("Technical", ["CS"], 3)},
                    {"name": "Communication", "questions_count": 10, "time": "20 min", "topics": ["Grammar"], "questions": self._generate_section_questions("Communication", ["Grammar"], 3)}
                ]
            }
        }
        
        return companies.get(company_id, companies.get("tcs"))
    
    def _generate_section_questions(self, section_name, topics, count):
        """Generate questions for a section."""
        questions = []
        for i in range(count):
            topic = topics[i % len(topics)] if topics else "General"
            questions.append({
                "id": i + 1,
                "question": f"{section_name} - {topic} Question {i+1}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": i % 4,
                "topic": topic
            })
        return questions
    
    def start_mock(self, email, company_id):
        """Start complete mock drive."""
        session_id = f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        company = self.get_company_sections(company_id)
        
        self.mock_sessions[session_id] = {
            "session_id": session_id,
            "email": email,
            "company": company["name"],
            "pattern": company["pattern"],
            "sections": company["sections"],
            "answers": [],
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        return {"status": "success", "session": self.mock_sessions[session_id]}
    
    def submit_answer(self, session_id, section_name, question_id, answer):
        """Submit answer for a question."""
        if session_id not in self.mock_sessions:
            return {"status": "error", "message": "Session not found"}
        
        self.mock_sessions[session_id]["answers"].append({
            "section": section_name,
            "question_id": question_id,
            "answer": answer,
            "submitted_at": datetime.now().isoformat()
        })
        
        return {"status": "success", "total_answers": len(self.mock_sessions[session_id]["answers"])}
    
    def complete_mock(self, session_id):
        """Complete mock drive and generate results."""
        if session_id not in self.mock_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.mock_sessions[session_id]
        session["status"] = "completed"
        
        total_questions = sum(s["questions_count"] for s in session["sections"])
        total_answered = len(session["answers"])
        
        # Calculate score
        score = (total_answered / total_questions * 100) if total_questions > 0 else 0
        
        results = {
            "session_id": session_id,
            "email": session["email"],
            "company": session["company"],
            "pattern": session["pattern"],
            "total_questions": total_questions,
            "answered": total_answered,
            "score": round(score, 1),
            "pass": score >= 65,
            "sections_completed": len(session["sections"]),
            "completed_at": datetime.now().isoformat()
        }
        
        self.mock_results[session_id] = results
        return {"status": "success", "results": results}
    
    def get_results(self, session_id):
        """Get mock drive results."""
        if session_id not in self.mock_results:
            return {"status": "error", "message": "Results not found"}
        return {"status": "success", "results": self.mock_results[session_id]}

company_mock = CompanyMockDrive()
