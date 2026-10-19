"""
Charvak Interview Prep Engine
AI-powered interview preparation with real AI scoring and credit integration.
Database-backed: charvak_interview_sessions, charvak_interview_answers.
"""
import os
import json
import logging
import secrets
import requests
from datetime import datetime
from typing import Dict, List, Optional
from global_config import OPENAI_MODEL

logger = logging.getLogger("charvakit.interviewprep")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
CREDITS_PER_SESSION = 8
QUESTIONS_PER_SESSION = int(os.getenv("INTERVIEW_QUESTIONS_PER_SESSION", "8"))


class InterviewPrepEngine:
    """Handles interview preparation with real AI evaluation."""

    def __init__(self):
        self._ensure_tables()
        logger.info(f"Interview Prep Engine ready (AI: {'ENABLED' if OPENAI_API_KEY else 'DISABLED'})")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_interview_sessions (
                    session_id TEXT PRIMARY KEY,
                    candidate_email TEXT NOT NULL,
                    role TEXT NOT NULL,
                    difficulty TEXT DEFAULT 'Intermediate',
                    credits_charged INTEGER DEFAULT 0,
                    total_score INTEGER DEFAULT 0,
                    max_score INTEGER DEFAULT 0,
                    questions_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'in_progress',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_interview_answers (
                    answer_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    question_num INTEGER NOT NULL,
                    question_text TEXT NOT NULL,
                    category TEXT,
                    user_answer TEXT,
                    ai_score INTEGER,
                    ai_feedback TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                ALTER TABLE charvak_interview_sessions
                    ADD COLUMN IF NOT EXISTS mode TEXT DEFAULT 'static'
            """)
            cur.execute("""
                ALTER TABLE charvak_interview_sessions
                    ADD COLUMN IF NOT EXISTS turn_count INTEGER DEFAULT 0
            """)
            cur.execute("""
                ALTER TABLE charvak_interview_sessions
                    ADD COLUMN IF NOT EXISTS max_turns INTEGER DEFAULT 12
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Interview tables init failed: {e}")

    def _call_openai(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> Optional[Dict]:
        """Call OpenAI and parse JSON response."""
        if not OPENAI_API_KEY:
            return None
        try:
            from openai_compat import build_payload
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=build_payload(OPENAI_MODEL, [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}], max_tokens=max_tokens, temperature=0.7, json_mode=True),
                timeout=30
            )
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            return None

    def _generate_questions(self, role: str, difficulty: str) -> List[Dict]:
        """AI generates role-specific interview questions."""
        system_prompt = "You are an expert technical interviewer. Generate realistic interview questions. Return JSON only."

        user_prompt = f"""Generate {QUESTIONS_PER_SESSION} interview questions for a "{role}" position at {difficulty} level.

Return JSON with this exact structure:
{{
  "questions": [
    {{"question": "...", "category": "Technical"}},
    {{"question": "...", "category": "Behavioral"}}
  ]
}}

Mix: 60% technical, 30% behavioral, 10% situational.
Make each question specific and role-relevant. No generic questions."""

        result = self._call_openai(system_prompt, user_prompt)

        if result and result.get("questions"):
            return result["questions"][:QUESTIONS_PER_SESSION]

        # Fallback questions
        return [
            {"question": f"Tell me about your experience relevant to the {role} role.", "category": "Behavioral"},
            {"question": f"What are the key technical skills required for a {role}?", "category": "Technical"},
            {"question": "Describe a challenging project you worked on and how you handled it.", "category": "Behavioral"},
            {"question": f"How do you stay updated with trends in {role}?", "category": "Situational"},
            {"question": "Tell me about a time you failed and what you learned.", "category": "Behavioral"},
        ]

    def _score_answer(self, question: str, answer: str, role: str, difficulty: str) -> Dict:
        """AI evaluates the user's answer and returns score + feedback."""
        system_prompt = "You are an expert interview coach. Evaluate answers objectively. Return JSON only."

        user_prompt = f"""Evaluate this interview answer.

Role: {role}
Difficulty: {difficulty}
Question: {question}
Candidate's Answer: {answer}

Score the answer 0-100 based on:
- Relevance to the question (30%)
- Depth and specificity (30%)
- Communication clarity (20%)
- Confidence and structure (20%)

Return JSON:
{{
  "score": 0-100,
  "feedback": "3-4 sentences of specific, actionable feedback",
  "strengths": ["point 1", "point 2"],
  "improvements": ["point 1", "point 2"]
}}"""

        result = self._call_openai(system_prompt, user_prompt, max_tokens=800)

        if result and "score" in result:
            return result

        # Fallback: word-count scoring
        word_count = len(answer.split())
        score = min(word_count * 4, 85) if word_count > 3 else 20
        return {
            "score": score,
            "feedback": "Answer recorded. AI evaluation unavailable at the moment.",
            "strengths": [],
            "improvements": ["Provide more specific examples"]
        }

    def start_session(self, data: Dict) -> Dict:
        """
        Start a new interview prep session.
        Charges credits, generates AI questions, creates DB session.
        """
        email = (data.get("candidate_email") or "").strip().lower()
        role = (data.get("role") or data.get("stack") or "Software Developer").strip()
        difficulty = (data.get("difficulty") or "Intermediate").strip()

        if not email:
            return {"status": "error", "message": "Email required"}

        # Check + deduct credits
        try:
            from ai_credit_engine import ai_credit_engine
            credit_result = ai_credit_engine.check_and_deduct(email, "interview_prep")
            if credit_result.get("status") != "success":
                return {
                    "status": "error",
                    "message": credit_result.get("message", "Insufficient credits"),
                    "credits_needed": CREDITS_PER_SESSION,
                    "top_up_url": "/pricing"
                }
        except Exception as e:
            logger.error(f"Credit check failed: {e}")
            return {"status": "error", "message": "Credit system error"}

        # Generate AI questions
        questions = self._generate_questions(role, difficulty)

        session_id = f"IP-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_interview_sessions
                    (session_id, candidate_email, role, difficulty, credits_charged,
                     questions_count, max_score, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'in_progress')
            """, (
                session_id, email, role, difficulty, CREDITS_PER_SESSION,
                len(questions), len(questions) * 100
            ))

            # Store questions as empty answers (question text pre-loaded)
            for i, q in enumerate(questions, 1):
                answer_id = f"ANS-{secrets.token_hex(4).upper()}"
                cur.execute("""
                    INSERT INTO charvak_interview_answers
                        (answer_id, session_id, question_num, question_text, category)
                    VALUES (%s, %s, %s, %s, %s)
                """, (answer_id, session_id, i, q.get("question", ""), q.get("category", "General")))

            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Session creation failed: {e}")
            return {"status": "error", "message": str(e)}

        logger.info(f"Session started: {session_id} for {email} ({role}, {difficulty})")

        return {
            "status": "success",
            "session_id": session_id,
            "questions_count": len(questions),
            "credits_charged": CREDITS_PER_SESSION,
            "message": f"Session started! {CREDITS_PER_SESSION} credits charged."
        }

    def get_session(self, session_id: str) -> Dict:
        """Get full session state including questions + answers."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT session_id, candidate_email, role, difficulty, credits_charged,
                       total_score, max_score, questions_count, status, started_at, completed_at
                FROM charvak_interview_sessions WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Session not found"}

            session = {
                "session_id": row[0],
                "candidate_email": row[1],
                "role": row[2],
                "difficulty": row[3],
                "credits_charged": row[4],
                "total_score": row[5],
                "max_score": row[6],
                "questions_count": row[7],
                "status": row[8],
                "started_at": row[9].isoformat() if row[9] else None,
                "completed_at": row[10].isoformat() if row[10] else None,
            }

            cur.execute("""
                SELECT answer_id, question_num, question_text, category,
                       user_answer, ai_score, ai_feedback
                FROM charvak_interview_answers
                WHERE session_id = %s ORDER BY question_num
            """, (session_id,))
            answers = []
            for r in cur.fetchall():
                answers.append({
                    "answer_id": r[0],
                    "question_num": r[1],
                    "question_text": r[2],
                    "category": r[3],
                    "user_answer": r[4],
                    "ai_score": r[5],
                    "ai_feedback": r[6],
                })

            session["answers"] = answers

            # Determine next unanswered question
            next_q = None
            for a in answers:
                if a["user_answer"] is None:
                    next_q = a
                    break
            session["next_question"] = next_q

            cur.close()
            conn.close()
            return {"status": "success", "session": session}
        except Exception as e:
            logger.error(f"get_session failed: {e}")
            return {"status": "error", "message": str(e)}

    def submit_answer(self, data: Dict) -> Dict:
        """Submit answer for a question. AI scores it. Returns feedback + next question."""
        session_id = data.get("session_id")
        answer_id = data.get("answer_id")
        user_answer = (data.get("answer") or "").strip()

        if not session_id or not answer_id or not user_answer:
            return {"status": "error", "message": "session_id, answer_id, and answer required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Get the answer row + session info
            cur.execute("""
                SELECT a.question_text, s.role, s.difficulty
                FROM charvak_interview_answers a
                JOIN charvak_interview_sessions s ON a.session_id = s.session_id
                WHERE a.answer_id = %s AND a.session_id = %s
            """, (answer_id, session_id))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Question not found"}

            question_text, role, difficulty = row

            # AI scoring
            evaluation = self._score_answer(question_text, user_answer, role, difficulty)
            score = evaluation.get("score", 0)
            feedback = evaluation.get("feedback", "")
            strengths = evaluation.get("strengths", [])
            improvements = evaluation.get("improvements", [])

            # Build feedback JSON
            feedback_full = json.dumps({
                "text": feedback,
                "strengths": strengths,
                "improvements": improvements
            })

            cur.execute("""
                UPDATE charvak_interview_answers
                SET user_answer = %s, ai_score = %s, ai_feedback = %s
                WHERE answer_id = %s
            """, (user_answer, score, feedback_full, answer_id))

            # Update session total score
            cur.execute("""
                UPDATE charvak_interview_sessions
                SET total_score = total_score + %s
                WHERE session_id = %s
            """, (score, session_id))

            # Find next unanswered question
            cur.execute("""
                SELECT answer_id, question_num, question_text, category
                FROM charvak_interview_answers
                WHERE session_id = %s AND user_answer IS NULL
                ORDER BY question_num LIMIT 1
            """, (session_id,))
            next_row = cur.fetchone()

            # If no more unanswered → complete session
            completed = next_row is None
            if completed:
                cur.execute("""
                    UPDATE charvak_interview_sessions
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (session_id,))

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "score": score,
                "feedback": feedback,
                "strengths": strengths,
                "improvements": improvements,
                "next_question": {
                    "answer_id": next_row[0],
                    "question_num": next_row[1],
                    "question_text": next_row[2],
                    "category": next_row[3],
                } if next_row else None,
                "completed": completed
            }
        except Exception as e:
            logger.error(f"submit_answer failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # Session 65a: Conversational interview mode
    # ============================================================

    def _generate_next_turn(self, role: str, difficulty: str,
                             previous_question: str, previous_answer: str,
                             turn_num: int, max_turns: int) -> Dict:
        """Generate the next question — either a follow-up or a new topic."""
        if not OPENAI_API_KEY:
            return {"question": f"Tell me about your experience with {role}.", "is_followup": False, "category": "General"}

        system_prompt = f"""You are a senior technical interviewer conducting a {role} interview at {difficulty} level.

CONTEXT: You are on turn {turn_num} of a maximum {max_turns}-turn interview.

DECISION RULES:
- If the previous answer was vague, shallow, or avoided the question: ask ONE probing follow-up.
- If the answer was strong or complete: move to a new topic at {difficulty} level.
- If turn_num is a multiple of 3 (turn 3, 6, 9): FORCE a new topic to prevent rabbit-holing.
- NEVER ask more than 2 follow-ups in a row on the same topic.

TONE: Professional, warm, curious. Like a good interviewer, not a robot.

Output JSON ONLY:
{{"question": "<the question text>", "is_followup": true_or_false, "category": "<topic>"}}"""

        user_prompt = f"""Previous question: {previous_question}

Candidate's answer: {previous_answer}

Generate the next turn."""

        result = self._call_openai(system_prompt, user_prompt, max_tokens=400)
        if not result or "question" not in result:
            return {"question": f"Can you share another example from your {role} experience?", "is_followup": False, "category": "General"}

        return {
            "question": result.get("question", f"Tell me more about your {role} experience."),
            "is_followup": bool(result.get("is_followup", False)),
            "category": result.get("category", "General"),
        }

    def start_conversational(self, data: Dict) -> Dict:
        """Start a conversational interview. First question generated, credits NOT yet deducted."""
        email = (data.get("candidate_email") or "").strip().lower()
        role = (data.get("role") or "Software Developer").strip()
        difficulty = (data.get("difficulty") or "Intermediate").strip()
        max_turns = int(data.get("max_turns") or 12)

        if not email:
            return {"status": "error", "message": "Email required"}

        # Pre-check credit balance (no deduction yet)
        try:
            from ai_credit_engine import ai_credit_engine
            credits_info = ai_credit_engine.get_user_credits(email)
            if credits_info.get("status") == "error":
                return {"status": "error", "message": credits_info.get("message", "Credit check failed")}
            remaining = credits_info.get("credits_remaining", 0)
            if remaining < CREDITS_PER_SESSION and email not in (credits_info.get("admin_emails") or []):
                # Non-admin without enough credits
                from database import db
                user = db.get_user_by_email(email)
                from main import ADMIN_EMAILS as _admin_set
                if email not in _admin_set:
                    return {
                        "status": "error",
                        "message": "Insufficient credits",
                        "credits_needed": CREDITS_PER_SESSION,
                        "top_up_url": "/pricing"
                    }
        except Exception as e:
            logger.error(f"Credit pre-check failed: {e}")

        # Generate FIRST question only (no batch)
        try:
            first_q = self._generate_questions(role, difficulty)
            first_question = first_q[0] if first_q else {"question": f"Tell me about your {role} experience.", "category": "General"}
        except Exception as e:
            logger.error(f"First question gen failed: {e}")
            return {"status": "error", "message": "AI generation failed"}

        # Deduct credits NOW (after AI success)
        try:
            from ai_credit_engine import ai_credit_engine
            credit_result = ai_credit_engine.check_and_deduct(email, "interview_prep")
            if credit_result.get("status") != "success":
                return {
                    "status": "error",
                    "message": credit_result.get("message", "Insufficient credits"),
                    "credits_needed": CREDITS_PER_SESSION,
                    "top_up_url": "/pricing"
                }
        except Exception as e:
            logger.error(f"Credit deduction failed: {e}")
            return {"status": "error", "message": "Credit system error"}

        session_id = f"IPC-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_interview_sessions
                    (session_id, candidate_email, role, difficulty, credits_charged,
                     questions_count, max_score, status, mode, turn_count, max_turns)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'in_progress', 'conversational', 1, %s)
            """, (
                session_id, email, role, difficulty, CREDITS_PER_SESSION,
                1, max_turns * 100, max_turns
            ))

            answer_id = f"ANS-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_interview_answers
                    (answer_id, session_id, question_num, question_text, category)
                VALUES (%s, %s, 1, %s, %s)
            """, (answer_id, session_id, first_question.get("question", ""), first_question.get("category", "General")))

            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Conversational session creation failed: {e}")
            return {"status": "error", "message": str(e)}

        logger.info(f"Conversational session started: {session_id} for {email} ({role}, {difficulty}, max_turns={max_turns})")

        return {
            "status": "success",
            "session_id": session_id,
            "mode": "conversational",
            "credits_charged": CREDITS_PER_SESSION,
            "turn": 1,
            "max_turns": max_turns,
            "first_question": {
                "answer_id": answer_id,
                "question_num": 1,
                "question_text": first_question.get("question", ""),
                "category": first_question.get("category", "General"),
            },
            "message": f"Session started! {CREDITS_PER_SESSION} credits charged."
        }

    def submit_turn(self, data: Dict) -> Dict:
        """Submit answer for current turn. AI scores it, generates next question."""
        session_id = data.get("session_id")
        answer_id = data.get("answer_id")
        user_answer = (data.get("answer") or "").strip()

        if not session_id or not answer_id or not user_answer:
            return {"status": "error", "message": "session_id, answer_id, answer required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Get session + current answer row
            cur.execute("""
                SELECT a.question_text, s.role, s.difficulty, s.turn_count, s.max_turns, s.mode
                FROM charvak_interview_answers a
                JOIN charvak_interview_sessions s ON a.session_id = s.session_id
                WHERE a.answer_id = %s AND a.session_id = %s
            """, (answer_id, session_id))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Answer row not found"}
            question_text, role, difficulty, turn_count, max_turns, mode = row

            if mode != "conversational":
                cur.close(); conn.close()
                return {"status": "error", "message": "Not a conversational session"}

            # Score the answer
            evaluation = self._score_answer(question_text, user_answer, role, difficulty)
            score = evaluation.get("score", 0)
            feedback = evaluation.get("feedback", "")
            strengths = evaluation.get("strengths", [])
            improvements = evaluation.get("improvements", [])

            feedback_full = json.dumps({
                "text": feedback,
                "strengths": strengths,
                "improvements": improvements
            })

            cur.execute("""
                UPDATE charvak_interview_answers
                SET user_answer = %s, ai_score = %s, ai_feedback = %s
                WHERE answer_id = %s
            """, (user_answer, score, feedback_full, answer_id))

            cur.execute("""
                UPDATE charvak_interview_sessions
                SET total_score = total_score + %s
                WHERE session_id = %s
            """, (score, session_id))

            # Check if this is the last turn
            done = turn_count >= max_turns

            next_question = None
            next_answer_id = None
            if not done:
                # Generate next question
                try:
                    nq = self._generate_next_turn(role, difficulty, question_text, user_answer, turn_count + 1, max_turns)
                except Exception as e:
                    logger.error(f"Next turn gen failed: {e}")
                    nq = {"question": f"Can you give another example from your {role} experience?", "is_followup": False, "category": "General"}

                next_answer_id = f"ANS-{secrets.token_hex(4).upper()}"
                cur.execute("""
                    INSERT INTO charvak_interview_answers
                        (answer_id, session_id, question_num, question_text, category)
                    VALUES (%s, %s, %s, %s, %s)
                """, (next_answer_id, session_id, turn_count + 1, nq.get("question", ""), nq.get("category", "General")))

                cur.execute("""
                    UPDATE charvak_interview_sessions
                    SET turn_count = turn_count + 1, questions_count = questions_count + 1
                    WHERE session_id = %s
                """, (session_id,))

                next_question = {
                    "answer_id": next_answer_id,
                    "question_num": turn_count + 1,
                    "question_text": nq.get("question", ""),
                    "category": nq.get("category", "General"),
                    "is_followup": nq.get("is_followup", False),
                }
            else:
                # Mark session complete
                cur.execute("""
                    UPDATE charvak_interview_sessions
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE session_id = %s
                """, (session_id,))

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "score": score,
                "feedback": feedback,
                "strengths": strengths,
                "improvements": improvements,
                "next_question": next_question,
                "done": done,
                "turn": turn_count,
                "max_turns": max_turns,
            }
        except Exception as e:
            logger.error(f"submit_turn failed: {e}")
            return {"status": "error", "message": str(e)}

    def complete_conversational(self, session_id: str) -> Dict:
        """Force-complete a conversational session (user clicked End interview)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT total_score, max_score, questions_count, candidate_email, role, difficulty
                FROM charvak_interview_sessions
                WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found"}
            total_score, max_score, questions_count, email, role, difficulty = row

            cur.execute("""
                UPDATE charvak_interview_sessions
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (session_id,))

            cur.execute("""
                SELECT question_num, question_text, user_answer, ai_score, ai_feedback
                FROM charvak_interview_answers
                WHERE session_id = %s AND user_answer IS NOT NULL
                ORDER BY question_num
            """, (session_id,))
            answers = cur.fetchall()
            transcript = [
                {
                    "question_num": a[0],
                    "question_text": a[1],
                    "user_answer": a[2],
                    "ai_score": a[3],
                    "ai_feedback": json.loads(a[4]) if a[4] else {},
                }
                for a in answers
            ]

            conn.commit()
            cur.close()
            conn.close()

            answered_count = len(transcript)
            avg_score = round(total_score / answered_count, 1) if answered_count > 0 else 0

            return {
                "status": "success",
                "overall_score": avg_score,
                "total_score": total_score,
                "max_score": max_score,
                "questions_answered": answered_count,
                "transcript": transcript,
            }
        except Exception as e:
            logger.error(f"complete_conversational failed: {e}")
            return {"status": "error", "message": str(e)}


    def get_dashboard(self, email: str) -> Dict:
        """Get user's interview prep history."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT session_id, role, difficulty, total_score, max_score,
                       questions_count, status, started_at, completed_at
                FROM charvak_interview_sessions
                WHERE candidate_email = %s
                ORDER BY started_at DESC LIMIT 50
            """, (email,))
            sessions = []
            for r in cur.fetchall():
                sessions.append({
                    "session_id": r[0],
                    "role": r[1],
                    "difficulty": r[2],
                    "total_score": r[3],
                    "max_score": r[4],
                    "questions_count": r[5],
                    "status": r[6],
                    "started_at": r[7].isoformat() if r[7] else None,
                    "completed_at": r[8].isoformat() if r[8] else None,
                })

            completed = [s for s in sessions if s["status"] == "completed"]
            avg_score = round(sum(s["total_score"] for s in completed) / len(completed), 1) if completed else 0

            cur.close()
            conn.close()

            return {
                "status": "success",
                "sessions": sessions,
                "count": len(sessions),
                "completed_count": len(completed),
                "average_score": avg_score
            }
        except Exception as e:
            logger.error(f"get_dashboard failed: {e}")
            return {"status": "error", "sessions": [], "count": 0, "average_score": 0}


interview_prep_engine = InterviewPrepEngine()
