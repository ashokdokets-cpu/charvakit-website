"""
Charvak IELTS Academic Engine
AI-powered IELTS practice: Listening, Reading, Writing.
Speaking deferred to Session M-2.
"""
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.ielts")


class IELTSEngine:
    """IELTS Academic practice engine (stateless orchestration)."""

    SECTIONS = [
        {"id": "listening", "name": "Listening", "questions": 40, "duration_min": 30,
         "note": "AI-generated MCQ practice; real IELTS uses recorded audio"},
        {"id": "reading", "name": "Reading", "questions": 40, "duration_min": 60,
         "note": "3 passages, 40 questions"},
        {"id": "writing", "name": "Writing", "questions": 2, "duration_min": 60,
         "note": "Task 1 (150 words) + Task 2 (250 words); AI band scoring"},
        {"id": "speaking", "name": "Speaking", "questions": 3, "duration_min": 14,
         "note": "3 parts: Interview, Long Turn, Discussion; audio + AI band scoring"},
    ]

    WRITING_TASK_1_MIN_WORDS = 150
    WRITING_TASK_2_MIN_WORDS = 250

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        logger.info("IELTS Engine ready | AI: %s",
                    "ENABLED" if self.openai_api_key else "DISABLED")

    # ============================================================
    # STATIC / INFO
    # ============================================================

    def get_sections(self) -> Dict:
        """List IELTS Academic sections available for practice."""
        return {
            "status": "success",
            "exam": "IELTS Academic",
            "sections": self.SECTIONS,
            "speaking_available": True,
            "speaking_note": "3-part test: interview, long turn, discussion. AI band scoring on 4 criteria.",
        }

    # ============================================================
    # AI HELPER (JSON mode - matches our 8-fix pattern)
    # ============================================================

    def _ai_json(self, prompt: str, max_tokens: int, temperature: float) -> Optional[Dict]:
        """Call OpenAI in JSON mode and return parsed dict, or None on failure."""
        if not self.openai_api_key:
            return None
        try:
            import requests
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}",
                         "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "response_format": {"type": "json_object"},
                },
                timeout=45,
            )
            response.raise_for_status()
            content = (response.json().get("choices", [{}])[0]
                       .get("message", {}).get("content") or "").strip()
            # Defensive: strip markdown fences even in JSON mode
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"IELTS AI call failed: {e}")
            return None

    # ============================================================
    # WRITING - prompt generation
    # ============================================================

    def generate_writing_prompt(self, task: int = 2, topic: Optional[str] = None) -> Dict:
        """
        Generate a Writing Task 1 or Task 2 prompt.
        Task 1: describe a chart/table/process (150 words)
        Task 2: essay in response to a point of view (250 words)
        """
        task = 2 if task not in (1, 2) else task

        if task == 1:
            task_desc = ("a report describing a chart, graph, table, or process diagram. "
                         "The candidate must write at least 150 words describing the data "
                         "or process objectively.")
            min_words = self.WRITING_TASK_1_MIN_WORDS
        else:
            task_desc = ("an essay responding to a point of view, argument, or problem. "
                         "The candidate must write at least 250 words arguing a position "
                         "with supporting examples.")
            min_words = self.WRITING_TASK_2_MIN_WORDS

        topic_line = f"Topic area: {topic}." if topic else "Choose a fresh, generic IELTS topic."

        prompt = (
            f"You are an IELTS Academic Writing examiner creating a Task {task} prompt. "
            f"Task {task} requires {task_desc} {topic_line}\n\n"
            "Return a JSON object: "
            '{"prompt": "the task prompt text (2-4 sentences)", '
            '"topic": "1-3 word topic label", '
            '"difficulty": "Easy|Medium|Hard", '
            '"sample_ideas": ["bullet 1", "bullet 2", "bullet 3"]}'
        )

        result = self._ai_json(prompt, max_tokens=500, temperature=0.8)

        if not result or "prompt" not in result:
            # Fallback - well-known style prompt
            fallback = {
                1: {
                    "prompt": ("The chart below shows the percentage of households in "
                               "different income brackets across four countries in 2024. "
                               "Summarise the information by selecting and reporting the "
                               "main features, and make comparisons where relevant."),
                    "topic": "Household Income",
                    "difficulty": "Medium",
                    "sample_ideas": ["Highest earners concentrated in Country A",
                                     "Middle-income share dropped in Country B",
                                     "Country D had the widest spread"],
                },
                2: {
                    "prompt": ("Some people believe that technology has made our lives "
                               "more complicated, while others believe it has made life "
                               "easier. Discuss both views and give your own opinion. "
                               "Give reasons for your answer and include any relevant "
                               "examples from your own knowledge or experience."),
                    "topic": "Technology & Life",
                    "difficulty": "Medium",
                    "sample_ideas": ["Simplified communication and access to information",
                                     "Information overload and privacy concerns",
                                     "Balanced view depending on context"],
                },
            }[task]
            return {
                "status": "success",
                "task": task,
                "prompt_id": f"IELTS-P-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "prompt": fallback["prompt"],
                "topic": fallback["topic"],
                "difficulty": fallback["difficulty"],
                "sample_ideas": fallback["sample_ideas"],
                "min_words": min_words,
                "ai_generated": False,
            }

        return {
            "status": "success",
            "task": task,
            "prompt_id": f"IELTS-P-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "prompt": result.get("prompt", ""),
            "topic": result.get("topic", "General"),
            "difficulty": result.get("difficulty", "Medium"),
            "sample_ideas": result.get("sample_ideas", []),
            "min_words": min_words,
            "ai_generated": True,
        }

    # ============================================================
    # WRITING - band scoring
    # ============================================================

    def evaluate_writing(self, essay: str, task: int = 2,
                         prompt_text: str = "", email: Optional[str] = None) -> Dict:
        """
        Score an IELTS Writing essay on the 4 official criteria.
        Returns 4 sub-bands + overall band (0-9, half-band rounded).

        Criteria (official IELTS):
          - Task Achievement (Task 1) / Task Response (Task 2)
          - Coherence & Cohesion
          - Lexical Resource
          - Grammatical Range & Accuracy
        """
        task = 2 if task not in (1, 2) else task
        essay = (essay or "").strip()
        word_count = len(essay.split())

        if not essay:
            return {"status": "error", "message": "Essay is empty"}
        if word_count < 50:
            return {"status": "error",
                    "message": f"Essay too short ({word_count} words). Minimum useful length is 50 words."}

        min_words = (self.WRITING_TASK_1_MIN_WORDS if task == 1
                     else self.WRITING_TASK_2_MIN_WORDS)
        criterion_1 = "Task Achievement" if task == 1 else "Task Response"

        eval_prompt = (
            f"You are a certified IELTS Academic Writing examiner. Score the following "
            f"Task {task} essay on the 4 official IELTS criteria.\n\n"
            f"Task prompt: {prompt_text or '(not provided)'}\n"
            f"Word count: {word_count} (minimum is {min_words})\n"
            f"Essay:\n\"\"\"{essay}\"\"\"\n\n"
            "Scoring rules:\n"
            "- Each criterion is scored on a 0-9 band scale in 0.5 increments\n"
            "- Overall band = average of 4 criteria, rounded to nearest 0.5\n"
            "- If word count is below minimum, cap Task Achievement/Response at 5.0\n"
            "- Be honest and calibrated - do not inflate\n\n"
            "Return a JSON object: {\n"
            f'  "task_achievement_or_response": <band 0-9>,\n'
            '  "coherence_cohesion": <band 0-9>,\n'
            '  "lexical_resource": <band 0-9>,\n'
            '  "grammatical_range_accuracy": <band 0-9>,\n'
            '  "overall_band": <band 0-9>,\n'
            '  "feedback": {\n'
            '    "task_achievement_or_response": "2-3 sentence feedback",\n'
            '    "coherence_cohesion": "2-3 sentence feedback",\n'
            '    "lexical_resource": "2-3 sentence feedback",\n'
            '    "grammatical_range_accuracy": "2-3 sentence feedback"\n'
            '  },\n'
            '  "strengths": ["...", "...", "..."],\n'
            '  "improvements": ["...", "...", "..."]\n'
            "}"
        )

        result = self._ai_json(eval_prompt, max_tokens=1200, temperature=0.3)

        if not result or "overall_band" not in result:
            # Fallback - heuristic score based on word count only
            return {
                "status": "success",
                "estimated": True,
                "ai_scored": False,
                "task": task,
                "word_count": word_count,
                "min_words": min_words,
                "overall_band": None,
                "task_achievement_or_response": None,
                "coherence_cohesion": None,
                "lexical_resource": None,
                "grammatical_range_accuracy": None,
                "feedback": {
                    "task_achievement_or_response": "AI scoring unavailable; word count only.",
                    "coherence_cohesion": "-",
                    "lexical_resource": "-",
                    "grammatical_range_accuracy": "-",
                },
                "strengths": [],
                "improvements": [],
                "message": ("AI scoring unavailable. Essay saved for review. "
                            "Word count: " + str(word_count)),
            }

        scored = {
            "status": "success",
            "estimated": True,
            "ai_scored": True,
            "task": task,
            "word_count": word_count,
            "min_words": min_words,
            "overall_band": result.get("overall_band"),
            "task_achievement_or_response": result.get("task_achievement_or_response"),
            "coherence_cohesion": result.get("coherence_cohesion"),
            "lexical_resource": result.get("lexical_resource"),
            "grammatical_range_accuracy": result.get("grammatical_range_accuracy"),
            "feedback": result.get("feedback", {}),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
            "criterion_1_label": criterion_1,
        }

        # Persist to results_system if email provided
        if email:
            try:
                from results_system import results_system
                overall = float(scored.get("overall_band") or 0)
                # Convert band (0-9) to 0-100 for the existing schema
                score_pct = round((overall / 9.0) * 100, 1) if overall else 0
                results_system.record_assessment_result(
                    email=email,
                    assessment_type="ielts_writing",
                    assessment_name=f"IELTS Writing Task {task}",
                    score=score_pct,
                    total_questions=1,
                    correct_answers=1 if overall >= 6 else 0,
                    details={
                        "overall_band": overall,
                        "task_achievement_or_response": scored["task_achievement_or_response"],
                        "coherence_cohesion": scored["coherence_cohesion"],
                        "lexical_resource": scored["lexical_resource"],
                        "grammatical_range_accuracy": scored["grammatical_range_accuracy"],
                        "word_count": word_count,
                        "task": task,
                        "prompt_text": prompt_text[:500],
                    },
                )
                scored["persisted"] = True
            except Exception as e:
                logger.warning(f"IELTS writing result persist failed: {e}")
                scored["persisted"] = False

        return scored


    # ============================================================
    # SPEAKING (Session N4)
    # ============================================================

    SPEAKING_PARTS = {
        1: {
            "name": "Introduction & Interview",
            "duration_min": 4,
            "description": "The examiner asks general questions about yourself, your home, work, studies, and interests.",
        },
        2: {
            "name": "Long Turn",
            "duration_min": 4,
            "description": "You receive a cue card with a topic. You get 1 minute to prepare, then speak for 1-2 minutes.",
        },
        3: {
            "name": "Discussion",
            "duration_min": 5,
            "description": "The examiner asks more abstract questions related to the Part 2 topic.",
        },
    }

    def generate_speaking_prompt(self, topic: Optional[str] = None) -> Dict:
        """Generate a full 3-part Speaking session.

        Returns a dict with prompts for Part 1, 2, and 3.
        """
        topic_line = f"Overall theme: {topic}." if topic else "Choose a fresh, general IELTS-appropriate theme."
        prompt = (
            f"You are a certified IELTS Speaking examiner creating a full 3-part speaking test.\n"
            f"{topic_line}\n\n"
            "Produce ONLY valid JSON in this exact shape:\n"
            "{\n"
            '  "topic": "...",\n'
            '  "part1_questions": ["...", "...", "..."],\n'
            '  "part2": {\n'
            '    "cue_card": "Describe ...",\n'
            '    "bullet_points": ["...", "...", "...", "..."]\n'
            "  },\n"
            '  "part3_questions": ["...", "...", "..."]\n'
            "}\n\n"
            "Requirements:\n"
            "- Part 1: 3 general, personal questions (home, work, hobbies, daily life).\n"
            "- Part 2: 1 cue card with exactly 4 bullet points.\n"
            "- Part 3: 3 abstract questions related to the Part 2 topic.\n"
            "- Everything must be appropriate for an IELTS Academic candidate.\n"
            "- NO markdown, NO prose outside JSON."
        )

        parsed = self._ai_json(prompt, max_tokens=800, temperature=0.7)
        if not parsed:
            # Fallback if AI fails
            parsed = {
                "topic": topic or "Daily Life",
                "part1_questions": [
                    "Where are you from?",
                    "Do you work or are you a student?",
                    "What do you like to do in your free time?",
                ],
                "part2": {
                    "cue_card": "Describe a memorable journey you have taken.",
                    "bullet_points": [
                        "Where you went",
                        "Who you went with",
                        "What you did there",
                        "Why it was memorable",
                    ],
                },
                "part3_questions": [
                    "Why do people enjoy travelling to new places?",
                    "How has travel changed in your country over the past 20 years?",
                    "Do you think travel will become more or less common in the future?",
                ],
            }

        parsed["prompt_id"] = f"IELTS-SPK-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        parsed["parts"] = self.SPEAKING_PARTS
        return {"status": "success", "session": parsed}

    def transcribe_audio(self, audio_bytes: bytes, filename: str = "audio.webm") -> Dict:
        """Transcribe audio via OpenAI Whisper.

        audio_bytes: raw bytes from the browser's MediaRecorder.
        filename: original filename (extension matters — .webm, .m4a, .ogg).
        """
        if not self.openai_api_key:
            return {"status": "error", "message": "OpenAI key not configured"}

        try:
            import openai as _openai
            import tempfile
            client = _openai.OpenAI(api_key=self.openai_api_key)
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1] or ".webm") as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            try:
                with open(tmp_path, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text",
                    )
                return {"status": "success", "transcript": str(transcript).strip()}
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Whisper transcription failed: {e}")
            return {"status": "error", "message": f"transcription failed: {e}"}

    def evaluate_speaking(self, responses: List[Dict], topic: str = "") -> Dict:
        """Score a full Speaking session on the 4 official IELTS criteria.

        responses: [
            {"part": 1, "question": "...", "transcript": "..."},
            {"part": 2, "question": "<cue card>", "transcript": "..."},
            {"part": 3, "question": "...", "transcript": "..."},
            ...
        ]
        """
        if not responses:
            return {"status": "error", "message": "No responses to evaluate"}

        # Build transcript summary
        summary_lines = []
        for r in responses:
            part = r.get("part", "?")
            q = r.get("question", "")[:120]
            t = r.get("transcript", "")
            summary_lines.append(f"[Part {part}] Q: {q}\nAnswer: {t}")
        summary = "\n\n".join(summary_lines)

        prompt = (
            "You are a certified IELTS Speaking examiner. Score the candidate's "
            "performance on the 4 official IELTS Speaking criteria.\n\n"
            f"Overall topic: {topic or 'not specified'}\n\n"
            f"Transcribed responses:\n{summary}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "fluency_coherence": 0.0,\n'
            '  "lexical_resource": 0.0,\n'
            '  "grammatical_range": 0.0,\n'
            '  "pronunciation": 0.0,\n'
            '  "overall_band": 0.0,\n'
            '  "feedback": "3-5 sentences of specific, constructive feedback."\n'
            "}\n\n"
            "Bands are 0-9 in 0.5 increments. Pronunciation is estimated from "
            "transcription confidence signals (may be less reliable than a "
            "live examiner). Be honest — most candidates land 5.0-7.0."
        )

        parsed = self._ai_json(prompt, max_tokens=600, temperature=0.3)

        if not parsed:
            return {"status": "error", "message": "AI scoring unavailable"}

        # Compute overall if AI didn't
        try:
            subs = [
                float(parsed.get("fluency_coherence", 0)),
                float(parsed.get("lexical_resource", 0)),
                float(parsed.get("grammatical_range", 0)),
                float(parsed.get("pronunciation", 0)),
            ]
            avg = sum(subs) / 4
            parsed["overall_band"] = round(avg * 2) / 2  # round to nearest 0.5
        except Exception:
            pass

        # Persist (non-fatal — email may be None for anonymous sessions)
        try:
            from results_system import results_system
            results_system.record_assessment_result(
                email="anon@charvak.local",
                assessment_type="ielts_speaking",
                assessment_name=f"IELTS Speaking ({topic or 'General'})",
                score=parsed.get("overall_band", 0),
                total_questions=len(responses),
                correct_answers=0,

                details={"sub_bands": {
                    "fluency_coherence": parsed.get("fluency_coherence"),
                    "lexical_resource": parsed.get("lexical_resource"),
                    "grammatical_range": parsed.get("grammatical_range"),
                    "pronunciation": parsed.get("pronunciation"),
                }, "feedback": parsed.get("feedback", "")},
            )
        except Exception as e:
            logger.warning(f"IELTS speaking persist failed: {e}")

        return {"status": "success", "evaluation": parsed, "response_count": len(responses)}
ielts_engine = IELTSEngine()
