"""
Interactive AI Tutor - Session 67a rebuild.
Persistent sessions + course context + openai_compat migration.
"""
import os
import json
import secrets
import logging
from datetime import datetime
from typing import Dict, Optional, List

from global_config import OPENAI_MODEL

logger = logging.getLogger("charvakit.ai_tutor")


class InteractiveTutor:
    """AI tutor with persistent sessions, course context, and multi-turn chat."""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self._ensure_tables()
        logger.info(f"Interactive AI Tutor ready (persistent) - OpenAI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")

    def _ensure_tables(self):
        """Self-healing DDL - create tables if they don't exist."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_tutor_sessions (
                    session_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL,
                    course_name TEXT NOT NULL,
                    enrollment_id TEXT,
                    week_num INTEGER,
                    topic TEXT,
                    user_level TEXT DEFAULT 'beginner',
                    turn_count INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'active',
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_tutor_messages (
                    message_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_tutor_sessions_email
                    ON charvak_tutor_sessions(email, started_at DESC)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_tutor_sessions_enrollment
                    ON charvak_tutor_sessions(enrollment_id)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_tutor_messages_session
                    ON charvak_tutor_messages(session_id, created_at)
            """)

            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Tutor tables init failed: {e}")

    def _load_course_context(self, enrollment_id: Optional[str], week_num: Optional[int]) -> Dict:
        """
        Load lesson content + curriculum outline for context injection.
        Returns {lesson_title, lesson_content, curriculum_outline, course_name}.
        Empty dict on any failure (graceful degradation).
        """
        if not enrollment_id:
            return {}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Load curriculum outline from enrollment
            cur.execute("""
                SELECT course_name, curriculum
                FROM charvak_enrollments
                WHERE enrollment_id = %s
            """, (enrollment_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {}
            course_name, curriculum_json = row

            # Extract lesson title from curriculum
            lesson_title = ""
            curriculum_outline = ""
            if curriculum_json:
                if isinstance(curriculum_json, dict):
                    curriculum = curriculum_json
                elif isinstance(curriculum_json, str):
                    try:
                        curriculum = json.loads(curriculum_json)
                    except Exception:
                        curriculum = {}
                else:
                    curriculum = {}

                # Build outline summary
                weeks = curriculum.get("weeks") or curriculum.get("curriculum") or []
                if isinstance(weeks, list):
                    outline_parts = []
                    for w in weeks[:15]:
                        if isinstance(w, dict):
                            wn = w.get("week") or w.get("week_num") or w.get("num") or "?"
                            wt = w.get("title") or w.get("topic") or ""
                            outline_parts.append(f"Week {wn}: {wt}")
                    curriculum_outline = "\n".join(outline_parts)

                    # Find current week's title
                    for w in weeks:
                        if isinstance(w, dict):
                            wn = w.get("week") or w.get("week_num") or w.get("num")
                            if week_num and wn == week_num:
                                lesson_title = w.get("title") or w.get("topic") or ""
                                break

            # Load current week's lesson content from charvak_course_lessons
            lesson_content = ""
            if week_num:
                cur.execute("""
                    SELECT topic, lesson_content
                    FROM charvak_course_lessons
                    WHERE enrollment_id = %s AND week_num = %s
                """, (enrollment_id, week_num))
                lesson_row = cur.fetchone()
                if lesson_row:
                    topic_val, content_val = lesson_row
                    if topic_val and not lesson_title:
                        lesson_title = topic_val
                    if content_val:
                        if isinstance(content_val, dict):
                            lesson_content = json.dumps(content_val, indent=2)[:3000]
                        elif isinstance(content_val, str):
                            lesson_content = content_val[:3000]
                        else:
                            lesson_content = str(content_val)[:3000]

            cur.close()
            conn.close()

            return {
                "course_name": course_name,
                "lesson_title": lesson_title,
                "lesson_content": lesson_content,
                "curriculum_outline": curriculum_outline,
            }
        except Exception as e:
            logger.warning(f"Course context load failed: {e}")
            return {}

    def _build_system_context(self, session: Dict, course_ctx: Dict) -> str:
        """Build system prompt from session + course context."""
        parts = [
            f"You are an AI tutor teaching {session.get('course_name', 'a course')} "
            f"to a {session.get('user_level', 'beginner')} student."
        ]

        if course_ctx.get("lesson_title"):
            parts.append(f"Current lesson (Week {session.get('week_num', '?')}): {course_ctx['lesson_title']}")

        if course_ctx.get("lesson_content"):
            parts.append(f"Lesson content:\n{course_ctx['lesson_content'][:2500]}")

        if course_ctx.get("curriculum_outline"):
            parts.append(f"Course outline:\n{course_ctx['curriculum_outline']}")

        parts.append(
            "Teach effectively: be concise, use examples tied to this lesson, "
            "and reference the specific content the student is studying."
        )

        return "\n\n".join(parts)

    def _call_ai(self, system_prompt: str, messages: List[Dict], max_tokens: int = 800,
                 temperature: float = 0.7) -> Optional[str]:
        """Call AI via openai_compat shim. Returns response text or None on failure."""
        if not self.openai_api_key:
            return None

        try:
            import requests
            from openai_compat import build_payload

            full_messages = [{"role": "system", "content": system_prompt}] + messages
            payload = build_payload(
                OPENAI_MODEL, full_messages,
                max_tokens=max_tokens, temperature=temperature, json_mode=False
            )

            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json=payload,
                timeout=20,
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Tutor AI call failed: {e}")
            return None

    def start_tutoring_session(self, email: str, course_name: str, topic: str,
                                user_level: str = "beginner",
                                enrollment_id: Optional[str] = None,
                                week_num: Optional[int] = None) -> Dict:
        """Start a persistent tutor session with course context."""
        if not email:
            return {"status": "error", "message": "Email required"}

        session_id = f"TUTOR-{secrets.token_hex(6).upper()}"

        # Load course context
        course_ctx = self._load_course_context(enrollment_id, week_num)

        # Build greeting
        greeting_system = self._build_system_context({
            "course_name": course_name,
            "user_level": user_level,
            "week_num": week_num,
        }, course_ctx)

        greeting_user = (
            f"Greet the student, briefly acknowledge they're on "
            f"Week {week_num or '?'} of {course_name}"
            + (f" ({course_ctx.get('lesson_title', '')})" if course_ctx.get("lesson_title") else "")
            + ", and ask what they'd like help with. Under 100 words."
        )

        greeting = self._call_ai(greeting_system, [{"role": "user", "content": greeting_user}], max_tokens=250)

        if not greeting:
            greeting = f"Hi! I'm your AI tutor for {course_name}. What would you like to explore?"

        # Persist session
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO charvak_tutor_sessions
                    (session_id, email, course_name, enrollment_id, week_num,
                     topic, user_level, turn_count, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 1, 'active')
            """, (session_id, email, course_name, enrollment_id, week_num,
                  topic or course_ctx.get("lesson_title") or "", user_level))

            # Store greeting as assistant message
            msg_id = f"TMSG-{secrets.token_hex(6).upper()}"
            cur.execute("""
                INSERT INTO charvak_tutor_messages
                    (message_id, session_id, role, content)
                VALUES (%s, %s, 'assistant', %s)
            """, (msg_id, session_id, greeting))

            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Tutor session insert failed: {e}")
            return {"status": "error", "message": f"Failed to create session: {e}"}

        return {
            "status": "success",
            "session_id": session_id,
            "ai_message": greeting,
            "course_context_loaded": bool(course_ctx.get("lesson_content")),
            "lesson_title": course_ctx.get("lesson_title", ""),
        }

    def chat_with_tutor(self, session_id: str, user_message: str) -> Dict:
        """Persistent chat - load history, generate response, save both."""
        if not session_id or not user_message:
            return {"status": "error", "message": "session_id and user_message required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Load session
            cur.execute("""
                SELECT email, course_name, enrollment_id, week_num, topic,
                       user_level, turn_count, status
                FROM charvak_tutor_sessions
                WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Session not found"}

            email, course_name, enrollment_id, week_num, topic, user_level, turn_count, status = row
            if status == "closed":
                cur.close()
                conn.close()
                return {"status": "error", "message": "Session is closed"}

            session = {
                "course_name": course_name,
                "user_level": user_level,
                "week_num": week_num,
                "topic": topic,
            }

            # Load last 10 messages for context
            cur.execute("""
                SELECT role, content
                FROM charvak_tutor_messages
                WHERE session_id = %s
                ORDER BY created_at DESC
                LIMIT 10
            """, (session_id,))
            history_rows = cur.fetchall()
            history_rows = list(reversed(history_rows))  # chronological

            # Build message list for OpenAI
            messages = []
            for role, content in history_rows:
                messages.append({
                    "role": "assistant" if role == "assistant" else "user",
                    "content": content,
                })
            messages.append({"role": "user", "content": user_message})

            # Load course context (fresh, in case lesson was updated)
            course_ctx = self._load_course_context(enrollment_id, week_num)
            system_prompt = self._build_system_context(session, course_ctx)

            # Call AI
            ai_response = self._call_ai(system_prompt, messages, max_tokens=800)
            if not ai_response:
                ai_response = "I'm having trouble reaching my knowledge base right now. Please try again in a moment."

            # Save user + assistant messages, update turn_count
            user_msg_id = f"TMSG-{secrets.token_hex(6).upper()}"
            ai_msg_id = f"TMSG-{secrets.token_hex(6).upper()}"

            cur.execute("""
                INSERT INTO charvak_tutor_messages
                    (message_id, session_id, role, content)
                VALUES (%s, %s, 'user', %s)
            """, (user_msg_id, session_id, user_message))

            cur.execute("""
                INSERT INTO charvak_tutor_messages
                    (message_id, session_id, role, content)
                VALUES (%s, %s, 'assistant', %s)
            """, (ai_msg_id, session_id, ai_response))

            cur.execute("""
                UPDATE charvak_tutor_sessions
                SET turn_count = turn_count + 1,
                    last_active_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            """, (session_id,))

            conn.commit()
            cur.close()
            conn.close()

            return {
                "status": "success",
                "ai_response": ai_response,
                "turn": turn_count + 1,
            }
        except Exception as e:
            logger.error(f"Tutor chat failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_session_messages(self, session_id: str) -> Dict:
        """Load all messages for a session (for UI resume)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT session_id, email, course_name, week_num, topic,
                       user_level, turn_count, status, started_at
                FROM charvak_tutor_sessions
                WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "Session not found"}

            session = {
                "session_id": row[0],
                "email": row[1],
                "course_name": row[2],
                "week_num": row[3],
                "topic": row[4],
                "user_level": row[5],
                "turn_count": row[6],
                "status": row[7],
                "started_at": row[8].isoformat() if row[8] else None,
            }

            cur.execute("""
                SELECT message_id, role, content, created_at
                FROM charvak_tutor_messages
                WHERE session_id = %s
                ORDER BY created_at
            """, (session_id,))

            messages = [
                {
                    "message_id": m[0],
                    "role": m[1],
                    "content": m[2],
                    "created_at": m[3].isoformat() if m[3] else None,
                }
                for m in cur.fetchall()
            ]

            cur.close()
            conn.close()

            return {"status": "success", "session": session, "messages": messages}
        except Exception as e:
            logger.error(f"Tutor get_session_messages failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_real_scenario(self, session_id: str) -> Dict:
        """Legacy endpoint - returns session stub."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT session_id, course_name, week_num, topic
                FROM charvak_tutor_sessions WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if not row:
                return {"status": "error", "message": "Session not found"}
            return {
                "status": "success",
                "session_id": row[0],
                "course_name": row[1],
                "week_num": row[2],
                "topic": row[3],
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def evaluate_answer(self, session_id: str, user_answer: str) -> Dict:
        """Legacy endpoint - returns stub evaluation."""
        return {
            "status": "success",
            "evaluation": "This endpoint is deprecated. Use chat_with_tutor for real-time feedback.",
        }


interactive_tutor = InteractiveTutor()