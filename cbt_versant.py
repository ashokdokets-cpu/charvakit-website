"""
Charvak Complete CBT Versant System
Audio recording, listening playback, proper section design
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.cbt_versant")

class CBTVersantSystem:
    def __init__(self):
        self.sessions = {}
        self.audio_recordings = {}
        logger.info("CBT Versant System ready")
    
    def get_section_design(self, section_id):
        """Get proper CBT design for each Versant section."""
        sections = {
            "read_aloud": {
                "name": "Read Aloud",
                "type": "speaking",
                "input": "audio_recording",
                "questions": 8,
                "time_per_question": 15,
                "instruction": "Read the sentence aloud. Click Record, read the sentence, then click Stop.",
                "prompts": [
                    "The company will announce quarterly results next week.",
                    "Please submit your assignment by Friday afternoon.",
                    "The new software update includes several improvements.",
                    "Our team meeting has been rescheduled to Monday.",
                    "Customer satisfaction is our top priority.",
                    "The annual report will be published in March.",
                    "Please review the document before signing.",
                    "The training session starts at nine o'clock sharp."
                ]
            },
            "repeats": {
                "name": "Repeats",
                "type": "listening_speaking",
                "input": "audio_playback_then_record",
                "questions": 16,
                "time_per_question": 10,
                "instruction": "Listen to the audio, then repeat exactly what you heard.",
                "prompts": [
                    "The quick brown fox jumps over the lazy dog.",
                    "Could you please repeat the last sentence?",
                    "I would like to schedule an appointment for tomorrow.",
                    "The conference will be held at the convention center."
                ]
            },
            "sentence_builds": {
                "name": "Sentence Builds",
                "type": "rearrangement",
                "input": "drag_drop_words",
                "questions": 10,
                "time_per_question": 15,
                "instruction": "Rearrange the words to form a correct sentence.",
                "prompts": [
                    "the / meeting / at / starts / nine / sharp",
                    "please / submit / the / report / by / Friday",
                    "the / team / completed / the / project"
                ]
            },
            "conversations": {
                "name": "Conversations",
                "type": "speaking",
                "input": "audio_recording",
                "questions": 10,
                "time_per_question": 20,
                "instruction": "Listen to the question and record your spoken answer.",
                "prompts": [
                    "Would you find a stove in a kitchen or a bedroom?",
                    "What would you do if you missed an important deadline?",
                    "How do you prioritize tasks when everything is urgent?"
                ]
            },
            "story_retelling": {
                "name": "Story Retelling",
                "type": "reading_speaking",
                "input": "read_then_record",
                "questions": 3,
                "time_per_question": 30,
                "instruction": "Read the passage, then retell it in your own words.",
                "prompts": [
                    "A young engineer joined a startup and learned to build scalable systems within six months.",
                    "The marketing team launched a campaign that doubled their customer base."
                ]
            },
            "summary_opinion": {
                "name": "Summary & Opinion",
                "type": "writing",
                "input": "typed_response",
                "questions": 1,
                "time_per_question": 1080,  # 18 minutes
                "instruction": "Write a summary and your opinion on the topic. This is the only section where you type.",
                "prompts": [
                    "Write a summary of the impact of artificial intelligence on modern workplaces."
                ]
            }
        }
        
        return sections.get(section_id, {"error": "Section not found"})
    
    def start_cbt_session(self, email):
        """Start a CBT Versant session."""
        session_id = f"CBT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.sessions[session_id] = {
            "session_id": session_id,
            "email": email,
            "started_at": datetime.now().isoformat(),
            "current_section": "read_aloud",
            "recordings": [],
            "answers": {},
            "status": "in_progress"
        }
        
        return {"status": "success", "session_id": session_id, "session": self.sessions[session_id]}
    
    def save_audio_recording(self, session_id, section_id, question_id, audio_blob):
        """Save audio recording for speaking sections."""
        if session_id not in self.sessions:
            return {"status": "error", "message": "Session not found"}
        
        recording_id = f"REC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        self.audio_recordings[recording_id] = {
            "recording_id": recording_id,
            "session_id": session_id,
            "section_id": section_id,
            "question_id": question_id,
            "audio_blob": audio_blob,
            "recorded_at": datetime.now().isoformat()
        }
        
        self.sessions[session_id]["recordings"].append(recording_id)
        
        return {"status": "success", "recording_id": recording_id}
    
    def submit_text_answer(self, session_id, section_id, question_id, answer):
        """Submit text answer (for writing section only)."""
        if session_id not in self.sessions:
            return {"status": "error", "message": "Session not found"}
        
        self.sessions[session_id]["answers"][f"{section_id}_{question_id}"] = answer
        
        return {"status": "success", "answer_recorded": True}
    
    def get_section_questions(self, section_id):
        """Get questions for a section with proper CBT instructions."""
        section = self.get_section_design(section_id)
        return {
            "status": "success",
            "section": section,
            "questions": section.get("prompts", [])
        }

cbt_versant = CBTVersantSystem()
