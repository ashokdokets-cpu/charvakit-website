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

# ============================================================
# TOPIC VOCABULARY — per role category, used for skill-gap analysis
# ============================================================

TOPIC_VOCABULARY = {
    "Engineering & Software": [
        "Fundamentals & Syntax",
        "Data Structures & Algorithms",
        "System Design & Architecture",
        "Debugging & Problem Solving",
        "Testing & Quality",
        "Tooling & Ecosystem",
        "Collaboration & Communication",
        "Domain Knowledge",
    ],
    "Data & Analytics": [
        "Statistics & Probability",
        "Data Wrangling & ETL",
        "Modeling & ML",
        "Evaluation & Experimentation",
        "Data Engineering & Pipelines",
        "Business Acumen",
        "Tooling (SQL / Python / R)",
        "Domain Knowledge",
    ],
    "Product & Design": [
        "Discovery & User Research",
        "Prioritization & Roadmapping",
        "Design & UX Principles",
        "Metrics & Experimentation",
        "Stakeholder Management",
        "Execution & Delivery",
        "Domain Knowledge",
        "Communication",
    ],
    "Business & Strategy": [
        "Analytical Reasoning",
        "Financial Acumen",
        "Market & Competitive Analysis",
        "Process & Operations",
        "Stakeholder Management",
        "Communication",
        "Domain Knowledge",
        "Tooling (Excel / BI / SQL)",
    ],
    "Go-to-Market": [
        "Strategy & Positioning",
        "Channel & Campaign Execution",
        "Metrics & Attribution",
        "Customer Insight",
        "Relationship Building",
        "Communication & Storytelling",
        "Tooling (CRM / Analytics)",
        "Domain Knowledge",
    ],
    "People & HR": [
        "Talent Acquisition",
        "Employee Relations",
        "Compensation & Benefits",
        "HR Operations & Compliance",
        "Learning & Development",
        "Analytics & Reporting",
        "Communication",
        "Domain Knowledge",
    ],
    "Domain-Specific": [
        "Core Domain Knowledge",
        "Regulatory & Compliance",
        "Technical Application",
        "Problem Solving",
        "Stakeholder Management",
        "Communication",
        "Tooling",
        "Safety & Ethics",
    ],
}


def _topic_vocabulary_for_role(role: str) -> List[str]:
    """Find the topic vocabulary for a role's category. Falls back to Engineering."""
    for category, roles in CAREER_ROLES.items():
        if role in roles:
            return TOPIC_VOCABULARY.get(category, TOPIC_VOCABULARY["Engineering & Software"])
    return TOPIC_VOCABULARY["Engineering & Software"]


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
            # Session 13: lazy learning-path cache column
            cur.execute("""
                ALTER TABLE charvak_career_assessments
                    ADD COLUMN IF NOT EXISTS learning_path_json JSONB
            """)
            # Session 17 Sprint A: readiness certificates
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_readiness_certificates (
                    certificate_id    TEXT PRIMARY KEY,
                    assessment_id     TEXT NOT NULL,
                    email             TEXT NOT NULL,
                    display_name      TEXT,
                    role              TEXT NOT NULL,
                    industry          TEXT NOT NULL,
                    level             TEXT NOT NULL,
                    readiness_score   INTEGER NOT NULL,
                    percentile        INTEGER,
                    benchmark_score   INTEGER,
                    verdict           TEXT,
                    payload_json      JSONB,
                    certificate_hash  TEXT NOT NULL,
                    source            TEXT NOT NULL DEFAULT 'written',
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_rdc_email
                    ON charvak_readiness_certificates (email, created_at DESC)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_rdc_hash
                    ON charvak_readiness_certificates (certificate_hash)
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_rdc_assessment
                    ON charvak_readiness_certificates (assessment_id)
            """)
            # Session 19: upgrade chain (Phase 2 size upgrade CTA)
            cur.execute("""
                ALTER TABLE charvak_readiness_certificates
                    ADD COLUMN IF NOT EXISTS supersedes TEXT
            """)
            cur.execute("""
                ALTER TABLE charvak_readiness_certificates
                    ADD COLUMN IF NOT EXISTS superseded_by TEXT
            """)
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_rdc_supersedes
                    ON charvak_readiness_certificates (supersedes)
                    WHERE supersedes IS NOT NULL
            """)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"career-assessment table init failed: {e}")

    # ------------------------------------------------------------
    # Sprint A helpers (Session 17)
    # ------------------------------------------------------------

    def _resolve_benchmark(self, role: str, industry: str, level: str) -> int:
        """
        Resolve the market benchmark for a (role, industry, level) combo.
        Reads benchmarks/role_readiness.json (cached by mtime).
        Resolution order:
          1. Exact (role, industry, level)
          2. Exact (role, *, level)
          3. Any (*, *, level) -> uses the first matching level entry
          4. Global default
        """
        import os as _os
        default_value = 65
        try:
            bench_path = _os.path.join(_os.path.dirname(__file__), "benchmarks", "role_readiness.json")
            if not _os.path.exists(bench_path):
                return default_value

            # Simple mtime-based cache
            mtime = _os.path.getmtime(bench_path)
            cached = getattr(self, "_bench_cache", None)
            if cached and cached.get("mtime") == mtime:
                data = cached["data"]
            else:
                with open(bench_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                self._bench_cache = {"mtime": mtime, "data": data}

            default_value = int(data.get("default", 65))
            benchmarks = data.get("benchmarks") or []

            # 1. Exact (role, industry, level)
            for b in benchmarks:
                if b.get("role") == role and b.get("industry") == industry and b.get("level") == level:
                    return int(b.get("benchmark", default_value))
            # 2. Wildcard industry
            for b in benchmarks:
                if b.get("role") == role and b.get("industry") == "*" and b.get("level") == level:
                    return int(b.get("benchmark", default_value))
            # 3. Any role, same level
            for b in benchmarks:
                if b.get("level") == level:
                    return int(b.get("benchmark", default_value))
            # 4. Global default
            return default_value
        except Exception as e:
            logger.error(f"_resolve_benchmark failed: {e}")
            return default_value

    def _generate_certificate_hash(self, certificate_id: str, email: str,
                                   readiness_score: int, created_at_iso: str) -> str:
        """
        HMAC-SHA256 of the certificate's identifying fields, truncated to
        16 hex chars. Uses READINESS_HMAC_KEY if set, else SECRET_KEY.
        Used by /api/readiness/verify/{hash} for employer-side verification.
        """
        import os as _os
        import hmac
        import hashlib

        key = (
            _os.getenv("READINESS_HMAC_KEY")
            or _os.getenv("SECRET_KEY")
            or "dev-only-not-secret"
        )
        payload = f"{certificate_id}|{(email or '').lower()}|{readiness_score}|{created_at_iso}"
        digest = hmac.new(key.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return digest[:16]

    # ------------------------------------------------------------
    # Sprint A: Role Readiness Certificate (Session 17)
    # ------------------------------------------------------------

    def _skill_gap_from_answers(self, questions, answers):
        """
        Aggregate per-topic skill gap from questions' 'topics' tags and
        the answers' scores. Returns a list of {topic, score, status}.
        """
        topic_scores = {}
        for i, q in enumerate(questions):
            topics = q.get("topics") or []
            if not topics:
                continue
            a = answers[i] if i < len(answers) else None
            if isinstance(a, dict):
                sc = a.get("score", 0)
            elif isinstance(a, (int, float)):
                sc = a
            else:
                sc = 0
            sc = int(sc) if sc is not None else 0
            for tp in topics:
                topic_scores.setdefault(tp, []).append(sc)

        out = []
        for tp, scores in topic_scores.items():
            if not scores:
                continue
            avg = int(round(sum(scores) / len(scores)))
            if avg >= 80:
                status = "strong"
            elif avg >= 55:
                status = "mixed"
            else:
                status = "weak"
            out.append({"topic": tp, "score": avg, "status": status})
        out.sort(key=lambda x: x["score"])
        return out

    def compute_role_readiness(self, data):
        """
        Compute and persist a Role Readiness Certificate.
        data = {email, assessment_id, display_name (optional)}
        Idempotent: one certificate per assessment_id.
        Returns {status, certificate_id, readiness_score, ...}.
        """
        import datetime as _dt
        email = (data.get("email") or "").strip().lower()
        assessment_id = (data.get("assessment_id") or "").strip()
        display_name = (data.get("display_name") or "").strip() or None

        if not email or not assessment_id:
            return {"status": "error", "message": "email and assessment_id required"}

        self._ensure_tables()
        self._ensure_format_columns()

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Idempotency check
            cur.execute("""
                SELECT certificate_id, certificate_hash, readiness_score, percentile,
                       benchmark_score, verdict, created_at
                FROM charvak_readiness_certificates
                WHERE assessment_id = %s
            """, (assessment_id,))
            existing = cur.fetchone()
            if existing:
                cur.close(); conn.close()
                cid = existing[0]
                return {
                    "status": "success",
                    "already_existed": True,
                    "certificate_id": cid,
                    "certificate_url": f"/readiness/{cid}",
                    "certificate_hash": existing[1],
                    "readiness_score": existing[2],
                    "percentile": existing[3],
                    "benchmark": existing[4],
                    "verdict": existing[5],
                    "created_at": existing[6].isoformat() if existing[6] else None,
                }

            # Load assessment
            cur.execute("""
                SELECT email, role, industry, level, format, num_questions,
                       questions_json, status, score, correct_count
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
            if row[7] != "completed":
                cur.close(); conn.close()
                return {"status": "error", "message": "Assessment not completed"}

            _, role, industry, level, fmt, num_questions, questions_json, _, score, correct_count = row
            fmt = fmt or "mcq"
            questions = questions_json if isinstance(questions_json, list) else json.loads(questions_json or "[]")
            total = len(questions)

            # Load answers
            cur.execute("""
                SELECT question_index, selected_index, is_correct, ai_score
                FROM charvak_career_assessment_answers
                WHERE assessment_id = %s ORDER BY question_index
            """, (assessment_id,))
            answer_rows = cur.fetchall()
            answers_map = {}
            for ar in answer_rows:
                q_idx, sel_idx, is_corr, ai_sc = ar
                answers_map[q_idx] = {
                    "selected_index": sel_idx,
                    "is_correct": is_corr,
                    "ai_score": ai_sc,
                }
            answers = [answers_map.get(i, {}) for i in range(total)]

            # ---- Component 1: binary correct % (30%) ----
            binary_correct = sum(1 for a in answers if a.get("is_correct"))
            binary_pct = (binary_correct / total * 100) if total > 0 else 0

            # ---- Component 2: AI-scored avg (25%) ----
            ai_scores = [a.get("ai_score") for a in answers if a.get("ai_score") is not None]
            ai_avg = (sum(ai_scores) / len(ai_scores)) if ai_scores else None

            # ---- Component 3: skill-gap closure (20%) ----
            per_answer_scores = []
            for i, q in enumerate(questions):
                a = answers[i] if i < len(answers) else {}
                if a.get("ai_score") is not None:
                    per_answer_scores.append({"score": a["ai_score"]})
                elif a.get("is_correct"):
                    per_answer_scores.append({"score": 100})
                else:
                    per_answer_scores.append({"score": 0})
            skill_gap = self._skill_gap_from_answers(questions, per_answer_scores)
            if skill_gap:
                status_map = {"strong": 100, "mixed": 70, "weak": 40}
                closure = sum(status_map[s["status"]] for s in skill_gap) / len(skill_gap)
            else:
                closure = binary_pct

            # ---- Component 4: ability baseline percentile (15%) ----
            skill_key = f"career_{fmt}"
            try:
                from ability_engine import ability_engine
                ability_info = ability_engine.get_ability(email, skill_key)
                ability_score = float(ability_info.get("ability_score", 1000.0))
            except Exception:
                ability_score = 1000.0
            ability_pct = max(0, min(100, (ability_score - 800) / 4))

            # ---- Component 5: difficulty adjustment (10%) ----
            level_mult = {
                "intern": 0.85, "junior": 0.92, "mid": 1.00,
                "senior": 1.08, "staff": 1.12,
                "manager": 1.10, "executive": 1.15,
            }
            level_key = (level or "mid").lower()
            diff_mult = level_mult.get(level_key, 1.00)
            diff_component = min(100, binary_pct * diff_mult)

            # ---- Blend ----
            if ai_avg is not None:
                readiness = (
                    0.30 * binary_pct
                    + 0.25 * ai_avg
                    + 0.20 * closure
                    + 0.15 * ability_pct
                    + 0.10 * diff_component
                )
            else:
                readiness = (
                    0.40 * binary_pct
                    + 0.25 * closure
                    + 0.20 * ability_pct
                    + 0.15 * diff_component
                )
            readiness_int = max(0, min(100, int(round(readiness))))

            # ---- Benchmark ----
            benchmark = self._resolve_benchmark(role, industry, level_key)

            # ---- Percentile ----
            import math as _math
            try:
                z = (readiness_int - benchmark) / 15.0
                percentile = int(round(50 + 50 * _math.erf(z / _math.sqrt(2))))
                percentile = max(5, min(99, percentile))
            except Exception:
                percentile = 50

            # ---- Verdict ----
            if readiness_int >= benchmark + 10:
                verdict = "Well above benchmark - strongly job ready"
            elif readiness_int >= benchmark:
                verdict = "Above benchmark - job ready"
            elif readiness_int >= benchmark - 10:
                verdict = "Near benchmark - close to job ready"
            else:
                verdict = "Below benchmark - skill gaps to close"

            # ---- Session 19: upgrade chain ----
            # If a prior certificate exists for the same (email, role, industry, level),
            # link the new one to it. The prior certificate is marked superseded.
            prior_certificate_id = None
            try:
                cur.execute("""
                    SELECT certificate_id FROM charvak_readiness_certificates
                    WHERE email = %s AND role = %s AND industry = %s AND level = %s
                    ORDER BY created_at DESC LIMIT 1
                """, (email, role, industry, level))
                prior_row = cur.fetchone()
                if prior_row:
                    prior_certificate_id = prior_row[0]
            except Exception as _e:
                logger.warning(f"upgrade chain lookup failed: {_e}")

            # ---- Certificate ID + hash ----
            certificate_id = f"RDC-{secrets.token_hex(6).upper()}"
            now_iso = _dt.datetime.now().isoformat()
            cert_hash = self._generate_certificate_hash(certificate_id, email, readiness_int, now_iso)

            # ---- Payload snapshot ----
            payload = {
                "skill_gap": skill_gap,
                "binary_pct": round(binary_pct, 1),
                "ai_avg": round(ai_avg, 1) if ai_avg is not None else None,
                "closure": round(closure, 1),
                "ability_pct": round(ability_pct, 1),
                "diff_mult": diff_mult,
                "total_questions": total,
                "binary_correct": binary_correct,
                "format": fmt,
            }

            # ---- Persist ----
            cur.execute("""
                INSERT INTO charvak_readiness_certificates
                    (certificate_id, assessment_id, email, display_name,
                     role, industry, level, readiness_score, percentile,
                     benchmark_score, verdict, payload_json, certificate_hash, source,
                     supersedes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, 'written',
                        %s)
            """, (
                certificate_id, assessment_id, email, display_name,
                role, industry, level, readiness_int, percentile,
                benchmark, verdict, json.dumps(payload), cert_hash,
                prior_certificate_id,
            ))

            # Mark the prior certificate as superseded
            if prior_certificate_id:
                cur.execute("""
                    UPDATE charvak_readiness_certificates
                    SET superseded_by = %s
                    WHERE certificate_id = %s
                """, (certificate_id, prior_certificate_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"compute_role_readiness failed: {e}")
            return {"status": "error", "message": f"Could not compute certificate: {e}"}

        return {
            "status": "success",
            "already_existed": False,
            "certificate_id": certificate_id,
            "certificate_url": f"/readiness/{certificate_id}",
            "certificate_hash": cert_hash,
            "readiness_score": readiness_int,
            "percentile": percentile,
            "benchmark": benchmark,
            "verdict": verdict,
            "role": role,
            "industry": industry,
            "level": level,
            "created_at": now_iso,
            "supersedes": prior_certificate_id,
        }

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
            "formats": self._format_registry(),
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
        registry = self._format_registry()
        if fmt not in registry:
            return {"status": "error", "message": f"Unknown format: {fmt}"}
        if not registry[fmt]["available"]:
            return {"status": "error", "message": f"Format '{fmt}' is coming soon"}

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

        # Cross-assessment adaptive baseline (reads ability_engine)
        baseline = self._baseline_hint(email, role, industry, fmt)
        difficulty_hint = baseline.get("hint", "baseline")

        # Generate questions (format-aware, adaptive-hint aware)
        questions = self._generate_questions(
            format_key=fmt,
            role=role, industry=industry,
            level_key=level_key, level_label=level_label,
            level_blurb=level_blurb, num_questions=num_questions,
            difficulty_hint=difficulty_hint,
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

        # Strip scoring answers before sending to frontend
        safe_questions = self._strip_answers_for_frontend(fmt, questions)

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
                "baseline_used": difficulty_hint,
                "ability_before": baseline.get("ability_score"),
                "prior_attempts": baseline.get("attempts", 0),
            },
            "message": f"{role} in {industry} assessment started",
        }

    # ------------------------------------------------------------
    # Format registry (Session 11 Phase 2a)
    # ------------------------------------------------------------

    def _format_registry(self) -> Dict:
        """
        Per-format metadata. Single source of truth for which formats
        are available, what shape their questions take, how they're
        scored, and what credit multiplier applies.
        """
        return {
            "mcq": {
                "label": "Multiple Choice",
                "scored_by": "deterministic",
                "available": True,
                "phase": 1,
                "question_shape": "{q, options: [4], correct_index}",
                "answer_kind": "choice",
                "credit_multiplier": 1.0,
                "description": "4-option MCQs, instant scoring",
            },
            "short_answer": {
                "label": "Short Answer",
                "scored_by": "hybrid",
                "available": True,
                "phase": 2,
                "question_shape": "{q, expected_answer, keywords: [...]}",
                "answer_kind": "text_short",
                "credit_multiplier": 1.0,
                "description": "1-3 sentence text answers, AI near-match scored",
            },
            "numeracy": {
                "label": "Numeracy",
                "scored_by": "deterministic",
                "available": True,
                "phase": 2,
                "question_shape": "{q, correct_number, tolerance}",
                "answer_kind": "number",
                "credit_multiplier": 1.0,
                "description": "Quantitative reasoning, exact or tolerance match",
            },
            "situational_judgment": {
                "label": "Situational Judgment",
                "scored_by": "deterministic",
                "available": True,
                "phase": 2,
                "question_shape": "{scenario, options: [5], best_index, worst_index}",
                "answer_kind": "choice_best_worst",
                "credit_multiplier": 1.0,
                "description": "Pick the best and worst response to a scenario",
            },
            "behavioral": {
                "label": "Behavioral (STAR)",
                "scored_by": "ai",
                "available": True,
                "phase": 2,
                "question_shape": "{prompt, rubric_star: {situation, task, action, result}}",
                "answer_kind": "text_long",
                "credit_multiplier": 1.33,
                "description": "STAR-format responses, AI-scored against rubric",
            },
            "system_design": {
                "label": "System Design",
                "scored_by": "ai",
                "available": True,
                "phase": 2,
                "question_shape": "{prompt, rubric: [criteria]}",
                "answer_kind": "text_long",
                "credit_multiplier": 1.33,
                "description": "Open-ended architecture prompts, AI-scored",
            },
            "debugging": {
                "label": "Debugging",
                "scored_by": "ai",
                "available": True,
                "phase": 2,
                "question_shape": "{buggy_code, language, correct_fix_summary, bug_class}",
                "answer_kind": "text_long",
                "credit_multiplier": 1.33,
                "description": "Diagnose a bug, describe the fix, AI-scored",
            },
            "case_study": {
                "label": "Case Study",
                "scored_by": "ai",
                "available": True,
                "phase": 2,
                "question_shape": "{scenario, questions: [sub-questions], rubric}",
                "answer_kind": "text_long",
                "credit_multiplier": 1.33,
                "description": "Business/analytics scenarios, AI-scored",
            },
            "coding": {
                "label": "Coding",
                "scored_by": "hybrid",
                "available": True,
                "phase": 2,
                "question_shape": "{problem, starter_code, language, test_cases}",
                "answer_kind": "code",
                "credit_multiplier": 1.33,
                "description": "Real code, tested against cases (Python only)",
            },
            "sql": {
                "label": "SQL",
                "scored_by": "hybrid",
                "available": True,
                "phase": 2,
                "question_shape": "{schema, task, expected_output}",
                "answer_kind": "sql",
                "credit_multiplier": 1.33,
                "description": "Query a schema, compare output (SQLite)",
            },
        }

    def _is_ai_scored_format(self, format_key: str) -> bool:
        registry = self._format_registry()
        return registry.get(format_key, {}).get("scored_by") in ("ai", "hybrid")

    # ------------------------------------------------------------
    # Prompt builders (one per format)
    # ------------------------------------------------------------

    def _build_prompt_for_format(
        self, format_key: str, role: str, industry: str,
        level_label: str, level_blurb: str, count: int,
        difficulty_hint: str = "baseline"
    ) -> str:
        """Dispatch to the format-specific prompt builder."""
        builders = {
            "mcq": self._prompt_mcq,
            "short_answer": self._prompt_short_answer,
            "numeracy": self._prompt_numeracy,
            "situational_judgment": self._prompt_sjt,
            "behavioral": self._prompt_behavioral,
            "system_design": self._prompt_system_design,
            "debugging": self._prompt_debugging,
            "case_study": self._prompt_case_study,
            "coding": self._prompt_coding,
            "sql": self._prompt_sql,
        }
        builder = builders.get(format_key)
        if not builder:
            # Fallback to MCQ
            return self._prompt_mcq(role, industry, level_label, level_blurb, count, difficulty_hint)
        return builder(role, industry, level_label, level_blurb, count, difficulty_hint)

    def _baseline_hint(self, email: str, role: str, industry: str, fmt: str) -> Dict:
        """
        Read the user's ability for this role+format and return a
        difficulty hint for the prompt. Cross-assessment adaptation:
        your last performance informs your next baseline.
        Returns {hint: str, ability_score: float|None, attempts: int}
        """
        try:
            from ability_engine import ability_engine
        except Exception as e:
            logger.warning(f"ability_engine unavailable: {e}")
            return {"hint": "baseline", "ability_score": None, "attempts": 0}

        # Skill key: format only (matches results_system.record_assessment_result
        # which uses skill=f"career_{fmt}")
        skill = f"career_{fmt}"

        try:
            info = ability_engine.get_ability(email, skill)
        except Exception as e:
            logger.warning(f"ability lookup failed for {skill}: {e}")
            return {"hint": "baseline", "ability_score": None, "attempts": 0}

        ability = info.get("ability_score")
        attempts = info.get("attempts", 0) or 0

        if ability is None or attempts == 0:
            return {"hint": "baseline", "ability_score": None, "attempts": 0}

        try:
            ability = float(ability)
        except (ValueError, TypeError):
            return {"hint": "baseline", "ability_score": None, "attempts": 0}

        # Elo bands. Standard Elo baseline is 1000.
        # Tightened 2026-10-03 after E2E: 100% on a mid-level MCQ moved
        # ability only 1012 (delta per assessment ~12 with K=25). Wider
        # bands (900/1100) would make "challenge" nearly unreachable.
        if ability < 950:
            hint = "foundation-first"
        elif ability < 1050:
            hint = "standard"
        else:
            hint = "challenge"

        return {"hint": hint, "ability_score": ability, "attempts": attempts}

    def _context_header(self, role: str, industry: str, level_label: str, level_blurb: str, difficulty_hint: str = "baseline") -> str:
        """Shared context block for all prompts. Includes topic-tagging + difficulty-hint."""
        topics = _topic_vocabulary_for_role(role)
        topic_list = ", ".join(topics)

        # Adaptive baseline: make the difficulty hint explicit to the AI
        if difficulty_hint == "foundation-first":
            hint_line = (
                "ADAPTIVE HINT: The candidate is still building confidence. "
                "Favor questions that test fundamentals clearly. Avoid "
                "overly tricky edge cases — the goal is to reinforce core "
                "understanding.\n\n"
            )
        elif difficulty_hint == "challenge":
            hint_line = (
                "ADAPTIVE HINT: The candidate has performed strongly before. "
                "Push the difficulty: include edge cases, trade-off "
                "scenarios, and questions that require deeper reasoning "
                "than the level_label alone would suggest.\n\n"
            )
        else:  # baseline or standard
            hint_line = ""

        return (
            f"TARGET ROLE: {role}\n"
            f"INDUSTRY: {industry}\n"
            f"EXPERIENCE LEVEL: {level_label} ({level_blurb})\n\n"
            + hint_line
            + f"Calibrate all questions to what a real interviewer at the "
            f"{level_label} level would ask for a {role} in {industry}. "
            f"Test practical knowledge, not trivia. Include trade-offs, "
            f"real-world scenarios, and tool familiarity appropriate to "
            f"the industry.\n\n"
            f"TOPIC TAGGING (required on every question):\n"
            f"Choose 1-2 topics from this list that best describe what the question tests:\n"
            f"  [{topic_list}]\n"
            f"Return each question with a \"topics\" array of 1-2 topic strings from the list above.\n\n"
        )

    def _prompt_mcq(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} multiple-choice questions for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each question MUST have exactly 4 options and one correct answer.\n"
            f"- correct_index is 0-based (0, 1, 2, or 3).\n"
            f"- CRITICAL: Vary correct_index across questions. Do NOT always put the correct answer at position 0.\n"
            f"- Aim for a roughly even distribution across 0, 1, 2, 3.\n"
            f"- Keep options concise (1-15 words each).\n"
            f"- Return exactly {count} questions.\n\n"
            f'Return JSON: {{"questions": [{{"q": "...", "options": ["...","...","...","..."], "correct_index": 0, "topics": ["...", "..."]}}]}}'
        )

    def _prompt_short_answer(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} short-answer questions for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each question expects a 1-3 sentence text answer.\n"
            f"- Provide an 'expected_answer' capturing the ideal response in 2-4 sentences.\n"
            f"- Provide 3-6 'keywords' that a correct answer must mention.\n"
            f"- Questions should test understanding, not memorization.\n"
            f"- Return exactly {count} questions.\n\n"
            f'Return JSON: {{"questions": [{{"q": "...", "expected_answer": "...", "keywords": ["...","...","..."], "topics": ["...", "..."]}}]}}'
        )

    def _prompt_numeracy(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} numeracy questions for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each question has a single numeric answer.\n"
            f"- Answers can be integers or decimals.\n"
            f"- Provide a 'tolerance' field: the acceptable absolute difference from correct_number.\n"
            f"  Use tolerance=0 for exact answers, or a small number (e.g. 0.5 or 5) for rounded answers.\n"
            f"- Include realistic business/technical scenarios (rates, budgets, KPIs, percentages).\n"
            f"- Return exactly {count} questions.\n\n"
            f'Return JSON: {{"questions": [{{"q": "...", "correct_number": 42.5, "tolerance": 0.5, "topics": ["...", "..."]}}]}}'
        )

    def _prompt_sjt(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} situational judgment questions for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each question presents a realistic workplace scenario.\n"
            f"- Provide 5 possible responses (options).\n"
            f"- Mark the single 'best_index' (most professional/effective) and 'worst_index' (least effective).\n"
            f"- Indexes are 0-based (0-4). best_index and worst_index must differ.\n"
            f"- Scenarios should reflect real pressure, trade-offs, or ethical decisions.\n"
            f"- Return exactly {count} questions.\n\n"
            f'Return JSON: {{"questions": [{{"scenario": "...", "options": ["...","...","...","...","..."], "best_index": 0, "worst_index": 4, "topics": ["...", "..."]}}]}}'
        )

    def _prompt_behavioral(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} behavioral interview prompts for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each prompt is a classic behavioral question suitable for STAR-format answers.\n"
            f"- Provide a 'rubric_star' object with 4 fields: situation, task, action, result.\n"
            f"  Each field describes what a strong STAR response should cover for this prompt.\n"
            f"- Prompts should reveal judgment, collaboration, and impact.\n"
            f"- Return exactly {count} questions.\n\n"
            f'Return JSON: {{"questions": [{{"prompt": "...", "rubric_star": {{"situation": "...", "task": "...", "action": "...", "result": "..."}}, "topics": ["...", "..."]}}]}}'
        )

    def _prompt_system_design(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} system design prompts for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each prompt is an open-ended architecture or design challenge.\n"
            f"- Provide a 'rubric' with 4-6 criteria a strong answer should address.\n"
            f"- Prompts should require trade-off analysis (scalability, cost, latency, reliability, security).\n"
            f"- Appropriate for {role} in {industry} at {level_label}.\n"
            f"- Return exactly {count} questions.\n\n"
            f'Return JSON: {{"questions": [{{"prompt": "...", "rubric": ["...","...","..."], "topics": ["...", "..."]}}]}}'
        )

    def _prompt_debugging(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} debugging challenges for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each challenge shows a small snippet of buggy code with a plausible-looking bug.\n"
            f"- Include the language (Python, JavaScript, SQL, etc.).\n"
            f"- Provide 'correct_fix_summary' — one sentence describing the fix.\n"
            f"- Provide 'bug_class' — e.g. 'off_by_one', 'null_reference', 'race_condition', 'logic_error'.\n"
            f"- Keep code snippets under 15 lines so they render well.\n"
            f"- Return exactly {count} questions.\n\n"
            f'Return JSON: {{"questions": [{{"buggy_code": "...", "language": "Python", "correct_fix_summary": "...", "bug_class": "...", "topics": ["...", "..."]}}]}}'
        )

    def _prompt_case_study(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        return (
            f"Generate {count} case study questions for a career readiness assessment.\n"
            + self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
            + f"Rules:\n"
            f"- Each case study presents a realistic business or product scenario.\n"
            f"- Include 1-3 'questions' the user must answer based on the scenario.\n"
            f"- Provide a 'rubric' with 4-6 criteria a strong analysis should cover.\n"
            f"- Scenario should require diagnosis, prioritization, or trade-off reasoning.\n"
            f"- Return exactly {count} case studies.\n\n"
            f'Return JSON: {{"questions": [{{"scenario": "...", "questions": ["...","..."], "rubric": ["...","..."], "topics": ["...", "..."]}}]}}'
        )
    def _prompt_coding(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        """Coding problems with real test cases. Python-only for now (Judge0 language_id=71)."""
        ctx = self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
        topics = _topic_vocabulary_for_role(role)
        return (
            f"{ctx}\n\n"
            f"Generate {count} coding problems for a {role} in {industry} at {level_label} level.\n"
            f"Focus on topics: {', '.join(topics[:5])}\n\n"
            f"STRICT RULES:\n"
            f"- Language is Python 3.\n"
            f"- Each problem reads input from stdin and writes output to stdout.\n"
            f"- Each problem has exactly 3 test cases with valid stdin and the exact expected stdout.\n"
            f"- Output must match EXACTLY (including trailing newline via print()).\n"
            f"- Test cases must be small (integers, short strings, short lists).\n"
            f"- Starter code should be a short comment + a hint, not a working solution.\n"
            f"- Difficulty: calibrate to {level_label}. One problem may be a warm-up, but at least one must be non-trivial.\n"
            f"- Do NOT include the solution in `starter_code`.\n"
            f"- Do NOT include any imports the candidate does not need.\n\n"
            f"Return STRICT JSON: {{\"questions\": [\n"
            f"  {{\n"
            f"    \"problem\": \"one paragraph describing what to write, with clear input/output spec\",\n"
            f"    \"starter_code\": \"# read input from stdin\\n# your code here\\n\",\n"
            f"    \"language\": \"python\",\n"
            f"    \"test_cases\": [\n"
            f"      {{\"stdin\": \"2 3\\n\", \"expected_output\": \"5\\n\"}},\n"
            f"      {{\"stdin\": \"10 -4\\n\", \"expected_output\": \"6\\n\"}},\n"
            f"      {{\"stdin\": \"0 0\\n\", \"expected_output\": \"0\\n\"}}\n"
            f"    ],\n"
            f"    \"topics\": [\"{topics[0] if topics else 'algorithms'}\"]\n"
            f"  }}\n"
            f"]}}\n"
            f"Return exactly {count} questions."
        )


    # ------------------------------------------------------------
    # Question generation
    # ------------------------------------------------------------

    def _prompt_sql(self, role, industry, level_label, level_blurb, count, difficulty_hint='baseline'):
        """SQL problems with SQLite schema + task + expected output (Judge0 language_id=82)."""
        ctx = self._context_header(role, industry, level_label, level_blurb, difficulty_hint)
        topics = _topic_vocabulary_for_role(role)
        return (
            f"{ctx}\n\n"
            f"Generate {count} SQL problems for a {role} in {industry} at {level_label} level.\n"
            f"Focus on topics: {', '.join(topics[:5])}\n\n"
            f"STRICT RULES:\n"
            f"- Dialect: SQLite 3 (language_id=82).\n"
            f"- Each problem has a schema (CREATE TABLE + INSERT rows) and a task (SELECT query to write).\n"
            f"- The candidate writes ONE SELECT query. Do NOT write it for them in starter_code.\n"
            f"- Keep schemas small: 1-2 tables, 2-5 rows each.\n"
            f"- CRITICAL: expected_output must contain EXACTLY the columns the task asks for, in the order asked.\n"
            f"  Do NOT include the primary key `id` unless the task explicitly asks for it.\n"
            f"  Example: task 'names of all users where id > 1' means SELECT name FROM users WHERE id > 1\n"
            f"    output is 'Bob\\nCharlie\\n' (1 column), NOT '2|Bob\\n3|Charlie\\n' (2 columns, wrong).\n"
            f"- Sort/ordering keys are NOT output columns. If the task says 'names of users ordered by age', the output is ONLY names (1 column), not names+age.\n"
            f"  Only include a column in expected_output if the task explicitly names it in the output description.\n"
            f"- expected_output MUST match SQLite's default stdout EXACTLY:\n"
            f"  - One line per row, columns joined by the pipe character '|'.\n"
            f"  - No column headers (headers are OFF by default in this environment).\n"
            f"  - Trailing newline after the last row.\n"
            f"  - Example for 'SELECT id, name FROM users ORDER BY id' with rows (1,'Alice'),(2,'Bob'):\n"
            f"    expected_output = \"1|Alice\\n2|Bob\\n\"\n"
            f"- Difficulty: calibrate to {level_label}. Cover a spread: filtering, JOINs, aggregation, sorting.\n"
            f"- Topics: tag each problem with 1-2 from the provided list.\n\n"
            f"Return STRICT JSON: {{\"questions\": [\n"
            f"  {{\n"
            f"    \"schema\": \"CREATE TABLE ...;\\nINSERT INTO ...;\",\n"
            f"    \"task\": \"one paragraph describing the query to write (output columns, filters, ordering)\",\n"
            f"    \"starter_code\": \"-- write your SELECT query here\\n\",\n"
            f"    \"expected_output\": \"col1|col2\\ncol3|col4\\n\",\n"
            f"    \"topics\": [\"{topics[0] if topics else 'SQL'}\"]\n"
            f"  }}\n"
            f"]}}\n"
            f"Return exactly {count} questions."
        )

    def _generate_questions(
        self, format_key: str, role: str, industry: str, level_key: str,
        level_label: str, level_blurb: str, num_questions: int,
        difficulty_hint: str = "baseline"
    ) -> List[Dict]:
        """
        Generate questions for the given format via OpenAI.
        Returns [] on failure. Validates + normalizes every question.
        """
        import os as _os
        api_key = _os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return []

        # SJT: best+worst per item, keep count as-is
        batches = []
        remaining = num_questions
        while remaining > 0:
            chunk = min(remaining, 10)
            batches.append(chunk)
            remaining -= chunk

        all_questions = []
        for batch_size in batches:
            batch = self._generate_one_batch(
                format_key=format_key,
                role=role, industry=industry,
                level_key=level_key, level_label=level_label,
                level_blurb=level_blurb, count=batch_size,
                difficulty_hint=difficulty_hint,
            )
            if not batch:
                return []
            all_questions.extend(batch)

        cleaned = []
        for raw_q in all_questions:
            q = self._normalize_question(format_key, raw_q)
            if q:
                cleaned.append(q)

        if len(cleaned) < num_questions:
            logger.warning(f"Format {format_key}: {len(cleaned)} valid, wanted {num_questions}")
        return cleaned[:num_questions]

    def _generate_one_batch(
        self, format_key: str, role: str, industry: str,
        level_key: str, level_label: str, level_blurb: str, count: int,
        difficulty_hint: str = "baseline"
    ) -> List[Dict]:
        """Single OpenAI call for a batch of questions in the given format."""
        import os as _os
        import requests
        api_key = _os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return []

        prompt = self._build_prompt_for_format(
            format_key=format_key,
            role=role, industry=industry,
            level_label=level_label, level_blurb=level_blurb, count=count,
            difficulty_hint=difficulty_hint,
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
            logger.error(f"AI batch failed for {format_key}: {e}")
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

    def _strip_answers_for_frontend(self, format_key: str, questions: List[Dict]) -> List[Dict]:
        """
        Remove any field that reveals the correct answer before sending
        to the frontend. Kept field set varies by format.
        """
        safe = []
        for q in questions:
            if format_key == "mcq":
                safe.append({"q": q.get("q", ""), "options": q.get("options", []),
                             "topics": q.get("topics", [])})
            elif format_key == "short_answer":
                safe.append({"q": q.get("q", ""), "topics": q.get("topics", [])})
            elif format_key == "numeracy":
                safe.append({"q": q.get("q", ""), "topics": q.get("topics", [])})
            elif format_key == "situational_judgment":
                safe.append({"scenario": q.get("scenario", ""), "options": q.get("options", []),
                             "topics": q.get("topics", [])})
            elif format_key == "behavioral":
                safe.append({"prompt": q.get("prompt", ""), "topics": q.get("topics", [])})
            elif format_key == "system_design":
                safe.append({"prompt": q.get("prompt", ""), "topics": q.get("topics", [])})
            elif format_key == "debugging":
                safe.append({
                    "buggy_code": q.get("buggy_code", ""),
                    "language": q.get("language", ""),
                    "topics": q.get("topics", []),
                })
            elif format_key == "case_study":
                safe.append({
                    "scenario": q.get("scenario", ""),
                    "questions": q.get("questions", []),
                    "topics": q.get("topics", []),
                })
            elif format_key == "coding":
                safe.append({
                    "problem": q.get("problem", ""),
                    "starter_code": q.get("starter_code", ""),
                    "language": q.get("language", "python"),
                    "topics": q.get("topics", []),
                })
            elif format_key == "sql":
                safe.append({
                    "schema": q.get("schema", ""),
                    "task": q.get("task", ""),
                    "starter_code": q.get("starter_code", ""),
                    "topics": q.get("topics", []),
                })
            else:
                safe.append({"q": q.get("q", "")})
        return safe

    # ------------------------------------------------------------
    # Answer / Complete
    # ------------------------------------------------------------

    def _ensure_format_columns(self) -> None:
        """Add answer_text, ai_score, ai_feedback columns. Idempotent."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                ALTER TABLE charvak_career_assessment_answers
                    ADD COLUMN IF NOT EXISTS answer_text TEXT,
                    ADD COLUMN IF NOT EXISTS ai_score INTEGER,
                    ADD COLUMN IF NOT EXISTS ai_feedback TEXT
            """)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"career-assessment column migration: {e}")

    def _normalize_topics_for_question(self, raw_topics) -> List[str]:
        """
        Soft-validate topic strings. Length-only check here; strict
        vocabulary validation happens at aggregation time when the role
        is known.
        """
        if not isinstance(raw_topics, list):
            return []
        out = []
        for t in raw_topics[:2]:
            if isinstance(t, str) and t.strip():
                out.append(t.strip())
        return out

    def _normalize_question(self, format_key: str, raw_q: Dict) -> Optional[Dict]:
        """Validate and normalize a raw question dict per format. Returns None if invalid."""
        if not isinstance(raw_q, dict):
            return None

        if format_key == "mcq":
            text = (raw_q.get("q") or "").strip()
            options = raw_q.get("options", [])
            ci = raw_q.get("correct_index")
            if not text or not isinstance(options, list) or len(options) < 4:
                return None
            if not isinstance(ci, int) or ci < 0 or ci >= len(options):
                return None
            q = {"q": text, "options": [str(o).strip() for o in options[:4]], "correct_index": ci,
                 "topics": self._normalize_topics_for_question(raw_q.get("topics"))}
            return self._shuffle_question_options(q)

        if format_key == "short_answer":
            text = (raw_q.get("q") or "").strip()
            expected = (raw_q.get("expected_answer") or "").strip()
            keywords = raw_q.get("keywords", [])
            if not text or not expected or not isinstance(keywords, list):
                return None
            return {"q": text, "expected_answer": expected,
                    "keywords": [str(k).strip() for k in keywords if str(k).strip()],
                    "topics": self._normalize_topics_for_question(raw_q.get("topics"))}

        if format_key == "numeracy":
            text = (raw_q.get("q") or "").strip()
            num = raw_q.get("correct_number")
            tol = raw_q.get("tolerance", 0)
            if not text or not isinstance(num, (int, float)):
                return None
            try:
                tol = float(tol)
            except (ValueError, TypeError):
                tol = 0.0
            return {"q": text, "correct_number": float(num), "tolerance": abs(tol),
                    "topics": self._normalize_topics_for_question(raw_q.get("topics"))}

        if format_key == "situational_judgment":
            scenario = (raw_q.get("scenario") or "").strip()
            options = raw_q.get("options", [])
            bi = raw_q.get("best_index")
            wi = raw_q.get("worst_index")
            if not scenario or not isinstance(options, list) or len(options) < 3:
                return None
            if not isinstance(bi, int) or not isinstance(wi, int) or bi == wi:
                return None
            if bi < 0 or bi >= len(options) or wi < 0 or wi >= len(options):
                return None
            # Shuffle options and recompute best/worst
            correct_best_text = options[bi]
            correct_worst_text = options[wi]
            opts = list(options)
            random.shuffle(opts)
            try:
                new_bi = opts.index(correct_best_text)
                new_wi = opts.index(correct_worst_text)
            except ValueError:
                new_bi, new_wi = bi, wi
            return {"scenario": scenario, "options": [str(o).strip() for o in opts],
                    "best_index": new_bi, "worst_index": new_wi,
                    "topics": self._normalize_topics_for_question(raw_q.get("topics"))}

        if format_key == "behavioral":
            prompt = (raw_q.get("prompt") or "").strip()
            rubric = raw_q.get("rubric_star", {})
            if not prompt or not isinstance(rubric, dict):
                return None
            return {"prompt": prompt, "rubric_star": {
                "situation": str(rubric.get("situation", "")),
                "task": str(rubric.get("task", "")),
                "action": str(rubric.get("action", "")),
                "result": str(rubric.get("result", "")),
            }, "topics": self._normalize_topics_for_question(raw_q.get("topics"))}

        if format_key == "system_design":
            prompt = (raw_q.get("prompt") or "").strip()
            rubric = raw_q.get("rubric", [])
            if not prompt or not isinstance(rubric, list):
                return None
            return {"prompt": prompt, "rubric": [str(r).strip() for r in rubric if str(r).strip()],
                    "topics": self._normalize_topics_for_question(raw_q.get("topics"))}

        if format_key == "debugging":
            code = (raw_q.get("buggy_code") or "").strip()
            lang = (raw_q.get("language") or "Python").strip()
            summary = (raw_q.get("correct_fix_summary") or "").strip()
            bug_class = (raw_q.get("bug_class") or "").strip()
            if not code or not summary:
                return None
            return {"buggy_code": code, "language": lang,
                    "correct_fix_summary": summary, "bug_class": bug_class,
                    "topics": self._normalize_topics_for_question(raw_q.get("topics"))}

        if format_key == "case_study":
            scenario = (raw_q.get("scenario") or "").strip()
            questions = raw_q.get("questions", [])
            rubric = raw_q.get("rubric", [])
            if not scenario or not isinstance(questions, list) or not questions:
                return None
            return {"scenario": scenario,
                    "questions": [str(q).strip() for q in questions if str(q).strip()],
                    "rubric": [str(r).strip() for r in rubric if str(r).strip()],
                    "topics": self._normalize_topics_for_question(raw_q.get("topics"))}

        if format_key == "coding":
            problem = (raw_q.get("problem") or "").strip()
            starter = (raw_q.get("starter_code") or "").strip()
            lang = (raw_q.get("language") or "python").strip().lower()
            tc_raw = raw_q.get("test_cases", [])
            if not problem or not isinstance(tc_raw, list) or not tc_raw:
                return None
            test_cases = []
            for tc in tc_raw:
                if not isinstance(tc, dict):
                    continue
                stdin = tc.get("stdin", "")
                expected = tc.get("expected_output", "")
                if not isinstance(stdin, str) or not isinstance(expected, str):
                    continue
                if not expected.strip():
                    continue
                test_cases.append({"stdin": stdin, "expected_output": expected})
            if not test_cases:
                return None
            # Cap test cases at 5 to bound Judge0 call cost per question
            test_cases = test_cases[:5]
            return {
                "problem": problem,
                "starter_code": starter or "# read input from stdin\n# your code here\n",
                "language": lang if lang in ("python",) else "python",
                "test_cases": test_cases,
                "topics": self._normalize_topics_for_question(raw_q.get("topics")),
            }

        if format_key == "sql":
            schema = (raw_q.get("schema") or "").strip()
            task = (raw_q.get("task") or "").strip()
            starter = (raw_q.get("starter_code") or "").strip()
            expected = raw_q.get("expected_output", "")
            if not schema or not task:
                return None
            if not isinstance(expected, str) or not expected.strip():
                return None
            # Ensure trailing newline for consistent exact-match
            if not expected.endswith("\n"):
                expected = expected + "\n"
            return {
                "schema": schema,
                "task": task,
                "starter_code": starter or "-- write your SELECT query here\n",
                "expected_output": expected,
                "topics": self._normalize_topics_for_question(raw_q.get("topics")),
            }

        return None

    def _score_deterministic(self, format_key: str, question: Dict, answer) -> Dict:
        """
        Score a deterministic format.
        Returns {score: 0-100, is_correct: bool, feedback: str|None}
        """
        if format_key == "mcq":
            try:
                ans = int(answer) if answer is not None else -1
            except (ValueError, TypeError):
                ans = -1
            correct = question.get("correct_index")
            ok = (ans == correct)
            return {"score": 100 if ok else 0, "is_correct": ok, "feedback": None}

        if format_key == "numeracy":
            try:
                ans = float(answer) if answer is not None and str(answer).strip() != "" else None
            except (ValueError, TypeError):
                ans = None
            if ans is None:
                return {"score": 0, "is_correct": False, "feedback": None}
            correct = question.get("correct_number", 0)
            tol = question.get("tolerance", 0)
            ok = abs(ans - correct) <= tol
            return {"score": 100 if ok else 0, "is_correct": ok,
                    "feedback": None if ok else f"Correct answer: {correct}"}

        if format_key == "situational_judgment":
            # Answer comes as {"best": int, "worst": int} or "best,worst" string
            best_ans, worst_ans = None, None
            if isinstance(answer, dict):
                best_ans = answer.get("best")
                worst_ans = answer.get("worst")
            elif isinstance(answer, str) and "," in answer:
                parts = answer.split(",")
                try:
                    best_ans = int(parts[0])
                    worst_ans = int(parts[1])
                except (ValueError, TypeError):
                    pass
            correct_best = question.get("best_index")
            correct_worst = question.get("worst_index")
            points = 0
            if best_ans == correct_best:
                points += 50
            if worst_ans == correct_worst:
                points += 50
            return {"score": points, "is_correct": points == 100, "feedback": None}

        if format_key == "short_answer":
            # Keyword matching. If 0 keywords, treat as fail-safe.
            text = str(answer or "").lower()
            if not text.strip():
                return {"score": 0, "is_correct": False, "feedback": None}
            keywords = [k.lower() for k in question.get("keywords", []) if k]
            if not keywords:
                # Fallback: length-based heuristic (weak but honest)
                score = min(len(text.split()) * 10, 60)
                return {"score": score, "is_correct": False,
                        "feedback": "No keywords configured; scored on completeness."}
            hits = sum(1 for k in keywords if k in text)
            ratio = hits / len(keywords)
            score = int(ratio * 100)
            return {"score": score, "is_correct": score >= 70,
                    "feedback": f"Matched {hits} of {len(keywords)} key concepts" if score < 100 else None}

        # Shouldn't reach here
        return {"score": 0, "is_correct": False, "feedback": None}

    def _score_ai_batch(self, format_key: str, questions: List[Dict],
                        answers: List, role: str, industry: str, level_label: str) -> List[Dict]:
        """
        Score all AI-scored format answers in ONE OpenAI call.
        Returns a list of {score, is_correct, feedback} matching `answers`.
        """
        import os as _os
        import requests
        api_key = _os.getenv("OPENAI_API_KEY", "")
        default = [{"score": 0, "is_correct": False, "feedback": "AI scoring unavailable"} for _ in answers]
        if not api_key:
            return default

        # Build scoring payload
        payload_items = []
        for i, (q, a) in enumerate(zip(questions, answers)):
            item = {"index": i, "answer": str(a or "")[:2000]}
            if format_key == "behavioral":
                item["prompt"] = q.get("prompt", "")
                item["rubric_star"] = q.get("rubric_star", {})
            elif format_key == "system_design":
                item["prompt"] = q.get("prompt", "")
                item["rubric"] = q.get("rubric", [])
            elif format_key == "debugging":
                item["buggy_code"] = q.get("buggy_code", "")
                item["language"] = q.get("language", "")
                item["correct_fix_summary"] = q.get("correct_fix_summary", "")
            elif format_key == "case_study":
                item["scenario"] = q.get("scenario", "")
                item["sub_questions"] = q.get("questions", [])
                item["rubric"] = q.get("rubric", [])
            payload_items.append(item)

        prompt = (
            f"You are scoring a {format_key} assessment for a {role} in {industry} "
            f"at {level_label} level.\n\n"
            f"For each item below, score the candidate's answer from 0-100 "
            f"against the rubric and expected quality. Be fair but rigorous.\n\n"
            f"ITEMS:\n{json.dumps(payload_items, ensure_ascii=False)[:12000]}\n\n"
            f"Return STRICT JSON: {{\"scores\": [{{\"index\": 0, \"score\": 75, "
            f"\"feedback\": \"one sentence\"}}]}}\n"
            f"Return exactly {len(answers)} scores, indexes 0..{len(answers)-1}."
        )

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "response_format": {"type": "json_object"},
                },
                timeout=90,
            )
            data = response.json()
            content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
            scores = parsed.get("scores", [])
            # Map back to answer order
            result = list(default)
            for s in scores:
                idx = s.get("index")
                if isinstance(idx, int) and 0 <= idx < len(answers):
                    sc = int(s.get("score", 0))
                    sc = max(0, min(100, sc))
                    result[idx] = {
                        "score": sc,
                        "is_correct": sc >= 70,
                        "feedback": str(s.get("feedback", ""))[:500],
                    }
            return result
        except Exception as e:
            logger.error(f"AI batch scoring failed for {format_key}: {e}")
            return default

    def _score_coding_batch(self, questions: List[Dict], answers: List) -> List[Dict]:
        """
        Score coding submissions via Judge0. Each question carries test_cases.
        Each answer is the candidate's Python source code (or None).

        Returns [{score, is_correct, feedback}] in question order.
        score = round(passed_cases / total_cases * 100).
        """
        try:
            from judge0_client import judge0_client, LANGUAGE_IDS
        except Exception as e:
            logger.error(f"judge0_client import failed: {e}")
            return [{"score": 0, "is_correct": False, "feedback": "Code execution unavailable"} for _ in answers]

        results = []
        for i, (q, a) in enumerate(zip(questions, answers)):
            source = (a or "").strip() if isinstance(a, str) else ""
            if not source:
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": "No code submitted",
                })
                continue

            test_cases = q.get("test_cases") or []
            if not test_cases:
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": "No test cases configured for this question",
                })
                continue

            lang = (q.get("language") or "python").lower()
            lang_id = LANGUAGE_IDS.get(lang, LANGUAGE_IDS["python"])

            try:
                exec_result = judge0_client.run_test_cases(
                    source_code=source,
                    test_cases=test_cases,
                    language_id=lang_id,
                )
            except Exception as e:
                logger.error(f"judge0 run failed for question {i}: {e}")
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": f"Execution error: {e}",
                })
                continue

            if exec_result.get("status") != "success":
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": exec_result.get("message", "Execution failed"),
                })
                continue

            passed = exec_result.get("passed", 0)
            total = exec_result.get("total", 0)
            score = exec_result.get("score", 0)
            results.append({
                "score": score,
                "is_correct": score >= 70,
                "feedback": f"{passed}/{total} test cases passed",
            })

        return results

    @staticmethod
    def _sql_outputs_match(actual: str, expected: str) -> bool:
        """
        Compare two SQL stdout strings with numeric tolerance and whitespace normalization.

        Rules:
        - Trailing/leading whitespace on each line is stripped.
        - Trailing blank lines are dropped.
        - Row counts must match.
        - Cell counts per row must match.
        - If both cells parse as float, compare with abs(a - b) < 1e-3.
        - Otherwise, exact string match.
        """
        def _rows(s: str):
            return [line.rstrip() for line in (s or "").strip("\n").split("\n")]

        a_rows = _rows(actual)
        e_rows = _rows(expected)

        # Drop trailing blank rows on both sides
        while a_rows and a_rows[-1] == "":
            a_rows.pop()
        while e_rows and e_rows[-1] == "":
            e_rows.pop()

        if len(a_rows) != len(e_rows):
            return False

        for la, le in zip(a_rows, e_rows):
            ca = [c.strip() for c in la.split("|")]
            ce = [c.strip() for c in le.split("|")]
            if len(ca) != len(ce):
                return False
            for va, ve in zip(ca, ce):
                # Numeric tolerance path
                try:
                    fa = float(va)
                    fe = float(ve)
                    if abs(fa - fe) > 1e-3:
                        return False
                    continue
                except (ValueError, TypeError):
                    pass
                # String path (case-sensitive)
                if va != ve:
                    return False

        return True

    def _score_sql_batch(self, questions: List[Dict], answers: List) -> List[Dict]:
        """
        Score SQL submissions via Judge0. Each question has {schema, task, expected_output}.
        Each answer is the candidate's SELECT query (or None).

        Runs the schema + query in Judge0 (SQLite), gets the raw stdout,
        compares against expected_output with _sql_outputs_match (float
        tolerance + whitespace normalization).

        Returns [{score, is_correct, feedback}] in question order. score = 100 or 0.
        """
        try:
            from judge0_client import judge0_client, LANGUAGE_IDS
        except Exception as e:
            logger.error(f"judge0_client import failed: {e}")
            return [{"score": 0, "is_correct": False, "feedback": "SQL execution unavailable"} for _ in answers]

        sql_lang_id = LANGUAGE_IDS.get("sqlite3", 82)

        results = []
        for i, (q, a) in enumerate(zip(questions, answers)):
            query = (a or "").strip() if isinstance(a, str) else ""
            if not query:
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": "No query submitted",
                })
                continue

            # Reject submissions that are only the starter comment
            if query.startswith("--") and "\n" not in query and "select" not in query.lower():
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": "No query submitted",
                })
                continue

            schema = (q.get("schema") or "").strip()
            expected = q.get("expected_output") or ""
            if not schema or not expected:
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": "Question misconfigured (missing schema or expected_output)",
                })
                continue

            full_source = f"{schema}\n\n{query}\n"

            # NOTE: we do NOT pass expected_output to Judge0 anymore. We
            # compare ourselves, so we get float tolerance + whitespace
            # normalization.
            try:
                exec_result = judge0_client.run_code(
                    source_code=full_source,
                    language_id=sql_lang_id,
                )
            except Exception as e:
                logger.error(f"judge0 sql run failed for question {i}: {e}")
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": f"Execution error: {e}",
                })
                continue

            if exec_result.get("status") != "success":
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": exec_result.get("message", "Execution failed"),
                })
                continue

            # If Judge0 itself reports an error status (not "Accepted"), fail early.
            raw_status = exec_result.get("raw_status", "") or ""
            if raw_status and raw_status.lower() not in ("accepted",):
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": f"Query failed: {raw_status}"[:200],
                })
                continue

            actual = exec_result.get("stdout", "") or ""
            if self._sql_outputs_match(actual, expected):
                results.append({
                    "score": 100,
                    "is_correct": True,
                    "feedback": "Query produced the expected output",
                })
            else:
                results.append({
                    "score": 0,
                    "is_correct": False,
                    "feedback": "Query produced different output",
                })

        return results

    def _aggregate_skill_gap(self, questions: List[Dict], scored: List[Dict]) -> List[Dict]:
        """
        Group question scores by topic and return per-topic aggregates.
        A question with 2 topics contributes its score to both.
        Questions with no topics are skipped (they can't be attributed).
        Returns a list sorted by pct ascending (weakest first).
        """
        buckets = {}  # topic -> {correct: int, total: int}
        for i, q in enumerate(questions):
            if i >= len(scored):
                break
            topics = q.get("topics") or []
            if not topics:
                continue
            sc = scored[i].get("score", 0)
            is_correct = scored[i].get("is_correct", False)
            for topic in topics:
                if not isinstance(topic, str) or not topic.strip():
                    continue
                topic = topic.strip()
                if topic not in buckets:
                    buckets[topic] = {"correct": 0, "total": 0}
                buckets[topic]["total"] += 1
                if is_correct:
                    buckets[topic]["correct"] += 1
                # Also track a running percentage for AI-scored formats
                buckets[topic].setdefault("pct_sum", 0)
                buckets[topic]["pct_sum"] = buckets[topic].get("pct_sum", 0) + sc

        result = []
        for topic, b in buckets.items():
            total = b["total"]
            if total == 0:
                continue
            correct = b["correct"]
            # Blend: use correct/total for determinism, but for AI-scored
            # formats the "correct" flag is >= 70%, which may be too strict.
            # Use average of two signals for fairness.
            correct_pct = round(correct / total * 100)
            avg_score_pct = round(b.get("pct_sum", 0) / total)
            blended = round((correct_pct + avg_score_pct) / 2)
            if blended >= 80:
                status = "strong"
            elif blended >= 55:
                status = "mixed"
            else:
                status = "weak"
            result.append({
                "topic": topic,
                "correct": correct,
                "total": total,
                "correct_pct": correct_pct,
                "avg_score_pct": avg_score_pct,
                "pct": blended,
                "status": status,
            })
        # Weakest first
        result.sort(key=lambda x: x["pct"])
        return result

    def _dispatch_scoring(
        self, format_key: str, questions: List[Dict], answers: List,
        role: str, industry: str, level_label: str
    ) -> List[Dict]:
        """
        Score every answer. Returns [{score, is_correct, feedback}] in order.
        AI-scored formats go through one batched OpenAI call; deterministic
        formats are scored per-answer with no API cost.
        """
        registry = self._format_registry()
        fmt_meta = registry.get(format_key, {})
        scored_by = fmt_meta.get("scored_by", "deterministic")

        if scored_by == "hybrid" and format_key == "coding":
            return self._score_coding_batch(questions, answers)
        if scored_by == "hybrid" and format_key == "sql":
            return self._score_sql_batch(questions, answers)

        if scored_by == "ai":
            return self._score_ai_batch(format_key, questions, answers,
                                        role, industry, level_label)

        results = []
        for q, a in zip(questions, answers):
            results.append(self._score_deterministic(format_key, q, a))
        return results

    def submit_answer(self, data: Dict) -> Dict:
        """
        Record one answer. Idempotent per (assessment_id, question_index).
        data = {email, assessment_id, question_index, answer (any type)}
        """
        email = (data.get("email") or "").strip().lower()
        assessment_id = (data.get("assessment_id") or "").strip()
        try:
            q_index = int(data.get("question_index"))
        except (ValueError, TypeError):
            return {"status": "error", "message": "question_index must be an integer"}
        answer = data.get("answer")

        if not email or not assessment_id:
            return {"status": "error", "message": "email and assessment_id required"}

        self._ensure_tables()
        self._ensure_format_columns()

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT email, questions_json, format FROM charvak_career_assessments WHERE assessment_id = %s",
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
            fmt = row[2] or "mcq"
            if q_index < 0 or q_index >= len(questions):
                cur.close(); conn.close()
                return {"status": "error", "message": "Invalid question_index"}

            result = self._dispatch_scoring(fmt, [questions[q_index]], [answer], "", "", "")

            selected_index = None
            answer_text = None
            if isinstance(answer, int):
                selected_index = answer
            elif isinstance(answer, str) and answer.isdigit():
                selected_index = int(answer)
            elif isinstance(answer, str):
                answer_text = answer
            elif isinstance(answer, dict):
                try:
                    answer_text = f"{answer.get('best')},{answer.get('worst')}"
                except Exception:
                    answer_text = json.dumps(answer)

            sc = result[0]["score"] if result else 0
            is_correct = result[0]["is_correct"] if result else False
            feedback = result[0]["feedback"] if result else None

            answer_id = f"ANS-{secrets.token_hex(4).upper()}"
            cur.execute("""
                INSERT INTO charvak_career_assessment_answers
                    (answer_id, assessment_id, question_index, selected_index,
                     is_correct, answer_text, ai_score, ai_feedback)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (assessment_id, question_index) DO UPDATE
                SET selected_index = EXCLUDED.selected_index,
                    is_correct = EXCLUDED.is_correct,
                    answer_text = EXCLUDED.answer_text,
                    ai_score = EXCLUDED.ai_score,
                    ai_feedback = EXCLUDED.ai_feedback,
                    answered_at = CURRENT_TIMESTAMP
            """, (answer_id, assessment_id, q_index, selected_index,
                  is_correct, answer_text, sc, feedback))
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
        data = {email, assessment_id, answers: Optional[List]}
        If answers provided, they're written first (single-shot submit).
        AI-scored formats use ONE batched OpenAI call for all answers.
        """
        email = (data.get("email") or "").strip().lower()
        assessment_id = (data.get("assessment_id") or "").strip()
        if not email or not assessment_id:
            return {"status": "error", "message": "email and assessment_id required"}

        self._ensure_tables()
        self._ensure_format_columns()

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT email, role, industry, level, size, num_questions,
                       questions_json, status, format
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

            _, role, industry, level, size, num_questions, questions_json, _, fmt = row
            fmt = fmt or "mcq"
            questions = questions_json if isinstance(questions_json, list) else json.loads(questions_json or "[]")
            total = len(questions)

            # Level label for scoring context
            level_label = next((l["label"] for l in CAREER_LEVELS if l["key"] == level), level)

            # If answers array provided, use it; else read from DB
            submitted = data.get("answers")
            if isinstance(submitted, list):
                answers = submitted[:total]
                while len(answers) < total:
                    answers.append(None)
            else:
                # Read stored answers
                cur.execute("""
                    SELECT question_index, selected_index, answer_text
                    FROM charvak_career_assessment_answers
                    WHERE assessment_id = %s ORDER BY question_index
                """, (assessment_id,))
                rows = cur.fetchall()
                answers_map = {}
                for r in rows:
                    q_idx, sel, txt = r
                    if txt is not None:
                        answers_map[q_idx] = txt
                    else:
                        answers_map[q_idx] = sel
                answers = [answers_map.get(i) for i in range(total)]

            # Score via dispatch (one batched AI call for AI formats)
            scored = self._dispatch_scoring(fmt, questions, answers, role, industry, level_label)

            # Persist per-answer scores
            for i in range(total):
                ans_val = answers[i] if i < len(answers) else None
                sc = scored[i]["score"] if i < len(scored) else 0
                corr = scored[i]["is_correct"] if i < len(scored) else False
                fb = scored[i].get("feedback") if i < len(scored) else None

                # Determine selected_index vs answer_text
                selected_index = None
                answer_text = None
                if isinstance(ans_val, int):
                    selected_index = ans_val
                elif isinstance(ans_val, str) and ans_val.isdigit():
                    selected_index = int(ans_val)
                elif isinstance(ans_val, str):
                    answer_text = ans_val
                elif isinstance(ans_val, dict):
                    try:
                        answer_text = f"{ans_val.get('best')},{ans_val.get('worst')}"
                    except Exception:
                        answer_text = json.dumps(ans_val)

                cur.execute("""
                    INSERT INTO charvak_career_assessment_answers
                        (answer_id, assessment_id, question_index, selected_index,
                         is_correct, answer_text, ai_score, ai_feedback)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (assessment_id, question_index) DO UPDATE
                    SET selected_index = EXCLUDED.selected_index,
                        is_correct = EXCLUDED.is_correct,
                        answer_text = EXCLUDED.answer_text,
                        ai_score = EXCLUDED.ai_score,
                        ai_feedback = EXCLUDED.ai_feedback,
                        answered_at = CURRENT_TIMESTAMP
                """, (f"ANS-{secrets.token_hex(4).upper()}", assessment_id, i,
                      selected_index, corr, answer_text, sc, fb))

            # Aggregate: per-question scores are 0-100; overall is the mean
            if total > 0:
                overall = round(sum(s["score"] for s in scored) / total)
            else:
                overall = 0
            correct_count = sum(1 for s in scored if s.get("is_correct"))
            passed = overall >= PASSING_SCORE

            cur.execute("""
                UPDATE charvak_career_assessments
                SET status = 'completed',
                    score = %s,
                    passed = %s,
                    correct_count = %s,
                    completed_at = CURRENT_TIMESTAMP
                WHERE assessment_id = %s
            """, (overall, passed, correct_count, assessment_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"complete_assessment failed: {e}")
            return {"status": "error", "message": "Could not complete assessment"}

        # NOTE: ability_engine.update_from_assessment is called internally
        # by results_system.record_assessment_result() when skill= is passed.
        # Do not call it here again (would double-count attempts).

        # Persist to /my-results feed (this also updates ability)
        try:
            from results_system import results_system
            results_system.record_assessment_result(
                email=email,
                assessment_type="career_readiness",
                assessment_name=f"{role} in {industry} ({fmt})",
                score=float(overall),
                total_questions=total,
                correct_answers=correct_count,
                details={
                    "assessment_id": assessment_id,
                    "role": role,
                    "industry": industry,
                    "level": level,
                    "size": size,
                    "format": fmt,
                },
                skill=f"career_{fmt}",
                difficulty=level,
            )
        except Exception as e:
            logger.warning(f"career-assessment result persistence failed: {e}")

        # Build per-question breakdown for the frontend
        breakdown = []
        for i in range(total):
            entry = {
                "index": i,
                "score": scored[i]["score"] if i < len(scored) else 0,
                "is_correct": scored[i].get("is_correct") if i < len(scored) else False,
                "feedback": scored[i].get("feedback") if i < len(scored) else None,
            }
            q = questions[i]
            if fmt == "mcq":
                entry["question"] = q.get("q", "")
                entry["your_answer"] = answers[i]
                entry["correct_index"] = q.get("correct_index")
            elif fmt in ("short_answer", "numeracy"):
                entry["question"] = q.get("q", "")
                entry["your_answer"] = answers[i]
            elif fmt == "situational_judgment":
                entry["question"] = q.get("scenario", "")
                entry["your_answer"] = answers[i]
                entry["best_index"] = q.get("best_index")
            elif fmt == "behavioral":
                entry["question"] = q.get("prompt", "")
                entry["your_answer"] = answers[i]
            elif fmt == "system_design":
                entry["question"] = q.get("prompt", "")
                entry["your_answer"] = answers[i]
            elif fmt == "debugging":
                entry["question"] = q.get("buggy_code", "")
                entry["your_answer"] = answers[i]
            elif fmt == "case_study":
                entry["question"] = q.get("scenario", "")
                entry["your_answer"] = answers[i]
            breakdown.append(entry)

        # Aggregate skill gap by topic
        skill_gap = self._aggregate_skill_gap(questions, scored)

        return {
            "status": "success",
            "assessment_id": assessment_id,
            "role": role,
            "industry": industry,
            "level": level,
            "format": fmt,
            "score": overall,
            "passed": passed,
            "correct_count": correct_count,
            "total_questions": total,
            "passing_score": PASSING_SCORE,
            "breakdown": breakdown,
            "skill_gap": skill_gap,
            "message": f"Career readiness: {overall}%",
        }

    # ------------------------------------------------------------
    # History / Get
    # ------------------------------------------------------------

    def generate_learning_path(self, assessment_id: str, email: str) -> Dict:
        """
        Generate (or return cached) learning path for a completed assessment.
        Lazily invoked - no credits charged, but stored so repeat visits are free.
        Returns weak/mixed topics + matched charvak_courses + AI-curated
        external resources + a weekly plan.
        """
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
                SELECT email, role, industry, level, format, status, score,
                       questions_json, learning_path_json
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
            if row[5] != "completed":
                cur.close(); conn.close()
                return {"status": "error", "message": "Assessment must be completed first"}

            _, role, industry, level, fmt, _, score, questions_json, cached_json = row
            questions = questions_json if isinstance(questions_json, list) else json.loads(questions_json or "[]")
            cached = cached_json if isinstance(cached_json, dict) else (json.loads(cached_json) if cached_json else None)

            if cached:
                cur.close(); conn.close()
                return {"status": "success", "cached": True, **cached}

            # Load answers to compute skill gap
            cur.execute("""
                SELECT question_index, is_correct, ai_score
                FROM charvak_career_assessment_answers
                WHERE assessment_id = %s
            """, (assessment_id,))
            answer_rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"learning path load failed: {e}")
            return {"status": "error", "message": "Could not load assessment"}

        # Recompute scored list for skill gap
        answers_by_idx = {r[0]: r for r in answer_rows}
        scored = []
        for i in range(len(questions)):
            r = answers_by_idx.get(i)
            if r:
                sc = r[2] if r[2] is not None else (100 if r[1] else 0)
                scored.append({"score": sc, "is_correct": bool(r[1]), "feedback": None})
            else:
                scored.append({"score": 0, "is_correct": False, "feedback": None})

        skill_gap = self._aggregate_skill_gap(questions, scored)
        # Weak + mixed topics are what we build a path around
        focus_topics = [g for g in skill_gap if g.get("status") in ("weak", "mixed")]

        # Distinguish "no topics at all" (old assessment, no tagging) from
        # "all strong" (real result, nothing to work on)
        if not skill_gap:
            result = {
                "assessment_id": assessment_id,
                "role": role,
                "industry": industry,
                "level": level,
                "score": score,
                "weak_topics": [],
                "strong_topics": [],
                "charvak_courses": [],
                "custom_course_candidates": [],
                "weekly_plan": [],
                "message": "This assessment doesn't have topic data (created before topic tagging). Take a new assessment to get a personalized learning path.",
            }
            self._cache_learning_path(assessment_id, result)
            return {"status": "success", "cached": False, **result}

        if not focus_topics:
            # All strong - return an honest "you're strong" message
            result = {
                "assessment_id": assessment_id,
                "role": role,
                "industry": industry,
                "level": level,
                "score": score,
                "weak_topics": [],
                "strong_topics": [g["topic"] for g in skill_gap if g.get("status") == "strong"],
                "charvak_courses": [],
                "custom_course_candidates": [],
                "weekly_plan": [],
                "message": "Strong across all topics - no weak areas to address. Consider a harder level or a different format.",
            }
            self._cache_learning_path(assessment_id, result)
            return {"status": "success", "cached": False, **result}

        # Fetch the charvak_courses catalog (25 rows) for AI matching
        courses_catalog = []
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT course_id, course_name, category, level, description
                FROM charvak_courses
                WHERE status IS NULL OR status = 'active' OR status = 'published'
                ORDER BY course_name
                LIMIT 30
            """)
            for r in cur.fetchall():
                courses_catalog.append({
                    "course_id": r[0],
                    "course_name": r[1],
                    "category": r[2],
                    "level": r[3],
                    "description": (r[4] or "")[:200],
                })
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"course catalog lookup failed: {e}")

        # AI call
        path = self._ai_generate_learning_path(
            role=role, industry=industry, level=level, fmt=fmt,
            score=score, focus_topics=focus_topics,
            strong_topics=[g["topic"] for g in skill_gap if g.get("status") == "strong"],
            courses_catalog=courses_catalog,
        )

        # Session 18: identify weak topics with no matching Charvak course.
        # These become "custom course candidates" — the frontend offers to
        # generate a private course for each (50 credits each).
        matched_course_ids = {c.get("course_id") for c in (path.get("charvak_courses") or []) if isinstance(c, dict)}
        matched_course_names = {c.get("course_name", "").lower() for c in (path.get("charvak_courses") or []) if isinstance(c, dict)}

        custom_course_candidates = []
        for topic_entry in focus_topics:
            topic_name = topic_entry.get("topic", "")
            if not topic_name:
                continue
            # A topic is "unmatched" if no returned course name contains any
            # significant word from the topic. This is a heuristic — the
            # catalog is small enough that name matching is reliable.
            topic_words = [w.lower() for w in topic_name.split() if len(w) > 3]
            matched = False
            for cname in matched_course_names:
                if any(w in cname for w in topic_words):
                    matched = True
                    break
            if not matched:
                custom_course_candidates.append({
                    "topic": topic_name,
                    "pct": topic_entry.get("pct", 0),
                    "status": topic_entry.get("status", "weak"),
                    "level": (level or "mid").lower(),
                    "role": role,
                    "industry": industry,
                })

        result = {
            "assessment_id": assessment_id,
            "role": role,
            "industry": industry,
            "level": level,
            "score": score,
            "weak_topics": [g["topic"] for g in focus_topics],
            "strong_topics": [g["topic"] for g in skill_gap if g.get("status") == "strong"],
            "charvak_courses": path.get("charvak_courses", []),
            "custom_course_candidates": custom_course_candidates,
            "weekly_plan": path.get("weekly_plan", []),
            "message": path.get("message", "Learning path generated."),
        }
        self._cache_learning_path(assessment_id, result)
        return {"status": "success", "cached": False, **result}

    def _cache_learning_path(self, assessment_id: str, path: Dict) -> None:
        """Store the generated path on the assessment row. Non-fatal."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE charvak_career_assessments
                SET learning_path_json = %s::jsonb
                WHERE assessment_id = %s
            """, (json.dumps(path), assessment_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"learning path cache failed: {e}")

    def _ai_generate_learning_path(
        self, role: str, industry: str, level: str, fmt: str,
        score: int, focus_topics: List[Dict], strong_topics: List[str],
        courses_catalog: List[Dict]
    ) -> Dict:
        """One OpenAI call to build a curated learning path."""
        import os as _os
        import requests
        api_key = _os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return {
                "message": "AI unavailable - no learning path generated.",
                "charvak_courses": [], "external_resources": [], "weekly_plan": [],
            }

        focus_str = ", ".join(f"{t['topic']} ({t['pct']}%)" for t in focus_topics)
        strong_str = ", ".join(strong_topics) if strong_topics else "(none)"
        courses_str = json.dumps(courses_catalog, ensure_ascii=False)[:5000] if courses_catalog else "[]"

        prompt = (
            f"You are a career coach building a personalized learning plan.\n\n"
            f"CANDIDATE\n"
            f"  Role: {role}\n"
            f"  Industry: {industry}\n"
            f"  Level: {level}\n"
            f"  Recent {fmt} assessment score: {score}%\n\n"
            f"WEAK / MIXED TOPICS (need improvement):\n  {focus_str}\n\n"
            f"STRONG TOPICS (no action needed):\n  {strong_str}\n\n"
            f"AVAILABLE CHARVAK COURSES (pick the best 2-4 that match weak topics):\n"
            f"{courses_str}\n\n"
            f"Return STRICT JSON with this exact shape:\n"
            f"{{\n"
            f'  "charvak_courses": [\n'
            f'    {{"course_id": "...", "course_name": "...", "reason": "why this course addresses a weak topic (1 sentence)"}}\n'
            f"  ],\n"
            f'  "weekly_plan": [\n'
            f'    {{"week": 1, "focus": "topic focus", "activities": ["activity 1", "activity 2"]}}\n'
            f"  ],\n"
            f'  "message": "2-3 sentence overview of the plan"\n'
            f"}}\n\n"
            f"Rules:\n"
            f"- Pick charvak_courses ONLY from the provided catalog (don't invent course IDs).\n"
            f"- If no course matches, return an empty array - don't force one.\n"
            f"- Weekly plan: 2-4 weeks, calibrated to the level ({level}).\n"
            f"- Be encouraging but honest about the gap.\n"
            f"- Do NOT reference external platforms (Coursera, Khan Academy, Udemy, YouTube, etc). Only Charvak courses exist.\n"
        )

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.4,
                    "response_format": {"type": "json_object"},
                },
                timeout=60,
            )
            data = response.json()
            content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
            if content.startswith("```"):
                content = content.split("```", 2)[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()
            parsed = json.loads(content)
            # Sanitize: only accept courses from the catalog
            valid_ids = {c["course_id"] for c in courses_catalog}
            valid_courses = []
            for c in parsed.get("charvak_courses", []):
                if isinstance(c, dict) and c.get("course_id") in valid_ids:
                    valid_courses.append(c)
            return {
                "charvak_courses": valid_courses,
                "weekly_plan": parsed.get("weekly_plan", []) if isinstance(parsed.get("weekly_plan"), list) else [],
                "message": str(parsed.get("message", ""))[:500],
            }
        except Exception as e:
            logger.error(f"learning path AI failed: {e}")
            return {
                "message": "AI unavailable - please try again later.",
                "charvak_courses": [], "external_resources": [], "weekly_plan": [],
            }

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