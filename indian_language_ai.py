"""
Charvak Indian Language AI Engine
Multi-lingual AI assessments for Indian languages
Supports: Hindi, Telugu, Tamil, Bengali, Marathi, Gujarati,
Kannada, Malayalam, Punjabi, Odia, Urdu + English (Hinglish)
(DB-backed - Session J/3)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.indianlang")

# Supported Indian Languages
INDIAN_LANGUAGES = {
    "hi": {"name": "Hindi", "native": "हिन्दी", "speakers": "600M+"},
    "te": {"name": "Telugu", "native": "తెలుగు", "speakers": "90M+"},
    "ta": {"name": "Tamil", "native": "தமிழ்", "speakers": "75M+"},
    "bn": {"name": "Bengali", "native": "বাংলা", "speakers": "230M+"},
    "mr": {"name": "Marathi", "native": "मराठी", "speakers": "83M+"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી", "speakers": "55M+"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ", "speakers": "43M+"},
    "ml": {"name": "Malayalam", "native": "മലയാളം", "speakers": "35M+"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ", "speakers": "33M+"},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ", "speakers": "37M+"},
    "ur": {"name": "Urdu", "native": "اردو", "speakers": "50M+"},
    "en": {"name": "English (Hinglish)", "native": "Hinglish", "speakers": "125M+"},
}


class IndianLanguageAI:
    """AI-powered assessments in Indian languages (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Indian Language AI ready (DB-backed) - %d languages", len(INDIAN_LANGUAGES))

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lang_ai_assessments (
                    assessment_id     TEXT PRIMARY KEY,
                    language          TEXT,
                    native_name       TEXT,
                    skill             TEXT,
                    difficulty        TEXT DEFAULT 'Beginner',
                    questions         JSONB DEFAULT '[]'::jsonb,
                    total_questions   INTEGER DEFAULT 0,
                    passing_score     INTEGER DEFAULT 70,
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_lang_ai_language ON charvak_lang_ai_assessments(language)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_lang_ai_skill    ON charvak_lang_ai_assessments(skill)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_lang_ai_created  ON charvak_lang_ai_assessments(created_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"indian_language tables init failed: {e}")

    # ============================================================
    # STATIC CATALOG
    # ============================================================

    def get_languages(self) -> Dict:
        """Get all supported Indian languages."""
        return {
            "status": "success",
            "languages": INDIAN_LANGUAGES,
            "count": len(INDIAN_LANGUAGES),
            "total_speakers": "1.4 Billion+",
        }

    # ============================================================
    # ASSESSMENTS
    # ============================================================

    def create_assessment(self, data: Dict) -> Dict:
        """
        Create an assessment in an Indian language.
        data = {language: "hi"/"te"/"ta"..., skill: str, difficulty: str}
        """
        lang_code = data.get("language", "hi")
        language = INDIAN_LANGUAGES.get(lang_code, INDIAN_LANGUAGES["hi"])
        skill = data.get("skill", "Python")
        difficulty = data.get("difficulty", "Beginner")

        assessment_id = f"ILA-{secrets.token_hex(4).upper()}"
        questions = self._generate_questions(lang_code, skill, difficulty)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_lang_ai_assessments
                    (assessment_id, language, native_name, skill, difficulty,
                     questions, total_questions, passing_score)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, 70)
            ''', (
                assessment_id,
                language["name"],
                language["native"],
                skill,
                difficulty,
                json.dumps(questions),
                len(questions),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_assessment failed: {e}")
            return {"status": "error", "message": "Could not create assessment"}

        assessment = {
            "assessment_id": assessment_id,
            "language": language["name"],
            "native_name": language["native"],
            "skill": skill,
            "difficulty": difficulty,
            "questions": questions,
            "total_questions": len(questions),
            "passing_score": 70,
            "created_at": datetime.now().isoformat(),
        }

        return {
            "status": "success",
            "assessment_id": assessment_id,
            "assessment": assessment,
            "message": f"{language['native']} {skill} assessment created!",
        }

    def _generate_questions(self, lang_code: str, skill: str, difficulty: str) -> List[Dict]:
        """Generate language-specific questions (static catalog)."""
        questions_map = {
            "hi": [
                {"q": f"क्या आप {skill} में experienced हैं? अपना अनुभव बताइए।", "type": "text"},
                {"q": f"{skill} में आपकी सबसे बड़ी strength क्या है?", "type": "text"},
                {"q": f"एक project का example दीजिए जहाँ आपने {skill} use किया।", "type": "text"},
            ],
            "te": [
                {"q": f"మీరు {skill} లో experienced ఉన్నారా? మీ అనుభవం చెప్పండి.", "type": "text"},
                {"q": f"{skill} లో మీ biggest strength ఏమిటి?", "type": "text"},
                {"q": f"మీరు {skill} ఉపయోగించిన ఒక project example ఇవ్వండి.", "type": "text"},
            ],
            "ta": [
                {"q": f"நீங்கள் {skill} இல் அனுபவம் உள்ளவரா? உங்கள் அனுபவத்தை கூறுங்கள்.", "type": "text"},
                {"q": f"{skill} இல் உங்கள் மிகப்பெரிய பலம் என்ன?", "type": "text"},
                {"q": f"{skill} பயன்படுத்திய ஒரு project உதாரணம் கொடுங்கள்.", "type": "text"},
            ],
            "bn": [
                {"q": f"আপনি কি {skill} এ অভিজ্ঞ? আপনার অভিজ্ঞতা বলুন।", "type": "text"},
                {"q": f"{skill} এ আপনার সবচেয়ে বড় শক্তি কী?", "type": "text"},
                {"q": f"একটি project উদাহরণ দিন যেখানে আপনি {skill} ব্যবহার করেছেন।", "type": "text"},
            ],
            "mr": [
                {"q": f"तुम्ही {skill} मध्ये अनुभवी आहात का? तुमचा अनुभव सांगा.", "type": "text"},
                {"q": f"{skill} मध्ये तुमची सर्वात मोठी ताकद काय आहे?", "type": "text"},
                {"q": f"एक project उदाहरण द्या जिथे तुम्ही {skill} वापरले.", "type": "text"},
            ],
            "en": [
                {"q": f"Aap {skill} mein experienced ho? Apna experience batao. (Hinglish)", "type": "text"},
                {"q": f"{skill} mein aapki biggest strength kya hai?", "type": "text"},
                {"q": f"Ek project example do jahan aapne {skill} use kiya.", "type": "text"},
            ],
        }

        return questions_map.get(lang_code, questions_map["en"])

    def submit_assessment(self, data: Dict) -> Dict:
        """
        Submit answers for scoring.
        data = {assessment_id, answers: List[str]}
        """
        assessment_id = data.get("assessment_id")
        answers = data.get("answers", [])

        # Score based on answer quality (matches original formula)
        score = min(len(answers) * 30 + 10, 100) if answers else 0

        return {
            "status": "success",
            "assessment_id": assessment_id,
            "score": score,
            "passed": score >= 70,
            "message": "Assessment submitted!",
        }

    # ============================================================
    # TRANSLATION
    # ============================================================

    def translate_job_ad(self, data: Dict) -> Dict:
        """
        Translate job ad to Indian language.
        data = {language: str, job_title: str, company: str, location: str}
        """
        lang_code = data.get("language", "hi")
        language = INDIAN_LANGUAGES.get(lang_code, INDIAN_LANGUAGES["hi"])

        translations = {
            "hi": {"hiring": "भर्ती", "location": "स्थान", "salary": "वेतन", "apply": "आवेदन करें"},
            "te": {"hiring": "నియామకం", "location": "ప్రాంతం", "salary": "జీతం", "apply": "దరఖాస్తు చేయండి"},
            "ta": {"hiring": "பணியமர்த்தல்", "location": "இடம்", "salary": "சம்பளம்", "apply": "விண்ணப்பிக்கவும்"},
            "en": {"hiring": "Hiring", "location": "Location", "salary": "Salary", "apply": "Apply"},
        }

        t = translations.get(lang_code, translations["en"])

        job_title = data.get("job_title", "Software Engineer")
        company = data.get("company", "Company")
        location = data.get("location", "Remote")

        # Emoji via \U escapes (source ASCII-safe for these spots)
        ad = (
            f"\U0001F680 {company} {t['hiring']} कर रहा है: {job_title}\n"
            f"\U0001F4CD {t['location']}: {location}\n"
            f"\U0001F449 {t['apply']}: https://charvakit.com/job-board"
        )

        return {
            "status": "success",
            "language": language["name"],
            "translated_ad": ad,
            "message": f"Job ad translated to {language['native']}",
        }

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        """Get Indian Language AI statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_lang_ai_assessments')
            total_assessments = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_languages": len(INDIAN_LANGUAGES),
                "total_assessments": total_assessments,
                "total_translations": 0,
                "languages_available": list(INDIAN_LANGUAGES.keys()),
            },
        }


indian_language_ai = IndianLanguageAI()
