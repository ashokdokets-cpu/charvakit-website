"""
Charvak Complete AI Mock Drive
AI generates exact question counts: TCS 25+10+2, Infosys 20+15+3, etc.
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.complete_mock")

class CompleteMockDrive:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.sessions = {}
        logger.info(f"Complete Mock Drive - AI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def get_company_config(self, company_id):
        """Get exact question counts for each company."""
        configs = {
            "tcs": {
                "name": "TCS", "pattern": "NQT",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "75 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Advanced", "count": 10, "time": "25 min", "topics": ["Advanced Quant", "Advanced Logic"]},
                    {"name": "Coding", "count": 2, "time": "55 min", "topics": ["DSA", "Problem Solving"]}
                ]
            },
            "infosys": {
                "name": "Infosys", "pattern": "InfyTQ",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS", "OOPs"]},
                    {"name": "Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                ]
            },
            "cognizant": {
                "name": "Cognizant", "pattern": "GenC",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quantitative", "Analytical", "Verbal"]},
                    {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Speaking", "Grammar"]},
                    {"name": "Programming", "count": 5, "time": "45 min", "topics": ["SQL", "Debugging"]}
                ]
            },
            "wipro": {
                "name": "Wipro", "pattern": "Elite NTH",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "48 min", "topics": ["Logical", "Quant"]},
                    {"name": "Communication", "count": 2, "time": "20 min", "topics": ["Essay", "Email"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic", "Intermediate"]}
                ]
            },
            "accenture": {
                "name": "Accenture", "pattern": "ASE",
                "sections": [
                    {"name": "Cognitive", "count": 25, "time": "60 min", "topics": ["Aptitude", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Grammar"]}
                ]
            }
        }
        return configs.get(company_id, configs["tcs"])
    
    def generate_ai_questions(self, topic, count):
        """Generate AI questions for a topic."""
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Generate {count} multiple-choice questions on {topic} for placement test. 4 options each. Return JSON array with q, options, correct."
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.95},
                    timeout=15
                )
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                import re
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    return json.loads(match.group())
            except Exception as e:
                logger.error(f"AI failed: {e}")
        
        # Fallback
        return [{"q": f"{topic} question {i+1}", "options": ["A", "B", "C", "D"], "correct": i % 4} for i in range(count)]
    
    def start_mock_drive(self, email, company_id):
        """Start mock drive with AI-generated questions matching exact counts."""
        config = self.get_company_config(company_id)
        session_id = f"MOCK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        sections_with_questions = []
        total_questions = 0
        
        for section in config["sections"]:
            topics = section["topics"]
            count = section["count"]
            questions_per_topic = max(1, count // len(topics))
            remaining = count
            
            section_questions = []
            for i, topic in enumerate(topics):
                num = questions_per_topic
                if i == len(topics) - 1:
                    num = remaining
                
                questions = self.generate_ai_questions(topic, num)
                for j, q in enumerate(questions):
                    section_questions.append({
                        "id": len(section_questions) + 1,
                        "question": q.get("q", q.get("question", f"{topic} Q{j+1}")),
                        "options": q.get("options", ["A", "B", "C", "D"]),
                        "correct": q.get("correct", 0),
                        "topic": topic
                    })
                remaining -= num
            
            sections_with_questions.append({
                "name": section["name"],
                "count": count,
                "time": section["time"],
                "topics": topics,
                "questions": section_questions
            })
            total_questions += len(section_questions)
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "email": email,
            "company": config["name"],
            "pattern": config["pattern"],
            "sections": sections_with_questions,
            "total_questions": total_questions,
            "answers": [],
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        
        return {"status": "success", "session": self.sessions[session_id]}
    
    def submit_answer(self, session_id, section_name, question_id, selected_option):
        """Submit answer."""
        if session_id not in self.sessions:
            return {"status": "error", "message": "Session not found"}
        
        self.sessions[session_id]["answers"].append({
            "section": section_name,
            "question_id": question_id,
            "selected": selected_option,
            "submitted_at": datetime.now().isoformat()
        })
        
        return {"status": "success", "total_answered": len(self.sessions[session_id]["answers"])}
    
    def complete_mock(self, session_id):
        """Complete mock and generate results."""
        if session_id not in self.sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.sessions[session_id]
        
        # Calculate score
        total_questions = session["total_questions"]
        correct = 0
        
        for answer in session["answers"]:
            for section in session["sections"]:
                for q in section["questions"]:
                    if q["id"] == answer["question_id"] and q["correct"] == answer["selected"]:
                        correct += 1
        
        score = (correct / total_questions * 100) if total_questions > 0 else 0
        
        results = {
            "session_id": session_id,
            "email": session["email"],
            "company": session["company"],
            "pattern": session["pattern"],
            "total_questions": total_questions,
            "answered": len(session["answers"]),
            "correct": correct,
            "score": round(score, 1),
            "pass": score >= 65,
            "sections": [{"name": s["name"], "count": s["count"]} for s in session["sections"]],
            "completed_at": datetime.now().isoformat()
        }
        
        # Record in results system
        from results_system import results_system
        results_system.record_assessment_result(
            session["email"],
            "company_mock",
            f"{session['company']} Mock Drive",
            score,
            total_questions,
            correct,
            {"pattern": session["pattern"]}
        )
        
        return {"status": "success", "results": results}

complete_mock = CompleteMockDrive()
