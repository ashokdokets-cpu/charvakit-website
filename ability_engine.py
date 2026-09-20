"""
Charvak Ability Engine (Session G2, C4)
Per-user, per-skill ability tracking using Elo-style scoring.
Start value: 1000. Bands: <900 Beginner, 900-1100 Intermediate, >=1100 Advanced.
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger("charvakit.ability")

DIFFICULTY_VALUE = {
    "beginner": 800,
    "easy": 800,
    "medium": 1000,
    "intermediate": 1000,
    "moderate": 1000,
    "hard": 1200,
    "advanced": 1200,
}

START_ABILITY = 1000.0
K_FACTOR = 24.0
BAND_LOW = 900.0
BAND_HIGH = 1100.0


class AbilityEngine:
    def __init__(self):
        self._ensure_tables()
        logger.info("Ability Engine ready (DB-backed)")

    def _ensure_tables(self):
        """Idempotent table creation, mirrors results_system pattern."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_user_ability (
                    email           TEXT NOT NULL,
                    skill           TEXT NOT NULL,
                    ability_score   NUMERIC(7,2) NOT NULL DEFAULT 1000.0,
                    attempts        INTEGER NOT NULL DEFAULT 0,
                    correct_total   INTEGER NOT NULL DEFAULT 0,
                    question_total  INTEGER NOT NULL DEFAULT 0,
                    last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (email, skill)
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_user_ability_email ON charvak_user_ability(email)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_user_ability_skill ON charvak_user_ability(skill)")
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"ability tables init failed: {e}")

    @staticmethod
    def expected_score(ability: float, difficulty_value: float) -> float:
        """Standard Elo expected outcome."""
        return 1.0 / (1.0 + 10.0 ** ((difficulty_value - ability) / 400.0))

    @staticmethod
    def recommend_difficulty(ability: float) -> str:
        if ability < BAND_LOW:
            return "beginner"
        if ability >= BAND_HIGH:
            return "advanced"
        return "intermediate"

    def get_ability(self, email: str, skill: str) -> Dict:
        """Return current ability row, or a neutral default if not found."""
        if not email or not skill:
            return {"email": email, "skill": skill, "ability_score": START_ABILITY,
                    "attempts": 0, "exists": False}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT ability_score, attempts, correct_total, question_total
                FROM charvak_user_ability WHERE email = %s AND skill = %s
            """, (email, skill))
            row = cur.fetchone()
            cur.close(); conn.close()
            if row:
                return {"email": email, "skill": skill,
                        "ability_score": float(row[0]), "attempts": int(row[1]),
                        "correct_total": int(row[2]), "question_total": int(row[3]),
                        "exists": True}
            return {"email": email, "skill": skill, "ability_score": START_ABILITY,
                    "attempts": 0, "correct_total": 0, "question_total": 0, "exists": False}
        except Exception as e:
            logger.error(f"get_ability failed: {e}")
            return {"email": email, "skill": skill, "ability_score": START_ABILITY,
                    "attempts": 0, "exists": False}

    def get_recommended_difficulty(self, email: str, skill: str) -> str:
        return self.recommend_difficulty(self.get_ability(email, skill)["ability_score"])

    def update_from_assessment(self, email: str, skill: str,
                                correct: int, total: int,
                                difficulty: Optional[str] = None) -> Dict:
        """Update ability after an assessment. Each question = one Elo game."""
        if not email or not skill or total <= 0:
            return {"status": "skipped", "reason": "missing email/skill or zero questions"}
        try:
            current = self.get_ability(email, skill)
            ability = current["ability_score"]
            diff_value = DIFFICULTY_VALUE.get((difficulty or "medium").lower(), 1000)

            expected = self.expected_score(ability, diff_value)
            actual = correct / total
            delta = K_FACTOR * (actual - expected)
            new_ability = max(100.0, min(3000.0, ability + delta))

            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_user_ability
                    (email, skill, ability_score, attempts, correct_total, question_total, last_updated)
                VALUES (%s, %s, %s, 1, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (email, skill) DO UPDATE SET
                    ability_score = %s,
                    attempts = charvak_user_ability.attempts + 1,
                    correct_total = charvak_user_ability.correct_total + %s,
                    question_total = charvak_user_ability.question_total + %s,
                    last_updated = CURRENT_TIMESTAMP
            """, (email, skill, round(new_ability, 2), correct, total,
                  round(new_ability, 2), correct, total))
            conn.commit()
            cur.close(); conn.close()

            return {
                "status": "success",
                "email": email,
                "skill": skill,
                "old_ability": round(ability, 2),
                "new_ability": round(new_ability, 2),
                "delta": round(delta, 2),
                "recommended_difficulty": self.recommend_difficulty(new_ability),
                "attempts": current["attempts"] + 1,
            }
        except Exception as e:
            logger.error(f"update_from_assessment failed: {e}")
            return {"status": "error", "message": str(e)}


ability_engine = AbilityEngine()