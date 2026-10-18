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
from global_config import OPENAI_MODEL

logger = logging.getLogger("charvakit.complete_mock")


# ============================================================
# Session 43-B1: Mock drive diagnostics constants
# ============================================================
# Industry-typical "passing" cutoff per company, in percent.
# These are based on the usually published cutoff for each
# company's freshers test. Replace with real data over time.
CUTOFFS = {
    "tcs": 60,
    "infosys": 55,
    "wipro": 55,
    "cognizant": 55,
    "hcl": 55,
    "hcltech": 55,
    "tech_mahindra": 55,
    "lti": 55,
    "mindtree": 55,
    "accenture": 60,
    "capgemini": 55,
    "ibm": 60,
    "deloitte": 65,
    "kpmg": 65,
    "ey": 65,
    "pwc": 65,
    "amazon": 70,
    "google": 75,
    "microsoft": 75,
}

# Recommended courses per weak topic. Falls back to a generic
# suggestion if the topic has no match.
TOPIC_TO_COURSE = {
    # ---------- Engineering topics ----------
    "Quant": ["Data Analytics [Beginner]", "Python for Data Science [Intermediate]"],
    "Advanced Quant": ["Data Analytics [Beginner]"],
    "Verbal": ["Business Communication"],
    "CS Fundamentals": ["Data Science & ML [Intermediate]", "Python Programming [Beginner]"],
    "Basic": ["Python Programming [Beginner]"],
    "DSA": ["Full Stack Web Development [Beginner]", "Python Programming [Beginner]"],
    "System Design": ["Cloud Architecture [Advanced]", "DevOps Engineering [Intermediate]"],
    "DBMS": ["SQL & Database [Beginner]"],
    "OS": ["DevOps Engineering [Intermediate]"],
    "Coding": ["Python Programming [Beginner]"],
    "Data Structures": ["Data Science & ML [Intermediate]"],
    "Algorithms": ["Data Science & ML [Intermediate]"],

    # ---------- Business Analyst topics (Session 43-C) ----------
    "Case Reasoning": ["Case Study Fundamentals", "Consulting Case Frameworks"],
    "Market Sizing": ["Consulting Math", "Case Study Fundamentals"],
    "Data Interpretation": ["Data Interpretation for Managers"],
    "Business Logic": ["Strategy Frameworks", "Business Ethics & Compliance"],
    "Business Writing": ["Business Communication"],
    "Reading": ["Business Communication"],
    "Product Metrics": ["Product Management Fundamentals"],
    "Product Case": ["Product Management Fundamentals"],
    "Financial Math": ["Financial Modelling in Excel"],
    "Financial Reasoning": ["Financial Modelling in Excel"],
    "Strategy": ["Strategy Frameworks"],
    "Grammar": ["Business Communication"],
    "Problem Solving": ["Full Stack Web Development [Beginner]"],
    "Advanced Logic": ["Data Science & ML [Intermediate]"],
}


def get_cutoff(company_id: str) -> int:
    """Return the freshers cutoff for a company, default 60."""
    return CUTOFFS.get((company_id or "").lower(), 60)


def get_course_suggestions(topic: str) -> list:
    """Return catalog course names matching a weak topic."""
    return TOPIC_TO_COURSE.get(topic, [])




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


    # ============================================================
    # Session 43-C: Business Analyst pattern variants (BA_VARIANTS)
    # ============================================================
    # Every consulting + services company gets a "Business Analyst"
    # pattern alongside the existing (generalist/analyst) pattern.
    # The existing patterns are NOT modified — the BA variants are
    # additional tracks an MBA student can choose.
    #
    # Each variant:
    #   - Aptitude (20 Q, 45 min)    — Quant, Logical, Verbal
    #   - Business Reasoning (15 Q, 40 min) — Case Reasoning, Market Sizing,
    #                                          Data Interpretation, Business Logic
    #   - Communication (5 Q, 15 min) — Grammar, Business Writing

    def _ba_variant(self, company_name: str, pattern_name: str = "Business Analyst") -> dict:
        """Return the standard Business Analyst pattern for a company."""
        return {
            "name": company_name,
            "pattern": pattern_name,
            "sections": [
                {
                    "name": "Aptitude",
                    "count": 20,
                    "time": "45 min",
                    "topics": ["Quant", "Logical", "Verbal"],
                },
                {
                    "name": "Business Reasoning",
                    "count": 15,
                    "time": "40 min",
                    "topics": ["Case Reasoning", "Market Sizing", "Data Interpretation", "Business Logic"],
                },
                {
                    "name": "Communication",
                    "count": 5,
                    "time": "15 min",
                    "topics": ["Grammar", "Business Writing"],
                },
            ],
        }

    def get_company_config_variant(self, company_id: str, pattern_id: str = None) -> dict:
        """
        Return a specific pattern config for a company.

        pattern_id=None returns the default pattern (existing behaviour).
        pattern_id="business_analyst" returns the BA variant.

        This method does NOT replace get_company_config — it wraps it
        and adds variants on top.
        """
        base = self.get_company_config(company_id)
        if not base:
            return None

        # BA variant companies
        ba_companies = {
            "deloitte": "Deloitte",
            "kpmg": "KPMG",
            "ey": "EY",
            "pwc": "PwC",
            "tcs": "TCS",
            "accenture": "Accenture",
            "capgemini": "Capgemini",
        }

        if pattern_id == "business_analyst":
            if company_id in ba_companies:
                return self._ba_variant(ba_companies[company_id])
            return None

        # Default: return the base config as-is
        return base

    def get_all_patterns(self, company_id: str) -> list:
        """
        Return all available patterns for a company.

        Each entry: {"id": "<slug>", "name": "<pattern>", "is_default": bool}
        """
        base = self.get_company_config(company_id)
        if not base:
            return []

        patterns = [
            {
                "id": "default",
                "name": base.get("pattern", "Default"),
                "is_default": True,
            }
        ]

        ba_companies = {"deloitte", "kpmg", "ey", "pwc", "tcs", "accenture", "capgemini"}
        if company_id in ba_companies:
            patterns.append({
                "id": "business_analyst",
                "name": "Business Analyst",
                "is_default": False,
            })

        return patterns


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
                    json={"model": OPENAI_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.95},
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


    def start_mock_drive(self, email, company_id, pattern_id=None):
        """Start mock drive with AI-generated questions matching exact counts."""
        # Session 42-3d: when a pattern_id is provided, load that pattern
        # from multi_pattern_company. Otherwise fall back to the single
        # default config in get_company_config().
        config = None
        if pattern_id:
            try:
                from multi_pattern_company import multi_pattern
                _company = multi_pattern.patterns.get(company_id)
                if _company:
                    _pattern = _company["patterns"].get(pattern_id)
                    if _pattern:
                        config = {
                            "name": _company["name"],
                            "pattern": _pattern["name"],
                            "sections": _pattern["sections"],
                        }
            except Exception as _e:
                logger.warning(f"pattern lookup failed ({company_id}/{pattern_id}): {_e}")
        if config is None:
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


    # ============================================================
    # Session 43-B1: Diagnostics — section + topic breakdown + cutoff
    # ============================================================

    # ============================================================
    # Session 43-B2: Question-by-question review + AI explanations
    # ============================================================

    def build_question_review(self, sections, answers):
        """
        Build a per-question review list:
        [{section, q_num, question, topic, options, your_index,
          your_text, correct_index, correct_text, is_correct}]
        """
        # Answer map: (section, q_id) -> selected_index
        ans_map = {}
        for sname, qid, sel in answers or []:
            ans_map[(sname, qid)] = sel

        review = []
        for sec in sections or []:
            sname = sec.get("name")
            for q in sec.get("questions", []) or []:
                qid = q.get("id")
                sel = ans_map.get((sname, qid))
                correct_idx = q.get("correct")
                options = q.get("options", []) or []
                your_text = options[sel] if isinstance(sel, int) and 0 <= sel < len(options) else None
                correct_text = options[correct_idx] if isinstance(correct_idx, int) and 0 <= correct_idx < len(options) else None
                review.append({
                    "section": sname,
                    "q_num": qid,
                    "question": q.get("question", ""),
                    "topic": q.get("topic") or "General",
                    "options": options,
                    "your_index": sel,
                    "your_text": your_text,
                    "correct_index": correct_idx,
                    "correct_text": correct_text,
                    "is_correct": (sel is not None and sel == correct_idx),
                })
        return review

    def generate_ai_explanations(self, wrong_questions):
        """
        Batch AI explanations for wrong answers.

        Input: list of dicts with {question, topic, options, correct_text, your_text}
        Output: {q_key: explanation_text}

        Behavior:
        - Batches up to 30 questions per OpenAI call (single call).
        - Hard ceiling of 90 questions total (3 chunks). Beyond that,
          remaining questions get a rule-based fallback explanation.
        - Any question not covered by the AI gets a rule-based fallback.
        - Silent-fail: never raises. Coverage is logged for observability.
        """
        if not wrong_questions:
            return {}
        if not self.openai_api_key:
            # No API key — fallback for all
            return self._fallback_explanations(wrong_questions, [])

        BATCH_SIZE = 30
        MAX_QUESTIONS = 90  # 3 chunks max

        # Slice to ceiling
        questions_to_explain = wrong_questions[:MAX_QUESTIONS]

        explanations = {}
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            import json as _json

            # Process in chunks of BATCH_SIZE
            for chunk_start in range(0, len(questions_to_explain), BATCH_SIZE):
                chunk = questions_to_explain[chunk_start:chunk_start + BATCH_SIZE]

                payload = []
                for i, wq in enumerate(chunk):
                    payload.append({
                        "id": i,
                        "question": wq.get("question", ""),
                        "topic": wq.get("topic", ""),
                        "correct": wq.get("correct_text", ""),
                        "student_answered": wq.get("your_text", ""),
                    })

                prompt = (
                    f"You are an exam coach for Indian campus placements. For each "
                    f"wrong answer below, explain in 2 short sentences why the correct "
                    f"answer is right and what the student should remember. Be specific "
                    f"and pedagogical — not generic.\n\n"
                    f"CRITICAL: You MUST return exactly {len(payload)} items in the "
                    f"explanations array — one for every input id from 0 to {len(payload)-1}. "
                    f"Do not skip or merge any.\n\n"
                    'Return ONLY valid JSON in this shape:\n'
                    '{"explanations": [{"id": <int>, "text": "<2-sentence explanation>"}, ...]}\n\n'
                    "Questions:\n" + _json.dumps(payload, indent=2)
                )

                from openai_compat import translate_kwargs
                resp = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert exam coach. Return JSON only. Never skip items."},
                        {"role": "user", "content": prompt},
                    ],
                    **translate_kwargs(OPENAI_MODEL, max_tokens=8000, temperature=0.3, json_mode=True),
                )
                raw = resp.choices[0].message.content
                parsed = _json.loads(raw)

                for item in parsed.get("explanations", []):
                    idx = item.get("id")
                    text = item.get("text", "")
                    if isinstance(idx, int) and 0 <= idx < len(chunk):
                        key = (chunk[idx].get("question") or "")[:200]
                        explanations[key] = text

            logger.info(
                f"AI explanations: requested={len(questions_to_explain)} "
                f"returned={len(explanations)}"
            )
        except Exception as e:
            logger.warning(f"AI explanations failed: {e}")

        # Fill in fallback explanations for any missed questions
        return self._fallback_explanations(wrong_questions, list(explanations.keys()), explanations)

    def _fallback_explanations(self, wrong_questions, covered_keys, existing=None):
        """
        Merge existing (AI) explanations with rule-based fallbacks for any
        wrong questions the AI did not cover.
        """
        result = dict(existing) if existing else {}
        for wq in wrong_questions:
            key = (wq.get("question") or "")[:200]
            if key in result:
                continue
            correct = wq.get("correct_text") or "the listed correct option"
            topic = wq.get("topic") or "this topic"
            result[key] = (
                f"The correct answer is {correct}. "
                f"Review {topic} — it was identified as a weak area in your report."
            )
        return result

    def compute_diagnostics(self, company_id, company_name, sections, answers):
        """
        Given the sections config + raw answers, compute:
        - section_breakdown: [{name, correct, total, pct}]
        - topic_breakdown:   [{topic, correct, total, pct}]  (weakest first)
        - cutoff_comparison: {cutoff_pct, your_pct, gap, verdict}
        - recommended_actions: [{action, reason, type}]

        `answers` is a list of (section_name, question_id, selected).
        `sections` is a list of {name, count, questions: [{id, topic, correct, ...}]}.
        """
        # Build a lookup: (section_name, question_id) -> {correct, topic}
        lookup = {}
        for sec in sections or []:
            sname = sec.get("name")
            for q in sec.get("questions", []) or []:
                lookup[(sname, q.get("id"))] = {
                    "correct_index": q.get("correct"),
                    "topic": q.get("topic") or "General",
                }

        # Answer map for O(1) lookup
        ans_map = {}
        for sname, qid, sel in answers or []:
            ans_map[(sname, qid)] = sel

        # --- Section breakdown ---
        section_breakdown = []
        for sec in sections or []:
            sname = sec.get("name")
            questions = sec.get("questions", []) or []
            correct = 0
            for q in questions:
                sel = ans_map.get((sname, q.get("id")))
                if sel is not None and sel == q.get("correct"):
                    correct += 1
            total = len(questions)
            pct = round(correct / total * 100, 1) if total else 0.0
            section_breakdown.append({
                "name": sname,
                "correct": correct,
                "total": total,
                "pct": pct,
            })

        # --- Topic breakdown ---
        topic_stats = {}
        for sec in sections or []:
            sname = sec.get("name")
            for q in sec.get("questions", []) or []:
                topic = q.get("topic") or "General"
                if topic not in topic_stats:
                    topic_stats[topic] = {"correct": 0, "total": 0}
                topic_stats[topic]["total"] += 1
                sel = ans_map.get((sname, q.get("id")))
                if sel is not None and sel == q.get("correct"):
                    topic_stats[topic]["correct"] += 1

        topic_breakdown = []
        for topic, stats in topic_stats.items():
            pct = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] else 0.0
            topic_breakdown.append({
                "topic": topic,
                "correct": stats["correct"],
                "total": stats["total"],
                "pct": pct,
            })
        # Weakest first
        topic_breakdown.sort(key=lambda t: t["pct"])

        # --- Cutoff comparison ---
        total_correct = sum(s["correct"] for s in section_breakdown)
        total_questions = sum(s["total"] for s in section_breakdown)
        your_pct = round(total_correct / total_questions * 100, 1) if total_questions else 0.0
        cutoff = get_cutoff(company_id)
        gap = round(your_pct - cutoff, 1)

        if your_pct >= cutoff:
            verdict = f"Above cut-off — you are ready for {company_name}"
        elif your_pct >= cutoff - 10:
            verdict = f"Close — {abs(gap):.0f} points below the {company_name} cut-off"
        elif your_pct >= cutoff - 25:
            verdict = f"Below cut-off — {abs(gap):.0f} points to close"
        else:
            verdict = f"Not yet ready — {abs(gap):.0f} points below the cut-off"

        cutoff_comparison = {
            "cutoff_pct": cutoff,
            "your_pct": your_pct,
            "gap": gap,
            "verdict": verdict,
            "passed": your_pct >= cutoff,
        }

        # --- Recommended actions ---
        recommendations = []

        # 1. Weakest section (only if there are >1 sections and one is clearly weak)
        if len(section_breakdown) > 1:
            weakest_section = min(section_breakdown, key=lambda s: s["pct"])
            if weakest_section["pct"] < cutoff:
                recommendations.append({
                    "type": "retake_section",
                    "action": f"Retake the {weakest_section['name']} section",
                    "reason": f"You scored {weakest_section['pct']:.0f}% — target {cutoff}%",
                })

        # 2. Course recommendations from the weakest topics
        weak_topics = [t for t in topic_breakdown if t["pct"] < cutoff][:3]
        seen_courses = set()
        for wt in weak_topics:
            suggestions = get_course_suggestions(wt["topic"])
            for course in suggestions:
                if course in seen_courses:
                    continue
                seen_courses.add(course)
                recommendations.append({
                    "type": "course",
                    "action": f"Take the course: {course}",
                    "reason": f"Fixes your weak area: {wt['topic']} ({wt['pct']:.0f}%)",
                })
                break  # one course per weak topic

        # 3. Retake the full drive
        if your_pct < cutoff:
            recommendations.append({
                "type": "retake_full",
                "action": f"Retake the full {company_name} drive",
                "reason": "After completing the course and section retake, aim for the cut-off",
            })

        # 4. If everything is above cutoff
        if not recommendations:
            recommendations.append({
                "type": "advance",
                "action": "You're ready — take the drive at a harder pattern",
                "reason": f"You scored above the {company_name} cut-off ({cutoff}%)",
            })

        # --- Question-by-question review (Session 43-B2) ---
        question_review = self.build_question_review(sections, answers)

        # Attach AI explanations to wrong answers
        wrong_items = [q for q in question_review if not q.get("is_correct")]
        if wrong_items:
            explanations = self.generate_ai_explanations(wrong_items)
            for q in question_review:
                key = (q.get("question") or "")[:200]
                q["ai_explanation"] = explanations.get(key, "")
        else:
            for q in question_review:
                q["ai_explanation"] = ""

        return {
            "section_breakdown": section_breakdown,
            "topic_breakdown": topic_breakdown,
            "cutoff_comparison": cutoff_comparison,
            "recommended_actions": recommendations,
            "question_review": question_review,
        }

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

            # Session 43-B1: compute full diagnostics
            try:
                diagnostics = self.compute_diagnostics(
                    company_id=company_id,
                    company_name=company_name,
                    sections=sections,
                    answers=answers,
                )
            except Exception as e:
                logger.warning(f"diagnostics failed: {e}")
                diagnostics = {
                    "section_breakdown": [],
                    "topic_breakdown": [],
                    "cutoff_comparison": {"cutoff_pct": 60, "your_pct": round(score, 1), "gap": 0, "verdict": "", "passed": passed},
                    "recommended_actions": [],
                }

            results = {
                "session_id": session_id,
                "email": email,
                "company": company_name,
                "company_id": company_id,
                "pattern": pattern,
                "total_questions": total_questions,
                "answered": answered,
                "correct": correct,
                "score": round(score, 1),
                "pass": passed,
                "sections": [{"name": s.get("name"), "count": s.get("count")} for s in sections],
                "diagnostics": diagnostics,
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