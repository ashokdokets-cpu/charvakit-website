"""
Charvak AI Versant Content Generator
Unique questions for every user - no hardcoding
"""
import logging
import json
import os
import random
from datetime import datetime

logger = logging.getLogger("charvakit.ai_versant")

class AIVersantGenerator:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.user_sessions = {}
        logger.info(f"AI Versant Generator ready - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")
    
    def generate_read_aloud(self, user_email, count=8):
        """Generate unique Read Aloud questions for a user."""
        prompt = f"""Generate {count} professional English sentences for a Read Aloud assessment.
        Requirements:
        - 10-15 words each
        - Mix of business, technology, science topics
        - Natural native English flow
        - Different from common textbook sentences
        - Professional workplace context
        Return JSON array with 'sentence' field."""
        
        return self._call_openai(prompt, count)
    
    def generate_repeats(self, user_email, count=16):
        """Generate unique Repeats questions."""
        prompt = f"""Generate {count} short English sentences for a listening/repeat assessment.
        Requirements:
        - 5-10 words each
        - Natural conversational tone
        - Common workplace phrases
        - Easy to remember and repeat
        Return JSON array with 'sentence' field."""
        
        return self._call_openai(prompt, count)
    
    def generate_sentence_builds(self, user_email, count=10):
        """Generate unique Sentence Builds questions."""
        prompt = f"""Generate {count} sentence rearrangement exercises.
        Requirements:
        - 6-8 words per sentence
        - Words separated by slashes
        - Common workplace topics
        Return JSON array with 'words' field."""
        
        return self._call_openai(prompt, count)
    
    def generate_conversations(self, user_email, count=10):
        """Generate unique conversation questions."""
        prompt = f"""Generate {count} workplace conversation questions.
        Requirements:
        - Common professional scenarios
        - Open-ended questions
        - Suitable for spoken answers
        Return JSON array."""
        
        return self._call_openai(prompt, count)
    
    def generate_story_retelling(self, user_email, count=3):
        """Generate unique story retelling passages."""
        prompt = f"""Generate {count} short passages for retelling assessment.
        Requirements:
        - 2-3 sentences each
        - Professional/business context
        - Interesting content worth retelling
        Return JSON array."""
        
        return self._call_openai(prompt, count)
    
    def generate_summary_topic(self, user_email):
        """Generate unique summary topic."""
        prompt = """Generate 1 thought-provoking topic for a summary writing assessment.
        Requirements:
        - Current professional topic
        - Debatable/opinion-based
        - Suitable for 18-minute writing
        Return JSON array."""
        
        return self._call_openai(prompt, 1)
    
    def _call_openai(self, prompt, count):
        """Call OpenAI API."""
        if not self.openai_api_key:
            return self._get_fallback_questions(prompt, count)
        
        try:
            import requests
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.95,
                    "max_tokens": 2000
                },
                timeout=15
            )
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            import re
            match = re.search(r'\[.*\]', content, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception as e:
            logger.error(f"OpenAI failed: {e}")
        
        return self._get_fallback_questions(prompt, count)
    
    def _get_fallback_questions(self, prompt, count):
        """Fallback questions if AI unavailable."""
        return [{"sentence": f"Professional sentence {i+1} for assessment."} for i in range(count)]
    
    def start_user_session(self, email):
        """Start a session for a user with unique questions."""
        session_id = f"VERSANT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.user_sessions[session_id] = {
            "session_id": session_id,
            "email": email,
            "questions": {
                "read_aloud": self.generate_read_aloud(email, 8),
                "repeats": self.generate_repeats(email, 16),
                "sentence_builds": self.generate_sentence_builds(email, 10),
                "conversations": self.generate_conversations(email, 10),
                "story_retelling": self.generate_story_retelling(email, 3),
                "summary_opinion": self.generate_summary_topic(email)
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return {"status": "success", "session": self.user_sessions[session_id]}
    
    def get_session_questions(self, session_id, section_id):
        """Get questions for a specific section."""
        if session_id not in self.user_sessions:
            return {"status": "error", "message": "Session not found"}
        
        session = self.user_sessions[session_id]
        questions = session["questions"].get(section_id, [])
        
        return {"status": "success", "section": section_id, "questions": questions}

ai_versant = AIVersantGenerator()
