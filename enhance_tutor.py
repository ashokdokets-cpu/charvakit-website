with open('interactive_tutor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Enhance the _ai_respond method to be a better teacher
old_respond = '''    def _ai_respond(self, session, user_message):
        """AI generates response based on context."""
        if self.openai_api_key:
            try:
                import requests
                
                # Build context from conversation
                context = "\\n".join([f"{c['role']}: {c['message'][:200]}" for c in session["conversation"][-5:]])
                
                prompt = f"""You are an AI tutor teaching {session['course']} on topic {session['topic']} to a {session['user_level']} student.
                
                Conversation so far:
                {context}
                
                Student says: {user_message}
                
                Respond as a helpful tutor:
                - Answer their question
                - Provide relevant example
                - Ask follow-up question
                - Give practice exercise if appropriate
                - Keep it conversational
                """
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 1000},
                    timeout=15
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"AI response failed: {e}")
        
        return "That's a great question! Let me explain with an example..."'''

new_respond = '''    def _ai_respond(self, session, user_message):
        """AI generates teaching response."""
        if self.openai_api_key:
            try:
                import requests
                
                context = "\\n".join([f"{c['role']}: {c['message'][:200]}" for c in session["conversation"][-5:]])
                
                prompt = f"""You are an expert AI tutor teaching {session['course']} on topic {session['topic']} to a {session['user_level']} student.
                
                Conversation:
                {context}
                
                Student: {user_message}
                
                Teach effectively:
                1. Answer their question clearly
                2. Provide a simple example
                3. Give a practice exercise
                4. Encourage and guide
                5. Keep response under 150 words
                """
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.8, "max_tokens": 500},
                    timeout=15
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
            except Exception as e:
                logger.error(f"AI response failed: {e}")
        
        return "Let me explain with an example..."'''

if old_respond in content:
    content = content.replace(old_respond, new_respond)
    with open('interactive_tutor.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ AI Tutor enhanced for teaching!')
else:
    print('Pattern not found')
