"""
Charvak North America - Semantic Vector Matching Engine
AI-powered matching beyond basic keyword search
(DB-backed - Session G/1)
"""
import json
import logging
import re
import secrets
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger("charvakit.na.vector_matcher")


class VectorMatcher:
    """Semantic vector matching for candidate-job pairing (history DB-backed)"""

    # Skill embeddings (simplified - in production, use pgvector/Pinecone)
    SKILL_EMBEDDINGS = {
        # Java ecosystem
        "java": ["spring boot", "microservices", "kafka", "hibernate", "jpa", "rest api", "j2ee", "maven", "gradle", "jenkins"],
        "spring boot": ["java", "microservices", "rest api", "kafka", "jpa", "spring cloud", "docker"],

        # Frontend
        "react": ["javascript", "typescript", "redux", "next.js", "graphql", "html", "css", "node.js", "webpack"],
        "angular": ["typescript", "javascript", "rxjs", "ngrx", "html", "css"],

        # Cloud/DevOps
        "aws": ["lambda", "ec2", "s3", "dynamodb", "cloudformation", "terraform", "docker", "kubernetes"],
        "kubernetes": ["docker", "helm", "aws", "azure", "gcp", "terraform", "ci/cd", "jenkins", "argocd"],
        "terraform": ["aws", "azure", "gcp", "infrastructure as code", "iac", "docker", "kubernetes"],

        # Data
        "python": ["django", "flask", "fastapi", "pandas", "numpy", "tensorflow", "pytorch", "data science", "ml"],
        "machine learning": ["python", "tensorflow", "pytorch", "scikit-learn", "deep learning", "nlp", "data science"],
        "data science": ["python", "r", "sql", "pandas", "numpy", "tableau", "power bi", "machine learning"],
    }

    def __init__(self):
        self._ensure_tables()
        logger.info("Vector Matching Engine ready (DB-backed) | %d skill categories", len(self.SKILL_EMBEDDINGS))

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_match_history (
                    match_id         TEXT PRIMARY KEY,
                    candidate_id     TEXT,
                    matches_count    INTEGER DEFAULT 0,
                    top_score        INTEGER DEFAULT 0,
                    matched_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_match_candidate ON charvak_na_match_history(candidate_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_match_time      ON charvak_na_match_history(matched_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"na_match_history tables init failed: {e}")

    # ============================================================
    # PURE / STATIC
    # ============================================================

    def expand_skills(self, skills: List[str]) -> List[str]:
        """Expand skills with related technologies"""
        expanded = set()
        for skill in skills:
            skill_lower = skill.lower().strip()
            expanded.add(skill_lower)
            if skill_lower in self.SKILL_EMBEDDINGS:
                for related in self.SKILL_EMBEDDINGS[skill_lower]:
                    expanded.add(related)
        return list(expanded)

    def calculate_match_score(self, candidate_skills: List[str],
                               job_skills: List[str],
                               candidate_rate: float = 0,
                               job_rate_min: float = 0,
                               job_rate_max: float = 0) -> Dict:
        """Calculate comprehensive match score"""
        expanded_candidate = self.expand_skills(candidate_skills)
        expanded_job = self.expand_skills(job_skills)

        direct_matches = set(s.lower() for s in candidate_skills) & set(s.lower() for s in job_skills)
        direct_score = len(direct_matches) / max(len(job_skills), 1) * 50

        semantic_matches = set(expanded_candidate) & set(expanded_job)
        semantic_score = len(semantic_matches) / max(len(expanded_job), 1) * 30

        rate_score = 0
        if candidate_rate > 0 and job_rate_min > 0:
            if job_rate_min <= candidate_rate <= job_rate_max:
                rate_score = 20
            elif candidate_rate < job_rate_min:
                rate_score = 15
            elif candidate_rate <= job_rate_max * 1.1:
                rate_score = 10
            else:
                rate_score = 0

        total_score = min(round(direct_score + semantic_score + rate_score), 100)

        return {
            "total_score": total_score,
            "direct_match_pct": round(len(direct_matches) / max(len(job_skills), 1) * 100),
            "semantic_match_pct": round(len(semantic_matches) / max(len(expanded_job), 1) * 100),
            "rate_compatible": rate_score > 0,
            "direct_matches": list(direct_matches),
            "semantic_matches": list(set(expanded_candidate) & set(expanded_job) - direct_matches),
            "missing_skills": list(set(s.lower() for s in job_skills) - set(s.lower() for s in candidate_skills)),
            "match_level": self._get_match_level(total_score),
        }

    def _get_match_level(self, score: int) -> str:
        if score >= 85: return "Excellent Match - Submit Immediately"
        if score >= 70: return "Strong Match - Recommend Submission"
        if score >= 55: return "Good Match - Consider Submitting"
        if score >= 40: return "Partial Match - Upskill Recommended"
        return "Weak Match - Not Recommended"

    # ============================================================
    # MATCHING (writes to history)
    # ============================================================

    def match_candidate_to_jobs(self, candidate: Dict, jobs: List[Dict]) -> List[Dict]:
        """Match a candidate against all available jobs"""
        matches = []
        for job in jobs:
            score = self.calculate_match_score(
                candidate_skills=candidate.get("skills", []),
                job_skills=job.get("skills_required", []),
                candidate_rate=candidate.get("rate", 0),
                job_rate_min=job.get("rate_range", {}).get("min", 0),
                job_rate_max=job.get("rate_range", {}).get("max", 0),
            )
            if score["total_score"] >= 40:
                matches.append({
                    "job_id": job["job_id"],
                    "job_title": job["title"],
                    "client": job["client"],
                    "location": job["location"],
                    "match_score": score,
                    "rate_range": job.get("rate_range"),
                })

        matches.sort(key=lambda x: x["match_score"]["total_score"], reverse=True)

        top_score = matches[0]["match_score"]["total_score"] if matches else 0
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            match_id = f"MATCH-{secrets.token_hex(4).upper()}"
            cur.execute('''
                INSERT INTO charvak_na_match_history
                    (match_id, candidate_id, matches_count, top_score)
                VALUES (%s, %s, %s, %s)
            ''', (match_id, candidate.get("id"), len(matches), top_score))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"match_candidate_to_jobs write failed: {e}")

        return matches

    def get_match_analytics(self) -> Dict:
        """Get matching analytics"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*), COALESCE(AVG(top_score), 0) FROM charvak_na_match_history')
            total, avg_score = cur.fetchone()
            total = int(total or 0)
            avg_score = float(avg_score or 0)

            if total == 0:
                cur.close(); conn.close()
                return {"total_matches": 0, "avg_score": 0, "top_skills": []}

            cur.execute('''
                SELECT candidate_id, matches_count, top_score, matched_at
                FROM charvak_na_match_history
                ORDER BY matched_at DESC
                LIMIT 5
            ''')
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_match_analytics failed: {e}")
            return {"total_matches": 0, "avg_score": 0, "top_skills": []}

        recent = [{
            "candidate_id": r[0],
            "matches": r[1],
            "top_score": r[2],
            "timestamp": r[3].isoformat() if hasattr(r[3], "isoformat") else str(r[3]),
        } for r in rows]

        return {
            "total_matches": total,
            "average_top_score": round(avg_score, 1),
            "recent_matches": recent,
        }


vector_matcher = VectorMatcher()