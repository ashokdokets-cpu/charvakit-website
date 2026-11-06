"""
Bench Matching Engine
Session 3 - Bench-Placement Agent

Scores every vendor JD against every bench candidate.
Score = 60% skill overlap + 20% auth + 10% rate + 10% availability.
"""

import os
import json
import logging
import uuid
from typing import Dict, List
import psycopg2
from dotenv import load_dotenv

load_dotenv(".env.local", override=True)
load_dotenv()

logger = logging.getLogger(__name__)


class BenchMatchingEngine:
    # Synonym groups - a JD skill matches any synonym on the candidate
    SKILL_SYNONYMS = {
        "ci/cd pipelines": [
            "github actions", "azure devops pipelines", "jenkins",
            "gitlab ci/cd", "bamboo", "circleci", "teamcity",
            "argo cd", "flux cd", "harness cd", "spinnaker",
            "ci/cd", "cicd", "continuous integration", "continuous deployment",
        ],
        "ci/cd": [
            "github actions", "azure devops pipelines", "jenkins",
            "gitlab ci/cd", "bamboo", "circleci", "teamcity",
            "argo cd", "flux cd", "harness cd", "spinnaker",
            "ci/cd pipelines", "cicd", "continuous integration",
        ],
        "aws": ["amazon web services", "aws"],
        "gcp": ["google cloud platform", "gcp"],
        "k8s": ["kubernetes"],
        "kubernetes": ["k8s"],
        "js": ["javascript"],
        "postgres": ["postgresql"],
        "rest api": ["rest", "restful", "http api"],
        "microservices": ["microservice", "micro services"],
        "docker": ["containers", "containerization"],
        "terraform": ["iac", "infrastructure as code"],
    }

    def __init__(self):
        self._ensure_table()

    def _ensure_table(self):
        """Self-healing DDL."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_bench_matches (
                    match_id TEXT PRIMARY KEY,
                    jd_id TEXT NOT NULL,
                    candidate_email TEXT NOT NULL,
                    candidate_id TEXT,
                    candidate_name TEXT,
                    match_score INTEGER NOT NULL,
                    skill_score INTEGER DEFAULT 0,
                    auth_score INTEGER DEFAULT 0,
                    rate_score INTEGER DEFAULT 0,
                    availability_score INTEGER DEFAULT 0,
                    matched_skills JSONB DEFAULT '[]'::jsonb,
                    missing_skills JSONB DEFAULT '[]'::jsonb,
                    computed_at TIMESTAMP DEFAULT NOW(),
                    status TEXT DEFAULT 'pending',
                    submitted_at TIMESTAMP,
                    vendor_response TEXT,
                    interviewed_at TIMESTAMP,
                    placed_at TIMESTAMP,
                    notes TEXT,
                    UNIQUE(jd_id, candidate_email)
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"_ensure_table failed: {e}")

    def _normalize_skill(self, s: str) -> str:
        """Lowercase + strip common suffixes for fuzzy matching."""
        if not s:
            return ""
        s = str(s).lower().strip()
        for suffix in [".js", ".net", " framework", " library", " (programming)"]:
            s = s.replace(suffix, "")
        return s

    def _skill_matches(self, jd_skill_norm: str, cand_norm_key: str) -> bool:
        """Check if a JD skill matches a candidate skill (substring + synonyms)."""
        if jd_skill_norm in cand_norm_key or cand_norm_key in jd_skill_norm:
            return True
        synonyms = self.SKILL_SYNONYMS.get(jd_skill_norm, [])
        for syn in synonyms:
            if syn in cand_norm_key or cand_norm_key in syn:
                return True
        for group, group_syns in self.SKILL_SYNONYMS.items():
            if group == jd_skill_norm:
                continue
            for syn in group_syns:
                if syn == jd_skill_norm:
                    if group in cand_norm_key or cand_norm_key in group:
                        return True
                    for other_syn in group_syns:
                        if other_syn in cand_norm_key or cand_norm_key in other_syn:
                            return True
        return False

    def _score_skills(self, jd_skills: List[str], candidate_skills: List[str]) -> Dict:
        """Score skill overlap. Returns {score: 0-60, matched: [], missing: []}."""
        if not jd_skills:
            return {"score": 30, "matched": [], "missing": []}

        jd_norm = {self._normalize_skill(s): s for s in jd_skills}
        cand_norm = {self._normalize_skill(s): s for s in (candidate_skills or [])}

        matched = []
        missing = []
        for jd_skill_norm, jd_skill_orig in jd_norm.items():
            found = False
            for cand_norm_key in cand_norm.keys():
                if self._skill_matches(jd_skill_norm, cand_norm_key):
                    matched.append(jd_skill_orig)
                    found = True
                    break
            if not found:
                missing.append(jd_skill_orig)

        overlap_pct = len(matched) / len(jd_skills) if jd_skills else 0
        return {
            "score": round(overlap_pct * 60),
            "matched": matched,
            "missing": missing,
        }

    def _score_auth(self, jd_auth: str, candidate_auth: str) -> int:
        """Score work auth fit. 0-20."""
        if not jd_auth or jd_auth == "Any":
            return 20

        jd_auth = str(jd_auth).upper()
        cand_auth = str(candidate_auth or "").upper()

        if jd_auth == cand_auth:
            return 20

        if "USC/GC ONLY" in jd_auth or "NO SPONSORSHIP" in jd_auth or "NO H1B" in jd_auth:
            if cand_auth in ("USC", "GC"):
                return 20
            return 0

        if cand_auth in jd_auth or jd_auth in cand_auth:
            return 20

        if cand_auth in ("H1B", "OPT", "H4-EAD", "L2-EAD") and "H1B" in jd_auth:
            return 15
        if cand_auth in ("H1B", "OPT", "H4-EAD", "L2-EAD") and "ANY" in jd_auth:
            return 20

        return 0

    def _score_rate(self, jd_min: float, jd_max: float,
                    cand_min: float, cand_max: float) -> int:
        """Score rate fit. 0-10."""
        if jd_min is None and jd_max is None:
            return 10
        if cand_min is None and cand_max is None:
            return 5

        jd_lo = jd_min or 0
        jd_hi = jd_max or (jd_min or 999)
        cand_lo = cand_min or 0
        cand_hi = cand_max or 999

        if cand_lo > jd_hi:
            return 0
        if cand_hi < jd_lo:
            return 3

        overlap = min(cand_hi, jd_hi) - max(cand_lo, jd_lo)
        jd_range = jd_hi - jd_lo
        if jd_range > 0:
            return round(5 + (overlap / jd_range) * 5)
        return 10

    def _score_availability(self, cand_avail: str) -> int:
        """Score availability. 0-10."""
        if not cand_avail:
            return 5
        cand_avail = str(cand_avail).lower()
        if "immediate" in cand_avail or "now" in cand_avail:
            return 10
        if "week" in cand_avail:
            return 8
        if "month" in cand_avail:
            return 5
        if "project" in cand_avail:
            return 2
        return 5

    def score_match(self, jd: Dict, candidate: Dict) -> Dict:
        """Compute full match score."""
        jd_skills = jd.get("skills_required") or []
        cand_skills = candidate.get("skills") or []

        skill = self._score_skills(jd_skills, cand_skills)
        auth = self._score_auth(jd.get("work_auth_required"), candidate.get("work_auth_status"))
        rate = self._score_rate(
            jd.get("rate_min"), jd.get("rate_max"),
            candidate.get("rate_min"), candidate.get("rate_max")
        )
        avail = self._score_availability(candidate.get("availability"))

        total = skill["score"] + auth + rate + avail

        return {
            "match_score": total,
            "skill_score": skill["score"],
            "auth_score": auth,
            "rate_score": rate,
            "availability_score": avail,
            "matched_skills": skill["matched"],
            "missing_skills": skill["missing"],
        }

    def run_matching_for_jd(self, jd_id: str) -> Dict:
        """Score all bench candidates for one JD."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()

            cur.execute("""
                SELECT jd_id, role_title, skills_required, rate_min, rate_max,
                       work_auth_required, location
                FROM charvak_vendor_jds
                WHERE jd_id = %s AND status = 'active'
            """, (jd_id,))
            jd_row = cur.fetchone()
            if not jd_row:
                cur.close()
                conn.close()
                return {"status": "error", "message": "JD not found or archived"}

            jd = {
                "jd_id": jd_row[0],
                "role_title": jd_row[1],
                "skills_required": jd_row[2] if isinstance(jd_row[2], list) else (json.loads(jd_row[2]) if jd_row[2] else []),
                "rate_min": float(jd_row[3]) if jd_row[3] else None,
                "rate_max": float(jd_row[4]) if jd_row[4] else None,
                "work_auth_required": jd_row[5],
                "location": jd_row[6],
            }

            cur.execute("""
                SELECT candidate_id, name, email, skills, work_auth_status,
                       availability, rate_min, rate_max
                FROM charvak_candidates
                WHERE bench_since IS NOT NULL
            """)
            cand_rows = cur.fetchall()

            matches_created = 0
            for cand_row in cand_rows:
                candidate = {
                    "candidate_id": cand_row[0],
                    "name": cand_row[1],
                    "email": cand_row[2],
                    "skills": cand_row[3] if isinstance(cand_row[3], list) else (json.loads(cand_row[3]) if cand_row[3] else []),
                    "work_auth_status": cand_row[4],
                    "availability": cand_row[5],
                    "rate_min": float(cand_row[6]) if cand_row[6] else None,
                    "rate_max": float(cand_row[7]) if cand_row[7] else None,
                }

                scores = self.score_match(jd, candidate)
                match_id = f"MATCH-{uuid.uuid4().hex[:12].upper()}"

                cur.execute("""
                    INSERT INTO charvak_bench_matches (
                        match_id, jd_id, candidate_email, candidate_id, candidate_name,
                        match_score, skill_score, auth_score, rate_score, availability_score,
                        matched_skills, missing_skills
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (jd_id, candidate_email) DO UPDATE SET
                        match_score = EXCLUDED.match_score,
                        skill_score = EXCLUDED.skill_score,
                        auth_score = EXCLUDED.auth_score,
                        rate_score = EXCLUDED.rate_score,
                        availability_score = EXCLUDED.availability_score,
                        matched_skills = EXCLUDED.matched_skills,
                        missing_skills = EXCLUDED.missing_skills,
                        computed_at = NOW()
                """, (
                    match_id, jd_id, candidate["email"], candidate["candidate_id"], candidate["name"],
                    scores["match_score"], scores["skill_score"], scores["auth_score"],
                    scores["rate_score"], scores["availability_score"],
                    json.dumps(scores["matched_skills"]),
                    json.dumps(scores["missing_skills"])
                ))
                matches_created += 1

            conn.commit()
            cur.close()
            conn.close()
            return {"status": "success", "jd_id": jd_id, "matches_computed": matches_created}

        except Exception as e:
            logger.error(f"run_matching_for_jd failed: {e}")
            return {"status": "error", "message": str(e)}

    def run_matching_for_all_jds(self) -> Dict:
        """Score all bench candidates for all active JDs."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            cur.execute("SELECT jd_id FROM charvak_vendor_jds WHERE status = 'active'")
            jd_ids = [r[0] for r in cur.fetchall()]
            cur.close()
            conn.close()

            results = []
            total_matches = 0
            for jd_id in jd_ids:
                r = self.run_matching_for_jd(jd_id)
                results.append(r)
                if r.get("status") == "success":
                    total_matches += r.get("matches_computed", 0)

            return {
                "status": "success",
                "jds_processed": len(jd_ids),
                "total_matches_computed": total_matches,
                "details": results
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_top_matches(self, limit: int = 20, min_score: int = 60,
                        work_auth: str = None, jd_id: str = None) -> Dict:
        """Return top matches sorted by score."""
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()

            where = ["m.match_score >= %s"]
            params = [min_score]

            if work_auth and work_auth != "Any":
                where.append("c.work_auth_status = %s")
                params.append(work_auth)

            if jd_id:
                where.append("m.jd_id = %s")
                params.append(jd_id)

            where_clause = " AND ".join(where)

            cur.execute(f"""
                SELECT m.match_id, m.jd_id, m.candidate_email, m.candidate_id,
                       m.candidate_name, m.match_score, m.skill_score, m.auth_score,
                       m.rate_score, m.availability_score, m.matched_skills,
                       m.missing_skills, m.computed_at, m.status, m.notes,
                       j.role_title, j.vendor_name, j.vendor_contact, j.rate_min,
                       j.rate_max, j.work_auth_required, j.client_name, j.location,
                       c.work_auth_status, c.availability
                FROM charvak_bench_matches m
                LEFT JOIN charvak_vendor_jds j ON m.jd_id = j.jd_id
                LEFT JOIN charvak_candidates c ON m.candidate_email = c.email
                WHERE {where_clause}
                ORDER BY m.match_score DESC
                LIMIT %s
            """, params + [limit])

            rows = cur.fetchall()
            cur.close()
            conn.close()

            matches = []
            for r in rows:
                matches.append({
                    "match_id": r[0],
                    "jd_id": r[1],
                    "candidate_email": r[2],
                    "candidate_id": r[3],
                    "candidate_name": r[4],
                    "match_score": r[5],
                    "skill_score": r[6],
                    "auth_score": r[7],
                    "rate_score": r[8],
                    "availability_score": r[9],
                    "matched_skills": r[10] if isinstance(r[10], list) else (json.loads(r[10]) if r[10] else []),
                    "missing_skills": r[11] if isinstance(r[11], list) else (json.loads(r[11]) if r[11] else []),
                    "computed_at": r[12].isoformat() if r[12] else None,
                    "status": r[13],
                    "notes": r[14],
                    "role_title": r[15],
                    "vendor_name": r[16],
                    "vendor_contact": r[17],
                    "jd_rate_min": float(r[18]) if r[18] else None,
                    "jd_rate_max": float(r[19]) if r[19] else None,
                    "jd_work_auth": r[20],
                    "client_name": r[21],
                    "jd_location": r[22],
                    "candidate_work_auth": r[23],
                    "candidate_availability": r[24],
                })

            return {"status": "success", "matches": matches, "total": len(matches)}
        except Exception as e:
            return {"status": "error", "message": str(e)}


bench_matching_engine = BenchMatchingEngine()