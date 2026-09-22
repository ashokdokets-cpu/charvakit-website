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

# Language section hints — used by _generate_via_ai to force correct
# script when topic matches a language name (e.g., WBPSC 'Bengali' section).
LANGUAGE_HINTS = {
    "Bengali":   ("Bengali",   "বাংলা (Bengali script)"),
    "Hindi":     ("Hindi",     "हिन्दी (Devanagari script)"),
    "Tamil":     ("Tamil",     "தமிழ் (Tamil script)"),
    "Telugu":    ("Telugu",    "తెలుగు (Telugu script)"),
    "Marathi":   ("Marathi",   "मराठी (Devanagari script)"),
    "Kannada":   ("Kannada",   "ಕನ್ನಡ (Kannada script)"),
    "Malayalam": ("Malayalam", "മലയാളം (Malayalam script)"),
    "Gujarati":  ("Gujarati",  "ગુજરાતી (Gujarati script)"),
    "Punjabi":   ("Punjabi",   "ਪੰਜਾਬੀ (Gurmukhi script)"),
    "Urdu":      ("Urdu",      "اردو (Urdu script)"),
}


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
        """Static catalog - 136 exams, 12 categories. Reference data, versioned with code."""
        return {
            "central_govt": {"name": "Central Government & Staff Recruitment", "icon": "central_govt", "exams": [
                {"id": "ssc_cgl", "name": "SSC CGL", "difficulty": "Medium", "full_name": "Combined Graduate Level", "tier": "Tier 1 & 2", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 100, "duration": "60 min"},
                {"id": "ssc_chsl", "name": "SSC CHSL", "difficulty": "Medium", "full_name": "Combined Higher Secondary", "tier": "Tier 1 & 2", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 100, "duration": "60 min"},
                {"id": "ssc_mts", "name": "SSC MTS", "difficulty": "Medium", "full_name": "Multi-Tasking Staff", "tier": "CBT", "sections": ["Reasoning", "Numerical", "English", "GK"], "questions": 90, "duration": "90 min"},
                {"id": "ssc_cpo", "name": "SSC CPO", "difficulty": "Medium", "full_name": "Sub-Inspector", "tier": "Tier 1 & 2", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 200, "duration": "120 min"},
                {"id": "ssc_je", "name": "SSC JE", "difficulty": "Medium", "full_name": "Junior Engineer", "tier": "CBT 1 & 2", "sections": ["Technical", "Reasoning", "Quant"], "questions": 200, "duration": "120 min"},
                {"id": "ssc_gd", "name": "SSC GD", "difficulty": "Medium", "full_name": "General Duty Constable", "tier": "CBT", "sections": ["Reasoning", "GK", "Numerical"], "questions": 80, "duration": "60 min"},
                {"id": "ssc_steno", "name": "SSC Stenographer", "difficulty": "Medium", "full_name": "Grade C & D", "tier": "CBT", "sections": ["Reasoning", "English", "GK"], "questions": 200, "duration": "120 min"},
                {"id": "rrb_ntpc", "name": "RRB NTPC", "difficulty": "Medium", "full_name": "Non-Technical Popular Categories", "tier": "CBT 1 & 2", "sections": ["Reasoning", "Quant", "GK"], "questions": 100, "duration": "90 min"},
                {"id": "rrb_group_d", "name": "RRB Group D", "difficulty": "Medium", "full_name": "Level-1 Posts", "tier": "CBT", "sections": ["Math", "Reasoning", "Science", "GK"], "questions": 100, "duration": "90 min"},
                {"id": "rrb_alp", "name": "RRB ALP", "difficulty": "Medium", "full_name": "Assistant Loco Pilot", "tier": "CBT 1 & 2", "sections": ["Math", "Reasoning", "Technical"], "questions": 75, "duration": "60 min"},
                {"id": "rrb_alp_cbat", "name": "RRB ALP CBAT", "difficulty": "Hard", "full_name": "Computer-Based Aptitude Test (Stage 3)", "tier": "CBAT", "sections": ["Analogies", "Decision Making", "Numerical Ability", "Memory", "Following Directions"], "formats": {"Analogies": "cbat", "Decision Making": "cbat", "Numerical Ability": "cbat", "Memory": "cbat", "Following Directions": "cbat"}, "questions": 100, "duration": "35 min"},
                {"id": "rrb_je", "name": "RRB JE", "difficulty": "Medium", "full_name": "Junior Engineer", "tier": "CBT 1 & 2", "sections": ["Technical", "Reasoning", "Quant"], "questions": 150, "duration": "120 min"},
                {"id": "upsc_epfo", "name": "UPSC EPFO", "difficulty": "Hard", "full_name": "Enforcement Officer", "tier": "CBT", "sections": ["Reasoning", "Quant", "English", "GK"], "questions": 120, "duration": "120 min"},
                {"id": "upsc_cse", "name": "UPSC CSE", "difficulty": "Hard", "full_name": "Civil Services Examination (Prelims)", "tier": "Prelims", "sections": ["General Studies", "CSAT"], "questions": 200, "duration": "120 min"}
            ]},
            "banking": {"name": "Banking & Financial", "icon": "banking", "exams": [
                {"id": "ibps_po", "name": "IBPS PO", "difficulty": "Medium", "full_name": "Probationary Officer", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "ibps_clerk", "name": "IBPS Clerk", "difficulty": "Medium", "full_name": "Customer Support Associate", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "ibps_so", "name": "IBPS SO", "difficulty": "Medium", "full_name": "Specialist Officer", "tier": "Prelims & Mains", "sections": ["Technical", "Reasoning", "English"], "questions": 150, "duration": "120 min"},
                {"id": "ibps_rrb_officer", "name": "IBPS RRB Officer", "difficulty": "Medium", "full_name": "Scale I, II, III", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 80, "duration": "45 min"},
                {"id": "ibps_rrb_assistant", "name": "IBPS RRB Assistant", "difficulty": "Medium", "full_name": "Multipurpose", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant"], "questions": 80, "duration": "45 min"},
                {"id": "sbi_po", "name": "SBI PO", "difficulty": "Medium", "full_name": "Probationary Officer", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "sbi_clerk", "name": "SBI Clerk", "difficulty": "Medium", "full_name": "Junior Associate", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "rbi_grade_b", "name": "RBI Grade B", "difficulty": "Medium", "full_name": "Direct Recruit", "tier": "Phase 1 & 2", "sections": ["Reasoning", "Quant", "English", "Finance"], "questions": 200, "duration": "120 min"},
                {"id": "rbi_assistant", "name": "RBI Assistant", "difficulty": "Medium", "full_name": "Assistant", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "sebi_grade_a", "name": "SEBI Grade A", "difficulty": "Medium", "full_name": "Assistant Manager", "tier": "Phase 1 & 2", "sections": ["Finance", "Reasoning", "English"], "questions": 200, "duration": "120 min"},
                {"id": "nabard", "name": "NABARD", "difficulty": "Medium", "full_name": "Grade A & B", "tier": "Prelims & Mains", "sections": ["Agriculture", "Finance", "Reasoning"], "questions": 200, "duration": "120 min"},
                {"id": "lic_aao", "name": "LIC AAO", "difficulty": "Medium", "full_name": "Assistant Administrative Officer", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "lic_ado", "name": "LIC ADO", "difficulty": "Medium", "full_name": "Apprentice Development Officer", "tier": "CBT", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"},
                {"id": "niacl_ao", "name": "NIACL AO", "difficulty": "Medium", "full_name": "New India Assurance AO", "tier": "Prelims & Mains", "sections": ["Reasoning", "Quant", "English"], "questions": 100, "duration": "60 min"}
            ]},
            "engineering": {"name": "Engineering & Technology", "icon": "engineering", "exams": [
                {"id": "jee_main", "name": "JEE Main", "difficulty": "Medium", "full_name": "Joint Entrance Examination", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 90, "duration": "180 min"},
                {"id": "bitsat", "name": "BITSAT", "difficulty": "Medium", "full_name": "BITS Admission Test", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math", "English"], "questions": 130, "duration": "180 min"},
                {"id": "viteee", "name": "VITEEE", "difficulty": "Medium", "full_name": "VIT Entrance Exam", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 125, "duration": "150 min"},
                {"id": "gate", "name": "GATE", "difficulty": "Hard", "full_name": "Graduate Aptitude Test", "tier": "CBT", "sections": ["Technical", "Aptitude", "Math"], "questions": 65, "duration": "180 min"},
                {"id": "isro", "name": "ISRO", "difficulty": "Hard", "full_name": "Scientist/Engineer", "tier": "CBT", "sections": ["Technical", "Aptitude"], "questions": 80, "duration": "90 min"},
                {"id": "barc", "name": "BARC", "difficulty": "Hard", "full_name": "OCES/DGFS", "tier": "CBT", "sections": ["Technical", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "drdo", "name": "DRDO CEPTAM", "difficulty": "Hard", "full_name": "Tier 1 & 2", "tier": "CBT", "sections": ["Technical", "Reasoning", "Quant"], "questions": 150, "duration": "120 min"},
                {"id": "jee_advanced", "name": "JEE Advanced", "difficulty": "Hard", "full_name": "Joint Entrance Examination Advanced", "tier": "Paper 1 & 2", "sections": ["Physics", "Chemistry", "Math"], "questions": 54, "duration": "180 min"},
                {"id": "srmjeee", "name": "SRMJEEE", "difficulty": "Medium", "full_name": "SRM Joint Engineering Entrance Examination", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math", "English", "Aptitude"], "questions": 125, "duration": "150 min"},
                {"id": "met_manipal", "name": "MET (Manipal)", "difficulty": "Medium", "full_name": "Manipal Entrance Test", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math", "English", "General Aptitude"], "questions": 100, "duration": "120 min"},
                {"id": "comedk_uget", "name": "COMEDK UGET", "difficulty": "Medium", "full_name": "Consortium of Medical, Engineering and Dental Colleges of Karnataka", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 180, "duration": "180 min"}
            ]},
            "defense": {"name": "Defense & Security", "icon": "defense", "exams": [
                {"id": "afcat", "name": "AFCAT", "difficulty": "Medium", "full_name": "Air Force Common Admission Test", "tier": "CBT", "sections": ["Verbal", "Numerical", "Reasoning", "GK"], "questions": 100, "duration": "120 min"},
                {"id": "army_agniveer", "name": "Army Agniveer", "difficulty": "Easy", "full_name": "Common Entrance Exam", "tier": "CEE Online", "sections": ["Math", "GK", "Reasoning"], "questions": 50, "duration": "60 min"},
                {"id": "navy_agniveer", "name": "Navy Agniveer", "difficulty": "Easy", "full_name": "SSR/MR", "tier": "INET Online", "sections": ["Math", "Science", "English"], "questions": 100, "duration": "60 min"},
                {"id": "airforce_agniveer", "name": "Airforce Agniveer", "difficulty": "Easy", "full_name": "Vayu", "tier": "STAR Online", "sections": ["Math", "Physics", "English"], "questions": 100, "duration": "60 min"},
                {"id": "coast_guard", "name": "Coast Guard", "difficulty": "Medium", "full_name": "Navik/Yantrik", "tier": "CBT", "sections": ["Math", "Science", "English"], "questions": 100, "duration": "60 min"},
                {"id": "capf", "name": "CAPF", "difficulty": "Medium", "full_name": "Constable/SI", "tier": "CBT Tier 1", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"}
            ]},
            "medical": {"name": "Medical & Healthcare", "icon": "medical", "exams": [
                {"id": "neet_pg", "name": "NEET PG", "difficulty": "Hard", "full_name": "Postgraduate Medical", "tier": "CBT", "sections": ["Medicine", "Surgery", "Pediatrics", "OBG"], "questions": 200, "duration": "210 min"},
                {"id": "neet_ug", "name": "NEET UG", "difficulty": "Hard", "full_name": "National Eligibility cum Entrance Test (Undergraduate)", "tier": "CBT", "sections": ["Physics", "Chemistry", "Biology"], "questions": 180, "duration": "200 min"},
                {"id": "ini_cet", "name": "INI-CET", "difficulty": "Hard", "full_name": "AIIMS/JIPMER/PGI", "tier": "CBT", "sections": ["Medicine", "Surgery", "Pediatrics"], "questions": 200, "duration": "180 min"},
                {"id": "fmge", "name": "FMGE", "difficulty": "Hard", "full_name": "Foreign Medical Graduate", "tier": "CBT", "sections": ["Medicine", "Surgery", "OBG"], "questions": 300, "duration": "300 min"},
                {"id": "neet_mds", "name": "NEET MDS", "difficulty": "Hard", "full_name": "Dental Master's", "tier": "CBT", "sections": ["Dental Anatomy", "Pathology", "Pharmacology"], "questions": 240, "duration": "180 min"},
                {"id": "gpat", "name": "GPAT", "difficulty": "Medium", "full_name": "Pharmacy Aptitude Test", "tier": "CBT", "sections": ["Pharmaceutics", "Pharmacology", "Chemistry"], "questions": 125, "duration": "180 min"}
            ]},
            "university": {"name": "University & Teaching", "icon": "university", "exams": [
                {"id": "cuet_ug", "name": "CUET UG", "difficulty": "Easy", "full_name": "Undergraduate", "tier": "CBT", "sections": ["Language", "Domain Subjects", "General Test"], "questions": 175, "duration": "195 min"},
                {"id": "cuet_pg", "name": "CUET PG", "difficulty": "Easy", "full_name": "Postgraduate", "tier": "CBT", "sections": ["Domain Subject", "General"], "questions": 100, "duration": "120 min"},
                {"id": "ugc_net", "name": "UGC NET", "difficulty": "Medium", "full_name": "Assistant Professor/JRF", "tier": "CBT", "sections": ["Teaching Aptitude", "Research Aptitude", "Subject"], "questions": 150, "duration": "180 min"},
                {"id": "csir_net", "name": "CSIR NET", "difficulty": "Hard", "full_name": "Science JRF", "tier": "CBT", "sections": ["Physical Sciences", "Chemical Sciences", "Life Sciences"], "questions": 150, "duration": "180 min"},
                {"id": "ctet", "name": "CTET", "difficulty": "Easy", "full_name": "Teacher Eligibility", "tier": "CBT", "sections": ["Child Development", "Math", "Language"], "questions": 150, "duration": "150 min"},
                {"id": "iit_jam", "name": "IIT JAM", "difficulty": "Hard", "full_name": "Joint Admission Test for Masters", "tier": "CBT", "sections": ["Biological Sciences", "Chemistry", "Geology", "Mathematics", "Mathematical Statistics", "Physics"], "questions": 60, "duration": "180 min"},
                {"id": "nimcet", "name": "NIMCET", "difficulty": "Medium", "full_name": "NIT MCA Common Entrance Test", "tier": "CBT", "sections": ["Mathematics", "Analytical Ability & Logical Reasoning", "Computer Awareness", "General English"], "questions": 120, "duration": "120 min"}
            ]},
            "management": {"name": "Management & Law", "icon": "management", "exams": [
                {"id": "cat", "name": "CAT", "difficulty": "Hard", "full_name": "IIM Admission", "tier": "CBT", "sections": ["VARC", "DILR", "Quant"], "questions": 66, "duration": "120 min"},
                {"id": "xat", "name": "XAT", "difficulty": "Hard", "full_name": "Xavier Aptitude Test", "tier": "CBT", "sections": ["Verbal", "Decision Making", "Quant"], "questions": 100, "duration": "180 min"},
                {"id": "nmat", "name": "NMAT", "difficulty": "Medium", "full_name": "NMIMS Admission", "tier": "CBT", "sections": ["Language", "Quant", "Logical"], "questions": 108, "duration": "120 min"},
                {"id": "snap", "name": "SNAP", "difficulty": "Medium", "full_name": "Symbiosis Admission", "tier": "CBT", "sections": ["General English", "Quant", "Reasoning"], "questions": 60, "duration": "60 min"},
                {"id": "cmat", "name": "CMAT", "difficulty": "Medium", "full_name": "Management Admission", "tier": "CBT", "sections": ["Quant", "Reasoning", "Language"], "questions": 100, "duration": "180 min"},
                {"id": "clat", "name": "CLAT PG", "difficulty": "Hard", "full_name": "Law Admission", "tier": "CBT", "sections": ["Legal Reasoning", "English", "GK"], "questions": 120, "duration": "120 min"},
                {"id": "ceed", "name": "CEED/UCEED", "difficulty": "Hard", "full_name": "Design Admissions", "tier": "CBT", "sections": ["Design Aptitude", "Visualization", "Creativity"], "questions": 100, "duration": "180 min"},
                {"id": "mat", "name": "MAT", "difficulty": "Medium", "full_name": "Management Aptitude Test (AIMA)", "tier": "CBT + PBT", "sections": ["Language Comprehension", "Mathematical Skills", "Data Analysis", "Intelligence & Critical Reasoning", "Indian & Global Environment"], "questions": 150, "duration": "150 min"},
                {"id": "atma", "name": "ATMA", "difficulty": "Medium", "full_name": "AIMS Test for Management Admissions", "tier": "CBT", "sections": ["Analytical Reasoning", "Quantitative Skills", "Verbal Skills"], "questions": 180, "duration": "180 min"},
                {"id": "mah_mba_cet", "name": "MAH MBA CET", "difficulty": "Medium", "full_name": "Maharashtra MBA Common Entrance Test", "tier": "CBT", "sections": ["Logical Reasoning", "Abstract Reasoning", "Quantitative Aptitude", "Verbal Ability & Reading Comprehension"], "questions": 200, "duration": "150 min"}
            ]},
            "state_exams": {"name": "State Level Exams", "icon": "state_exams", "exams": [
                {"id": "mht_cet", "name": "MHT-CET", "difficulty": "Easy", "full_name": "Maharashtra", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 150, "duration": "180 min"},
                {"id": "ap_eapcet", "name": "AP EAPCET", "difficulty": "Easy", "full_name": "Andhra Pradesh", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 160, "duration": "180 min"},
                {"id": "ts_eapcet", "name": "TS EAPCET", "difficulty": "Easy", "full_name": "Telangana", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 160, "duration": "180 min"},
                {"id": "wbjee", "name": "WBJEE", "difficulty": "Easy", "full_name": "West Bengal", "tier": "CBT", "sections": ["Physics", "Chemistry", "Math"], "questions": 155, "duration": "180 min"},
                {"id": "upsssc", "name": "UPSSSC", "difficulty": "Easy", "full_name": "Uttar Pradesh", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "mppeb", "name": "MPPEB", "difficulty": "Easy", "full_name": "Madhya Pradesh (Vyapam)", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "rsmssb", "name": "RSMSSB", "difficulty": "Easy", "full_name": "Rajasthan", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "jssc", "name": "JSSC", "difficulty": "Easy", "full_name": "Jharkhand", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "bpsc", "name": "BPSC", "difficulty": "Medium", "full_name": "Bihar", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "appsc", "name": "APPSC", "difficulty": "Medium", "full_name": "Andhra Pradesh PSC", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"},
                {"id": "tspsc", "name": "TSPSC", "difficulty": "Medium", "full_name": "Telangana PSC", "tier": "CBT", "sections": ["Reasoning", "GK", "Math"], "questions": 100, "duration": "120 min"}
            ]},
            "international": {"name": "International Exams", "icon": "international", "exams": [
                {"id": "gmat_focus", "name": "GMAT Focus Edition", "difficulty": "Hard", "full_name": "Graduate Management Admission Test", "tier": "Section-Adaptive CAT", "sections": ["Quantitative Reasoning", "Verbal Reasoning", "Data Insights"], "questions": 64, "duration": "135 min"},
                {"id": "gre_general", "name": "GRE General Test", "difficulty": "Hard", "full_name": "Graduate Record Examination", "tier": "Section-Adaptive", "sections": ["Verbal Reasoning", "Quantitative Reasoning", "Analytical Writing"], "questions": 82, "duration": "118 min"},
                {"id": "toefl_ibt", "name": "TOEFL iBT", "difficulty": "Medium", "full_name": "Test of English as a Foreign Language - Internet Based Test", "tier": "CBT", "sections": ["Reading", "Listening", "Speaking", "Writing"], "questions": 40, "duration": "116 min"},
                {"id": "ielts_academic", "name": "IELTS Academic", "difficulty": "Medium", "full_name": "International English Language Testing System (Academic)", "tier": "CBT", "sections": ["Listening", "Reading", "Writing"], "formats": {"Listening": "mcq", "Reading": "mcq", "Writing": "essay"}, "questions": 80, "duration": "150 min"}
            ]},
            "state_pcs": {"name": "State Civil Services", "icon": "state_pcs", "exams": [
                {"id": "uppsc_pcs", "name": "UPPSC PCS", "difficulty": "Medium", "full_name": "UP Combined State / Upper Subordinate Services", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "UP Special"], "questions": 150, "duration": "120 min"},
                {"id": "mpsc_rajyaseva", "name": "MPSC Rajyaseva", "difficulty": "Medium", "full_name": "Maharashtra Civil Services", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "MH Special"], "questions": 150, "duration": "120 min"},
                {"id": "rpsc_ras", "name": "RPSC RAS", "difficulty": "Medium", "full_name": "Rajasthan Administrative Service", "tier": "Prelims & Mains", "sections": ["General Studies", "GK", "Raj Special"], "questions": 150, "duration": "150 min"},
                {"id": "wbpsc_wbcs", "name": "WBCS", "difficulty": "Medium", "full_name": "West Bengal Civil Service", "tier": "Prelims & Mains", "sections": ["General Studies", "English", "Bengali", "GK"], "questions": 200, "duration": "150 min"},
                {"id": "tnpsc_group1", "name": "TNPSC Group 1", "difficulty": "Medium", "full_name": "Tamil Nadu Public Service Commission Group 1", "tier": "Prelims & Mains", "sections": ["General Studies", "Aptitude", "TN Special"], "questions": 200, "duration": "180 min"},
                {"id": "kpsc_kas", "name": "KPSC KAS", "difficulty": "Medium", "full_name": "Karnataka Administrative Service", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "KA Special"], "questions": 150, "duration": "120 min"},
                {"id": "mppsc_sse", "name": "MPPSC SSE", "difficulty": "Medium", "full_name": "MP State Service Examination", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "MP Special"], "questions": 150, "duration": "120 min"},
                {"id": "gpsc_class12", "name": "GPSC Class 1 & 2", "difficulty": "Medium", "full_name": "Gujarat Public Service Commission", "tier": "Prelims & Mains", "sections": ["General Studies", "GK", "Gujarat Special"], "questions": 200, "duration": "180 min"},
                {"id": "opsc_ocs", "name": "OPSC OCS", "difficulty": "Medium", "full_name": "Odisha Civil Services", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "Odisha Special"], "questions": 150, "duration": "120 min"},
                {"id": "apsc_cce", "name": "APSC CCE", "difficulty": "Medium", "full_name": "Assam Combined Competitive Exam", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "Assam Special"], "questions": 150, "duration": "120 min"},
                {"id": "cgpsc_sse", "name": "CGPSC SSE", "difficulty": "Medium", "full_name": "Chhattisgarh State Service Examination", "tier": "Prelims & Mains", "sections": ["General Studies", "Aptitude", "CG Special"], "questions": 150, "duration": "120 min"},
                {"id": "jpsc_ccs", "name": "JPSC CCS", "difficulty": "Medium", "full_name": "Jharkhand Combined Civil Services", "tier": "Prelims & Mains", "sections": ["General Studies", "Aptitude", "Jharkhand Special"], "questions": 150, "duration": "120 min"},
                {"id": "ukpsc_pcs", "name": "UKPSC PCS", "difficulty": "Medium", "full_name": "Uttarakhand Public Service Commission", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "UK Special"], "questions": 150, "duration": "120 min"},
                {"id": "hpsc_hcs", "name": "HPSC HCS", "difficulty": "Medium", "full_name": "Haryana Civil Services", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "Haryana Special"], "questions": 100, "duration": "120 min"},
                {"id": "ppsc_pcs", "name": "PPSC PCS", "difficulty": "Medium", "full_name": "Punjab Civil Services", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "Punjab Special"], "questions": 120, "duration": "120 min"},
                {"id": "kpsc_kerala", "name": "Kerala PSC KAS", "difficulty": "Medium", "full_name": "Kerala Administrative Service", "tier": "Prelims & Mains", "sections": ["General Studies", "Aptitude", "Kerala Special"], "questions": 100, "duration": "75 min"},
                {"id": "mpsc_manipur", "name": "Manipur PSC", "difficulty": "Medium", "full_name": "Manipur Civil Services", "tier": "Prelims & Mains", "sections": ["General Studies", "Aptitude", "Manipur Special"], "questions": 120, "duration": "120 min"},
                {"id": "jkpsc_kas", "name": "JKPSC KAS", "difficulty": "Medium", "full_name": "J&K Combined Competitive Services", "tier": "Prelims & Mains", "sections": ["General Studies", "CSAT", "J&K Special"], "questions": 120, "duration": "120 min"},
                {"id": "tnpsc_group2", "name": "TNPSC Group 2", "difficulty": "Medium", "full_name": "Tamil Nadu Public Service Commission Group 2", "tier": "Prelims & Mains", "sections": ["General Studies", "Aptitude", "TN Special"], "questions": 200, "duration": "180 min"},
                {"id": "tpsc_tcs", "name": "TPSC TCS", "difficulty": "Medium", "full_name": "Tripura Civil Services", "tier": "Prelims & Mains", "sections": ["General Studies", "Aptitude", "Tripura Special"], "questions": 100, "duration": "120 min"}
            ]},
            "state_police": {"name": "State Police", "icon": "state_police", "exams": [
                {"id": "up_police", "name": "UP Police", "difficulty": "Easy", "full_name": "UP Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical"], "questions": 160, "duration": "120 min"},
                {"id": "bihar_police", "name": "Bihar Police", "difficulty": "Easy", "full_name": "Bihar Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Hindi"], "questions": 100, "duration": "120 min"},
                {"id": "rajasthan_police", "name": "Rajasthan Police", "difficulty": "Easy", "full_name": "Rajasthan Police Constable & SI", "tier": "CBT", "sections": ["Reasoning", "GK", "Numerical", "Rajasthan GK"], "questions": 150, "duration": "120 min"},
                {"id": "delhi_police", "name": "Delhi Police", "difficulty": "Easy", "full_name": "Delhi Police Constable", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical"], "questions": 100, "duration": "90 min"},
                {"id": "haryana_police", "name": "Haryana Police", "difficulty": "Easy", "full_name": "Haryana Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical"], "questions": 100, "duration": "90 min"},
                {"id": "mp_police", "name": "MP Police", "difficulty": "Easy", "full_name": "MP Police Constable", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical"], "questions": 100, "duration": "120 min"},
                {"id": "maharashtra_police", "name": "Maharashtra Police", "difficulty": "Easy", "full_name": "Maharashtra Police Constable", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Marathi"], "questions": 100, "duration": "90 min"},
                {"id": "punjab_police", "name": "Punjab Police", "difficulty": "Easy", "full_name": "Punjab Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Punjabi"], "questions": 100, "duration": "120 min"},
                {"id": "kerala_police", "name": "Kerala Police", "difficulty": "Easy", "full_name": "Kerala Police Constable", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Malayalam"], "questions": 100, "duration": "75 min"},
                {"id": "karnataka_police", "name": "Karnataka Police", "difficulty": "Easy", "full_name": "Karnataka Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Kannada"], "questions": 100, "duration": "90 min"},
                {"id": "tn_police", "name": "Tamil Nadu Police", "difficulty": "Easy", "full_name": "TN Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Tamil"], "questions": 100, "duration": "90 min"},
                {"id": "telangana_police", "name": "Telangana Police", "difficulty": "Easy", "full_name": "Telangana Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Telugu"], "questions": 100, "duration": "90 min"},
                {"id": "ap_police", "name": "Andhra Pradesh Police", "difficulty": "Easy", "full_name": "AP Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Telugu"], "questions": 100, "duration": "90 min"},
                {"id": "gujarat_police", "name": "Gujarat Police", "difficulty": "Easy", "full_name": "Gujarat Police Constable", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Gujarati"], "questions": 100, "duration": "90 min"},
                {"id": "wb_police", "name": "West Bengal Police", "difficulty": "Easy", "full_name": "WB Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Bengali"], "questions": 100, "duration": "90 min"},
                {"id": "odisha_police", "name": "Odisha Police", "difficulty": "Easy", "full_name": "Odisha Police Constable & SI", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Odia"], "questions": 100, "duration": "90 min"},
                {"id": "jharkhand_police", "name": "Jharkhand Police", "difficulty": "Easy", "full_name": "Jharkhand Police Constable", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Hindi"], "questions": 100, "duration": "90 min"},
                {"id": "chhattisgarh_police", "name": "Chhattisgarh Police", "difficulty": "Easy", "full_name": "CG Police Constable", "tier": "CBT", "sections": ["General Knowledge", "Reasoning", "Numerical", "Hindi"], "questions": 100, "duration": "90 min"}
            ]},
            "state_tet": {"name": "State Teacher Eligibility", "icon": "state_tet", "exams": [
                {"id": "uptet", "name": "UPTET", "difficulty": "Easy", "full_name": "Uttar Pradesh Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Language"], "questions": 150, "duration": "150 min"},
                {"id": "reet", "name": "REET", "difficulty": "Easy", "full_name": "Rajasthan Eligibility Examination for Teachers", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Language"], "questions": 150, "duration": "150 min"},
                {"id": "maha_tet", "name": "MAHA TET", "difficulty": "Easy", "full_name": "Maharashtra Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Language"], "questions": 150, "duration": "150 min"},
                {"id": "tntet", "name": "TNTET", "difficulty": "Easy", "full_name": "Tamil Nadu Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Tamil"], "questions": 150, "duration": "150 min"},
                {"id": "kartet", "name": "KARTET", "difficulty": "Easy", "full_name": "Karnataka Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Kannada"], "questions": 150, "duration": "150 min"},
                {"id": "utet", "name": "UTET", "difficulty": "Easy", "full_name": "Uttarakhand Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Language"], "questions": 150, "duration": "150 min"},
                {"id": "wbtet", "name": "WB TET", "difficulty": "Easy", "full_name": "West Bengal Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Bengali"], "questions": 150, "duration": "150 min"},
                {"id": "mptet", "name": "MP TET", "difficulty": "Easy", "full_name": "Madhya Pradesh Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Hindi"], "questions": 150, "duration": "150 min"},
                {"id": "jtet", "name": "JTET", "difficulty": "Easy", "full_name": "Jharkhand Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Language"], "questions": 150, "duration": "150 min"},
                {"id": "otet", "name": "OTET", "difficulty": "Easy", "full_name": "Odisha Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Odia"], "questions": 150, "duration": "150 min"},
                {"id": "pstet", "name": "PSTET", "difficulty": "Easy", "full_name": "Punjab State Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Punjabi"], "questions": 150, "duration": "150 min"},
                {"id": "hptet", "name": "HP TET", "difficulty": "Easy", "full_name": "Himachal Pradesh Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Language"], "questions": 150, "duration": "150 min"},
                {"id": "aptet", "name": "AP TET", "difficulty": "Easy", "full_name": "Andhra Pradesh Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Telugu"], "questions": 150, "duration": "150 min"},
                {"id": "tstet", "name": "TS TET", "difficulty": "Easy", "full_name": "Telangana State Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Telugu"], "questions": 150, "duration": "150 min"},
                {"id": "ktet", "name": "KTET", "difficulty": "Easy", "full_name": "Kerala Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Malayalam"], "questions": 150, "duration": "150 min"},
                {"id": "assam_tet", "name": "Assam TET", "difficulty": "Easy", "full_name": "Assam Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Assamese"], "questions": 150, "duration": "150 min"},
                {"id": "bihar_tet", "name": "Bihar TET", "difficulty": "Easy", "full_name": "Bihar Teacher Eligibility Test", "tier": "CBT", "sections": ["Child Development", "Math", "EVS", "Hindi"], "questions": 150, "duration": "150 min"}
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
            logger.info(f"bank lookup: {exam_id}/{topic} -> {len(rows)} rows (wanted {count})")
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

    def _fetch_bank_questions(self, exam_id: str, topic: str, count: int) -> List[Dict]:
        """Fetch N bank questions for a single topic. Returns [] on miss/error."""
        conn = None
        try:
            from database import db
            conn = db.get_pooled_connection()
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
            cur.close()
            logger.info(f"bank lookup: {exam_id}/{topic} -> {len(rows)} rows (wanted {count})")
        except Exception as e:
            logger.error(f"_fetch_bank_questions failed: {e}")
            return []
        finally:
            if conn:
                db.release_pooled_connection(conn)
        return [{
            "question_id": r[0],
            "question": r[1],
            "options": r[2] if isinstance(r[2], list) else json.loads(r[2] or "[]"),
            "correct": r[3],
            "explanation": r[4] or "",
            "difficulty": r[5] or "Medium",
        } for r in rows]

    def _fetch_bank_multi(self, exam_id: str, topics: List[str], per_topic: int) -> Dict[str, List[Dict]]:
        """Fetch per_topic questions for EACH topic in ONE DB round trip."""
        if not topics:
            return {}
        conn = None
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT topic, question_id, question_text, options, correct_index,
                       explanation, difficulty
                FROM (
                    SELECT topic, question_id, question_text, options, correct_index,
                           explanation, difficulty,
                           ROW_NUMBER() OVER (PARTITION BY topic ORDER BY RANDOM()) AS rn
                    FROM charvak_exam_question_bank
                    WHERE exam_id = %s AND topic = ANY(%s)
                ) sub
                WHERE rn <= %s
            ''', (exam_id, topics, per_topic))
            rows = cur.fetchall()
            cur.close()
            logger.info(f"bank multi-lookup: {exam_id} topics={topics} -> {len(rows)} rows")
        except Exception as e:
            logger.error(f"_fetch_bank_multi failed: {e}")
            return {}
        finally:
            if conn:
                db.release_pooled_connection(conn)

        grouped = {}
        for r in rows:
            t = r[0]
            grouped.setdefault(t, []).append({
                "question_id": r[1],
                "question": r[2],
                "options": r[3] if isinstance(r[3], list) else json.loads(r[3] or "[]"),
                "correct": r[4],
                "explanation": r[5] or "",
                "difficulty": r[6] or "Medium",
            })
        return grouped

    def _get_exam_difficulty(self, exam_id: str) -> str:
        """Look up difficulty for an exam. Default: Medium."""
        for cat in self.exams.values():
            for e in cat.get("exams", []):
                if e.get("id") == exam_id:
                    return e.get("difficulty", "Medium")
        return "Medium"

    def _generate_via_ai(self, exam_id: str, topic: str, count: int) -> List[Dict]:
        """Generate questions via OpenAI and insert into bank."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            logger.warning("OPENAI_API_KEY missing - returning stub questions")
            return self._stub_questions(exam_id, topic, count)

        exam_name = self._get_exam_name(exam_id)
        difficulty = self._get_exam_difficulty(exam_id)

        # Language-specific hint if topic name is a language
        lang_note = ""
        if topic in LANGUAGE_HINTS:
            lang_name, lang_script = LANGUAGE_HINTS[topic]
            lang_note = (
                f"\nLANGUAGE REQUIREMENT:\n"
                f"- Write ALL questions and ALL 4 options in {lang_script}.\n"
                f"- Do NOT use English text.\n"
                f"- Questions should test {lang_name} literature, grammar, "
                f"vocabulary, and comprehension.\n"
            )
        elif topic == "English":
            lang_note = (
                "\nLANGUAGE REQUIREMENT:\n"
                "- This is an English comprehension/grammar/vocabulary section.\n"
                "- Write questions in English that test English language skills "
                "(reading, grammar, vocabulary, sentence correction).\n"
            )

        # N2.1 — diversity requirements to prevent semantic near-dupes
        diversity_rules = (
            "\nDIVERSITY REQUIREMENTS (CRITICAL):\n"
            "- Each question MUST test a DIFFERENT specific fact, concept, or skill.\n"
            "- Do NOT generate multiple questions testing the same idea with "
            "slightly different wording (e.g., 5 arithmetic series with different numbers).\n"
            "- Aim for coverage of AT LEAST 8 distinct subtopics within the topic.\n"
            "- If the topic is narrow (e.g., 'Bengali Literature'), focus on "
            "different authors, eras, genres, or works.\n"
            "- If you cannot produce all requested questions with true diversity, "
            "produce fewer instead of duplicating.\n"
            "- BAD example: 5 questions all asking 'find next in series X, Y, Z'.\n"
            "- GOOD example: one series, one analogy, one odd-one-out, "
            "one coding, one blood relation, one direction sense.\n"
        )

        prompt = (
            f"You are creating {count} practice questions for the {exam_name} exam.\n"
            f"Topic: {topic}\n"
            f"Difficulty: {difficulty}\n"
            f"{lang_note}"
            f"{diversity_rules}"
            "\nSTRICT RULES:\n"
            "- Return EXACTLY 4 options per question. Never 3. Never 5.\n"
            "- Every question must be UNIQUE - no repeats of the same prompt.\n"
            "- VERIFY that the correct answer appears in the 4 options. If the "
            "correct answer is 30, then 30 MUST be one of the 4 options.\n"
            "- If you cannot produce 4 valid options with the correct answer "
            "included, replace the question with a different one that works.\n"
            "- Return ONLY valid JSON. No markdown, no prose, no code fences.\n\n"
            "Format: an array of objects, each with:\n"
            '{"question": "...", "options": ["...", "...", "...", "..."], '
            '"correct": 0, "explanation": "..."}\n'
            "where 'correct' is the 0-based index of the correct option."
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
        """Start a mock test - batched bank fetch, correct distribution."""
        import time as _t
        _t0 = _t.time()

        try:
            count = max(1, min(int(count), 50))
        except Exception:
            count = 10

        # Resolve sections from catalog
        exam_sections = []
        for cat in self.exams.values():
            for e in cat.get("exams", []):
                if e.get("id") == exam_id:
                    exam_sections = e.get("sections", [])
                    break
            if exam_sections:
                break

        questions = []
        resolved_topic = topic or "Mixed"

        if topic:
            # Caller gave us a topic
            questions = self._fetch_bank_questions(exam_id, topic, count)
            if len(questions) < count:
                needed = count - len(questions)
                fresh = self._generate_via_ai(exam_id, topic, needed)
                questions = (questions + fresh)[:count]
            resolved_topic = topic

        elif exam_sections:
            # Mixed mock - batched query, even distribution
            n = len(exam_sections)
            base = count // n
            remainder = count % n
            per_section = base + (1 if remainder else 0)  # over-fetch for safety

            all_rows = self._fetch_bank_multi(exam_id, exam_sections, per_section)

            for i, sec in enumerate(exam_sections):
                take = base + (1 if i < remainder else 0)
                sec_rows = all_rows.get(sec, [])[:take]
                questions.extend(sec_rows)

            # Top up if bank was short
            if len(questions) < count:
                needed = count - len(questions)
                fresh = self._generate_via_ai(exam_id, exam_sections[0], needed)
                questions = (questions + fresh)[:count]
            resolved_topic = "Mixed"

        else:
            # No sections - fallback
            questions = self._fetch_bank_questions(exam_id, "General", count)
            if len(questions) < count:
                needed = count - len(questions)
                fresh = self._generate_via_ai(exam_id, "General", needed)
                questions = (questions + fresh)[:count]
            resolved_topic = "General"

        questions = questions[:count]
        build_time = _t.time() - _t0
        logger.info(f"start_mock_test: exam={exam_id} topic={resolved_topic} "
                    f"questions={len(questions)} build_time={build_time:.2f}s")

        test_id = f"TEST-{secrets.token_hex(6).upper()}"

        _t1 = _t.time()
        conn = None
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_exam_mock_tests
                    (test_id, email, exam_id, topic, status, total_questions)
                VALUES (%s, %s, %s, %s, 'in_progress', %s)
            ''', (test_id, email, exam_id, resolved_topic, len(questions)))
            conn.commit()
            cur.close()
        except Exception as e:
            logger.error(f"start_mock_test failed: {e}")
            if conn:
                db.release_pooled_connection(conn)
            return {"status": "error", "message": "Could not start mock test"}
        finally:
            if conn:
                db.release_pooled_connection(conn)
        db_time = _t.time() - _t1
        logger.info(f"start_mock_test: DB insert took {db_time:.2f}s")

        return {
            "status": "success",
            "test_id": test_id,
            "exam_id": exam_id,
            "email": email,
            "topic": resolved_topic,
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
