with open('ai_versant.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add AI audio content generation
addition = '''
    def generate_audio_content(self, section_type, count):
        """AI generates audio-specific content for Versant sections."""
        if self.openai_api_key:
            try:
                import requests
                
                if section_type == "repeats":
                    prompt = f"Generate {count} short English sentences (5-8 words each) for a listening/repeat test. These will be played as audio. Use natural conversational tone, common workplace phrases. Return JSON array of strings."
                elif section_type == "read_aloud":
                    prompt = f"Generate {count} English sentences (10-15 words each) for a reading aloud test. These will be read by the candidate. Use professional workplace context. Return JSON array of strings."
                else:
                    prompt = f"Generate {count} English sentences for Versant test. Return JSON array of strings."
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.openai_api_key}"},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.9, "max_tokens": 1000},
                    timeout=15
                )
                data = response.json()
                content_text = data["choices"][0]["message"]["content"]
                
                import re
                match = re.search(r'\\[.*\\]', content_text, re.DOTALL)
                if match:
                    questions = json.loads(match.group())
                    return {"status": "success", "content": questions, "ai_generated": True, "audio_ready": True}
            except Exception as e:
                logger.error(f"AI audio content failed: {e}")
        
        return {"status": "success", "content": [], "ai_generated": False, "audio_ready": False}
'''

if 'generate_audio_content' not in content:
    content = content.replace('    def generate_repeats', addition + '\n    def generate_repeats', 1)
    with open('ai_versant.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('✅ AI audio content generation added!')
else:
    print('Already exists')
