"""
Charvak Company Assessment System
Company-specific mock drives with AI question generation, monitoring, results
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.company_assessment")

class CompanyAssessmentSystem:
    def __init__(self):
        self.company_sessions = {}
        self.company_results = {}
        logger.info("Company Assessment System ready")
    
    def get_company_details(self, company_id):
        """Get company-specific assessment details."""
        companies = {
            "tcs": {
                "name": "TCS",
                "patterns": ["NQT", "Digital", "Innovator"],
                "sections": [
                    {"name": "Aptitude", "questions": 25, "time": "75 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Advanced", "questions": 10, "time": "25 min", "topics": ["Advanced Quant", "Advanced Logic"]},
                    {"name": "Coding", "questions": 2, "time": "55 min", "topics": ["DSA", "Problem Solving"]}
                ],
                "platform": "iON",
                "negative_marking": False,
                "cutoff": "70%"
            },
            "cognizant": {
                "name": "Cognizant",
                "patterns": ["GenC", "GenC Elevate", "GenC Pro"],
                "sections": [
                    {"name": "Aptitude", "questions": 20, "time": "60 min", "topics": ["Quantitative", "Analytical", "Verbal"]},
                    {"name": "Communication", "questions": 10, "time": "20 min", "topics": ["Speaking", "Grammar"]},
                    {"name": "Programming", "questions": 5, "time": "45 min", "topics": ["SQL", "Debugging"]}
                ],
                "platform": "Mettl",
                "negative_marking": False,
                "cutoff": "65%"
            },
            "wipro": {
                "name": "Wipro",
                "patterns": ["Elite NTH", "Turbo"],
                "sections": [
                    {"name": "Aptitude", "questions": 20, "time": "48 min", "topics": ["Logical", "Quant"]},
                    {"name": "Communication", "questions": 2, "time": "20 min", "topics": ["Essay", "Email"]},
                    {"name": "Coding", "questions": 2, "time": "45 min", "topics": ["Basic", "Intermediate"]}
                ],
                "platform": "AMCAT",
                "negative_marking": False,
                "cutoff": "65%"
            },
            "infosys": {
                "name": "Infosys",
                "patterns": ["InfyTQ", "HackWithInfy"],
                "sections": [
                    {"name": "Aptitude", "questions": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "questions": 15, "time": "30 min", "topics": ["DSA", "DBMS", "Networks"]},
                    {"name": "Coding", "questions": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                ],
                "platform": "InfyTQ",
                "negative_marking": False,
                "cutoff": "70%"
            },
            "accenture": {
                "name": "Accenture",
                "patterns": ["ASE", "Advanced ASE"],
                "sections": [
                    {"name": "Cognitive", "questions": 25, "time": "60 min", "topics": ["Aptitude", "Logical"]},
                    {"name": "Technical", "questions": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "questions": 10, "time": "20 min", "topics": ["Grammar", "Comprehension"]}
                ],
                "platform": "Custom",
                "negative_marking": False,
                "cutoff": "65%"
            },
            "capgemini": {
                "name": "Capgemini",
                "patterns": ["Exceller", "Pro"],
                "sections": [
                    {"name": "Aptitude", "questions": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "questions": 15, "time": "30 min", "topics": ["DSA", "DBMS"]},
                    {"name": "Coding", "questions": 2, "time": "45 min", "topics": ["Basic Coding"]}
                ],
                "platform": "Exceller",
                "negative_marking": False,
                "cutoff": "60%"
            },
            "ibm": {
                "name": "IBM",
                "patterns": ["Associate", "Developer"],
                "sections": [
                    {"name": "Aptitude", "questions": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "questions": 10, "time": "30 min", "topics": ["DSA", "OOPs"]},
                    {"name": "Coding", "questions": 2, "time": "45 min", "topics": ["Basic", "DSA"]}
                ],
                "platform": "Custom",
                "negative_marking": False,
                "cutoff": "65%"
            },
            "deloitte": {
                "name": "Deloitte",
                "patterns": ["Analyst", "Consultant"],
                "sections": [
                    {"name": "Aptitude", "questions": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "questions": 10, "time": "30 min", "topics": ["CS Basics"]},
                    {"name": "Communication", "questions": 5, "time": "15 min", "topics": ["Grammar", "Writing"]}
                ],
                "platform": "Custom",
                "negative_marking": False,
                "cutoff": "65%"
            },
            "hcl": {
                "name": "HCLTech",
                "patterns": ["TechBee", "TSS"],
                "sections": [
                    {"name": "Aptitude", "questions": 20, "time": "60 min", "topics": ["Quant", "English"]},
                    {"name": "Technical", "questions": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Coding", "questions": 2, "time": "30 min", "topics": ["Basic"]}
                ],
                "platform": "Custom",
                "negative_marking": False,
                "cutoff": "70%"
            }
        }
        
        return companies.get(company_id, {"error": "Company not found"})
    
    def start_company_mock(self, email, company_id, pattern=None):
        """Start a company-specific mock drive."""
        session_id = f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        company = self.get_company_details(company_id)
        
        self.company_sessions[session_id] = {
            "session_id": session_id,
            "email": email,
            "company_id": company_id,
            "company_name": company.get("name", company_id),
            "pattern": pattern or company.get("patterns", [""])[0],
            "sections": company.get("sections", []),
            "started_at": datetime.now().isoformat(),
            "answers": [],
            "status": "in_progress"
        }
        
        return {"status": "success", "session": self.company_sessions[session_id]}
    
    def generate_company_questions(self, company_id, section_name, count=5):
        """Generate AI questions for company-specific section."""
        company = self.get_company_details(company_id)
        
        # Find section
        section = next((s for s in company.get("sections", []) if s["name"] == section_name), None)
        
        if not section:
            return {"status": "error", "message": "Section not found"}
        
        # Generate questions based on section topics
        questions = self._generate_section_questions(section["topics"], count)
        
        return {
            "status": "success",
            "company": company["name"],
            "section": section_name,
            "questions": questions
        }
    
    def _generate_section_questions(self, topics, count):
        """Generate questions for topics."""
        questions = []
        for i in range(count):
            topic = topics[i % len(topics)] if topics else "General"
            questions.append({
                "id": i + 1,
                "topic": topic,
                "question": f"Question {i+1} on {topic}",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": 0,
                "difficulty": "medium"
            })
        return questions
    
    def submit_company_answer(self, session_id, question_id, answer):
        """Submit answer for company mock."""
        if session_id not in self.company_sessions:
            return {"status": "error", "message": "Session not found"}
        
        self.company_sessions[session_id]["answers"].append({
            "question_id": question_id,
            "answer": answer,
            "submitted_at": datetime.now().isoformat()
        })
        
        return {"status": "success", "total_answers": len(self.company_sessions[session_id]["answers"])}
    
    def complete_company_mock(self, session_id):
        """Complete mock drive and generate results."""
        if session_id not in self.company_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.company_sessions[session_id]
        session["status"] = "completed"
        
        # Generate results
        total = len(session["answers"])
        score = 75  # Placeholder - in production, calculate actual score
        
        results = {
            "session_id": session_id,
            "email": session["email"],
            "company": session["company_name"],
            "pattern": session["pattern"],
            "total_questions": total,
            "score": score,
            "passed": score >= 65,
            "cutoff": 65,
            "sections_completed": len(session["sections"]),
            "completed_at": datetime.now().isoformat()
        }
        
        self.company_results[session_id] = results
        
        return {"status": "success", "results": results}
    
    def get_company_results(self, session_id):
        """Get company mock results."""
        if session_id not in self.company_results:
            return {"status": "error", "message": "Results not found"}
        return {"status": "success", "results": self.company_results[session_id]}

company_assessment = CompanyAssessmentSystem()
