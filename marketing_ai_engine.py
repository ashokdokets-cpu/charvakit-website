"""
Charvak Marketing AI Engine
Inspired by Foundry AI Labs - AI marketing automation
(DB-backed - Session F/3)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.marketingai")


class MarketingAIEngine:
    """AI-powered marketing automation for Charvak (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Marketing AI Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_marketing_job_ads (
                    ad_id       TEXT PRIMARY KEY,
                    job_title   TEXT,
                    company     TEXT,
                    ad_text     TEXT,
                    platforms   JSONB DEFAULT '[]'::jsonb,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_marketing_ads_company ON charvak_marketing_job_ads(company)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_marketing_ads_title   ON charvak_marketing_job_ads(job_title)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_marketing_social_posts (
                    post_id     TEXT PRIMARY KEY,
                    topic       TEXT,
                    platform    TEXT,
                    audience    TEXT,
                    post_text   TEXT,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_marketing_posts_platform ON charvak_marketing_social_posts(platform)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_marketing_lead_drips (
                    drip_id     TEXT PRIMARY KEY,
                    lead_name   TEXT,
                    lead_email  TEXT,
                    service     TEXT,
                    sequence    JSONB DEFAULT '[]'::jsonb,
                    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_marketing_drips_email   ON charvak_marketing_lead_drips(lead_email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_marketing_drips_service ON charvak_marketing_lead_drips(service)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"marketing_ai tables init failed: {e}")

    # ============================================================
    # 1. AI JOB AD GENERATOR
    # ============================================================

    async def generate_job_ad(self, data: Dict) -> Dict:
        """
        Generate professional job ad from basic details.
        data = {job_title, company, location, skills, salary_range}
        """
        ad_id = f"AD-{secrets.token_hex(4).upper()}"

        job_title = data.get("job_title", "Software Engineer")
        company = data.get("company", "Company")
        location = data.get("location", "Remote")
        skills = ", ".join(data.get("skills", []))
        salary = data.get("salary_range", "Competitive")

        ad_text = (
            "\U0001F680 We're Hiring: " + job_title + " at " + company + "!\n\n"
            "\U0001F4CD Location: " + location + "\n"
            "\U0001F4B0 Salary: " + salary + "\n\n"
            "\u2728 What You'll Do:\n"
            "\u2022 Build innovative solutions using " + skills + "\n"
            "\u2022 Collaborate with a world-class team\n"
            "\u2022 Make real impact from day one\n\n"
            "\U0001F3AF What We're Looking For:\n"
            "\u2022 Strong skills in " + skills + "\n"
            "\u2022 Problem-solving mindset\n"
            "\u2022 Passion for technology\n\n"
            "\U0001F31F Why Join Us:\n"
            "\u2022 AI-powered work environment\n"
            "\u2022 Growth opportunities\n"
            "\u2022 Inclusive culture (34 languages!)\n\n"
            "\U0001F449 Apply now: https://charvakit.com/job-board\n\n"
            "#Hiring #" + job_title.replace(' ', '') + " #" + company.replace(' ', '') + " #TechJobs\n"
        )

        platforms = ["LinkedIn", "Twitter", "WhatsApp"]

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_marketing_job_ads
                    (ad_id, job_title, company, ad_text, platforms)
                VALUES (%s, %s, %s, %s, %s::jsonb)
            ''', (ad_id, job_title, company, ad_text, json.dumps(platforms)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"generate_job_ad write failed: {e}")

        return {
            "status": "success",
            "ad_id": ad_id,
            "ad_text": ad_text,
            "message": "Job ad generated! Ready to post.",
            "suggested_platforms": ["LinkedIn", "Twitter/X", "WhatsApp"],
        }

    # ============================================================
    # 2. SOCIAL MEDIA POST GENERATOR
    # ============================================================

    async def generate_social_post(self, data: Dict) -> Dict:
        """
        Generate platform-specific social media posts.
        data = {topic, tone, platform, audience}
        """
        post_id = f"POST-{secrets.token_hex(4).upper()}"
        topic = data.get("topic", "AI in Hiring")
        platform = data.get("platform", "linkedin").lower()
        audience = data.get("audience", "employers")

        linkedin_employers = (
            "\U0001F4BC " + topic + ": The future of work is AI-powered.\n\n"
            "At Charvak, we're helping companies hire smarter with:\n"
            "\u2705 AI-verified candidates\n"
            "\u2705 48-hour placement\n"
            "\u2705 90% cost reduction\n\n"
            "Learn more: https://charvakit.com/for-employers\n\n"
            "#AI #Hiring #FutureOfWork"
        )
        linkedin_candidates = (
            "\U0001F3AF " + topic + ": Your career deserves better.\n\n"
            "Join Charvak's global talent pool:\n"
            "\u2705 Free skill verification\n"
            "\u2705 Verified badges\n"
            "\u2705 Jobs in 50+ countries\n\n"
            "Start now: https://charvakit.com/candidate-signup\n\n"
            "#CareerGrowth #TechJobs #AI"
        )
        twitter_employers = (
            "Stop paying 20% agency fees.\n\n"
            "Charvak: 2% success fee + 48hr hiring + AI-verified talent.\n\n"
            "https://charvakit.com/for-employers\n\n"
            "#hiring #startup"
        )
        twitter_candidates = (
            "Your resume lies. Your skills don't.\n\n"
            "Get AI-verified in 10 min. Free.\n\n"
            "https://charvakit.com/candidate-signup\n\n"
            "#jobsearch #career"
        )
        whatsapp_employers = (
            "\U0001F3E2 Hiring? Charvak offers 2% fee (vs 20% agencies), "
            "48hr placement, AI-verified candidates.\n\n"
            "Post free: https://charvakit.com/post-job"
        )
        whatsapp_candidates = (
            "\U0001F3AF Free skill check + verified badge + 48hr job matching!\n\n"
            "Join: https://charvakit.com/candidate-signup"
        )

        templates = {
            "linkedin": {"employers": linkedin_employers, "candidates": linkedin_candidates},
            "twitter":  {"employers": twitter_employers,  "candidates": twitter_candidates},
            "whatsapp": {"employers": whatsapp_employers, "candidates": whatsapp_candidates},
        }

        post_text = templates.get(platform, templates["linkedin"]).get(audience, linkedin_employers)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_marketing_social_posts
                    (post_id, topic, platform, audience, post_text)
                VALUES (%s, %s, %s, %s, %s)
            ''', (post_id, topic, platform, audience, post_text))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"generate_social_post write failed: {e}")

        return {
            "status": "success",
            "post_id": post_id,
            "post_text": post_text,
            "platform": platform,
            "message": f"{platform} post generated for {audience}!",
        }

    # ============================================================
    # 3. LEAD DRIP SEQUENCE
    # ============================================================

    async def create_lead_drip(self, data: Dict) -> Dict:
        """
        Create automated lead nurture sequence.
        data = {lead_name, lead_email, service_interest}
        """
        drip_id = f"DRIP-{secrets.token_hex(4).upper()}"
        service = data.get("service_interest", "IT Staffing")
        lead_name = data.get("lead_name")
        lead_email = data.get("lead_email")

        drip_sequence = [
            {"day": 0, "channel": "email",
             "message": f"Hi {lead_name}, thanks for your interest in {service}! We'll reach out within 24 hours."},
            {"day": 1, "channel": "whatsapp",
             "message": f"Hi {lead_name}, this is Charvak. Ready to discuss your {service} needs?"},
            {"day": 3, "channel": "email",
             "message": f"Quick follow-up: Charvak can save you 90% on {service}. Want to see how?"},
            {"day": 7, "channel": "email",
             "message": f"Last follow-up: Ready to transform your {service}? Book a call: https://charvakit.com/contact"},
        ]

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_marketing_lead_drips
                    (drip_id, lead_name, lead_email, service, sequence)
                VALUES (%s, %s, %s, %s, %s::jsonb)
            ''', (drip_id, lead_name, lead_email, service, json.dumps(drip_sequence)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_lead_drip write failed: {e}")

        return {
            "status": "success",
            "drip_id": drip_id,
            "sequence": drip_sequence,
            "message": f"Lead drip created for {lead_name}!",
        }

    # ============================================================
    # 4. CALENDAR BOOKING (stateless)
    # ============================================================

    async def generate_booking_link(self, data: Dict) -> Dict:
        """
        Generate calendar booking link for demo/meeting.
        data = {host_name, meeting_type, duration}
        """
        booking_id = f"BOOK-{secrets.token_hex(4).upper()}"
        meeting_type = data.get("meeting_type", "Demo")

        return {
            "status": "success",
            "booking_id": booking_id,
            "booking_link": f"https://charvakit.com/contact?booking={booking_id}",
            "meeting_type": meeting_type,
            "message": "Booking link ready! Share with clients.",
        }

    def get_stats(self) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_marketing_job_ads')
            job_ads = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COUNT(*) FROM charvak_marketing_social_posts')
            social_posts = int(cur.fetchone()[0] or 0)
            cur.execute('SELECT COUNT(*) FROM charvak_marketing_lead_drips')
            lead_drips = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "job_ads_generated": job_ads,
                "social_posts_generated": social_posts,
                "lead_drips_created": lead_drips,
            },
        }


marketing_ai_engine = MarketingAIEngine()