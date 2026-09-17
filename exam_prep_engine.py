"""
Charvak Global Exam Preparation Center
Complete AI-powered exam prep - 67 exams, 8 categories
(DB-backed - Session C/3)
"""
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.exam_prep")


class ExamPrepEngine:
    def __init__(self):
        self.exams = self._initialize_exams()
        self._ensure_tables()
        logger.info("Exam Prep Engine ready (DB-backed) - 67 exams, 8 categories")

    def _ensure_tables(self):
        """Idempotent table creation for exam prep tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_exam_question_bank (
                    question_id      TEXT PRIMARY KEY,
                    exam_id          TEXT NOT NULL,
                    topic            TEXT NOT NULL,
                    question_text    TEXT NOT NULL,
                    options          JSONB NOT NULL DEFAULT '[]'::jsonb,
                    correct_index    INTEGER NOT NULL DEFAULT 0,
                    explanation      TEXT DEFAULT '',
                    difficulty       TEXT DEFAULT 'Medium',
                    generated_by     TEXT DEFAULT 'ai',
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(exam_id, topic, question_text)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_qb_exam_topic ON charvak_exam_question_bank(exam_id, topic)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_qb_difficulty ON charvak_exam_question_bank(difficulty)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_exam_mock_tests (
                    test_id          TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    exam_id          TEXT NOT NULL,
                    topic            TEXT DEFAULT '',
                    status           TEXT NOT NULL DEFAULT 'in_progress',
                    total_questions  INTEGER DEFAULT 0,
                    correct_count    INTEGER DEFAULT 0,
                    score_pct        NUMERIC(5,2) DEFAULT 0,
                    started_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at     TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_tests_email ON charvak_exam_mock_tests(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_tests_exam ON charvak_exam_mock_tests(exam_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_tests_status ON charvak_exam_mock_tests(status)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_exam_test_answers (
                    answer_id        TEXT PRIMARY KEY,
                    test_id          TEXT NOT NULL,
                    question_id      TEXT NOT NULL,
                    selected_index   INTEGER,
                    is_correct       BOOLEAN DEFAULT FALSE,
                    answered_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(test_id, question_id)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_answers_test ON charvak_exam_test_answers(test_id)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_exam_user_progress (
                    email               TEXT NOT NULL,
                    exam_id             TEXT NOT NULL,
                    topic               TEXT NOT NULL DEFAULT '',
                    questions_attempted INTEGER DEFAULT 0,
                    questions_correct   INTEGER DEFAULT 0,
                    tests_completed     INTEGER DEFAULT 0,
                    best_score_pct      NUMERIC(5,2) DEFAULT 0,
                    last_practiced_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (email, exam_id, topic)
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_prog_email ON charvak_exam_user_progress(email)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_exam_study_plans (
                    plan_id          TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    exam_id          TEXT NOT NULL,
                    target_date      TEXT,
                    daily_minutes    INTEGER DEFAULT 60,
                    topics           JSONB DEFAULT '[]'::jsonb,
                    status           TEXT NOT NULL DEFAULT 'active',
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_plans_email ON charvak_exam_study_plans(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_exam_plans_status ON charvak_exam_study_plans(status)''')

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"exam_prep tables init failed: {e}")

    def _initialize_exams(self) -> Dict:
        """Static catalog - 67 exams, 8 categories. Reference data, versioned with code."""
        return {
            "central_govt": {"name": "Central Government & Staff Recruitment", "icon": "central_govt", "exams": [
                {"id": "ssc_cgl", "name": "SSC CGL", "full_name": "Combined Graduate Level", "tier": "Tier 1 & 2", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 100, "duration": "60 min"},
                {"id": "ssc_chsl", "name": "SSC CHSL", "full_name": "Combined Higher Secondary", "tier": "Tier 1 & 2", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 100, "duration": "60 min"},
                {"id": "ssc_mts", "name": "SSC MTS", "full_name": "Multi-Tasking Staff", "tier": "CBT", "sections": ["Reasoning", "Numerical", "English", "GK"], "questions": 90, "duration": "90 min"},
                {"id": "ssc_cpo", "name": "SSC CPO", "full_name": "Sub-Inspector", "tier": "Tier 1 & 2", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 200, "duration": "120 min"},
                {"id": "ssc_je", "name": "SSC JE", "full_name": "Junior Engineer", "tier": "CBT 1 & 2", "sections": ["Technical", "Reasoning", "Quant"], "questions": 200, "duration": "120 min"},
                {"id": "ssc_gd", "name": "SSC GD", "full_name": "General Duty Constable", "tier": "CBT", "sections": ["Reasoning", "GK", "Numerical"], "questions": 80, "duration": "60 min"},
                {"id": "ssc_steno", "name": "SSC Stenographer", "full_name": "Grade C & D", "tier": "CBT", "sections": ["Reasoning", "English", "GK"], "questions": 200, "duration": "120 min"},
                {"id": "rrb_ntpc", "name": "RRB NTPC", "full_name": "Non-Technical Popular Categories", "tier": "CBT 1 & 2", "sections": ["Reasoning", "Quant", "GK"], "questions": 100, "duration": "90 min"},
                {"id": "rrb_group_d", "name": "RRB Group D", "full_name": "Level-1 Posts", "tier": "CBT", "sections": ["Math", "Reasoning", "Science", "GK"], "questions": 100, "duration": "90 min"},
                {"id": "rrb_alp", "name": "RRB ALP", "full_name": "Assistant Loco Pilot", "tier": "CBT 1 & 2", "sections": ["Math", "Reasoning", "Technical"], "questions": 75, "duration": "60 min"},
                {"id": "rrb_je", "name": "RRB JE", "full_name": "Junior Engineer", "tier": "CBT 1 & 2", "sections": ["Technical", "Reasoning", "Quant"], "questions": 150, "duration": "120 min"},
                {"id": "upsc_epfo", "name": "UPSC EPFO", "full_name": "Enforcement Officer", "tier": "CBT", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 120, "duration": "120 min"}
            ]},
            "banking": {"name": "Banking & Financial", "icon": "banking", "exams": [
                {"id": "ibps_po", "name": "IBPS PO", "full_name": "Probationary Officer", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "ibps_clerk", "name": "IBPS Clerk", "full_name": "Customer Support Associate", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "ibps_so", "name": "IBPS SO", "full_name": "Specialist Officer", "tier": "Prelims & Mains", "sections": ["Technical", "Reasoning", "English"], "questions": 150, "duration": "120 min"},
                {"id": "ibps_rrb_officer", "name": "IBPS RRB Officer", "full_name": "Scale I, II, III", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 80, "duration": "45 min"},
                {"id": "ibps_rrb_assistant", "name": "IBPS RRB Assistant", "full_name": "Multipurpose", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant"], "questions": 80, "duration": "45 min"},
                {"id": "sbi_po", "name": "SBI PO", "full_name": "Probationary Officer", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "sbi_clerk", "name": "SBI Clerk", "full_name": "Junior Associate", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "rbi_grade_b", "name": "RBI Grade B", "full_name": "Direct Recruit", "tier": "Phase 1 & 2", "sections": ["Reasoning", "Quant", "English", "Finance"], "questions": 200, "duration": "120 min"},
                {"id": "rbi_assistant", "name": "RBI Assistant", "full_name": "Assistant", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "sebi_grade_a", "name": "SEBI Grade A", "full_name": "Assistant Manager", "tier": "Phase 1 & 2", "sections": ["Finance", "Reasoning", "English"], "questions": 200, "duration": "120 min"},
                {"id": "nabard", "name": "NABARD", "full_name": "Grade A & B", "tier": "Prelims & Mains", "sections": ["Agriculture", "Finance", "Reasoning"], "questions": 200, "duration": "120 min"},
                {"id": "lic_aao", "name": "LIC AAO", "full_name": "Assistant Administrative Officer", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "lic_ado", "name": "LIC ADO", "full_name": "Apprentice Development Officer", "tier": "CBT", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "niacl_ao", "name": "NIACL AO", "full_name": "New India Assurance AO", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"}
            ]},
            "engineering": {"name": "Engineering & Technology", "icon": "engineering", "exams": [
                {"id": "jee_main", "name": "JEE Main", "full_name": "Joint Entrance Examination", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 90, "duration": "180 min"},
                {"id": "bitsat", "name": "BITSAT", "full_name": "BITS Admission Test", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math", "English"], "questions": 130, "duration": "180 min"},
                {"id": "viteee", "name": "VITEEE", "full_name": "VIT Entrance Exam", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 125, "duration": "150 min"},
                {"id": "gate", "name": "GATE", "full_name": "Graduate Aptitude Test", "tier": "CBT", "sections": ["Technical", "Aptitude", "Math"], "questions": 65, "duration": "180 min"},
                {"id": "isro", "name": "ISRO", "full_name": "Scientist/Engineer", "tier": "CBT", "sections": ["Technical", "Aptitude"], "questions": 80, "duration": "90 min"},
                {"id": "barc", "name": "BARC", "full_name": "OCES/DGFS", "tier": "CBT", "sections": ["Technical", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "drdo", "name": "DRDO CEPTAM", "full_name": "Tier 1 & 2", "tier": "CBT", "sections": ["Technical", "Reasoning", "Quant"], "questions": 150, "duration": "120 min"}
            ]},
            "defense": {"name": "Defense & Security", "icon": "defense", "exams": [
                {"id": "afcat", "name": "AFCAT", "full_name": "Air Force Common Admission Test", "tier": "CBT", "sections": ["Verbal", "Numerical", "Reasoning", "GK"], "questions": 100, "duration": "120 min"},
                {"id": "army_agniveer", "name": "Army Agniveer", "full_name": "Common Entrance Exam", "tier": "CEE Online", "sections": ["Math", "GK", "Reasoning"], "questions": 50, "duration": "60 min"},
                {"id": "navy_agniveer", "name": "Navy Agniveer", "full_name": "SSR/MR", "tier": "INET Online", "sections": ["Math", "Science", "English"], "questions": 100, "duration": "60 min"},
                {"id": "airforce_agniveer", "name": "Airforce Agniveer", "full_name": "Vayu", "tier": "STAR Online", "sections": ["Math", "Physics", "English"], "questions": 100, "duration": "60 min"},
                {"id": "coast_guard", "name": "Coast Guard", "full_name": "Navik/Yantrik", "tier": "CBT", "sections": ["Math", "Science", "English"], "questions": 100, "duration": "60 min"},
                {"id": "capf", "name": "CAPF", "full_name": "Constable/SI", "tier": "CBT Tier 1", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"}
            ]},
            "medical": {"name": "Medical & Healthcare", "icon": "medical", "exams": [
                {"id": "neet_pg", "name": "NEET PG", "full_name": "Postgraduate Medical", "tier": "CBT", "sections": ["Medicine", "Surgery", "Pediatrics", "OBG"], "questions": 200, "duration": "210 min"},
                {"id": "ini_cet", "name": "INI-CET", "full_name": "AIIMS/JIPMER/PGI", "tier": "CBT", "sections": ["Medicine", "Surgery", "Pediatrics"], "questions": 200, "duration": "180 min"},
                {"id": "fmge", "name": "FMGE", "full_name": "Foreign Medical Graduate", "tier": "CBT", "sections": ["Medicine", "Surgery", "OBG"], "questions": 300, "duration": "300 min"},
                {"id": "neet_mds", "name": "NEET MDS", "full_name": "Dental Master's", "tier": "CBT", "sections": ["Dental Anatomy", "Pathology", "Pharmacology"], "questions": 240, "duration": "180 min"},
                {"id": "gpat", "name": "GPAT", "full_name": "Pharmacy Aptitude Test", "tier": "CBT", "sections": ["Pharmaceutics", "Pharmacology", "Chemistry"], "questions": 125, "duration": "180 min"}
            ]},
            "university": {"name": "University & Teaching", "icon": "university", "exams": [
                {"id": "cuet_ug", "name": "CUET UG", "full_name": "Undergraduate", "tier": "CBT", "sections": ["Language", "Domain Subjects", "General Test"], "questions": 175, "duration": "195 min"},
                {"id": "cuet_pg", "name": "CUET PG", "full_name": "Postgraduate", "tier": "CBT", "sections": ["Domain Subject", "General"], "questions": 100, "duration": "120 min"},
                {"id": "ugc_net", "name": "UGC NET", "full_name": "Assistant Professor/JRF", "tier": "CBT", "sections": ["Teaching Aptitude", "Research Aptitude", "Subject"], "questions": 150, "duration": "180 min"},
                {"id": "csir_net", "name": "CSIR NET", "full_name": "Science JRF", "tier": "CBT", "sections": ["Physical Sciences", "Chemical Sciences", "Life Sciences"], "questions": 150, "duration": "180 min"},
                {"id": "ctet", "name": "CTET", "full_name": "Teacher Eligibility", "tier": "CBT", "sections": ["Child Development", "Math", "Language"], "questions": 150, "duration": "150 min"}
            ]},
            "management": {"name": "Management & Law", "icon": "management", "exams": [
                {"id": "cat", "name": "CAT", "full_name": "IIM Admission", "tier": "CBT", "sections": ["VARC", "DILR", "Quant"], "questions": 66, "duration": "120 min"},
                {"id": "xat", "name": "XAT", "full_name": "Xavier Aptitude Test", "tier": "CBT", "sections": ["Verbal", "Decision Making", "Quant"], "questions": 100, "duration": "180 min"},
                {"id": "nmat", "name": "NMAT", "full_name": "NMIMS Admission", "tier": "CBT", "sections": ["Language", "Quant", "Logical"], "questions": 108, "duration": "120 min"},
                {"id": "snap", "name": "SNAP", "full_name": "Symbiosis Admission", "tier": "CBT", "sections": ["General English", "Quant", "Reasoning"], "questions": 60, "duration": "60 min"},
                {"id": "cmat", "name": "CMAT", "full_name": "Management Admission", "tier": "CBT", "sections": ["Quant", "Reasoning", "Language"], "questions": 100, "duration": "180 min"},
                {"id": "clat", "name": "CLAT PG", "full_name": "Law Admission", "tier": "CBT", "sections": ["Legal Reasoning", "English", "GK"], "questions": 120, "duration": "120 min"},
                {"id": "ceed", "name": "CEED/UCEED", "full_name": "Design Admissions", "tier": "CBT", "sections": ["Design Aptitude", "Visualization", "Creativity"], "questions": 100, "duration": "180 min"}
            ]},
            "state_exams": {"name": "State Level Exams", "icon": "state_exams", "exams": [
                {"id": "mht_cet", "name": "MHT-CET", "full_name": "Maharashtra", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 150, "duration": "180 min"},
                {"id": "ap_eapcet", "name": "AP EAPCET", "full_name": "Andhra Pradesh", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 160, "duration": "180 min"},
                {"id": "ts_eapcet", "name": "TS EAPCET", "full_name": "Telangana", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 160, "duration": "180 min"},
                {"id": "wbjee", "name": "WBJEE", "full_name": "West Bengal", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 155, "duration": "180 min"},
                {"id": "upsssc", "name": "UPSSSC", "full_name": "Uttar Pradesh", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "mppeb", "name": "MPPEB", "full_name": "Madhya Pradesh (Vyapam)", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "rsmssb", "name": "RSMSSB", "full_name": "Rajasthan", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "jssc", "name": "JSSC", "full_name": "Jharkhand", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "bpsc", "name": "BPSC", "full_name": "Bihar", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "appsc", "name": "APPSC", "full_name": "Andhra Pradesh PSC", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "tspsc", "name": "TSPSC", "full_name": "Telangana PSC", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"}
            ]}
        }

    def get_all_categories(self) -> Dict:
        """Get all categories with exam counts."""
        categories = []
        total_exams = 0
        for cat_id, cat_data in self.exams.items():
            categories.append({"id": cat_id, "name": cat_data["name"], "icon": cat_data["icon"], "exam_count": len(cat_data["exams"])})
            total_exams += len(cat_data["exams"])
        return {"status": "success", "total_categories": len(categories), "total_exams": total_exams, "categories": categories}

    def get_exams_by_category(self, category_id: str) -> Dict:
        """Get all exams in a category."""
        if category_id not in self.exams:
            return {"status": "error", "message": "Category not found"}
        return {"status": "success", "category": self.exams[category_id]["name"], "icon": self.exams[category_id]["icon"], "exams": self.exams[category_id]["exams"]}

    def get_exam_details(self, exam_id: str) -> Dict:
        """Get details for specific exam."""
        for cat_data in self.exams.values():
            for exam in cat_data["exams"]:
                if exam["id"] == exam_id:
                    return {"status": "success", "exam": exam, "category": cat_data["name"]}
        return {"status": "error", "message": f"Exam {exam_id} not found"}

    def _get_exam_name(self, exam_id: str) -> str:
        for cat_data in self.exams.values():
            for exam in cat_data["exams"]:
                if exam["id"] == exam_id:
                    return exam["name"]
        return exam_id

    def _stub_questions(self, exam_id: str, topic: str, count: int) -> List[Dict]:
        """Fallback stub questions if AI is unavailable."""
        questions = []
        for i in range(count):
            difficulty = "Easy" if i < count // 3 else "Medium" if i < 2 * count // 3 else "Hard"
            questions.append({
                "question_id": f"STUB-{secrets.token_hex(4).upper()}",
                "question": f"{topic} - Question {i + 1} (stub)",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct": i % 4,
                "explanation": f"Explanation for question {i + 1}",
                "difficulty": difficulty,
            })
        return questions

    def _load_from_bank(self, exam_id: str, topic: str, count: int) -> List[Dict]:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT question_id, question_text, options, correct_index,
                       explanation, difficulty
                FROM charvak_exam_question_bank
                WHERE exam_id = %s AND topic = %s
                ORDER BY RANDOM()
                LIMIT %s
            ''', (exam_id, topic, count))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_load_from_bank failed: {e}")
            return []

        return [{
            "question_id": r[0],
            "question": r[1],
            "options": r[2] if isinstance(r[2], list) else json.loads(r[2] or "[]"),
            "correct": r[3],
            "explanation": r[4] or "",
            "difficulty": r[5] or "Medium",
        } for r in rows]

    def _generate_via_ai(self, exam_id: str, topic: str, count: int) -> List[Dict]:
        """Generate questions via OpenAI and insert into bank."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.warning("OPENAI_API_KEY missing - returning stub questions")
            return self._stub_questions(exam_id, topic, count)

        exam_name = self._get_exam_name(exam_id)
        prompt = (
            f"Generate {count} multiple-choice practice questions for the {exam_name} exam, "
            f"topic: {topic}. Return ONLY a JSON array. Each item: "
            '{"question": "...", "options": ["A","B","C","D"], "correct": 0, '
            '"explanation": "...", "difficulty": "Easy|Medium|Hard"} '
            "where 'correct' is the 0-based index of the correct option. No markdown, no prose."
        )

        try:
            import requests
            r = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                },
                timeout=45,
            )
            r.raise_for_status()
            content = r.json()["choices"][0]["message"]["content"].strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
        except Exception as e:
            logger.error(f"AI question generation failed: {e}")
            return self._stub_questions(exam_id, topic, count)

        inserted = []
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            for q in parsed:
                qid = f"QB-{secrets.token_hex(4).upper()}"
                options = q.get("options", [])
                correct = int(q.get("correct", 0))
                if not options or not (0 <= correct < len(options)):
                    continue
                try:
                    cur.execute('''
                        INSERT INTO charvak_exam_question_bank
                            (question_id, exam_id, topic, question_text, options,
                             correct_index, explanation, difficulty, generated_by)
                        VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, 'ai')
                        ON CONFLICT (exam_id, topic, question_text) DO NOTHING
                    ''', (
                        qid, exam_id, topic, q.get("question", ""),
                        json.dumps(options), correct,
                        q.get("explanation", ""), q.get("difficulty", "Medium"),
                    ))
                except Exception as inner:
                    logger.error(f"insert question failed: {inner}")
                    continue
                inserted.append({
                    "question_id": qid,
                    "question": q.get("question", ""),
                    "options": options,
                    "correct": correct,
                    "explanation": q.get("explanation", ""),
                    "difficulty": q.get("difficulty", "Medium"),
                })
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"AI bank insert failed: {e}")
            return self._stub_questions(exam_id, topic, count)

        if not inserted:
            return self._stub_questions(exam_id, topic, count)
        return inserted

    def generate_questions(self, exam_id: str, topic: str, count: int = 10) -> Dict:
        """Generate practice questions - bank-first, AI-fill, cache."""
        if exam_id not in [e["id"] for cat in self.exams.values() for e in cat["exams"]]:
            return {"status": "error", "message": f"Exam {exam_id} not found"}

        try:
            count = max(1, min(int(count), 50))
        except Exception:
            count = 10

        bank = self._load_from_bank(exam_id, topic, count)
        if len(bank) >= count:
            return {"status": "success", "exam_id": exam_id, "topic": topic,
                    "questions": bank[:count], "source": "bank"}

        needed = count - len(bank)
        fresh = self._generate_via_ai(exam_id, topic, needed)
        combined = bank + fresh
        return {"status": "success", "exam_id": exam_id, "topic": topic,
                "questions": combined[:count], "source": "bank+ai" if bank else "ai"}

    def start_mock_test(self, exam_id: str, email: str, topic: str = None, count: int = 10) -> Dict:
        """Start a mock test - generates questions, persists attempt."""
        topic = topic or "General"
        try:
            count = max(1, min(int(count), 50))
        except Exception:
            count = 10

        gen = self.generate_questions(exam_id, topic, count)
        if gen.get("status") != "success":
            return gen
        questions = gen["questions"]

        test_id = f"TEST-{secrets.token_hex(6).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_exam_mock_tests
                    (test_id, email, exam_id, topic, status, total_questions)
                VALUES (%s, %s, %s, %s, 'in_progress', %s)
            ''', (test_id, email, exam_id, topic, len(questions)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_mock_test failed: {e}")
            return {"status": "error", "message": "Could not start mock test"}

        return {
            "status": "success",
            "test_id": test_id,
            "exam_id": exam_id,
            "email": email,
            "topic": topic,
            "total_questions": len(questions),
            "questions": questions,
            "started_at": datetime.now().isoformat(),
        }

    def submit_answer(self, test_id: str, question_id: str, selected_index: int) -> Dict:
        """Record an answer for a question in a mock test."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT status FROM charvak_exam_mock_tests WHERE test_id = %s', (test_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Test not found"}
            if row[0] != "in_progress":
                cur.close(); conn.close()
                return {"status": "error", "message": "Test already completed"}

            cur.execute('SELECT correct_index FROM charvak_exam_question_bank WHERE question_id = %s', (question_id,))
            qrow = cur.fetchone()
            if not qrow:
                cur.close(); conn.close()
                return {"status": "error", "message": "Question not found"}

            is_correct = int(selected_index) == int(qrow[0])
            answer_id = f"ANS-{secrets.token_hex(4).upper()}"

            cur.execute('''
                INSERT INTO charvak_exam_test_answers
                    (answer_id, test_id, question_id, selected_index, is_correct)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (test_id, question_id)
                DO UPDATE SET selected_index = EXCLUDED.selected_index,
                              is_correct = EXCLUDED.is_correct,
                              answered_at = CURRENT_TIMESTAMP
            ''', (answer_id, test_id, question_id, int(selected_index), is_correct))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"submit_answer failed: {e}")
            return {"status": "error", "message": "Could not submit answer"}

        return {"status": "success", "is_correct": is_correct}

    def complete_test(self, test_id: str) -> Dict:
        """Score and finalize a mock test, update user progress."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT email, exam_id, topic, total_questions, status
                FROM charvak_exam_mock_tests WHERE test_id = %s
            ''', (test_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Test not found"}
            email, exam_id, topic, total_questions, status = row
            if status == "completed":
                cur.close(); conn.close()
                return {"status": "error", "message": "Test already completed"}

            cur.execute('''
                SELECT COUNT(*), COALESCE(SUM(CASE WHEN is_correct THEN 1 ELSE 0 END), 0)
                FROM charvak_exam_test_answers WHERE test_id = %s
            ''', (test_id,))
            attempted, correct = cur.fetchone()
            attempted = int(attempted or 0)
            correct = int(correct or 0)
            total = int(total_questions or 0) or attempted or 1
            score_pct = round(correct * 100.0 / total, 2)

            cur.execute('''
                UPDATE charvak_exam_mock_tests
                SET status = 'completed', correct_count = %s, score_pct = %s,
                    completed_at = CURRENT_TIMESTAMP
                WHERE test_id = %s
            ''', (correct, score_pct, test_id))

            cur.execute('''
                INSERT INTO charvak_exam_user_progress
                    (email, exam_id, topic, questions_attempted, questions_correct,
                     tests_completed, best_score_pct, last_practiced_at)
                VALUES (%s, %s, %s, %s, %s, 1, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (email, exam_id, topic) DO UPDATE SET
                    questions_attempted = charvak_exam_user_progress.questions_attempted + EXCLUDED.questions_attempted,
                    questions_correct   = charvak_exam_user_progress.questions_correct   + EXCLUDED.questions_correct,
                    tests_completed     = charvak_exam_user_progress.tests_completed     + 1,
                    best_score_pct      = GREATEST(charvak_exam_user_progress.best_score_pct, EXCLUDED.best_score_pct),
                    last_practiced_at   = CURRENT_TIMESTAMP
            ''', (email, exam_id, topic, attempted, correct, score_pct))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"complete_test failed: {e}")
            return {"status": "error", "message": "Could not complete test"}

        return {
            "status": "success",
            "test_id": test_id,
            "correct_count": correct,
            "total_questions": total,
            "score_pct": score_pct,
        }

    def get_user_progress(self, email: str, exam_id: str = None) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if exam_id:
                cur.execute('''
                    SELECT email, exam_id, topic, questions_attempted, questions_correct,
                           tests_completed, best_score_pct, last_practiced_at
                    FROM charvak_exam_user_progress
                    WHERE email = %s AND exam_id = %s
                    ORDER BY last_practiced_at DESC
                ''', (email, exam_id))
            else:
                cur.execute('''
                    SELECT email, exam_id, topic, questions_attempted, questions_correct,
                           tests_completed, best_score_pct, last_practiced_at
                    FROM charvak_exam_user_progress
                    WHERE email = %s
                    ORDER BY last_practiced_at DESC
                ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_user_progress failed: {e}")
            return {"status": "error", "message": "Could not load progress"}

        progress = [{
            "email": r[0], "exam_id": r[1], "topic": r[2],
            "questions_attempted": r[3], "questions_correct": r[4],
            "tests_completed": r[5], "best_score_pct": float(r[6]) if r[6] is not None else 0,
            "last_practiced_at": r[7].isoformat() if hasattr(r[7], "isoformat") else str(r[7]),
        } for r in rows]
        return {"status": "success", "progress": progress, "count": len(progress)}

    def get_test_history(self, email: str, exam_id: str = None) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if exam_id:
                cur.execute('''
                    SELECT test_id, email, exam_id, topic, status, total_questions,
                           correct_count, score_pct, started_at, completed_at
                    FROM charvak_exam_mock_tests
                    WHERE email = %s AND exam_id = %s
                    ORDER BY started_at DESC
                ''', (email, exam_id))
            else:
                cur.execute('''
                    SELECT test_id, email, exam_id, topic, status, total_questions,
                           correct_count, score_pct, started_at, completed_at
                    FROM charvak_exam_mock_tests
                    WHERE email = %s
                    ORDER BY started_at DESC
                ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_test_history failed: {e}")
            return {"status": "error", "message": "Could not load history"}

        history = [{
            "test_id": r[0], "email": r[1], "exam_id": r[2], "topic": r[3],
            "status": r[4], "total_questions": r[5], "correct_count": r[6],
            "score_pct": float(r[7]) if r[7] is not None else 0,
            "started_at": r[8].isoformat() if hasattr(r[8], "isoformat") else str(r[8]),
            "completed_at": r[9].isoformat() if r[9] and hasattr(r[9], "isoformat") else None,
        } for r in rows]
        return {"status": "success", "history": history, "count": len(history)}

    def create_study_plan(self, data: Dict) -> Dict:
        plan_id = f"PLAN-{secrets.token_hex(4).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_exam_study_plans
                    (plan_id, email, exam_id, target_date, daily_minutes, topics, status)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, 'active')
            ''', (
                plan_id,
                data.get("email"),
                data.get("exam_id"),
                data.get("target_date", ""),
                int(data.get("daily_minutes", 60)),
                json.dumps(data.get("topics", [])),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_study_plan failed: {e}")
            return {"status": "error", "message": "Could not create study plan"}
        return {"status": "success", "plan_id": plan_id, "message": "Study plan created!"}

    def get_study_plan(self, email: str, exam_id: str = None) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            if exam_id:
                cur.execute('''
                    SELECT plan_id, email, exam_id, target_date, daily_minutes, topics, status, created_at
                    FROM charvak_exam_study_plans
                    WHERE email = %s AND exam_id = %s
                    ORDER BY created_at DESC
                ''', (email, exam_id))
            else:
                cur.execute('''
                    SELECT plan_id, email, exam_id, target_date, daily_minutes, topics, status, created_at
                    FROM charvak_exam_study_plans
                    WHERE email = %s
                    ORDER BY created_at DESC
                ''', (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_study_plan failed: {e}")
            return {"status": "error", "message": "Could not load study plans"}

        plans = [{
            "plan_id": r[0], "email": r[1], "exam_id": r[2], "target_date": r[3],
            "daily_minutes": r[4],
            "topics": r[5] if isinstance(r[5], list) else json.loads(r[5] or "[]"),
            "status": r[6],
            "created_at": r[7].isoformat() if hasattr(r[7], "isoformat") else str(r[7]),
        } for r in rows]
        return {"status": "success", "plans": plans, "count": len(plans)}


exam_prep_engine = ExamPrepEngine()
