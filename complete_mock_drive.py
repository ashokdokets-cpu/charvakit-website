"""
Charvak Complete AI Mock Drive
AI generates exact question counts: TCS 25+10+2, Infosys 20+15+3, etc.
Database-backed: sessions and answers persist across restarts.
"""
import logging
import json
import os
import secrets
from datetime import datetime

logger = logging.getLogger("charvakit.complete_mock")


class CompleteMockDrive:
    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self._ensure_tables()
        logger.info(f"Complete Mock Drive - AI: {'ENABLED' if self.openai_api_key else 'DISABLED'}")

    def _ensure_tables(self):
        """Idempotent table creation for mock drives."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_mock_sessions (
                    session_id       TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    company_id       TEXT NOT NULL,
                    company_name     TEXT NOT NULL,
                    pattern          TEXT NOT NULL,
                    sections_json    JSONB NOT NULL,
                    total_questions  INTEGER NOT NULL,
                    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at     TIMESTAMP,
                    status           TEXT NOT NULL DEFAULT 'in_progress',
                    score            NUMERIC(5,2),
                    correct_count    INTEGER,
                    passed           BOOLEAN                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_mock_answers (
                    answer_id     TEXT PRIMARY KEY,
                    session_id    TEXT NOT NULL,
                    section_name  TEXT NOT NULL,
                    question_id   INTEGER NOT NULL,
                    selected      INTEGER NOT NULL,
                    submitted_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, section_name, question_id)
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"mock tables init failed: {e}")

    def get_company_config(self, company_id):
        """Get exact question counts for each company."""
        configs = {
            "tcs": {
                "name": "TCS", "pattern": "NQT",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "75 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Advanced", "count": 10, "time": "25 min", "topics": ["Advanced Quant", "Advanced Logic"]},
                    {"name": "Coding", "count": 2, "time": "55 min", "topics": ["DSA", "Problem Solving"]}
                ]
            },
            "infosys": {
                "name": "Infosys", "pattern": "InfyTQ",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS", "OOPs"]},
                    {"name": "Coding", "count": 3, "time": "90 min", "topics": ["DSA", "Algorithms"]}
                ]
            },
            "cognizant": {
                "name": "Cognizant", "pattern": "GenC",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quantitative", "Analytical", "Verbal"]},
                    {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Speaking", "Grammar"]},
                    {"name": "Programming", "count": 5, "time": "45 min", "topics": ["SQL", "Debugging"]}
                ]
            },
            "wipro": {
                "name": "Wipro", "pattern": "Elite NTH",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "48 min", "topics": ["Logical", "Quant"]},
                    {"name": "Communication", "count": 2, "time": "20 min", "topics": ["Essay", "Email"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic", "Intermediate"]}
                ]
            },
            "accenture": {
                "name": "Accenture", "pattern": "ASE",
                "sections": [
                    {"name": "Cognitive", "count": 25, "time": "60 min", "topics": ["Aptitude", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 10, "time": "20 min", "topics": ["Grammar"]}
                ]
            },
            "capgemini": {
                "name": "Capgemini", "pattern": "Exceller",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "DBMS"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "ibm": {
                "name": "IBM", "pattern": "Associate",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA", "OOPs"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic", "DSA"]}
                ]
            },
            "hcl": {
                "name": "HCLTech", "pattern": "TechBeE",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Verbal"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Coding", "count": 2, "time": "30 min", "topics": ["Basic"]}
                ]
            },
            "tech_mahindra": {
                "name": "Tech Mahindra", "pattern": "Talent",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "lti": {
                "name": "LTI", "pattern": "GET",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "mindtree": {
                "name": "Mindtree", "pattern": "Graduate",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["DSA"]},
                    {"name": "Coding", "count": 2, "time": "45 min", "topics": ["Basic"]}
                ]
            },
            "deloitte": {
                "name": "Deloitte", "pattern": "Analyst",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "kpmg": {
                "name": "KPMG", "pattern": "Analyst",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "ey": {
                "name": "EY", "pattern": "Associate",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "pwc": {
                "name": "PwC", "pattern": "Associate",
                "sections": [
                    {"name": "Aptitude", "count": 25, "time": "60 min", "topics": ["Quant", "Logical", "Verbal"]},
                    {"name": "Technical", "count": 10, "time": "30 min", "topics": ["CS Fundamentals"]},
                    {"name": "Communication", "count": 5, "time": "15 min", "topics": ["Grammar"]}
                ]
            },
            "amazon": {
                "name": "Amazon", "pattern": "SDE",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                    {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                ]
            },
            "google": {
                "name": "Google", "pattern": "SWE",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                    {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                ]
            },
            "microsoft": {
                "name": "Microsoft", "pattern": "SWE",
                "sections": [
                    {"name": "Aptitude", "count": 20, "time": "60 min", "topics": ["Quant", "Logical"]},
                    {"name": "Technical", "count": 15, "time": "30 min", "topics": ["DSA", "Algorithms"]},
                    {"name": "Coding", "count": 2, "time": "60 min", "topics": ["DSA", "Problem Solving"]}
                ]
            }
        }
        return configs.get(company_id, configs["tcs"])

    def _sanitize_questions(self, questions):
        """Validate AI output. Correct is an integer 0..len(options)-1.
        Maps string-correct back to option index; falls back to 0."""
        if not isinstance(questions, list):
            return []
        out = []
        for item in questions:
            if not isinstance(item, dict):
                continue
            q_text = item.get("q") or item.get("question") or ""
            options = item.get("options") or ["A", "B", "C", "D"]
            if not isinstance(options, list) or len(options) == 0:
                options = ["A", "B", "C", "D"]
            correct_raw = item.get("correct", 0)
            correct_idx = 0
            if isinstance(correct_raw, int):
                correct_idx = correct_raw
            elif isinstance(correct_raw, str):
                stripped = correct_raw.strip()
                matched = False
                for idx, opt in enumerate(options):
                    if str(opt).strip().lower() == stripped.lower():
                        correct_idx = idx
                        matched = True
                        break
                if not matched:
                    if len(stripped) == 1 and stripped.upper() in ("A", "B", "C", "D"):
                        correct_idx = ord(stripped.upper()) - ord("A")
                    else:
                        correct_idx = 0
            if correct_idx < 0 or correct_idx >= len(options):
                correct_idx = 0
            out.append({
                "q": q_text,
                "options": options,
                "correct": correct_idx
            })
        return out

    def generate_ai_questions(self, topic, count):
        """Generate AI questions for a topic."""
        if self.openai_api_key:
            try:
                import requests
                prompt = (
                    "Generate " + str(count) + " multiple-choice questions on " + topic
                    + " for placement test. Return a JSON array. Each item must have:"
                    + ' "q" (question text), "options" (array of 4 strings), and'
                    + ' "correct" which is the 0-based INDEX (0, 1, 2, or 3) of the correct option.'
                )
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": "Bearer " + self.openai_api_key},
                    json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "temperature": 0.95},
                    timeout=15
                )
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                import re as _re
                match = _re.search(r"\[.*\]", content, _re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    return self._sanitize_questions(parsed)
            except Exception as e:
                logger.error(f"AI failed: {e}")

        # Fallback
        return [
            {"q": f"{topic} question {i+1}",
             "options": ["A", "B", "C", "D"],
             "correct": i % 4}
            for i in range(count)
        ]


    def start_mock_drive(self, email, company_id):
        """Start mock drive with AI-generated questions matching exact counts."""
        config = self.get_company_config(company_id)
        session_id = f"MOCK-{secrets.token_hex(6).upper()}"

        sections_with_questions = []
        total_questions = 0

        for section in config["sections"]:
            topics = section["topics"]
            count = section["count"]
            questions_per_topic = max(1, count // len(topics))
            remaining = count

            section_questions = []
            for i, topic in enumerate(topics):
                num = questions_per_topic
                if i == len(topics) - 1:
                    num = remaining

                questions = self.generate_ai_questions(topic, num)
                for j, q in enumerate(questions):
                    section_questions.append({
                        "id": len(section_questions) + 1,
                        "question": q.get("q", q.get("question", f"{topic} Q{j+1}")),
                        "options": q.get("options", ["A", "B", "C", "D"]),
                        "correct": q.get("correct", 0),
                        "topic": topic
                    })
                remaining -= num

            sections_with_questions.append({
                "name": section["name"],
                "count": count,
                "time": section["time"],
                "topics": topics,
                "questions": section_questions
            })
            total_questions += len(section_questions)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_mock_sessions
                    (session_id, email, company_id, company_name, pattern,
                     sections_json, total_questions, status)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, 'in_progress')
            """, (session_id, email, company_id, config["name"], config["pattern"],
                  json.dumps(sections_with_questions), total_questions))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"start_mock_drive persist failed: {e}")
            return {"status": "error", "message": str(e)}

        session = {
            "session_id": session_id,
            "email": email,
            "company": config["name"],
            "pattern": config["pattern"],
            "sections": sections_with_questions,
            "total_questions": total_questions,
            "answers": [],
            "started_at": datetime.now().isoformat(),
            "status": "in_progress"
        }
        return {"status": "success", "session": session}

    def submit_answer(self, session_id, section_name, question_id, selected_option):
        """Submit answer. Idempotent per (session, section, question)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT session_id FROM charvak_mock_sessions WHERE session_id = %s", (session_id,))
            if not cur.fetchone():
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found"}
            try:
                selected_int = int(selected_option)
            except (ValueError, TypeError):
                selected_int = 0
            answer_id = "ANS-" + secrets.token_hex(6).upper()
            cur.execute("""
                INSERT INTO charvak_mock_answers
                    (answer_id, session_id, section_name, question_id, selected)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (session_id, section_name, question_id)
                DO UPDATE SET selected = EXCLUDED.selected,
                              submitted_at = CURRENT_TIMESTAMP
            """, (answer_id, session_id, section_name, question_id, selected_int))
            cur.execute("SELECT COUNT(*) FROM charvak_mock_answers WHERE session_id = %s", (session_id,))
            total_answered = cur.fetchone()[0]
            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "total_answered": total_answered}
        except Exception as e:
            logger.error(f"submit_answer failed: {e}")
            return {"status": "error", "message": str(e)}


    def complete_mock(self, session_id):
        """Complete mock: score from persisted answers, record result, update session."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT email, company_id, company_name, pattern, sections_json, total_questions
                FROM charvak_mock_sessions WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Session not found"}
            email, company_id, company_name, pattern, sections_json, total_questions = row
            sections = sections_json if isinstance(sections_json, list) else json.loads(sections_json or "[]")

            cur.execute("""
                SELECT section_name, question_id, selected
                FROM charvak_mock_answers WHERE session_id = %s
            """, (session_id,))
            answers = cur.fetchall()

            correct = 0
            for ans_section, ans_qid, ans_selected in answers:
                for section in sections:
                    if section.get("name") != ans_section:
                        continue
                    for q in section.get("questions", []):
                        if q.get("id") == ans_qid and q.get("correct") == ans_selected:
                            correct += 1

            score = (correct / total_questions * 100) if total_questions > 0 else 0
            passed = score >= 65
            answered = len(answers)

            cur.execute("""
                UPDATE charvak_mock_sessions
                SET completed_at = CURRENT_TIMESTAMP,
                    status = 'completed',
                    score = %s, correct_count = %s, passed = %s
                WHERE session_id = %s
            """, (round(score, 1), correct, passed, session_id))
            conn.commit()
            cur.close(); conn.close()

            results = {
                "session_id": session_id,
                "email": email,
                "company": company_name,
                "pattern": pattern,
                "total_questions": total_questions,
                "answered": answered,
                "correct": correct,
                "score": round(score, 1),
                "pass": passed,
                "sections": [{"name": s.get("name"), "count": s.get("count")} for s in sections],
                "completed_at": datetime.now().isoformat()
            }

            try:
                from results_system import results_system
                results_system.record_assessment_result(
                    email,
                    "company_mock",
                    f"{company_name} Mock Drive",
                    score,
                    total_questions,
                    correct,
                    {"pattern": pattern},
                    skill=f"mock_{company_id}"
                )
            except Exception as e:
                logger.warning(f"results_system call failed: {e}")

            return {"status": "success", "results": results}
        except Exception as e:
            logger.error(f"complete_mock failed: {e}")
            return {"status": "error", "message": str(e)}


complete_mock = CompleteMockDrive()
