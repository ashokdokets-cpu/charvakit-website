"""
Charvak Career Assessment Engine
Session 10 Phase 1 — MCQ career readiness assessments calibrated to
(role x industry x experience level). Session 11+ adds more formats.
"""

import os
import json
import logging
import secrets
import random
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.career_assessment")


# ============================================================
# CATALOG — single source of truth for the whole product
# ============================================================

CAREER_ROLES = {
    "Engineering & Software": [
        "Frontend Engineer", "Backend Engineer", "Full-Stack Engineer",
        "Mobile Engineer (iOS)", "Mobile Engineer (Android)",
        "Mobile Engineer (Cross-Platform)",
        "Data Engineer", "ML Engineer", "AI Engineer",
        "DevOps Engineer", "Site Reliability Engineer (SRE)",
        "Platform Engineer", "Cloud Engineer",
        "Security Engineer", "Application Security Engineer",
        "Penetration Tester", "QA / Test Engineer",
        "Automation Test Engineer", "Embedded Systems Engineer",
        "Firmware Engineer", "Solutions Architect",
        "Enterprise Architect", "Technical Program Manager",
        "Technical Writer", "Developer Advocate",
    ],
    "Data & Analytics": [
        "Data Analyst", "Data Scientist", "Business Intelligence Analyst",
        "Analytics Engineer", "Quantitative Analyst", "Statistician",
        "Machine Learning Researcher", "Applied Scientist",
    ],
    "Product & Design": [
        "Product Manager", "Technical Product Manager", "Product Owner",
        "Project Manager", "Scrum Master", "Program Manager",
        "UX Designer", "UI Designer", "Product Designer",
        "UX Researcher", "Interaction Designer", "Visual Designer",
        "Motion Designer", "Graphic Designer", "Service Designer",
    ],
    "Business & Strategy": [
        "Business Analyst", "Systems Analyst", "Management Consultant",
        "Strategy Consultant", "Operations Manager", "Operations Analyst",
        "Finance Analyst", "Financial Analyst", "Accountant", "Auditor",
        "Investment Banking Analyst", "Risk Analyst", "Compliance Officer",
        "Legal Counsel", "Corporate Lawyer", "Paralegal",
    ],
    "Go-to-Market": [
        "Marketing Specialist", "Growth Marketer", "Performance Marketer",
        "Content Strategist", "Content Writer / Copywriter",
        "SEO Specialist", "Social Media Manager", "Brand Manager",
        "Product Marketing Manager", "Demand Generation Manager",
        "Sales Executive (SDR/BDR)", "Account Executive",
        "Account Manager", "Sales Engineer",
        "Customer Success Manager", "Customer Support Specialist",
        "Partnerships Manager", "Community Manager", "Events Manager",
    ],
    "People & HR": [
        "Recruiter / Talent Acquisition", "HR Generalist",
        "HR Business Partner", "HR Operations Specialist",
        "Learning & Development Specialist",
        "Compensation & Benefits Analyst", "People Analytics Specialist",
    ],
    "Domain-Specific": [
        "Healthcare Administrator", "Clinical Research Associate",
        "Pharmacovigilance Specialist", "Medical Coder",
        "Teacher / Educator", "Curriculum Designer",
        "Academic Researcher", "Civil Engineer", "Mechanical Engineer",
        "Electrical Engineer", "Chemical Engineer", "Industrial Engineer",
        "Petroleum Engineer", "Aerospace Engineer",
        "Biomedical Engineer", "Environmental Engineer",
    ],
}

CAREER_INDUSTRIES = [
    "IT / Tech (general)", "SaaS / B2B Software", "FinTech / Payments",
    "InsurTech", "RegTech", "WealthTech", "Banking / BFSI",
    "HealthTech / Digital Health", "BioTech / Life Sciences",
    "MedTech / Medical Devices", "Pharma", "EdTech", "LegalTech",
    "AgriTech", "FoodTech", "PropTech / Real Estate",
    "Construction Tech", "LogisticsTech / Supply Chain",
    "Mobility / Transportation", "Aviation / Aerospace",
    "Automotive (EV / Traditional)", "Robotics", "Semiconductors",
    "Cybersecurity", "Cloud Infrastructure", "AI / ML Research",
    "Data Infrastructure / Analytics", "Web3 / Blockchain / Crypto",
    "Gaming / Esports", "Media & Entertainment", "Streaming / OTT",
    "Music", "Publishing", "AdTech", "MarTech",
    "RetailTech / E-commerce", "D2C / Consumer Brands",
    "Marketplace / Platform", "Travel & Hospitality",
    "Food & Beverage / QSR", "Telecom", "Energy / Oil & Gas",
    "Renewables / CleanTech", "Utilities", "Mining & Metals",
    "Chemicals", "Consumer Packaged Goods (CPG)",
    "Fashion & Apparel", "Beauty & Wellness", "Sports & Fitness",
    "Non-profit / NGO", "Government / Public Sector / GovTech",
    "Defense & Space", "Education (K-12 / Higher Ed)",
    "Consulting / Professional Services", "Staffing & Recruiting",
    "Freelance / Gig Economy", "HR Tech", "Legal Services",
    "Accounting / Audit", "Investment / PE / VC", "Insurance",
    "Print / Packaging", "Agriculture / Farming",
    "Fishing / Aquaculture", "Forestry",
]

CAREER_LEVELS = [
    {"key": "intern",    "label": "Intern / Student",  "years": "0 years (student)", "blurb": "Fundamentals, tooling, basic problem solving"},
    {"key": "junior",    "label": "Junior",            "years": "0-2 years",         "blurb": "Applied basics, small features, learning under guidance"},
    {"key": "mid",       "label": "Mid-Level",         "years": "2-5 years",         "blurb": "Owns features, trade-offs, real-world scenarios"},
    {"key": "senior",    "label": "Senior",            "years": "5-10 years",        "blurb": "Architecture, strategy, cross-functional influence"},
    {"key": "staff",     "label": "Staff / Principal", "years": "10+ years",         "blurb": "Org-wide impact, systems thinking, technical vision"},
    {"key": "manager",   "label": "Manager / Director","years": "People leadership", "blurb": "Prioritization, delivery, coaching teams"},
    {"key": "executive", "label": "Executive (VP/C-level)", "years": "Org leadership", "blurb": "Strategy, P&L, board-level decisions"},
]

CAREER_FORMATS = [
    {"key": "mcq", "label": "Multiple Choice", "phase": 1, "available": True,
     "description": "4-option MCQs, deterministic scoring"},
    # Phase 2 will add: coding, sql, system_design, debugging,
    # behavioral, case_study, short_answer, numeracy, situational_judgment
]

# Size options -> credits (mirrored in ai_credit_engine.py)
CAREER_SIZES = {
    "quick":    {"questions": 10, "credits": 15, "key": "career_assessment_quick"},
    "standard": {"questions": 15, "credits": 25, "key": "career_assessment_standard"},
    "full":     {"questions": 20, "credits": 35, "key": "career_assessment_full"},
}

PASSING_SCORE = 70


class CareerAssessmentEngine:
    """Career readiness assessments calibrated to role x industry x level."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Career Assessment Engine ready")

    def _ensure_tables(self) -> None:
        """Create career-assessment tables if they don't exist."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_career_assessments (
                    assessment_id  TEXT PRIMARY KEY,
                    email          TEXT NOT NULL,
                    role           TEXT NOT NULL,
                    industry       TEXT NOT NULL,
                    level          TEXT NOT NULL,
                    format         TEXT NOT NULL DEFAULT 'mcq',
                    size           TEXT NOT NULL DEFAULT 'quick',
                    num_questions  INTEGER NOT NULL DEFAULT 10,
                    questions_json JSONB NOT NULL DEFAULT '[]'::jsonb,
                    status         TEXT NOT NULL DEFAULT 'in_progress',
                    score          INTEGER,
                    passed         BOOLEAN,
                    correct_count  INTEGER,
                    started_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at   TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_career_assess_email
                    ON charvak_career_assessments (email, started_at DESC)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_career_assess_status
                    ON charvak_career_assessments (status, started_at DESC)
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_career_assessment_answers (
                    answer_id      TEXT PRIMARY KEY,
                    assessment_id  TEXT NOT NULL,
                    question_index INTEGER NOT NULL,
                    selected_index INTEGER,
                    is_correct     BOOLEAN,
                    answered_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(assessment_id, question_index)
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_career_answers_assess
                    ON charvak_career_assessment_answers (assessment_id, question_index)
            """)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"career-assessment table init failed: {e}")

    # ------------------------------------------------------------
    # Catalog
    # ------------------------------------------------------------

    def get_catalog(self) -> Dict:
        """Return the full catalog. Public, no auth."""
        return {
            "status": "success",
            "roles": CAREER_ROLES,
            "industries": CAREER_INDUSTRIES,
            "levels": CAREER_LEVELS,
            "formats": CAREER_FORMATS,
            "sizes": {k: {"questions": v["questions"], "credits": v["credits"]}
                      for k, v in CAREER_SIZES.items()},
            "passing_score": PASSING_SCORE,
        }

    # ------------------------------------------------------------
    # Start
    # ------------------------------------------------------------

    def start_assessment(self, data: Dict) -> Dict:
        """
        Create a career assessment.
        data = {email, role, industry, level, size, format}
        """
        email = (data.get("email") or "").strip().lower()
        role = (data.get("role") or "").strip()
        industry = (data.get("industry") or "").strip()
        level_key = (data.get("level") or "mid").strip().lower()
        size_key = (data.get("size") or "quick").strip().lower()
        fmt = (data.get("format") or "mcq").strip().lower()

        if not email:
            return {"status": "error", "message": "email required"}
        if not role:
            return {"status": "error", "message": "role required"}
        if not industry:
            return {"status": "error", "message": "industry required"}

        # Validate
        if size_key not in CAREER_SIZES:
            return {"status": "error", "message": f"Unknown size: {size_key}"}
        if level_key not in [l["key"] for l in CAREER_LEVELS]:
            return {"status": "error", "message": f"Unknown level: {level_key}"}
        if fmt != "mcq":
            return {"status": "error", "message": f"Format '{fmt}' not available yet"}

        # Flatten role list for validation
        all_roles = []
        for cat, roles in CAREER_ROLES.items():
            all_roles.extend(roles)
        if role not in all_roles:
            return {"status": "error", "message": f"Unknown role: {role}"}
        if industry not in CAREER_INDUSTRIES:
            return {"status": "error", "message": f"Unknown industry: {industry}"}

        size = CAREER_SIZES[size_key]
        num_questions = size["questions"]
        level_label = next((l["label"] for l in CAREER_LEVELS if l["key"] == level_key), level_key)
        level_blurb = next((l["blurb"] for l in CAREER_LEVELS if l["key"] == level_key), "")

        self._ensure_tables()

        # Generate questions
        questions = self._generate_questions(
            role=role, industry=industry,
            level_key=level_key, level_label=level_label,
            level_blurb=level_blurb, num_questions=num_questions,
        )
        if not questions:
            return {"status": "error", "message": "Could not generate questions. Please try again."}

        assessment_id = f"CAR-{secrets.token_hex(5).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_career_assessments
                    (assessment_id, email, role, industry, level, format,
                     size, num_questions, questions_json, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, 'in_progress')
            """, (assessment_id, email, role, industry, level_key, fmt,
                  size_key, num_questions, json.dumps(questions)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"start_assessment persist failed: {e}")
            return {"status": "error", "message": "Could not save assessment"}

        # Strip correct_index before sending to frontend
        safe_questions = []
        for q in questions:
            safe_questions.append({
                "q": q.get("q", ""),
                "options": q.get("options", []),
            })

        return {
            "status": "success",
            "assessment_id": assessment_id,
            "assessment": {
                "assessment_id": assessment_id,
                "role": role,
                "industry": industry,
                "level": level_key,
                "level_label": level_label,
                "format": fmt,
                "size": size_key,
                "num_questions": num_questions,
                "questions": safe_questions,
                "passing_score": PASSING_SCORE,
                "started_at": datetime.now().isoformat(),
            },
            "message": f"{role} in {industry} assessment started",
        }

    # ------------------------------------------------------------
    # Question generation
    # ------------------------------------------------------------

    def _generate_questions(
        self, role: str, industry: str, level_key: str,
        level_label: str, level_blurb: str, num_questions: int
    ) -> List[Dict]:
        """Generate MCQs via OpenAI. Batched for 15/20. Returns [] on failure."""
        import os as _os
        api_key = _os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return []

        batches = []
        remaining = num_questions
        while remaining > 0:
            chunk = min(remaining, 10)
            batches.append(chunk)
            remaining -= chunk

        all_questions = []
        for batch_size in batches:
            batch = self._generate_one_batch(
                role=role, industry=industry,
                level_key=level_key, level_label=level_label,
                level_blurb=level_blurb, count=batch_size,
            )
            if not batch:
                return []
            all_questions.extend(batch)

        cleaned = []
        for q in all_questions:
            if not isinstance(q, dict):
                continue
            text = (q.get("q") or "").strip()
            options = q.get("options", [])
            ci = q.get("correct_index")
            if not text or not isinstance(options, list) or len(options) < 2:
                continue
            if not isinstance(ci, int) or ci < 0 or ci >= len(options):
                continue
            cleaned_q = {
                "q": text,
                "options": [str(o).strip() for o in options[:4]],
                "correct_index": ci,
            }
            cleaned_q = self._shuffle_question_options(cleaned_q)
            cleaned.append(cleaned_q)

        if len(cleaned) < num_questions:
            logger.warning(f"Generated {len(cleaned)} valid, wanted {num_questions}")
        return cleaned[:num_questions]

    def _generate_one_batch(
        self, role: str, industry: str, level_key: str,
        level_label: str, level_blurb: str, count: int
    ) -> List[Dict]:
        """Single OpenAI call for a batch of MCQs. Returns [] on failure."""
        import os as _os
        import requests
        api_key = _os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return []

        prompt = (
            f"Generate {count} multiple-choice questions for a career readiness "
            f"assessment.\n"
            f"TARGET ROLE: {role}\n"
            f"INDUSTRY: {industry}\n"
            f"EXPERIENCE LEVEL: {level_label} ({level_blurb})\n"
            f"\n"
            f"Calibrate the questions to what a real interviewer at the "
            f"{level_label} level would ask for a {role} in {industry}.\n"
            f"\n"
            f"Rules:\n"
            f"- Each question MUST have exactly 4 options and one correct answer.\n"
            f"- Test practical knowledge, not trivia.\n"
            f"- Include trade-offs, real-world scenarios, and tool familiarity "
            f"appropriate to {industry}.\n"
            f"- correct_index is 0-based (0, 1, 2, or 3).\n"
            f"- CRITICAL: Vary correct_index across questions. Do NOT always "
            f"put the correct answer at position 0.\n"
            f"- Aim for a roughly even distribution across 0, 1, 2, 3.\n"
            f"- Keep options concise (1-15 words each).\n"
            f"- Questions and options in English.\n"
            f"- Return exactly {count} questions.\n"
            f"\n"
            f'Return JSON: {{"questions": [{{"q": "...", "options": ["...","...","...","..."], "correct_index": 0}}]}}'
        )

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "response_format": {"type": "json_object"},
                },
                timeout=45,
            )
            resp = response.json()
            content = (resp.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
            questions = parsed.get("questions", [])
            if questions and isinstance(questions, list):
                return questions
            return []
        except Exception as e:
            logger.error(f"career-assessment AI batch failed: {e}")
            return []

    def _shuffle_question_options(self, q: Dict) -> Dict:
        """Shuffle options and recompute correct_index. Safety net."""
        options = list(q.get("options", []))
        ci = q.get("correct_index")
        if not options or not isinstance(ci, int) or ci < 0 or ci >= len(options):
            return q
        correct_text = options[ci]
        random.shuffle(options)
        q["options"] = options
        try:
            q["correct_index"] = options.index(correct_text)
        except ValueError:
            q["correct_index"] = ci
        return q

    # ------------------------------------------------------------
    # Answer / Complete
    # ------------------------------------------------------------

    def submit_answer(self, data: Dict) -> Dict:
        """
        Record one answer. Idempotent per (assessment_id, question_index).
        data = {email, assessment_id, question_index, selected_index}
        """
        email = (data.get("email") or "").strip().lower()
        assessment_id = (data.get("assessment_id") or "").strip()
        try:
            q_index = int(data.get("question_index"))
            selected = int(data.get("selected_index"))
        except (ValueError, TypeError):
            return {"status": "error", "message": "question_index and selected_index must be integers"}

        if not email or not assessment_id:
            return {"status": "error", "message": "email and assessment_id required"}

        self._ensure_tables()

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            # Ownership check
            cur.execute(
                "SELECT email, questions_json FROM charvak_career_assessments WHERE assessment_id = %s",
                (assessment_id,),
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Assessment not found"}
            if row[0] != email:
                cur.close(); conn.close()
                return {"status": "error", "message": "Not your assessment"}

            questions = row[1] if isinstance(row[1], list) else json.loads(row[1] or "[]")
            if q_index < 0 or q_index >= len(questions):
                cur.close(); conn.close()
                return {"status": "error", "message": "Invalid question_index"}

            correct_index = questions[q_index].get("correct_index")
            is_correct = (selected == correct_index)

            answer_id = f"ANS-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_career_assessment_answers
                    (answer_id, assessment_id, question_index, selected_index, is_correct)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (assessment_id, question_index) DO UPDATE
                SET selected_index = EXCLUDED.selected_index,
                    is_correct = EXCLUDED.is_correct,
                    answered_at = CURRENT_TIMESTAMP
            """, (answer_id, assessment_id, q_index, selected, is_correct))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"submit_answer failed: {e}")
            return {"status": "error", "message": "Could not save answer"}

        return {"status": "success", "assessment_id": assessment_id,
                "question_index": q_index, "recorded": True}

    def complete_assessment(self, data: Dict) -> Dict:
        """
        Score the assessment and persist to charvak_assessment_results.
        data = {email, assessment_id, answers: Optional[List[int]]}
        If answers provided, they're written first (single-shot submit).
        """
        email = (data.get("email") or "").strip().lower()
        assessment_id = (data.get("assessment_id") or "").strip()
        if not email or not assessment_id:
            return {"status": "error", "message": "email and assessment_id required"}

        self._ensure_tables()

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT email, role, industry, level, size, num_questions,
                       questions_json, status
                FROM charvak_career_assessments
                WHERE assessment_id = %s
            """, (assessment_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Assessment not found"}
            if row[0] != email:
                cur.close(); conn.close()
                return {"status": "error", "message": "Not your assessment"}
            if row[7] == "completed":
                cur.close(); conn.close()
                return {"status": "error", "message": "Assessment already completed"}

            _, role, industry, level, size, num_questions, questions_json, _ = row
            questions = questions_json if isinstance(questions_json, list) else json.loads(questions_json or "[]")

            # Optional bulk answer write
            if isinstance(data.get("answers"), list):
                for i, sel in enumerate(data["answers"]):
                    if i >= len(questions):
                        break
                    try:
                        sel_int = int(sel) if sel is not None else -1
                    except (ValueError, TypeError):
                        sel_int = -1
                    correct_index = questions[i].get("correct_index")
                    is_correct = (sel_int == correct_index)
                    cur.execute("""
                        INSERT INTO charvak_career_assessment_answers
                            (answer_id, assessment_id, question_index, selected_index, is_correct)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (assessment_id, question_index) DO UPDATE
                        SET selected_index = EXCLUDED.selected_index,
                            is_correct = EXCLUDED.is_correct,
                            answered_at = CURRENT_TIMESTAMP
                    """, (f"ANS-{secrets.token_hex(4).upper()}",
                          assessment_id, i, sel_int, is_correct))

            # Score
            cur.execute("""
                SELECT question_index, is_correct
                FROM charvak_career_assessment_answers
                WHERE assessment_id = %s
            """, (assessment_id,))
            answered = cur.fetchall()
            answered_map = {r[0]: r[1] for r in answered}
            correct_count = sum(1 for r in answered if r[1])
            total = len(questions)
            score = round(correct_count / total * 100) if total > 0 else 0
            passed = score >= PASSING_SCORE

            cur.execute("""
                UPDATE charvak_career_assessments
                SET status = 'completed',
                    score = %s,
                    passed = %s,
                    correct_count = %s,
                    completed_at = CURRENT_TIMESTAMP
                WHERE assessment_id = %s
            """, (score, passed, correct_count, assessment_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"complete_assessment failed: {e}")
            return {"status": "error", "message": "Could not complete assessment"}

        # Persist to the shared assessment_results table (feeds /my-results)
        try:
            from results_system import results_system
            results_system.record_assessment_result(
                email=email,
                assessment_type="career_readiness",
                assessment_name=f"{role} in {industry}",
                score=float(score),
                total_questions=total,
                correct_answers=correct_count,
                details={
                    "assessment_id": assessment_id,
                    "role": role,
                    "industry": industry,
                    "level": level,
                    "size": size,
                    "format": "mcq",
                },
                skill=f"career_{role.lower().replace(' ', '_')}",
            )
        except Exception as e:
            logger.warning(f"career-assessment result persistence failed: {e}")

        return {
            "status": "success",
            "assessment_id": assessment_id,
            "role": role,
            "industry": industry,
            "level": level,
            "score": score,
            "passed": passed,
            "correct_count": correct_count,
            "total_questions": total,
            "passing_score": PASSING_SCORE,
            "message": f"Career readiness: {score}%",
        }

    # ------------------------------------------------------------
    # History / Get
    # ------------------------------------------------------------

    def get_history(self, email: str) -> Dict:
        """List past assessments for an email."""
        email = (email or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}

        self._ensure_tables()
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT assessment_id, role, industry, level, format, size,
                       num_questions, status, score, passed, correct_count,
                       started_at, completed_at
                FROM charvak_career_assessments
                WHERE email = %s
                ORDER BY started_at DESC
                LIMIT 100
            """, (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_history failed: {e}")
            return {"status": "error", "message": "Could not list history"}

        assessments = []
        for r in rows:
            assessments.append({
                "assessment_id": r[0],
                "role": r[1],
                "industry": r[2],
                "level": r[3],
                "format": r[4],
                "size": r[5],
                "num_questions": r[6],
                "status": r[7],
                "score": r[8],
                "passed": r[9],
                "correct_count": r[10],
                "started_at": r[11].isoformat() if r[11] else None,
                "completed_at": r[12].isoformat() if r[12] else None,
            })
        return {"status": "success", "assessments": assessments, "count": len(assessments)}

    def get_assessment(self, assessment_id: str, email: str) -> Dict:
        """Fetch a single assessment (for resume or review)."""
        assessment_id = (assessment_id or "").strip()
        email = (email or "").strip().lower()
        if not assessment_id or not email:
            return {"status": "error", "message": "assessment_id and email required"}

        self._ensure_tables()
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT assessment_id, email, role, industry, level, format,
                       size, num_questions, questions_json, status, score,
                       passed, correct_count, started_at, completed_at
                FROM charvak_career_assessments
                WHERE assessment_id = %s
            """, (assessment_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Assessment not found"}
            if row[1] != email:
                cur.close(); conn.close()
                return {"status": "error", "message": "Not your assessment"}

            questions = row[8] if isinstance(row[8], list) else json.loads(row[8] or "[]")

            # Strip correct_index if still in progress (don't leak answers)
            status = row[9]
            safe_questions = []
            for q in questions:
                if status == "completed":
                    safe_questions.append({
                        "q": q.get("q"),
                        "options": q.get("options", []),
                        "correct_index": q.get("correct_index"),
                    })
                else:
                    safe_questions.append({
                        "q": q.get("q"),
                        "options": q.get("options", []),
                    })

            result = {
                "assessment_id": row[0],
                "role": row[2],
                "industry": row[3],
                "level": row[4],
                "format": row[5],
                "size": row[6],
                "num_questions": row[7],
                "questions": safe_questions,
                "status": status,
                "score": row[10],
                "passed": row[11],
                "correct_count": row[12],
                "started_at": row[13].isoformat() if row[13] else None,
                "completed_at": row[14].isoformat() if row[14] else None,
            }
            cur.close(); conn.close()
            return {"status": "success", "assessment": result}
        except Exception as e:
            logger.error(f"get_assessment failed: {e}")
            return {"status": "error", "message": "Could not load assessment"}


# Singleton
career_assessment_engine = CareerAssessmentEngine()