"""
Charvak Company Pattern Content Engine
Real company test patterns, engaging content, placement-focused
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.company_content")

class CompanyContentEngine:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.company_content = self._initialize_company_content()
        self.user_progress = {}
        logger.info("Company Content Engine ready")
    
    def _initialize_company_content(self):
        """Initialize real company test patterns with actual topics."""
        return {
            "tcs": {
                "name": "TCS",
                "real_pattern": "TCS NQT (National Qualifier Test)",
                "sections": {
                    "foundation": {
                        "name": "Foundation Section",
                        "duration": "75 min",
                        "questions": 25,
                        "topics": [
                            {"topic": "Quantitative Aptitude", "subtopics": ["Percentages", "Profit & Loss", "Time & Work", "Speed & Distance", "Ratio & Proportion"]},
                            {"topic": "Logical Reasoning", "subtopics": ["Syllogisms", "Blood Relations", "Coding-Decoding", "Series Completion", "Analogies"]},
                            {"topic": "Verbal Ability", "subtopics": ["Reading Comprehension", "Sentence Correction", "Synonyms", "Antonyms", "Para Jumbles"]}
                        ]
                    },
                    "advanced": {
                        "name": "Advanced Section",
                        "duration": "25 min",
                        "questions": 10,
                        "topics": [
                            {"topic": "Advanced Quantitative", "subtopics": ["Probability", "Permutation & Combination", "Geometry", "Trigonometry"]},
                            {"topic": "Advanced Logical", "subtopics": ["Data Sufficiency", "Critical Reasoning", "Decision Making"]}
                        ]
                    },
                    "coding": {
                        "name": "Coding Section",
                        "duration": "55 min",
                        "questions": 2,
                        "topics": [
                            {"topic": "Data Structures", "subtopics": ["Arrays", "Strings", "Linked Lists"]},
                            {"topic": "Algorithms", "subtopics": ["Sorting", "Searching", "Recursion"]}
                        ]
                    }
                },
                "difficulty": "Moderate",
                "keywords": ["NQT", "Placement", "Fresher"]
            },
            "infosys": {
                "name": "Infosys",
                "real_pattern": "InfyTQ Certification + HackWithInfy",
                "sections": {
                    "aptitude": {
                        "name": "Aptitude Section",
                        "duration": "60 min",
                        "questions": 20,
                        "topics": [
                            {"topic": "Quantitative", "subtopics": ["Number Systems", "Percentages", "Time & Work", "Profit & Loss"]},
                            {"topic": "Logical Reasoning", "subtopics": ["Puzzles", "Seating Arrangement", "Data Interpretation"]}
                        ]
                    },
                    "technical": {
                        "name": "Technical Section",
                        "duration": "30 min",
                        "questions": 15,
                        "topics": [
                            {"topic": "DSA", "subtopics": ["Arrays", "Trees", "Graphs", "Dynamic Programming"]},
                            {"topic": "DBMS", "subtopics": ["SQL Queries", "Normalization", "Transactions"]},
                            {"topic": "OOPs", "subtopics": ["Inheritance", "Polymorphism", "Encapsulation"]}
                        ]
                    },
                    "coding": {
                        "name": "Coding Section",
                        "duration": "90 min",
                        "questions": 3,
                        "topics": [
                            {"topic": "Problem Solving", "subtopics": ["Arrays", "Strings", "Recursion", "Dynamic Programming"]}
                        ]
                    }
                },
                "difficulty": "Moderate to Hard",
                "keywords": ["InfyTQ", "HackWithInfy", "Certification"]
            },
            "wipro": {
                "name": "Wipro",
                "real_pattern": "Wipro Elite NTH (National Talent Hunt)",
                "sections": {
                    "aptitude": {
                        "name": "Aptitude Section",
                        "duration": "48 min",
                        "questions": 20,
                        "topics": [
                            {"topic": "Logical Reasoning", "subtopics": ["Series", "Analogies", "Coding-Decoding"]},
                            {"topic": "Quantitative", "subtopics": ["Percentages", "Ratios", "Averages"]}
                        ]
                    },
                    "communication": {
                        "name": "Written Communication",
                        "duration": "20 min",
                        "questions": 2,
                        "topics": [
                            {"topic": "Essay Writing", "subtopics": ["Current Affairs", "Technology Trends"]},
                            {"topic": "Email Writing", "subtopics": ["Professional Email", "Business Communication"]}
                        ]
                    },
                    "coding": {
                        "name": "Coding Section",
                        "duration": "45 min",
                        "questions": 2,
                        "topics": [
                            {"topic": "Basic Programming", "subtopics": ["Arrays", "Strings", "Loops"]}
                        ]
                    }
                },
                "difficulty": "Easy to Moderate",
                "keywords": ["Elite NTH", "Talent Hunt", "Fresher"]
            }
        }
    
    def get_company_test_pattern(self, company_id):
        """Get real test pattern for a company."""
        if company_id in self.company_content:
            return {"status": "success", "pattern": self.company_content[company_id]}
        return {"status": "error", "message": "Company pattern not found"}
    
    def get_section_topics(self, company_id, section_id):
        """Get topics for a specific section."""
        company = self.company_content.get(company_id)
        if not company:
            return {"status": "error", "message": "Company not found"}
        
        section = company["sections"].get(section_id)
        if not section:
            return {"status": "error", "message": "Section not found"}
        
        return {"status": "success", "section": section}
    
    def generate_company_questions(self, company_id, section_id, count=5):
        """Generate questions based on real company pattern."""
        company = self.company_content.get(company_id)
        if not company:
            return {"status": "error", "message": "Company not found"}
        
        section = company["sections"].get(section_id)
        if not section:
            return {"status": "error", "message": "Section not found"}
        
        # Generate questions for each topic
        questions = []
        topics = section["topics"]
        
        for i in range(count):
            topic_group = topics[i % len(topics)]
            topic = topic_group["topic"]
            subtopic = topic_group["subtopics"][i % len(topic_group["subtopics"])]
            
            questions.append({
                "id": i + 1,
                "company": company["name"],
                "section": section["name"],
                "topic": topic,
                "subtopic": subtopic,
                "question": f"Practice question on {subtopic} for {company['name']} {company['real_pattern']}",
                "difficulty": company["difficulty"]
            })
        
        return {"status": "success", "questions": questions}
    
    def get_placement_roadmap(self, company_id):
        """Get placement preparation roadmap for a company."""
        company = self.company_content.get(company_id)
        if not company:
            return {"status": "error", "message": "Company not found"}
        
        return {
            "status": "success",
            "company": company["name"],
            "pattern": company["real_pattern"],
            "roadmap": [
                {"week": 1, "focus": "Foundation - Basics", "activities": ["Review aptitude basics", "Practice 20 questions daily"]},
                {"week": 2, "focus": "Section-specific practice", "activities": ["Mock section tests", "Identify weak areas"]},
                {"week": 3, "focus": "Full mock drives", "activities": ["Complete mock tests", "Time management"]},
                {"week": 4, "focus": "Final preparation", "activities": ["Revise weak areas", "Company-specific drills"]}
            ],
            "success_tips": [
                f"Focus on {company['difficulty']} difficulty questions",
                f"Practice {company['sections'].get('aptitude', {}).get('name', 'Aptitude')} regularly",
                "Take mock tests under timed conditions",
                "Review mistakes and improve"
            ]
        }
    
    def track_user_progress(self, email, company_id, section_score):
        """Track user progress toward placement."""
        if email not in self.user_progress:
            self.user_progress[email] = {}
        
        if company_id not in self.user_progress[email]:
            self.user_progress[email][company_id] = {
                "sections_completed": 0,
                "total_score": 0,
                "mock_tests": 0,
                "started_at": datetime.now().isoformat()
            }
        
        progress = self.user_progress[email][company_id]
        progress["sections_completed"] += 1
        progress["total_score"] += section_score
        progress["mock_tests"] += 1
        progress["last_updated"] = datetime.now().isoformat()
        
        return {"status": "success", "progress": progress}
    
    def get_user_readiness(self, email, company_id):
        """Calculate placement readiness for a company."""
        if email not in self.user_progress or company_id not in self.user_progress[email]:
            return {
                "status": "success",
                "readiness": "Not Started",
                "message": f"Start practicing for {company_id.upper()} to improve readiness"
            }
        
        progress = self.user_progress[email][company_id]
        avg_score = progress["total_score"] / max(1, progress["sections_completed"])
        
        if avg_score >= 75:
            readiness = "Placement Ready 🎯"
        elif avg_score >= 60:
            readiness = "Almost Ready 📈"
        elif avg_score >= 40:
            readiness = "In Progress 📚"
        else:
            readiness = "Needs Practice 💪"
        
        return {
            "status": "success",
            "company": company_id.upper(),
            "average_score": round(avg_score, 1),
            "sections_completed": progress["sections_completed"],
            "mock_tests_taken": progress["mock_tests"],
            "readiness": readiness
        }

company_content_engine = CompanyContentEngine()
