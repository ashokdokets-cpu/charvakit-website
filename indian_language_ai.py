"""
Charvak Indian Language AI Engine
Multi-lingual AI assessments for Indian languages
Supports: Hindi, Telugu, Tamil, Bengali, Marathi, Gujarati,
Kannada, Malayalam, Punjabi, Odia, Urdu + English (Hinglish)
(DB-backed - Session J/3)
"""
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Dict, List, Optional

# Global language catalog (34+ languages). Used for AI prompt naming and
# metadata fallback. Wrapped in try/except so a global_config import failure
# never takes down the language engine.
try:
    from global_config import LANGUAGES as _GLOBAL_LANGUAGES
except Exception:
    _GLOBAL_LANGUAGES = {}

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

# English names used in AI prompts. Covers all INDIAN_LANGUAGES keys
# PLUS every key in global_config.LANGUAGES (Session G1).
LANG_NAME_FOR_PROMPT = {
    # Indian
    "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "bn": "Bengali",
    "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "ml": "Malayalam",
    "pa": "Punjabi", "or": "Odia", "ur": "Urdu", "en": "English",
    # Global (from global_config.LANGUAGES)
    "es": "Spanish", "fr": "French", "de": "German", "zh": "Mandarin Chinese",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "pt": "Portuguese",
    "ru": "Russian", "it": "Italian", "nl": "Dutch", "tr": "Turkish",
    "vi": "Vietnamese", "th": "Thai", "id": "Indonesian", "ms": "Malay",
    "fil": "Filipino", "sw": "Swahili", "am": "Amharic", "ha": "Hausa",
    "yo": "Yoruba", "ig": "Igbo", "zu": "Zulu", "so": "Somali",
}


def LANG_META(lang_code: str) -> Dict:
    """Resolve language metadata for DB storage.

    Priority: INDIAN_LANGUAGES -> global_config.LANGUAGES -> generic fallback.
    Returns {name: English, native: <native script>, speakers: str}.
    """
    if lang_code in INDIAN_LANGUAGES:
        return INDIAN_LANGUAGES[lang_code]
    if lang_code in _GLOBAL_LANGUAGES:
        meta = _GLOBAL_LANGUAGES[lang_code]
        return {
            "name": LANG_NAME_FOR_PROMPT.get(lang_code, meta.get("name", lang_code)),
            "native": meta.get("name", lang_code),
            "speakers": "",
        }
    return {"name": lang_code, "native": lang_code, "speakers": ""}

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
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_lang_ai_submissions (
                    submission_id   TEXT PRIMARY KEY,
                    assessment_id   TEXT NOT NULL,
                    email           TEXT,
                    answers         JSONB DEFAULT '[]'::jsonb,
                    score           INTEGER DEFAULT 0,
                    passed          BOOLEAN DEFAULT FALSE,
                    submitted_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_lang_ai_subs_assessment ON charvak_lang_ai_submissions(assessment_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_lang_ai_subs_email      ON charvak_lang_ai_submissions(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_lang_ai_subs_submitted  ON charvak_lang_ai_submissions(submitted_at)''')
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
        Create a multiple-choice assessment in an Indian language.
        data = {language, skill, difficulty, num_questions}
        """
        lang_code = data.get("language", "hi")
        language = INDIAN_LANGUAGES.get(lang_code, INDIAN_LANGUAGES["hi"])
        skill = data.get("skill", "Python")
        difficulty = data.get("difficulty", "Beginner")
        try:
            num_questions = int(data.get("num_questions") or 10)
        except (ValueError, TypeError):
            num_questions = 10
        num_questions = max(5, min(num_questions, 20))
        # Round to the 10/15/20 UI options
        if num_questions not in (10, 15, 20):
            num_questions = 10

        assessment_id = f"ILA-{secrets.token_hex(4).upper()}"
        questions = self._generate_questions(lang_code, skill, difficulty, num_questions)

        if not questions:
            return {"status": "error", "message": "Could not generate questions. Please try again."}

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

        # Strip correct_index before sending to the frontend (cheat prevention)
        safe_questions = []
        for q in questions:
            safe_questions.append({
                "q": q.get("q", ""),
                "options": q.get("options", []),
            })

        assessment = {
            "assessment_id": assessment_id,
            "language": language["name"],
            "native_name": language["native"],
            "skill": skill,
            "difficulty": difficulty,
            "questions": safe_questions,
            "total_questions": len(safe_questions),
            "passing_score": 70,
            "created_at": datetime.now().isoformat(),
        }

        return {
            "status": "success",
            "assessment_id": assessment_id,
            "assessment": assessment,
            "message": f"{language['native']} {skill} assessment created!",
        }

    def _generate_questions(self, lang_code: str, skill: str, difficulty: str, num_questions: int = 10) -> List[Dict]:
        """Generate language-specific questions.
        Tries AI generation first (multilingual via OpenAI), falls back to static catalog.
        """
        # Path 1: AI generation (preferred)
        ai_questions = self._generate_questions_via_ai(lang_code, skill, difficulty, num_questions)
        if ai_questions:
            return ai_questions

        # Path 2: Static fallback only for languages we have catalogs for.
        # Non-Indian languages return [] so the caller falls back explicitly
        # rather than receiving mismatched questions.
        if lang_code in INDIAN_LANGUAGES:
            return self._generate_questions_static(lang_code, skill, num_questions)
        return []

    def _generate_questions_via_ai(self, lang_code: str, skill: str, difficulty: str, num_questions: int = 10) -> List[Dict]:
        """Generate N multiple-choice questions in the target Indian language."""
        import os as _os
        api_key = _os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return []

        lang_name = LANG_NAME_FOR_PROMPT.get(lang_code, "English")

        # Batch: 1 call for <=10, 2 calls for 15 or 20
        batches = []
        remaining = num_questions
        while remaining > 0:
            chunk = min(remaining, 10)
            batches.append(chunk)
            remaining -= chunk

        all_questions = []
        for batch_size in batches:
            batch = self._generate_one_batch(lang_code, lang_name, skill, difficulty, batch_size)
            if not batch:
                # If any batch fails, bail so we don't half-generate
                return []
            all_questions.extend(batch)

        # Validate shape
        cleaned = []
        for q in all_questions:
            if not isinstance(q, dict):
                continue
            text = q.get("q", "").strip()
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
            # Safety net: shuffle options so correct answer is not always at 0
            cleaned_q = self._shuffle_question_options(cleaned_q)
            cleaned.append(cleaned_q)

        if len(cleaned) < num_questions:
            logger.warning(f"AI generated {len(cleaned)} valid questions, wanted {num_questions}")
        return cleaned[:num_questions]

    def _shuffle_question_options(self, q: Dict) -> Dict:
        """Shuffle options and recompute correct_index. Safety net for lazy AI."""
        import random
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

    def _generate_one_batch(self, lang_code: str, lang_name: str, skill: str, difficulty: str, count: int) -> List[Dict]:
        """Single OpenAI call for a batch of MCQs. Returns [] on failure."""
        import os as _os
        import requests
        api_key = _os.getenv("OPENAI_API_KEY", "")

        prompt = (
            f"Generate {count} multiple-choice assessment questions in {lang_name} "
            f"(lang code: {lang_code}) for the skill: {skill}, difficulty: {difficulty}.\n"
            f"Each question MUST have exactly 4 options and one correct answer.\n"
            f"Return JSON: {{\"questions\": [{{\"q\": \"...\", \"options\": [\"...\",\"...\",\"...\",\"...\"], \"correct_index\": 0}}]}}\n"
            f"IMPORTANT:\n"
            f"- All 'q' values and all options must be written in the {lang_name} script, not English.\n"
            f"- correct_index is 0-based (0, 1, 2, or 3).\n"
            f"- CRITICAL: Vary correct_index across questions. Do NOT always put the correct answer at position 0.\n"
            f"- Aim for a roughly even distribution of correct answers across positions 0, 1, 2, and 3.\n"
            f"- Keep options short (1-10 words each).\n"
            f"- Make questions job-interview appropriate and unambiguous.\n"
            f"- Return exactly {count} questions."
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
                timeout=40,
            )
            data = response.json()
            content = (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
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
            logger.error(f"AI MCQ batch generation failed for {lang_code}: {e}")
            return []

    def _generate_questions_static(self, lang_code: str, skill: str, num_questions: int = 10) -> List[Dict]:
        """
        Minimal MCQ fallback when AI is unavailable.
        Generates generic multiple-choice questions about the skill.
        All are in English since we can't safely template in 12 languages
        without proper UTF-8 source. AI is the primary path.
        """
        templates = [
            {
                "q": f"Which of the following best describes a common use case for {skill}?",
                "options": [
                    f"Building production systems that rely on {skill}",
                    "Formatting documents in a word processor",
                    "Designing physical circuit boards",
                    "Managing payroll for large teams",
                ],
                "correct_index": 0,
            },
            {
                "q": f"What is a key benefit of using {skill} in a professional context?",
                "options": [
                    "It increases typing speed",
                    "It solves specific technical problems efficiently",
                    "It reduces screen brightness",
                    "It changes the operating system",
                ],
                "correct_index": 1,
            },
            {
                "q": f"Which statement about {skill} is most accurate?",
                "options": [
                    "It has no practical application",
                    "It is only used by hobbyists",
                    "It requires understanding of core concepts to apply well",
                    "It cannot be learned online",
                ],
                "correct_index": 2,
            },
            {
                "q": f"When would a professional most likely choose to use {skill}?",
                "options": [
                    "Only on weekends",
                    "When no other tool exists",
                    "As part of solving a task that matches its strengths",
                    "Never in a team setting",
                ],
                "correct_index": 2,
            },
            {
                "q": f"Which is a common challenge when working with {skill}?",
                "options": [
                    "Too much documentation",
                    "Requires ongoing learning as the field evolves",
                    "No community support",
                    "Cannot be tested",
                ],
                "correct_index": 1,
            },
            {
                "q": f"How should someone new to {skill} begin learning it?",
                "options": [
                    "By memorizing every API before writing code",
                    "By building small projects and iterating",
                    "By only reading theory, never practicing",
                    "By avoiding all documentation",
                ],
                "correct_index": 1,
            },
            {
                "q": f"Which is generally considered good practice with {skill}?",
                "options": [
                    "Writing the longest possible code",
                    "Avoiding all comments and documentation",
                    "Testing incrementally and documenting decisions",
                    "Never asking for code review",
                ],
                "correct_index": 2,
            },
            {
                "q": f"In a team setting, how is {skill} typically used?",
                "options": [
                    "By a single developer in isolation, never shared",
                    "Collaboratively, with version control and reviews",
                    "Only during emergencies",
                    "Only on production systems",
                ],
                "correct_index": 1,
            },
            {
                "q": f"Which best describes the role of {skill} in a real project?",
                "options": [
                    "It is decorative and optional",
                    "It is a tool applied where its strengths match the task",
                    "It replaces all other tools",
                    "It is only for research",
                ],
                "correct_index": 1,
            },
            {
                "q": f"How would you evaluate whether a solution using {skill} is good?",
                "options": [
                    "By counting lines of code",
                    "By how well it meets requirements, is readable, and is maintainable",
                    "By how obscure it is",
                    "By how quickly it was written, regardless of correctness",
                ],
                "correct_index": 1,
            },
            {
                "q": f"Which is a sign that someone has strong {skill} fundamentals?",
                "options": [
                    "They can recite every API from memory",
                    "They can explain trade-offs and pick appropriate tools",
                    "They avoid all documentation",
                    "They never ask questions",
                ],
                "correct_index": 1,
            },
            {
                "q": f"What is a reasonable first step when facing an unfamiliar problem in {skill}?",
                "options": [
                    "Assume you cannot solve it",
                    "Break it into smaller parts and research each",
                    "Copy random code from the internet",
                    "Skip testing",
                ],
                "correct_index": 1,
            },
            {
                "q": f"Which is NOT generally good practice with {skill}?",
                "options": [
                    "Writing tests",
                    "Documenting key decisions",
                    "Sharing state globally without reason",
                    "Reviewing code with peers",
                ],
                "correct_index": 2,
            },
            {
                "q": f"How should you think about performance when using {skill}?",
                "options": [
                    "Ignore it entirely",
                    "Optimize prematurely before measuring",
                    "Measure first, then optimize based on evidence",
                    "Only optimize for one user",
                ],
                "correct_index": 2,
            },
            {
                "q": f"What role does documentation play with {skill}?",
                "options": [
                    "None - it slows developers down",
                    "It is essential for maintainability and onboarding",
                    "It is only for academic work",
                    "It should be hidden from users",
                ],
                "correct_index": 1,
            },
            {
                "q": f"Which is a common misconception about {skill}?",
                "options": [
                    "It requires practice to master",
                    "Once learned, it never changes",
                    "It has trade-offs",
                    "It benefits from community knowledge",
                ],
                "correct_index": 1,
            },
            {
                "q": f"How should you handle errors when working with {skill}?",
                "options": [
                    "Suppress all errors silently",
                    "Log, surface, and handle errors explicitly",
                    "Restart the entire system on any error",
                    "Ignore errors under 1 second",
                ],
                "correct_index": 1,
            },
            {
                "q": f"Which best supports continuous improvement with {skill}?",
                "options": [
                    "Avoiding feedback",
                    "Regular code review and reflecting on outcomes",
                    "Never reading others' code",
                    "Only working alone",
                ],
                "correct_index": 1,
            },
            {
                "q": f"How would you introduce {skill} to a new codebase?",
                "options": [
                    "Rewrite everything immediately",
                    "Integrate incrementally with tests and clear scope",
                    "Add it without discussion or documentation",
                    "Avoid integrating at all",
                ],
                "correct_index": 1,
            },
            {
                "q": f"What is the most important quality when applying {skill} to solve a problem?",
                "options": [
                    "Speed only",
                    "Understanding the problem before choosing a solution",
                    "Avoiding all collaboration",
                    "Using the most complex approach available",
                ],
                "correct_index": 1,
            },
        ]
        return templates[:max(1, num_questions)]

    def submit_assessment(self, data: Dict) -> Dict:
        """
        Submit answers for scoring (deterministic, MCQ).
        data = {assessment_id, answers: List[int], email}
        """
        assessment_id = data.get("assessment_id")
        email = (data.get("email") or "").strip().lower()
        answers = data.get("answers", [])

        if not assessment_id:
            return {"status": "error", "message": "assessment_id required"}
        if not isinstance(answers, list):
            answers = []

        # Load the assessment to get correct_index for each question
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute(
                "SELECT questions, total_questions, passing_score FROM charvak_lang_ai_assessments WHERE assessment_id = %s",
                (assessment_id,),
            )
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Assessment not found"}
            questions = row[0] if isinstance(row[0], list) else json.loads(row[0] or "[]")
            total_questions = row[1] or len(questions)
            passing_score = row[2] or 70
        except Exception as e:
            logger.error(f"submit_assessment lookup failed: {e}")
            return {"status": "error", "message": "Could not load assessment"}

        # Score: compare each answer to correct_index
        correct_count = 0
        graded = []
        for i, q in enumerate(questions):
            correct_idx = q.get("correct_index")
            submitted = answers[i] if i < len(answers) else None
            try:
                submitted_int = int(submitted) if submitted is not None and submitted != "" else -1
            except (ValueError, TypeError):
                submitted_int = -1
            is_correct = (submitted_int == correct_idx)
            if is_correct:
                correct_count += 1
            graded.append({
                "index": i,
                "submitted": submitted_int,
                "correct": correct_idx,
                "is_correct": is_correct,
            })

        score = round(correct_count / total_questions * 100) if total_questions > 0 else 0
        passed = score >= passing_score
        submission_id = f"LSUB-{secrets.token_hex(4).upper()}"

        try:
            cur.execute("""
                INSERT INTO charvak_lang_ai_submissions
                    (submission_id, assessment_id, email, answers, score, passed)
                VALUES (%s, %s, %s, %s::jsonb, %s, %s)
            """, (
                submission_id, assessment_id, email,
                json.dumps(answers), score, passed,
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"submit_assessment persist failed: {e}")

        return {
            "status": "success",
            "submission_id": submission_id,
            "assessment_id": assessment_id,
            "score": score,
            "passed": passed,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "passing_score": passing_score,
            "message": f"Assessment scored: {score}%",
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
        language = LANG_META(lang_code)

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
                "languages_available": list(INDIAN_LANGUAGES.keys()),
            },
        }


indian_language_ai = IndianLanguageAI()
