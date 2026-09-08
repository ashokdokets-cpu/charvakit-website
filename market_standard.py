"""
Charvak Market-Standard Question Generator
Correct question counts, market standards, results generation
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.market_standard")

class MarketStandardGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.results_store = {}
        logger.info("Market Standard Generator ready")
    
    def get_versant_market_standard(self):
        """Get Versant market-standard sections with exact question counts."""
        return {
            "status": "success",
            "assessment": "Versant English Test",
            "total_duration": "50 minutes",
            "sections": [
                {
                    "section": "Read Aloud",
                    "questions": 8,
                    "time_per_question": "15 seconds",
                    "total_time": "2 minutes",
                    "skill": "Pronunciation, Fluency",
                    "market_standard": "Pearson Versant - 8 items"
                },
                {
                    "section": "Repeats",
                    "questions": 16,
                    "time_per_question": "10 seconds",
                    "total_time": "3 minutes",
                    "skill": "Listening, Memory",
                    "market_standard": "Pearson Versant - 16 items"
                },
                {
                    "section": "Sentence Builds",
                    "questions": 10,
                    "time_per_question": "15 seconds",
                    "total_time": "3 minutes",
                    "skill": "Grammar, Structure",
                    "market_standard": "Pearson Versant - 10 items"
                },
                {
                    "section": "Conversations",
                    "questions": 10,
                    "time_per_question": "20 seconds",
                    "total_time": "4 minutes",
                    "skill": "Comprehension, Response",
                    "market_standard": "Pearson Versant - 10 items"
                },
                {
                    "section": "Story Retelling",
                    "questions": 3,
                    "time_per_question": "30 seconds",
                    "total_time": "2 minutes",
                    "skill": "Retention, Structure",
                    "market_standard": "Pearson Versant - 3 items"
                },
                {
                    "section": "Summary & Opinion",
                    "questions": 1,
                    "time_per_question": "18 minutes",
                    "total_time": "18 minutes",
                    "skill": "Writing, Expression",
                    "market_standard": "Pearson Versant - 1 item"
                }
            ],
            "total_questions": 48,
            "scoring": {
                "sentence_mastery": "0-80",
                "vocabulary": "0-80",
                "fluency": "0-80",
                "pronunciation": "0-80"
            },
            "cefr_levels": ["A1", "A2", "B1", "B2", "C1", "C2"]
        }
    
    def get_mcq_market_standard(self):
        """Get MCQ market-standard categories with question counts."""
        return {
            "status": "success",
            "assessment": "MCQ Assessment",
            "categories": [
                {
                    "category": "Aptitude & Logical",
                    "topics": 7,
                    "questions_per_topic": 10,
                    "total_questions": 70,
                    "topics_list": ["Quant", "Probability", "Data Interpretation", "Logical Reasoning", "Syllogisms", "Coding-Decoding", "Pattern Recognition"]
                },
                {
                    "category": "Technical CS",
                    "topics": 6,
                    "questions_per_topic": 10,
                    "total_questions": 60,
                    "topics_list": ["Data Structures", "Algorithms", "OOPs", "Operating Systems", "DBMS/SQL", "Computer Networks"]
                },
                {
                    "category": "Pseudocode",
                    "topics": 4,
                    "questions_per_topic": 10,
                    "total_questions": 40,
                    "topics_list": ["C", "C++", "Java", "Python"]
                },
                {
                    "category": "Domain-Specific",
                    "topics": 4,
                    "questions_per_topic": 10,
                    "total_questions": 40,
                    "topics_list": ["Cloud", "Web Development", "Cybersecurity", "Agile"]
                }
            ],
            "total_topics": 21,
            "total_questions": 210
        }
    
    def get_company_market_standard(self):
        """Get company patterns with market-standard sections."""
        return {
            "status": "success",
            "companies": [
                {
                    "company": "TCS",
                    "patterns": ["NQT", "Digital", "Innovator"],
                    "sections": [
                        {"name": "Foundation", "questions": 25, "time": "75 min"},
                        {"name": "Advanced", "questions": 10, "time": "25 min"},
                        {"name": "Coding", "questions": 2, "time": "55 min"}
                    ]
                },
                {
                    "company": "Cognizant",
                    "patterns": ["GenC", "GenC Elevate", "GenC Pro"],
                    "sections": [
                        {"name": "Aptitude", "questions": 20, "time": "60 min"},
                        {"name": "Communication", "questions": 10, "time": "20 min"},
                        {"name": "Programming", "questions": 5, "time": "45 min"}
                    ]
                },
                {
                    "company": "Infosys",
                    "patterns": ["InfyTQ", "HackWithInfy"],
                    "sections": [
                        {"name": "Aptitude", "questions": 20, "time": "60 min"},
                        {"name": "Technical", "questions": 15, "time": "30 min"},
                        {"name": "Coding", "questions": 3, "time": "90 min"}
                    ]
                },
                {
                    "company": "Wipro",
                    "patterns": ["Elite NTH", "Turbo"],
                    "sections": [
                        {"name": "Aptitude", "questions": 20, "time": "48 min"},
                        {"name": "Communication", "questions": 2, "time": "20 min"},
                        {"name": "Coding", "questions": 2, "time": "45 min"}
                    ]
                },
                {
                    "company": "Accenture",
                    "patterns": ["ASE", "Advanced ASE"],
                    "sections": [
                        {"name": "Cognitive", "questions": 25, "time": "60 min"},
                        {"name": "Technical", "questions": 15, "time": "30 min"},
                        {"name": "Communication", "questions": 10, "time": "20 min"}
                    ]
                }
            ]
        }
    
    def generate_versant_questions(self, section_id, count=None):
        """Generate Versant questions for a section."""
        section_prompts = {
            "read_aloud": [
                "The implementation of artificial intelligence has transformed how businesses approach customer service.",
                "Sustainable development requires a balanced approach between economic growth and environmental protection.",
                "The quarterly financial report indicates a significant improvement in operational efficiency.",
                "Effective communication skills are essential for professional success in any industry.",
                "The research team has developed an innovative solution to address climate change challenges.",
                "Organizations must adapt to rapidly changing market conditions to remain competitive.",
                "The integration of cloud computing has revolutionized data management across enterprises.",
                "Successful project management requires careful planning and continuous monitoring."
            ],
            "repeats": [
                "The meeting has been rescheduled to Thursday afternoon.",
                "Please submit your report by the end of this week.",
                "The new policy takes effect from the first of next month.",
                "We need to review the proposal before making a decision.",
                "The training session will be held in the main conference room.",
                "Customer feedback is essential for improving our services."
            ],
            "sentence_builds": [
                "the / meeting / starts / at / nine / sharp",
                "please / submit / the / report / by / Friday",
                "the / team / completed / the / project",
                "we / will / discuss / the / budget / next / week"
            ],
            "conversations": [
                "Would you find a stove in a kitchen or a bedroom?",
                "What would you do if you missed an important deadline?",
                "How do you prioritize tasks when everything is urgent?",
                "What is the best way to handle a difficult customer?"
            ],
            "story_retelling": [
                "A young engineer joined a startup and learned to build scalable systems within six months.",
                "The marketing team launched a campaign that doubled their customer base in three months."
            ],
            "summary_opinion": [
                "Write a summary of the impact of artificial intelligence on modern workplaces."
            ]
        }
        
        prompts = section_prompts.get(section_id, [])
        if count:
            prompts = prompts[:count]
        
        return {"status": "success", "section": section_id, "questions": prompts}
    
    def generate_mcq_questions(self, category, topic, count=10):
        """Generate MCQ questions for a category/topic."""
        if self.openai_api_key:
            try:
                import requests
                prompt = f"Generate {count} MCQ questions on {topic} ({category}). 4 options each. Return JSON array."
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
                    return {"status": "success", "questions": json.loads(match.group()), "ai_generated": True}
            except Exception as e:
                logger.error(f"AI failed: {e}")
        
        return {
            "status": "success",
            "questions": [{"id": i+1, "question": f"{topic} question {i+1}", "options": ["A", "B", "C", "D"], "correct": 0} for i in range(count)],
            "ai_generated": False
        }
    
    def generate_results(self, email, assessment_type, answers, total_questions):
        """Generate results report."""
        correct = sum(1 for a in answers if a.get("is_correct", False))
        score = (correct / total_questions * 100) if total_questions > 0 else 0
        
        if assessment_type == "versant":
            cefr = self._get_cefr_level(score)
        else:
            cefr = None
        
        results = {
            "email": email,
            "assessment_type": assessment_type,
            "total_questions": total_questions,
            "correct_answers": correct,
            "score": round(score, 1),
            "cefr_level": cefr,
            "pass": score >= 60,
            "generated_at": datetime.now().isoformat()
        }
        
        self.results_store[email] = results
        return {"status": "success", "results": results}
    
    def _get_cefr_level(self, score):
        if score >= 90: return "C2 (Mastery)"
        elif score >= 75: return "C1 (Advanced)"
        elif score >= 60: return "B2 (Upper Intermediate)"
        elif score >= 45: return "B1 (Intermediate)"
        elif score >= 30: return "A2 (Elementary)"
        else: return "A1 (Beginner)"

market_standard = MarketStandardGenerator()
