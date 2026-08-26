"""
Charvak Final Year Project Assistant
Helps students with complete final year project lifecycle
"""
import logging
from datetime import datetime
from typing import Dict, List
import secrets

logger = logging.getLogger("charvakit.fyp")


class FinalYearProjectEngine:
    """Complete final year project support."""
    
    def __init__(self):
        self.projects = []
        logger.info("Final Year Project Engine ready")
    
    def suggest_topics(self, data: Dict) -> Dict:
        """
        Suggest project topics based on branch/domain.
        data = {branch, domain, difficulty, interests}
        """
        branch = data.get("branch", "Computer Science")
        domain = data.get("domain", "AI/ML")
        
        topics = {
            "Computer Science": {
                "AI/ML": [
                    "Chatbot for College Enquiry System",
                    "Disease Prediction using ML",
                    "Face Recognition Attendance System",
                    "Sentiment Analysis for Product Reviews",
                    "Stock Price Prediction using LSTM"
                ],
                "Web Development": [
                    "College Management System",
                    "E-Learning Platform",
                    "Online Voting System",
                    "Food Delivery App",
                    "Hospital Management System"
                ],
                "Data Science": [
                    "Customer Churn Prediction",
                    "Credit Card Fraud Detection",
                    "Recommendation System",
                    "Time Series Forecasting",
                    "Social Media Analytics"
                ]
            },
            "Electronics": {
                "IoT": [
                    "Smart Home Automation",
                    "Weather Monitoring System",
                    "Smart Agriculture System",
                    "Health Monitoring Wearable",
                    "Smart Parking System"
                ]
            }
        }
        
        branch_topics = topics.get(branch, {}).get(domain, topics["Computer Science"]["AI/ML"])
        
        project_id = f"FYP-{secrets.token_hex(4).upper()}"
        
        result = {
            "project_id": project_id,
            "branch": branch,
            "domain": domain,
            "suggested_topics": branch_topics,
            "recommended": branch_topics[0],
            "difficulty": data.get("difficulty", "Intermediate"),
            "message": "Choose a topic, or ask for more suggestions!"
        }
        
        self.projects.append(result)
        return {"status": "success", **result}
    
    def generate_proposal(self, data: Dict) -> Dict:
        """
        Generate project proposal.
        data = {topic, branch, domain}
        """
        topic = data.get("topic", "Project")
        
        proposal = {
            "title": topic,
            "abstract": f"This project focuses on {topic}, addressing key challenges in the field. The proposed solution leverages modern technologies to deliver practical outcomes, with measurable impact on the target domain.",
            "objectives": [
                f"Study existing approaches to {topic}",
                f"Design an efficient solution for {topic}",
                f"Implement and test the proposed system",
                f"Document findings and future enhancements"
            ],
            "scope": f"The project covers end-to-end development of {topic}, including requirements analysis, design, implementation, testing, and deployment.",
            "tech_stack": self._suggest_tech_stack(topic),
            "modules": self._suggest_modules(topic),
            "timeline": [
                "Week 1-2: Requirements & Research",
                "Week 3-4: Design & Architecture",
                "Week 5-8: Implementation",
                "Week 9-10: Testing & Fixes",
                "Week 11-12: Documentation & Submission"
            ]
        }
        
        return {"status": "success", "proposal": proposal}
    
    def generate_documentation(self, data: Dict) -> Dict:
        """
        Generate project documentation outline.
        """
        topic = data.get("topic", "Project")
        
        docs = {
            "chapters": [
                {"chapter": 1, "title": "Introduction", "content": f"Background, problem statement, objectives of {topic}"},
                {"chapter": 2, "title": "Literature Review", "content": "Review of existing systems and research papers"},
                {"chapter": 3, "title": "System Design", "content": "Architecture, modules, database design, UML diagrams"},
                {"chapter": 4, "title": "Implementation", "content": "Code structure, key algorithms, screenshots"},
                {"chapter": 5, "title": "Testing & Results", "content": "Test cases, results analysis, performance metrics"},
                {"chapter": 6, "title": "Conclusion & Future Work", "content": "Summary, limitations, future enhancements"}
            ],
            "diagrams_needed": ["Use Case Diagram", "ER Diagram", "Class Diagram", "Sequence Diagram", "Activity Diagram"],
            "documents": ["SRS (Software Requirements Specification)", "SDD (System Design Document)", "User Manual", "Test Report"]
        }
        
        return {"status": "success", "documentation": docs}
    
    def generate_viva_questions(self, topic: str) -> Dict:
        """Generate viva questions."""
        questions = [
            f"Explain the motivation behind choosing {topic}?",
            "What are the key modules of your project?",
            "Which technologies did you use and why?",
            "What challenges did you face during development?",
            "How does your project differ from existing solutions?",
            "What future enhancements would you suggest?",
            "Explain the architecture of your system.",
            "What testing methodology did you use?",
            "How would you scale your solution?",
            "What did you learn from this project?"
        ]
        
        return {
            "status": "success",
            "questions": questions,
            "tips": [
                "Know every line of your code",
                "Be confident about your architecture choices",
                "Have real metrics/results ready",
                "Prepare a 2-minute project summary",
                "Keep documentation handy for reference"
            ]
        }
    
    def _suggest_tech_stack(self, topic: str) -> List[str]:
        """Suggest tech stack based on topic."""
        topic_lower = topic.lower()
        if "ml" in topic_lower or "ai" in topic_lower or "prediction" in topic_lower:
            return ["Python", "TensorFlow/PyTorch", "Flask/FastAPI", "PostgreSQL", "React"]
        if "web" in topic_lower or "portal" in topic_lower or "management" in topic_lower:
            return ["React", "Node.js", "Express", "MongoDB", "Bootstrap"]
        if "app" in topic_lower or "mobile" in topic_lower:
            return ["Flutter/React Native", "Firebase", "REST API"]
        return ["Python", "React", "PostgreSQL", "Docker"]
    
    def _suggest_modules(self, topic: str) -> List[str]:
        """Suggest project modules."""
        return [
            "User Authentication & Management",
            f"Core {topic} Module",
            "Admin Dashboard",
            "Reporting & Analytics",
            "Notifications System",
            "Settings & Configuration"
        ]
    
    def get_stats(self) -> Dict:
        return {
            "status": "success",
            "stats": {
                "total_projects": len(self.projects),
                "topics_suggested": len(self.projects)
            }
        }


final_year_project_engine = FinalYearProjectEngine()