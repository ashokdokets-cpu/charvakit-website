"""
Charvak AI Pattern Question Generator
OpenAI generates unique questions for every pattern
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.ai_pattern_questions")

class AIPatternQuestionGenerator:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.question_cache = {}
        logger.info(f"AI Pattern Questions - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def generate_pattern_questions(self, company_name, pattern_name, sections):
        """Generate AI questions for all sections of a pattern."""
        generated_sections = []
        
        for section in sections:
            topics = section["topics"]
            count = section["count"]
            
            questions = []
            questions_per_topic = max(1, count // len(topics))
            remaining = count
            
            for i, topic in enumerate(topics):
                num = questions_per_topic
                if i == len(topics) - 1:
                    num = remaining
                
                topic_questions = self._generate_topic_questions(company_name, pattern_name, topic, num)
                questions.extend(topic_questions)
                remaining -= num
            
            generated_sections.append({
                "name": section["name"],
                "count": count,
                "topics": topics,
                "questions": questions[:count]
            })
        
        return generated_sections
    
    def _generate_topic_questions(self, company_name, pattern_name, topic, count):
        """Generate AI questions for a specific topic."""
        cache_key = f"{company_name}_{pattern_name}_{topic}_{count}"
        
        if cache_key in self.question_cache:
            return self.question_cache[cache_key]
        
        if self.openai_api_key:
            questions = self._call_openai(company_name, pattern_name, topic, count)
            if questions:
                self.question_cache[cache_key] = questions
                return questions
        
        # Fallback with varied questions
        return self._get_varied_fallback(company_name, topic, count)
    
    def _call_openai(self, company_name, pattern_name, topic, count):
        """Call OpenAI to generate unique questions."""
        try:
            import requests
            
            prompt = f"""Generate {count} UNIQUE multiple-choice questions for {company_name} {pattern_name} placement test on {topic}.
            Requirements:
            - Each question DIFFERENT from others
            - Relevant to {topic}
            - 4 options with one correct answer
            - Professional market-standard quality
            - No repetition within this set
            Return JSON array with: q (question text), options (4 options), correct (index 0-3)
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
                timeout=20
            )
            
            data = response.json()
            content_text = data["choices"][0]["message"]["content"]
            
            import re
            match = re.search(r'\[.*\]', content_text, re.DOTALL)
            if match:
                questions = json.loads(match.group())
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
    
    def _get_varied_fallback(self, company_name, topic, count):
        """Varied fallback questions if AI unavailable."""
        bank = {
            "Quant": [
                "What is 25% of 400?", "Train travels 360 km in 6 hours. Speed?",
                "LCM of 12 and 18?", "5 workers do job in 10 days. 10 workers?",
                "What is 20% of 500?", "Car covers 240 km in 4 hrs. 7 hrs?",
                "Average of 10,20,30,40,50?", "15% of Rs.2000?",
                "3x + 7 = 22, x = ?", "8 workers in 12 days. 16 workers?"
            ],
            "Logical": [
                "A > B, B > C. Then?", "Next: 1, 4, 9, 16, ?",
                "Complete: 2, 3, 5, 7, 11, ?", "Different: Apple, Banana, Carrot?",
                "Monday, 3 days ago?", "Complete: 5, 10, 20, 40, ?",
                "Next: 2, 6, 12, 20, 30, ?", "CAT=24, DOG=?",
                "Complete: 1, 3, 6, 10, 15, ?", "Z, X, V, T, ?"
            ],
            "DSA": [
                "LIFO data structure?", "Binary search complexity?",
                "FIFO data structure?", "Not linear structure?",
                "Max children in binary tree?", "Best for recursion?",
                "Hash table used for?", "Root first traversal?",
                "Self-balancing BST?", "Linked list vs array?"
            ]
        }
        
        questions = bank.get(topic, [f"{topic} question {i+1}" for i in range(count)])
        
        formatted = []
        for i in range(count):
            q_text = questions[i % len(questions)]
            options = self._get_options_for_topic(topic, i)
            formatted.append({
                "id": i + 1,
                "question": q_text,
                "options": options,
                "correct": i % 4,
                "topic": topic,
                "ai_generated": False
            })
        return formatted
    
    def _get_options_for_topic(self, topic, index):
        """Get options for fallback questions."""
        option_sets = {
            "Quant": [["80", "100", "120", "150"], ["50", "55", "60", "65"], ["24", "36", "48", "72"], ["3", "5", "7", "10"]],
            "Logical": [["A > C", "A < C", "A = C", "Cannot say"], ["20", "25", "30", "36"], ["13", "14", "15", "16"], ["Apple", "Banana", "Carrot", "Mango"]],
            "DSA": [["Queue", "Stack", "Array", "Linked List"], ["O(1)", "O(log n)", "O(n)", "O(n²)"], ["Stack", "Queue", "Tree", "Graph"], ["Array", "Stack", "Tree", "Queue"]]
        }
        
        sets = option_sets.get(topic, [["Option A", "Option B", "Option C", "Option D"]])
        return sets[index % len(sets)]

ai_pattern_questions = AIPatternQuestionGenerator()
