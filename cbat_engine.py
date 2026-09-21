"""
Charvak RRB ALP CBAT Engine
Computer-Based Aptitude Test (Stage 3 of RRB ALP selection).
6 sub-tests: Analogies, Decision Making, Numerical Ability,
Memory (Short), Memory (Long), Following Directions.

Delivery: image-based, strict per-question timing, no back-navigation.
DB-backed: sessions + answers persisted.
"""
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.cbat")


class CBATEngine:
    """RRB ALP CBAT engine. DB-backed, per-question timed, no back-nav."""

    SUB_TESTS = {
        "analogies": {
            "name": "Analogies",
            "description": "Verbal and visual analogy pairs",
            "questions": 20,
            "time_per_q_ms": 15000,
            "svg_required": False,
        },
        "decision_making": {
            "name": "Decision Making",
            "description": "Situational judgment under time pressure",
            "questions": 15,
            "time_per_q_ms": 30000,
            "svg_required": False,
        },
        "numerical_ability": {
            "name": "Numerical Ability",
            "description": "Arithmetic and quick calculation",
            "questions": 20,
            "time_per_q_ms": 20000,
            "svg_required": False,
        },
        "memory_short": {
            "name": "Memory (Short)",
            "description": "Brief exposure, then recall",
            "questions": 15,
            "time_per_q_ms": 10000,
            "view_ms": 5000,
            "svg_required": True,
        },
        "memory_long": {
            "name": "Memory (Long)",
            "description": "Extended exposure, detailed recall",
            "questions": 10,
            "time_per_q_ms": 15000,
            "view_ms": 15000,
            "svg_required": True,
        },
        "following_directions": {
            "name": "Following Directions",
            "description": "Spatial navigation with route steps",
            "questions": 20,
            "time_per_q_ms": 20000,
            "svg_required": True,
        },
    }

    PASS_THRESHOLD = 60.0

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self._ensure_tables()
        logger.info("CBAT Engine ready | AI: %s",
                    "ENABLED" if self.openai_api_key else "DISABLED")

    def _ensure_tables(self):
        """Idempotent table creation (mirrors migration)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_cbat_sessions (
                    session_id       TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    sub_test         TEXT NOT NULL,
                    sections_json    JSONB NOT NULL,
                    total_questions  INTEGER NOT NULL,
                    total_time_ms    INTEGER NOT NULL,
                    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at     TIMESTAMP,
                    status           TEXT NOT NULL DEFAULT 'in_progress',
                    score            NUMERIC(5,2),
                    correct_count    INTEGER,
                    passed           BOOLEAN
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cbat_sessions_email ON charvak_cbat_sessions(email)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cbat_sessions_sub_test ON charvak_cbat_sessions(sub_test)")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_cbat_answers (
                    answer_id       TEXT PRIMARY KEY,
                    session_id      TEXT NOT NULL,
                    question_index  INTEGER NOT NULL,
                    selected        INTEGER,
                    time_taken_ms   INTEGER,
                    is_correct      BOOLEAN,
                    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, question_index)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cbat_answers_session ON charvak_cbat_answers(session_id)")
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"CBAT tables init failed: {e}")

    # ============================================================
    # INFO
    # ============================================================

    def get_sub_tests(self) -> Dict:
        """Return the 6 CBAT sub-tests with metadata."""
        return {
            "status": "success",
            "exam": "RRB ALP CBAT",
            "full_name": "Computer-Based Aptitude Test (Stage 3)",
            "sub_tests": [
                {"id": k, **v} for k, v in self.SUB_TESTS.items()
            ],
            "pass_threshold": self.PASS_THRESHOLD,
        }

    # ============================================================
    # QUESTION GENERATION
    # ============================================================

    def _ai_json(self, prompt: str, max_tokens: int = 3000, temperature: float = 0.7) -> Optional[Dict]:
        """Call OpenAI in JSON mode. Returns parsed dict or None."""
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
                timeout=60,
            )
            response.raise_for_status()
            content = (response.json().get("choices", [{}])[0]
                       .get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"CBAT AI call failed: {e}")
            return None

    def _fallback_questions(self, sub_test: str, count: int) -> List[Dict]:
        """Deterministic fallback questions when AI is unavailable."""
        if sub_test == "analogies":
            base = [
                {"prompt": "Book : Reading :: Fork : ?", "options": ["Eating", "Cooking", "Metal", "Drawing"], "correct": 0},
                {"prompt": "Clock : Time :: Thermometer : ?", "options": ["Heat", "Mercury", "Weather", "Temperature"], "correct": 3},
                {"prompt": "Doctor : Patient :: Lawyer : ?", "options": ["Court", "Client", "Law", "Judge"], "correct": 1},
                {"prompt": "Bird : Nest :: Bee : ?", "options": ["Honey", "Flower", "Hive", "Sting"], "correct": 2},
                {"prompt": "Puppy : Dog :: Calf : ?", "options": ["Cow", "Horse", "Goat", "Sheep"], "correct": 0},
            ]
        elif sub_test == "decision_making":
            base = [
                {"prompt": "You witness a colleague taking office supplies home. What is the best action?",
                 "options": ["Ignore it", "Report to manager immediately", "Confront them privately", "Tell other colleagues"],
                 "correct": 2},
                {"prompt": "A train is delayed and you will miss a critical meeting. What is the most professional action?",
                 "options": ["Wait silently", "Call the client and reschedule", "Blame the railway", "Send an angry email"],
                 "correct": 1},
                {"prompt": "You receive an urgent task but lack necessary info. Best first step?",
                 "options": ["Start anyway", "Ask the requestor for clarification", "Delegate it", "Skip it"],
                 "correct": 1},
            ]
        elif sub_test == "numerical_ability":
            base = [
                {"prompt": "What is 15% of 240?", "options": ["36", "24", "32", "40"], "correct": 0},
                {"prompt": "If a train travels 120 km in 90 minutes, what is its speed in km/h?", "options": ["60", "80", "90", "120"], "correct": 1},
                {"prompt": "Solve: 7 x 8 + 12 ÷ 4 = ?", "options": ["58", "59", "60", "61"], "correct": 0},
                {"prompt": "What is the next number: 3, 6, 12, 24, ?", "options": ["36", "42", "48", "60"], "correct": 2},
                {"prompt": "A shop gives 25% discount on Rs. 800. Final price?", "options": ["600", "650", "700", "750"], "correct": 0},
            ]
        elif sub_test in ("memory_short", "memory_long"):
            base = [
                {"prompt": "Which of these was in the grid?",
                 "svg": '<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg"><rect width="200" height="200" fill="#f8f9fa" stroke="#ccc"/><text x="30" y="50" font-size="24" font-family="Arial">7</text><text x="100" y="50" font-size="24" font-family="Arial">3</text><text x="30" y="120" font-size="24" font-family="Arial">9</text><text x="100" y="120" font-size="24" font-family="Arial">2</text></svg>',
                 "options": ["7", "5", "8", "1"], "correct": 0},
            ]
        elif sub_test == "following_directions":
            base = [
                {"prompt": "Start at (0,0). Move 3 East, 2 South, 1 West. Where are you?",
                 "svg": '<svg width="300" height="200" xmlns="http://www.w3.org/2000/svg" style="background:#f8f9fa"><text x="10" y="20" font-family="Arial" font-size="14">N ↑ E -></text></svg>',
                 "options": ["(2,-2)", "(2,2)", "(3,-2)", "(4,-2)"], "correct": 0},
            ]
        else:
            base = [{"prompt": f"Sample question {i+1}", "options": ["A", "B", "C", "D"], "correct": 0} for i in range(count)]

        out = []
        for i in range(count):
            q = base[i % len(base)].copy()
            q["id"] = i + 1
            q["index"] = i
            out.append(q)
        return out

    def _generate_questions(self, sub_test: str, count: int) -> List[Dict]:
        """Generate CBAT questions via AI, with fallback."""
        config = self.SUB_TESTS.get(sub_test)
        if not config:
            return self._fallback_questions(sub_test, count)

        time_per_q = config["time_per_q_ms"]
        view_ms = config.get("view_ms")

        # Sub-test-specific instructions
        if sub_test == "analogies":
            type_desc = ("verbal analogies of the form 'A : B :: C : ?'. "
                         "The candidate picks the best match from 4 options.")
        elif sub_test == "decision_making":
            type_desc = ("situational judgment scenarios. Each presents a workplace "
                         "or safety situation with 4 possible actions; the best action "
                         "is the most professional and appropriate.")
        elif sub_test == "numerical_ability":
            type_desc = ("arithmetic and quick calculation questions. Number series, "
                         "percentages, speed/distance, work/time. Solvable in 15-20 seconds.")
        elif sub_test == "memory_short":
            type_desc = ("memory recall after brief exposure. Each question shows a grid "
                         "of 4-6 items/numbers briefly, then asks which item was present. "
                         "SVG field must be a valid SVG markup string showing a 2x2 or 2x3 grid "
                         "with 4-6 short items (numbers or letters).")
        elif sub_test == "memory_long":
            type_desc = ("extended memory recall. Each question shows a larger grid "
                         "(3x3 or 3x4) of items for 15 seconds, then asks which item was "
                         "present or missing. SVG must be a valid SVG string.")
        elif sub_test == "following_directions":
            type_desc = ("spatial navigation. Each question asks where a person ends up "
                         "after a sequence of directional moves from a starting point. "
                         "SVG should show a small compass or grid reference.")
        else:
            type_desc = "general aptitude questions."

        prompt = (
            f"You are creating practice questions for the RRB ALP CBAT "
            f"(Computer-Based Aptitude Test) sub-test: {config['name']}.\n\n"
            f"Question type: {type_desc}\n\n"
            f"Generate exactly {count} UNIQUE questions. Each has 4 options, "
            f"only one correct answer.\n\n"
            "Return a JSON object with a 'questions' array. Each question:\n"
            '{"prompt": "question text", '
            '"options": ["A", "B", "C", "D"], '
            '"correct": <0-3 integer index>, '
            '"svg": "<optional SVG markup string or omit for non-visual questions>"}\n\n'
            "RULES:\n"
            "- No duplicate prompts\n"
            "- correct must be an INT 0-3, not a string\n"
            "- If a question is visual (memory/following-directions), provide a simple "
            "  SVG string under 500 chars. Otherwise omit the svg field.\n"
            "- Keep questions answerable in the time limit.\n"
        )

        result = self._ai_json(prompt, max_tokens=3500, temperature=0.7)

        questions = []
        if result and isinstance(result.get("questions"), list):
            for i, q in enumerate(result["questions"][:count]):
                if not isinstance(q, dict) or not q.get("prompt"):
                    continue
                options = q.get("options", [])
                if not isinstance(options, list) or len(options) < 2:
                    continue
                correct = q.get("correct", 0)
                if isinstance(correct, str):
                    try:
                        correct = int(correct)
                    except Exception:
                        correct = 0
                if not isinstance(correct, int):
                    correct = 0
                if correct < 0 or correct >= len(options):
                    correct = 0
                questions.append({
                    "id": i + 1,
                    "index": i,
                    "prompt": str(q["prompt"])[:500],
                    "options": [str(o)[:200] for o in options[:4]],
                    "correct": correct,
                    "svg": str(q.get("svg", ""))[:1500] if q.get("svg") else None,
                    "time_limit_ms": time_per_q,
                    "view_ms": view_ms,
                })

        # Fill with fallback if AI returned too few
        if len(questions) < count:
            logger.warning(f"CBAT {sub_test}: AI returned {len(questions)}/{count}, using fallback for rest")
            fallback = self._fallback_questions(sub_test, count - len(questions))
            for fq in fallback:
                fq["id"] = len(questions) + 1
                fq["index"] = len(questions)
                fq["time_limit_ms"] = time_per_q
                fq["view_ms"] = view_ms
                questions.append(fq)

        return questions[:count]

    # ============================================================
    # SESSION LIFECYCLE
    # ============================================================

    def start_cbat_session(self, email: str, sub_test: str) -> Dict:
        """Start a CBAT session for one sub-test. Generates and freezes questions."""
        if sub_test not in self.SUB_TESTS:
            return {"status": "error", "message": f"Unknown sub-test: {sub_test}"}
        if not email:
            return {"status": "error", "message": "Email required"}

        config = self.SUB_TESTS[sub_test]
        count = config["questions"]
        session_id = f"CBAT-{secrets.token_hex(6).upper()}"

        questions = self._generate_questions(sub_test, count)
        total_time_ms = sum(q.get("time_limit_ms", 20000) for q in questions)

        payload = {
            "sub_test": sub_test,
            "sub_test_name": config["name"],
            "questions": questions,
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_cbat_sessions
                    (session_id, email, sub_test, sections_json,
                     total_questions, total_time_ms, status)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s, 'in_progress')
            """, (session_id, email.lower().strip(), sub_test,
                  json.dumps(payload), len(questions), total_time_ms))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"CBAT session insert failed: {e}")
            return {"status": "error", "message": "Could not start session"}

        # Return first question only (strict sequencing - no back-nav, no full list)
        first_q = self._public_question(questions[0]) if questions else None

        return {
            "status": "success",
            "session_id": session_id,
            "sub_test": sub_test,
            "sub_test_name": config["name"],
            "total_questions": len(questions),
            "total_time_ms": total_time_ms,
            "current_index": 0,
            "question": first_q,
        }

    def _public_question(self, q: Dict) -> Dict:
        """Strip the correct answer before sending to frontend."""
        return {
            "index": q.get("index"),
            "prompt": q.get("prompt"),
            "options": q.get("options", []),
            "svg": q.get("svg"),
            "time_limit_ms": q.get("time_limit_ms", 20000),
            "view_ms": q.get("view_ms"),
        }

    def submit_cbat_answer(self, session_id: str, question_index: int,
                           selected: Optional[int], time_taken_ms: int) -> Dict:
        """Record one answer (idempotent - no back-nav, second submit is ignored)."""
        if not session_id:
            return {"status": "error", "message": "session_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT sections_json, total_questions, status
                FROM charvak_cbat_sessions WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found"}

            sections_json, total_questions, status = row
            if status == "completed":
                cur.close(); conn.close()
                return {"status": "error", "message": "Session already completed"}

            if question_index < 0 or question_index >= total_questions:
                cur.close(); conn.close()
                return {"status": "error", "message": "Invalid question index"}

            payload = sections_json if isinstance(sections_json, dict) else json.loads(sections_json)
            questions = payload.get("questions", [])
            if question_index >= len(questions):
                cur.close(); conn.close()
                return {"status": "error", "message": "Question out of range"}

            q = questions[question_index]
            correct_idx = q.get("correct", 0)
            is_correct = (selected is not None and int(selected) == int(correct_idx))

            answer_id = f"CA-{secrets.token_hex(4).upper()}"

            # UNIQUE(session_id, question_index) - the ON CONFLICT DO NOTHING enforces
            # idempotency AND prevents back-navigation (second submit ignored).
            cur.execute("""
                INSERT INTO charvak_cbat_answers
                    (answer_id, session_id, question_index, selected, time_taken_ms, is_correct)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (session_id, question_index) DO NOTHING
            """, (answer_id, session_id, question_index,
                  selected if selected is not None else None,
                  time_taken_ms, is_correct))
            inserted = cur.rowcount

            conn.commit()

            # Fetch next question if any
            next_index = question_index + 1
            next_question = None
            if next_index < len(questions):
                next_question = self._public_question(questions[next_index])

            cur.close(); conn.close()

            return {
                "status": "success",
                "recorded": inserted == 1,
                "question_index": question_index,
                "next_index": next_index if next_question else None,
                "next_question": next_question,
            }
        except Exception as e:
            logger.error(f"CBAT answer submit failed: {e}")
            return {"status": "error", "message": str(e)}

    def complete_cbat_session(self, session_id: str) -> Dict:
        """Score the session, persist result to charvak_assessment_results."""
        if not session_id:
            return {"status": "error", "message": "session_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT email, sub_test, total_questions, status
                FROM charvak_cbat_sessions WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found"}

            email, sub_test, total_questions, status = row

            cur.execute("""
                SELECT COUNT(*), COUNT(*) FILTER (WHERE is_correct = TRUE)
                FROM charvak_cbat_answers WHERE session_id = %s
            """, (session_id,))
            answered, correct = cur.fetchone()
            answered = int(answered or 0)
            correct = int(correct or 0)

            score = round((correct / total_questions) * 100, 2) if total_questions > 0 else 0.0
            passed = score >= self.PASS_THRESHOLD

            if status != "completed":
                cur.execute("""
                    UPDATE charvak_cbat_sessions
                    SET completed_at = CURRENT_TIMESTAMP,
                        status = 'completed',
                        score = %s,
                        correct_count = %s,
                        passed = %s
                    WHERE session_id = %s
                """, (score, correct, passed, session_id))
                conn.commit()

            cur.close(); conn.close()

            # Persist to assessment results (reuse results_system)
            try:
                from results_system import results_system
                sub_test_name = self.SUB_TESTS.get(sub_test, {}).get("name", sub_test)
                results_system.record_assessment_result(
                    email=email,
                    assessment_type="cbat",
                    assessment_name=f"RRB ALP CBAT - {sub_test_name}",
                    score=score,
                    total_questions=total_questions,
                    correct_answers=correct,
                    details={"sub_test": sub_test, "answered": answered,
                             "session_id": session_id},
                )
            except Exception as e:
                logger.warning(f"CBAT result persist failed: {e}")

            return {
                "status": "success",
                "session_id": session_id,
                "sub_test": sub_test,
                "total_questions": total_questions,
                "answered": answered,
                "correct": correct,
                "score": score,
                "passed": passed,
                "pass_threshold": self.PASS_THRESHOLD,
            }
        except Exception as e:
            logger.error(f"CBAT complete failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_cbat_status(self, session_id: str) -> Dict:
        """Return current state - used for resume on refresh."""
        if not session_id:
            return {"status": "error", "message": "session_id required"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT sections_json, total_questions, status, score, correct_count
                FROM charvak_cbat_sessions WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found"}

            sections_json, total_questions, status, score, correct_count = row

            cur.execute("""
                SELECT question_index FROM charvak_cbat_answers
                WHERE session_id = %s ORDER BY question_index DESC LIMIT 1
            """, (session_id,))
            last = cur.fetchone()
            cur.close(); conn.close()

            payload = sections_json if isinstance(sections_json, dict) else json.loads(sections_json)
            questions = payload.get("questions", [])

            next_index = (int(last[0]) + 1) if last else 0
            next_q = None
            if status != "completed" and next_index < len(questions):
                next_q = self._public_question(questions[next_index])

            return {
                "status": "success",
                "session_id": session_id,
                "sub_test": payload.get("sub_test"),
                "total_questions": total_questions,
                "current_index": next_index,
                "question": next_q,
                "session_status": status,
                "final_score": float(score) if score is not None else None,
                "correct_count": correct_count,
            }
        except Exception as e:
            logger.error(f"CBAT status failed: {e}")
            return {"status": "error", "message": str(e)}


cbat_engine = CBATEngine()