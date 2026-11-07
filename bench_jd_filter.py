"""
Bench JD Filter - Session 108G

Gates incoming JDs by 3 criteria before they enter the pipeline:
  1. Visa compatibility (H1B / OPT / H4-EAD)
  2. Location (US or remote-US only)
  3. Skill overlap (>=30% of JD skills match a bench candidate)

Rate is NOT a gate - used only for scoring, never rejection.

Rejected JDs are logged to charvak_rejected_jds for audit.
"""

import os
import re
import json
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class BenchJDFilter:
    """Filter incoming JDs by bench relevance."""

    VISA_COMPAT = {
        "H1B":    ["H1B", "Any", "Not specified", ""],
        "OPT":    ["OPT", "H1B", "Any", "Not specified", ""],
        "H4-EAD": ["H4-EAD", "H1B", "Any", "Not specified", ""],
        "GC":     ["GC", "Any", "Not specified", ""],
        "USC":    ["USC", "Any", "Not specified", ""],
    }

    NON_US = [
        "germany", "deutschland", "berlin", "munich", "münchen", "hamburg",
        "frankfurt", "cologne", "köln", "düsseldorf", "stuttgart", "leipzig",
        "homeoffice", "augsburg", "dortmund", "essen", "bremen", "dresden",
        "hanover", "nuremberg", "bonn", "karlsruhe", "mannheim", "wiesbaden",
        "uk", "united kingdom", "london", "manchester", "edinburgh",
        "france", "paris", "lyon", "netherlands", "amsterdam", "rotterdam",
        "spain", "madrid", "barcelona", "italy", "milan", "rome",
        "poland", "warsaw", "krakow", "portugal", "lisbon", "porto",
        "ireland", "dublin", "sweden", "stockholm", "norway", "oslo",
        "denmark", "copenhagen", "finland", "helsinki", "austria", "vienna",
        "belgium", "brussels", "switzerland", "zurich", "zürich",
        "india", "bangalore", "bengaluru", "mumbai", "delhi", "pune",
        "japan", "tokyo", "china", "shanghai", "beijing",
        "singapore", "hong kong", "uae", "dubai", "abu dhabi",
        "israel", "tel aviv", "australia", "sydney", "melbourne",
        "brazil", "são paulo", "mexico", "mexico city",
        "south africa", "johannesburg", "russia", "moscow",
    ]

    US_SIGNALS = [
        "usa", "united states", "u.s.", "us only", "us remote", "us-based",
        "united states of america", "us-remote",
        "canada", "ontario", "quebec", "toronto", "vancouver", "montreal",
        "north america", "worldwide", "anywhere", "global",
    ]

    def __init__(self):
        self._config_cache = None

    def _get_config(self):
        """Load config from DB (cached per instantiation)."""
        if self._config_cache:
            return self._config_cache
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT skill_overlap_min, log_rejected_jds, retention_days, rate_weight
                FROM charvak_bench_relevance_config
                WHERE config_id = %s
            """, ("default",))
            row = cur.fetchone()
            cur.close()
            conn.close()
            if row:
                self._config_cache = {
                    "skill_overlap_min": float(row[0]),
                    "log_rejected_jds": bool(row[1]),
                    "retention_days": int(row[2]),
                    "rate_weight": float(row[3]),
                }
            else:
                self._config_cache = {
                    "skill_overlap_min": 0.30,
                    "log_rejected_jds": True,
                    "retention_days": 30,
                    "rate_weight": 0.10,
                }
        except Exception as e:
            logger.warning(f"config load failed, using defaults: {e}")
            self._config_cache = {
                "skill_overlap_min": 0.30,
                "log_rejected_jds": True,
                "retention_days": 30,
                "rate_weight": 0.10,
            }
        return self._config_cache

    def set_config(self, skill_overlap_min=None, log_rejected_jds=None,
                   retention_days=None, rate_weight=None):
        """Update config in DB. Clears cache."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            updates = []
            params = []
            if skill_overlap_min is not None:
                updates.append("skill_overlap_min = %s")
                params.append(float(skill_overlap_min))
            if log_rejected_jds is not None:
                updates.append("log_rejected_jds = %s")
                params.append(bool(log_rejected_jds))
            if retention_days is not None:
                updates.append("retention_days = %s")
                params.append(int(retention_days))
            if rate_weight is not None:
                updates.append("rate_weight = %s")
                params.append(float(rate_weight))
            if not updates:
                return {"status": "error", "message": "No updates provided"}
            updates.append("updated_at = NOW()")
            set_clause = ", ".join(updates)
            sql = "UPDATE charvak_bench_relevance_config SET " + set_clause + " WHERE config_id = %s"
            params.append("default")
            cur.execute(sql, params)
            conn.commit()
            cur.close()
            conn.close()
            self._config_cache = None
            return {"status": "success"}
        except Exception as e:
            logger.error(f"set_config failed: {e}")
            return {"status": "error", "message": str(e)}

    def _get_bench_candidates(self):
        """Load all bench candidates with skills + visa + rate."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT candidate_id, name, email, skills, work_auth_status,
                       rate_min, rate_max, availability
                FROM charvak_candidates
                WHERE bench_since IS NOT NULL
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()
            candidates = []
            for r in rows:
                skills = r[3] if isinstance(r[3], list) else (json.loads(r[3]) if r[3] else [])
                candidates.append({
                    "candidate_id": r[0],
                    "name": r[1],
                    "email": r[2],
                    "skills": skills,
                    "work_auth_status": r[4] or "",
                    "rate_min": float(r[5]) if r[5] else None,
                    "rate_max": float(r[6]) if r[6] else None,
                    "availability": r[7] or "",
                })
            return candidates
        except Exception as e:
            logger.error(f"_get_bench_candidates failed: {e}")
            return []

    def _normalize_skill(self, s):
        """
        Lowercase + strip + comprehensive synonym map (Session 108E).

        Expanded to handle common tech-skill variations that caused
        false-negative 0% rejections:
        - AI/ML: 'artificial intelligence' -> 'ai', 'machine learning' -> 'ml'
        - JS/TS: 'js' -> 'javascript', 'nodejs' -> 'node', 'reactjs' -> 'react'
        - Cloud: 'amazon web services' -> 'aws', 'google cloud' -> 'gcp'
        - Backend: 'golang' -> 'go', 'c#' -> 'csharp', '.net' -> 'dotnet'
        - Databases: 'postgresql' -> 'postgres', 'mongo' -> 'mongodb'
        - DevOps: 'ci/cd' -> 'cicd', 'continuous integration' -> 'cicd'
        """
        if not s:
            return ""
        s = str(s).lower().strip()
        # Collapse whitespace and strip punctuation
        s = re.sub(r"\s+", " ", s)
        s = s.strip(".,;:()[]{}")

        synonyms = {
            # Container orchestration
            "kubernetes": "k8s",
            "k8s": "k8s",
            "kube": "k8s",

            # ML / AI family
            "machine learning": "ml",
            "ml": "ml",
            "artificial intelligence": "ai",
            "ai": "ai",
            "artificial intelligence / machine learning": "ml",
            "ai/ml": "ml",
            "ml/ai": "ml",
            "deep learning": "ml",
            "generative ai": "ai",
            "genai": "ai",
            "gen ai": "ai",
            "llm": "llm",
            "large language model": "llm",
            "large language models": "llm",
            "nlp": "nlp",
            "natural language processing": "nlp",
            "computer vision": "cv",

            # Data science
            "data science": "data-science",
            "data scientist": "data-science",
            "data engineering": "data-engineering",
            "data engineer": "data-engineering",

            # Databases
            "postgresql": "postgres",
            "postgres": "postgres",
            "postgres sql": "postgres",
            "mongo": "mongodb",
            "mongodb": "mongodb",
            "ms sql server": "sqlserver",
            "microsoft sql server": "sqlserver",
            "sql server": "sqlserver",
            "sqlserver": "sqlserver",

            # JavaScript / TypeScript
            "javascript": "javascript",
            "js": "javascript",
            "ecmascript": "javascript",
            "typescript": "typescript",
            "ts": "typescript",
            "nodejs": "node",
            "node.js": "node",
            "node js": "node",
            "node": "node",

            # Frontend
            "reactjs": "react",
            "react.js": "react",
            "react js": "react",
            "react": "react",
            "vuejs": "vue",
            "vue.js": "vue",
            "vue": "vue",
            "angularjs": "angular",
            "angular.js": "angular",
            "angular": "angular",
            "nextjs": "next",
            "next.js": "next",
            "next": "next",

            # Backend
            "golang": "go",
            "go": "go",
            "go lang": "go",
            "python3": "python",
            "python 3": "python",
            "python": "python",
            "java": "java",
            "java 8": "java",
            "java 11": "java",
            "java 17": "java",
            ".net": "dotnet",
            "dotnet": "dotnet",
            "asp.net": "aspnet",
            "aspnet": "aspnet",
            "c#": "csharp",
            "csharp": "csharp",
            "c sharp": "csharp",

            # Cloud
            "amazon web services": "aws",
            "aws": "aws",
            "google cloud platform": "gcp",
            "google cloud": "gcp",
            "gcp": "gcp",
            "microsoft azure": "azure",
            "azure": "azure",

            # DevOps / CI-CD
            "docker": "docker",
            "terraform": "terraform",
            "ansible": "ansible",
            "jenkins": "jenkins",
            "ci/cd": "cicd",
            "cicd": "cicd",
            "ci cd": "cicd",
            "continuous integration": "cicd",
            "continuous delivery": "cicd",
            "continuous deployment": "cicd",
            "devops": "devops",

            # Other
            "graphql": "graphql",
            "rest": "rest",
            "rest api": "rest",
            "restful": "rest",
            "microservices": "microservices",
            "micro services": "microservices",
            "agile": "agile",
            "scrum": "agile",
            "kanban": "agile",

            # ML/AI libraries (map to ml/ai so ML jobs match)
            "tensorflow": "ml",
            "pytorch": "ml",
            "hugging face": "ml",
            "huggingface": "ml",
            "scikit-learn": "ml",
            "sklearn": "ml",
            "keras": "ml",
            "scipy": "ml",
            "pandas": "data-science",
            "numpy": "data-science",
            "jupyter": "data-science",
            "llm engineering": "llm",
            "prompt engineering": "llm",
            "rag": "llm",
            "fine-tuning": "ml",
            "fine tuning": "ml",

            # Generic dev tools often on resumes
            "git": "git",
            "github": "git",
            "gitlab": "git",
        }

        return synonyms.get(s, s)
    def _is_us_or_remote(self, location, raw_text=None):
        """
        Return True if location is US, Canada, or remote/worldwide.

        Checks both the parsed location AND the raw text (belt-and-suspenders).
        If parsed location is empty/ambiguous but raw text mentions a non-US
        city/country, reject.
        """
        loc = (location or "").lower().strip()
        text = (raw_text or "").lower()

        # Combined search across location + raw text
        combined = loc + " " + text

        # US/global signal wins (explicit US mention)
        if any(sig in loc for sig in self.US_SIGNALS):
            return True

        # Non-US signal in PARSED location -> reject
        if any(kw in loc for kw in self.NON_US):
            return False

        # If location is empty or generic ("Remote", ""), check raw text
        # but be careful: many US jobs mention "Berlin office" in boilerplate
        # Only reject if non-US signal appears in the SUBJECT-like portion of text
        # (first 500 chars) AND no US signal exists in text
        if not loc or loc in ("remote", "anywhere", ""):
            text_head = text[:500]
            has_us_in_text = any(sig in text for sig in self.US_SIGNALS)
            has_non_us_in_text = any(kw in text_head for kw in self.NON_US)
            if has_non_us_in_text and not has_us_in_text:
                return False

        return True

    def _extract_jd_visa(self, jd):
        """Extract visa requirement from JD work_auth field or description."""
        work_auth = (jd.get("work_auth_required") or "").strip()
        if work_auth and work_auth.lower() not in ("any", "not specified", ""):
            return work_auth
        text = ((jd.get("raw_text") or "") + " " + (jd.get("description") or "")).lower()
        if "no sponsorship" in text or "no h1b" in text or "us citizen only" in text:
            return "USC"
        if "h1b" in text or "h-1b" in text or "sponsorship available" in text:
            return "H1B"
        if "opt" in text:
            return "OPT"
        if "h4-ead" in text or "h4 ead" in text or "ead" in text:
            return "H4-EAD"
        return "Any"

    def _is_visa_compatible(self, jd_visa, candidate_visa):
        """
        Check if candidate can apply to this JD.

        Logic:
        - If JD says "Any" or unspecified -> any candidate can apply
        - Otherwise JD visa must be in candidate's allowed list
        """
        jd_visa = (jd_visa or "Any").strip()
        candidate_visa = (candidate_visa or "").strip()
        if not candidate_visa:
            return True  # candidate visa unknown -> allow (benefit of doubt)
        # If JD is open to any visa -> allow
        if jd_visa.lower() in ("any", "not specified", ""):
            return True
        # Otherwise check exact match against candidate's allowed list
        allowed = self.VISA_COMPAT.get(candidate_visa, ["Any", "Not specified", ""])
        return jd_visa in allowed

    def _skill_overlap_pct(self, jd_skills, candidate_skills):
        """Percentage of JD skills candidate has."""
        if not jd_skills:
            return 1.0
        jd_norm = set(self._normalize_skill(s) for s in jd_skills if s)
        cand_norm = set(self._normalize_skill(s) for s in candidate_skills if s)
        if not jd_norm:
            return 1.0
        matched = jd_norm & cand_norm
        return len(matched) / len(jd_norm)

    def is_relevant(self, jd):
        """
        Returns (is_relevant: bool, reason: str, best_candidate_name: str | None,
                 best_candidate_email: str | None, best_overlap: float).
        """
        candidates = self._get_bench_candidates()
        if not candidates:
            return (True, "no_bench_candidates", None, None, 0.0)

        config = self._get_config()
        min_overlap = config["skill_overlap_min"]

        # Gate 1: Location (checks both parsed location AND raw text)
        location = jd.get("location") or jd.get("jd_location") or ""
        raw_text = jd.get("raw_text") or jd.get("description") or ""
        if not self._is_us_or_remote(location, raw_text):
            self._log_rejection(jd, "non_us_location", None, 0.0)
            return (False, "non_us_location", None, None, 0.0)

        # Gate 2: Visa
        jd_visa = self._extract_jd_visa(jd)
        compatible_candidates = [
            c for c in candidates
            if self._is_visa_compatible(jd_visa, c["work_auth_status"])
        ]
        if not compatible_candidates:
            self._log_rejection(jd, "visa_incompatible", None, 0.0)
            return (False, "visa_incompatible", None, None, 0.0)

        # Gate 3: Skill overlap (Session 108E: concentration bonus + title fallback)
        jd_skills = jd.get("skills_required") or jd.get("skills") or []
        if isinstance(jd_skills, str):
            jd_skills = [s.strip() for s in jd_skills.split(",") if s.strip()]

        # Normalize JD skills once for concentration calculation
        jd_norm = [self._normalize_skill(s) for s in jd_skills if s]
        jd_norm_set = set(jd_norm)

        # Extract role title for title-fallback check
        jd_title = (jd.get("role_title") or jd.get("title") or "").lower().strip()

        best_overlap = 0.0
        best_cand = None
        best_concentration = 0.0
        best_title_match = False

        for c in compatible_candidates:
            # 1. Base overlap
            overlap = self._skill_overlap_pct(jd_skills, c["skills"])

            # 2. Concentration bonus: if top-3 JD skills are all in candidate skills,
            #    that's a real signal even if overall % is low (e.g. Python+SQL in a
            #    10-skill JD = 20% but those are the core skills)
            cand_norm_set = set(self._normalize_skill(s) for s in (c.get("skills") or []) if s)
            top_3 = list(jd_norm_set)[:3]
            if top_3:
                top_3_hits = sum(1 for s in top_3 if s in cand_norm_set)
                concentration = top_3_hits / len(top_3)
            else:
                concentration = 0.0

            # 3. Title fallback: does the JD title contain any of the candidate's skills?
            title_match = False
            if jd_title:
                for cs in cand_norm_set:
                    # Only count non-generic skills (length >= 3)
                    if len(cs) >= 3 and cs in jd_title:
                        title_match = True
                        break
                # Also check if the candidate's job_title is in JD title
                cand_role = (c.get("job_title") or "").lower().strip()
                if cand_role and len(cand_role) >= 4 and cand_role in jd_title:
                    title_match = True

            # Track best candidate by overlap (first pass)
            if overlap > best_overlap:
                best_overlap = overlap
                best_cand = c
                best_concentration = concentration
                best_title_match = title_match

        # Augment best_overlap with bonuses for the winning candidate
        if best_cand:
            # Concentration bonus: if >=2/3 of top JD skills match, +15%
            if best_concentration >= 0.66 and best_overlap < min_overlap:
                boosted = min(best_overlap + 0.15, 1.0)
                if boosted >= min_overlap:
                    best_overlap = boosted

            # Title fallback: if title literally contains a candidate skill
            # AND they have at least 1 skill match, allow (this catches "ML Engineer"
            # where candidate has PyTorch/TensorFlow but no literal 'ai' skill)
            if best_title_match and best_overlap >= 0.10 and best_overlap < min_overlap:
                boosted = min(best_overlap + 0.20, 1.0)
                if boosted >= min_overlap:
                    best_overlap = boosted

        if best_overlap < min_overlap:
            reason = f"low_skill_overlap_{best_overlap:.0%}"
            self._log_rejection(jd, reason, best_cand["name"] if best_cand else None, best_overlap)
            return (False, reason, best_cand["name"] if best_cand else None,
                    best_cand["email"] if best_cand else None, best_overlap)

        # Tag the reason so we know which path allowed it
        if best_title_match and best_concentration >= 0.66:
            reason = f"relevant_title+conc_{best_overlap:.0%}"
        elif best_concentration >= 0.66:
            reason = f"relevant_conc_{best_overlap:.0%}"
        elif best_title_match:
            reason = f"relevant_title_{best_overlap:.0%}"
        else:
            reason = f"relevant_{best_overlap:.0%}"

        return (True, reason,
                best_cand["name"] if best_cand else None,
                best_cand["email"] if best_cand else None, best_overlap)

    def _log_rejection(self, jd, reason, best_candidate_hint, overlap_pct):
        """Log rejected JD to charvak_rejected_jds for audit."""
        config = self._get_config()
        if not config.get("log_rejected_jds", True):
            return
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            skills = jd.get("skills_required") or jd.get("skills") or []
            if isinstance(skills, list):
                skills_str = ", ".join(str(s) for s in skills[:15])
            else:
                skills_str = str(skills)[:500]
            cur.execute("""
                INSERT INTO charvak_rejected_jds
                (rejected_id, source, raw_email_subject, raw_email_from,
                 role_title, company, location, skills_required,
                 work_auth_required, rate_min, rate_max, raw_json,
                 reject_reason, best_candidate_hint, skills_overlap_pct)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                f"REJ-{uuid.uuid4().hex[:12].upper()}",
                jd.get("source") or "unknown",
                jd.get("raw_email_subject"),
                jd.get("raw_email_from"),
                jd.get("role_title") or jd.get("title"),
                jd.get("company"),
                jd.get("location") or jd.get("jd_location"),
                skills_str,
                jd.get("work_auth_required"),
                jd.get("rate_min"),
                jd.get("rate_max"),
                json.dumps(jd.get("raw_json") or {}),
                reason,
                best_candidate_hint,
                float(overlap_pct) if overlap_pct else 0.0,
            ))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.warning(f"_log_rejection failed: {e}")

    def get_rejection_stats(self, days=7):
        """Stats on rejected JDs in last N days."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT reject_reason, COUNT(*)
                FROM charvak_rejected_jds
                WHERE rejected_at > NOW() - INTERVAL '%s days'
                GROUP BY reject_reason
                ORDER BY COUNT(*) DESC
            """, (days,))
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return {"status": "success", "stats": [{"reason": r[0], "count": r[1]} for r in rows]}
        except Exception as e:
            return {"status": "error", "message": str(e)}


# Singleton
bench_jd_filter = BenchJDFilter()