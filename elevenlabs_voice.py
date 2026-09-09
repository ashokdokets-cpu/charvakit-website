"""
Charvak ElevenLabs AI Voice Integration
Professional AI voice for Versant audio playback
"""
import logging
import json
import os
import base64
import requests

logger = logging.getLogger("charvakit.elevenlabs")

class ElevenLabsVoice:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.api_key = os.getenv("ELEVENLABS_API_KEY", "")
        self.voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default "Rachel" voice
        self.base_url = "https://api.elevenlabs.io/v1"
        logger.info(f"ElevenLabs: {'ENABLED' if self.api_key else 'DISABLED'}")
    
    def text_to_speech(self, text, voice_id=None):
        """Convert text to speech using ElevenLabs."""
        if not self.api_key:
            return {"status": "error", "message": "ElevenLabs API key not set"}
        
        voice = voice_id or self.voice_id
        
        try:
            response = requests.post(
                f"{self.base_url}/text-to-speech/{voice}",
                headers={
                    "xi-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                },
                timeout=20
            )
            
            if response.status_code == 200:
                # Return audio as base64
                audio_base64 = base64.b64encode(response.content).decode('utf-8')
                return {
                    "status": "success",
                    "audio_base64": audio_base64,
                    "content_type": "audio/mpeg"
                }
            else:
                elif response.status_code == 429:
                import time
                time.sleep(3)
                return {"status": "error", "message": "ElevenLabs rate limit reached. Please wait a moment."}
            else:
                return {"status": "error", "message": f"ElevenLabs error: {response.status_code}"}
        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_audio_for_questions(self, questions):
        """Generate audio for multiple questions."""
        audio_results = []
        
        for i, question in enumerate(questions):
            result = self.text_to_speech(question)
            if result["status"] == "success":
                audio_results.append({
                    "question_index": i,
                    "question": question,
                    "audio_base64": result["audio_base64"]
                })
        
        return {"status": "success", "total": len(audio_results), "audio_files": audio_results}
    
    def get_available_voices(self):
        """Get available ElevenLabs voices."""
        if not self.api_key:
            return {"status": "error", "message": "API key not set"}
        
        try:
            response = requests.get(
                f"{self.base_url}/voices",
                headers={"xi-api-key": self.api_key},
                timeout=10
            )
            if response.status_code == 200:
                voices = response.json().get("voices", [])
                return {
                    "status": "success",
                    "voices": [
                        {"voice_id": v["voice_id"], "name": v["name"]}
                        for v in voices[:10]
                    ]
                }
        except Exception as e:
            logger.error(f"Get voices failed: {e}")
        
        return {"status": "error", "message": "Failed to get voices"}

elevenlabs_voice = ElevenLabsVoice()
