"""
Charvak CBT Versant System — DB-backed (Session V3)
Audio recording, Whisper transcription, AI band scoring.

Replaces in-memory session/answer stores with Postgres tables:
  charvak_versant_sessions  (session lifecycle + score)
  charvak_versant_answers   (per-question audio transcript / text)
"""
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.cbt_versant")


class CBTVersantSystem:
    """Versant English Assessment — 6 sections, DB-backed."""

    # ============================================================
    # SECTION DESIGN (kept from old engine; verified against real Versant)
    # ============================================================
    SECTIONS = {
        "read_aloud": {
            "name": "Read Aloud",
            "input": "audio_recording",
            "questions": 8,
            "time_per_question": 15,
            "instruction": "Read the sentence aloud. Click Record, read, then click Stop.",
            "audio_prompt": False,
        },
        "repeats": {
            "name": "Repeats",
            "input": "audio_playback_then_record",
            "questions": 16,
            "time_per_question": 10,
            "instruction": "Listen to the audio, then repeat exactly what you heard.",
            "audio_prompt": True,
        },
        "sentence_builds": {
            "name": "Sentence Builds",
            "input": "rearrangement",
            "questions": 10,
            "time_per_question": 15,
            "instruction": "Rearrange the words to form a correct sentence.",
            "audio_prompt": False,
        },
        "conversations": {
            "name": "Conversations",
            "input": "audio_recording",
            "questions": 10,
            "time_per_question": 20,
            "instruction": "Listen to the question and record your spoken answer.",
            "audio_prompt": True,
        },
        "story_retelling": {
            "name": "Story Retelling",
            "input": "read_then_record",
            "questions": 3,
            "time_per_question": 30,
            "instruction": "Read the passage, then retell it in your own words.",
            "audio_prompt": False,
        },
        "summary_opinion": {
            "name": "Summary & Opinion",
            "input": "typed_response",
            "questions": 1,
            "time_per_question": 1080,
            "instruction": "Write a summary and your opinion on the topic.",
            "audio_prompt": False,
        },
    }

    SECTION_ORDER = ["read_aloud", "repeats", "sentence_builds",
                     "conversations", "story_retelling", "summary_opinion"]

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        logger.info("CBT Versant System ready (DB-backed) | AI: %s",
                    "ENABLED" if self.openai_api_key else "DISABLED")

    # ============================================================
    # INFO
    # ============================================================
    def get_section_design(self, section_id: str) -> Dict:
        return self.SECTIONS.get(section_id, {"error": "Section not found"})

    def get_section_questions(self, section_id: str) -> Dict:
        section = self.get_section_design(section_id)
        return {"status": "success", "section": section,
                "questions": section.get("prompts", [])}

    def get_all_sections(self) -> Dict:
        return {
            "status": "success",
            "sections": [
                {"id": sid, **self.SECTIONS[sid]}
                for sid in self.SECTION_ORDER
            ],
            "total_questions": sum(self.SECTIONS[s]["questions"] for s in self.SECTION_ORDER),
        }

    # ============================================================
    # SESSION LIFECYCLE
    # ============================================================
    def create_session(self, email: str) -> Dict:
        """Create a new Versant session and generate all questions via ai_versant.

        Persists session to charvak_versant_sessions.
        Returns the full session dict with questions in details_json.
        """
        if not email:
            return {"status": "error", "message": "email required"}

        # Generate questions via ai_versant (already exists)
        try:
            from ai_versant import ai_versant
            gen = ai_versant.start_user_session(email)
            questions = gen.get("session", {}).get("questions", {}) or {}
        except Exception as e:
            logger.error(f"ai_versant generation failed: {e}")
            return {"status": "error", "message": f"question generation failed: {e}"}

        session_id = f"VERSANT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"

        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_versant_sessions
                    (session_id, email, status, details_json)
                VALUES (%s, %s, 'in_progress', %s::jsonb)
            """, (session_id, email, json.dumps({"questions": questions})))
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.error(f"create_session DB insert failed: {e}")
            return {"status": "error", "message": "could not create session"}

        return {
            "status": "success",
            "session_id": session_id,
            "email": email,
            "sections": self.SECTION_ORDER,
            "section_design": self.SECTIONS,
            "questions": questions,
            "started_at": datetime.now().isoformat(),
        }

    def get_session(self, session_id: str) -> Dict:
        """Load session state + questions from DB."""
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT session_id, email, status, started_at, completed_at,
                       overall_score, details_json
                FROM charvak_versant_sessions
                WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.error(f"get_session failed: {e}")
            return {"status": "error", "message": str(e)}

        if not row:
            return {"status": "error", "message": "session not found"}

        details = row[6] if isinstance(row[6], dict) else json.loads(row[6] or "{}")

        return {
            "status": "success",
            "session_id": row[0],
            "email": row[1],
            "session_status": row[2],   # renamed: was duplicated 'status' key
            "started_at": row[3].isoformat() if row[3] else None,
            "completed_at": row[4].isoformat() if row[4] else None,
            "overall_score": float(row[5]) if row[5] is not None else None,
            "details": details,
            "questions": details.get("questions", {}),
            "section_design": self.SECTIONS,
        }

    # ============================================================
    # ANSWER SAVING
    # ============================================================
    def save_text_answer(self, session_id: str, section_id: str,
                         question_id: str, question_text: str,
                         answer_text: str) -> Dict:
        """Save a typed answer (used by Summary & Opinion)."""
        if not session_id or not answer_text:
            return {"status": "error", "message": "session_id and answer_text required"}
        return self._upsert_answer(session_id, section_id, question_id,
                                   question_text, answer_text=answer_text)

    def save_audio_answer(self, session_id: str, section_id: str,
                          question_id: str, question_text: str,
                          audio_bytes: bytes, filename: str = "answer.webm") -> Dict:
        """Transcribe audio via Whisper, then save transcript."""
        if not session_id:
            return {"status": "error", "message": "session_id required"}
        if not audio_bytes:
            return {"status": "error", "message": "empty audio"}

        transcript = self._transcribe(audio_bytes, filename)
        if transcript is None:
            return {"status": "error", "message": "transcription failed"}

        return self._upsert_answer(session_id, section_id, question_id,
                                   question_text, transcript=transcript)

    # V7b — Known Whisper hallucination patterns (Youtube spam, silence)
    _HALLUCINATION_PATTERNS = [
        "チャンネル登録をお願いいたします",
        "ご視聴ありがとうございました",
        "チャンネル登録",
        "おやすみなさい",
        "Please subscribe",
        "Share this video",
        "Subscribe to my channel",
        "Thanks for watching",
        "Thank you for watching",
        "字幕",
        "Amara.org",
    ]

    def _clean_transcript(self, text: str) -> str:
        """Filter Whisper hallucinations. Returns cleaned text."""
        if not text:
            return ""
        t = text.strip()
        # Empty or punctuation-only
        if not any(c.isalnum() for c in t):
            return ""
        # Known hallucination patterns
        for pat in self._HALLUCINATION_PATTERNS:
            if pat.lower() in t.lower():
                logger.info(f"Filtered hallucination: {t[:80]}")
                return ""
        # Too short to be a real answer (< 2 real chars)
        if len(t) < 2:
            return ""
        return t

    def _transcribe(self, audio_bytes: bytes, filename: str) -> Optional[str]:
        """Call Whisper. Returns transcript or None on error.

        Enforces English language, filters hallucinated captions.
        """
        if not self.openai_api_key:
            logger.warning("OpenAI key missing — cannot transcribe")
            return None
        # Skip tiny audio (likely empty recording)
        if len(audio_bytes) < 2000:  # < ~2KB, likely silence
            logger.info(f"Skipping tiny audio: {len(audio_bytes)} bytes")
            return ""
        try:
            import openai as _openai
            import tempfile
            client = _openai.OpenAI(api_key=self.openai_api_key)
            suffix = os.path.splitext(filename)[1] or ".webm"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            try:
                with open(tmp_path, "rb") as audio_file:
                    result = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text",
                        language="en",
                    )
                cleaned = self._clean_transcript(str(result))
                return cleaned
            finally:
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Whisper failed: {e}")
            return None

    def _upsert_answer(self, session_id, section_id, question_id,
                       question_text, answer_text=None, transcript=None) -> Dict:
        """Insert-or-update one answer row."""
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_versant_answers
                    (session_id, section_id, question_id, question_text,
                     answer_text, transcript)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, section_id, question_id)
                DO UPDATE SET
                    question_text = EXCLUDED.question_text,
                    answer_text   = COALESCE(EXCLUDED.answer_text,   charvak_versant_answers.answer_text),
                    transcript    = COALESCE(EXCLUDED.transcript,    charvak_versant_answers.transcript),
                    answered_at   = NOW()
                RETURNING answer_id
            """, (session_id, section_id, question_id, question_text,
                  answer_text, transcript))
            answer_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
            return {"status": "success", "answer_id": answer_id,
                    "saved": "text" if answer_text else "audio"}
        except Exception as e:
            logger.error(f"_upsert_answer failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # COMPLETE + SCORE
    # ============================================================
    def complete_session(self, session_id: str) -> Dict:
        """Aggregate all answers, score via AI, mark session completed."""
        # Load session + answers
        session = self.get_session(session_id)
        # V7a: get_session returns "status":"success" for the API; the
        # session's own state is now in "session_status".
        if session.get("status") != "success":
            return session

        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT section_id, question_id, question_text,
                       COALESCE(transcript, answer_text, '') AS content
                FROM charvak_versant_answers
                WHERE session_id = %s
                ORDER BY section_id, question_id
            """, (session_id,))
            rows = cur.fetchall()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.error(f"complete_session fetch failed: {e}")
            return {"status": "error", "message": "could not load answers"}

        if not rows:
            return {"status": "error", "message": "no answers submitted"}

        # Build scoring prompt
        summary_lines = []
        for section_id, qid, qtext, content in rows:
            summary_lines.append(
                f"[{section_id}] Q: {(qtext or '')[:100]}\nA: {content[:300]}"
            )
        summary = "\n\n".join(summary_lines)

        scores = self._score_versant(summary, len(rows))
        if scores is None:
            return {"status": "error", "message": "AI scoring unavailable"}

        # Persist results
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_versant_sessions
                SET status = 'completed',
                    completed_at = NOW(),
                    overall_score = %s,
                    details_json = details_json || %s::jsonb
                WHERE session_id = %s
            """, (scores.get("overall_score", 0),
                  json.dumps({"scoring": scores}),
                  session_id))
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.error(f"complete_session update failed: {e}")
            return {"status": "error", "message": "could not save score"}

        # Also persist to charvak_assessment_results for cross-test history
        try:
            from results_system import results_system
            results_system.record_assessment_result(
                email=session.get("email") or "anon@charvak.local",
                assessment_type="versant",
                assessment_name="Versant English Assessment",
                score=float(scores.get("overall_score", 0)),
                total_questions=len(rows),
                correct_answers=0,
                details={"scores": scores},
            )
        except Exception as e:
            logger.warning(f"Versant persist to assessment_results failed: {e}")

        return {"status": "success", "session_id": session_id, "scoring": scores}

    def _score_versant(self, summary: str, response_count: int) -> Optional[Dict]:
        """Call OpenAI to score on 5 Versant criteria."""
        if not self.openai_api_key:
            return None
        prompt = (
            "You are a certified Versant English Test examiner. Score the candidate's "
            "performance on the 5 official Versant criteria.\n\n"
            f"Candidate responses ({response_count} total):\n{summary[:6000]}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "overall_score": 0,\n'
            '  "pronunciation": 0,\n'
            '  "fluency": 0,\n'
            '  "vocabulary": 0,\n'
            '  "sentence_mastery": 0,\n'
            '  "coherence": 0,\n'
            '  "feedback": "3-5 sentences of specific, constructive feedback."\n'
            "}\n\n"
            "Scores are 20-80 (Versant scale). Be honest — most candidates land 30-60. "
            "Empty or nonsense answers should score 20."
        )
        try:
            import requests
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}",
                         "Content-Type": "application/json"},
                json={"model": "gpt-4o-mini",
                      "messages": [{"role": "user", "content": prompt}],
                      "temperature": 0.3,
                      "response_format": {"type": "json_object"}},
                timeout=45,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            # Clamp overall to 20-80
            try:
                ov = int(parsed.get("overall_score", 0) or 0)
                parsed["overall_score"] = max(20, min(80, ov))
            except Exception:
                parsed["overall_score"] = 20
            return parsed
        except Exception as e:
            logger.error(f"_score_versant failed: {e}")
            return None


cbt_versant = CBTVersantSystem()