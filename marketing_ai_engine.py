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

    async def generate_booking_kit(self, data: Dict) -> Dict:
        """
        AI-generated outreach kit for a demo/meeting.

        Replaces the previous stub generate_booking_link which returned
        a random ID and a static URL with no real value.

        data = {email, host_name, business_name, meeting_type,
                duration_min, context}
        """
        import json, secrets
        from datetime import datetime

        email = (data.get("email") or "").strip().lower()
        host_name = (data.get("host_name") or "").strip()
        business_name = (data.get("business_name") or "").strip()
        meeting_type = data.get("meeting_type", "Demo")
        duration_min = int(data.get("duration_min") or 30)
        context = (data.get("context") or "").strip()

        if not email:
            return {"status": "error", "message": "email required"}
        if not host_name or not business_name:
            return {"status": "error", "message": "host_name and business_name required"}

        # Generate the slug from business name + random suffix
        slug_base = "".join(c if c.isalnum() else "-" for c in business_name.lower())[:30].strip("-")
        slug = f"{slug_base}-{secrets.token_hex(3)}" if slug_base else secrets.token_hex(6)
        booking_link = f"https://www.charvakit.com/contact?ref={slug}"

        prompt = f"""You are a B2B sales copywriter. Build a personalized outreach kit for a meeting.

Host: {host_name}
Business: {business_name}
Meeting Type: {meeting_type}
Duration: {duration_min} minutes
Context: {context or '(general demo)'}

Return STRICT JSON:
{{
  "value_proposition": "one sentence pitch tailored to this meeting",
  "email_draft": "short cold outreach email (under 120 words), ends with a call to book",
  "linkedin_message": "LinkedIn connection message (under 300 chars)",
  "whatsapp_message": "WhatsApp message (under 200 chars, more casual)",
  "meeting_agenda": [
    {{"minute": 0, "topic": "Welcome + context"}},
    {{"minute": 5, "topic": "..."}}
  ],
  "follow_up_sequence": [
    {{"timing": "Day -1", "channel": "email", "subject": "...", "body": "..."}},
    {{"timing": "Day 0", "channel": "whatsapp", "message": "..."}},
    {{"timing": "Day +1", "channel": "email", "subject": "...", "body": "..."}}
  ],
  "objection_handlers": [
    {{"objection": "...", "response": "..."}}
  ]
}}
Only return the JSON."""

        try:
            from openai import OpenAI
            import os
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.4,
                timeout=45,
            )
            raw = resp.choices[0].message.content or "{}"
            if raw.startswith("```"):
                raw = raw.strip("`")
                if raw.startswith("json\n"):
                    raw = raw[5:]
            kit = json.loads(raw)
        except Exception as e:
            logger.warning(f"generate_booking_kit AI call failed: {e}")
            kit = {
                "value_proposition": f"Personalized {meeting_type} for {business_name}.",
                "email_draft": f"Hi,\n\n{host_name} here from {business_name}. I'd love to show you how we can help. Would a {duration_min}-minute {meeting_type} work?\n\nBook: {booking_link}",
                "linkedin_message": f"Hi! {host_name} from {business_name}. Would love to share something that might help. Open to a quick {meeting_type}?",
                "whatsapp_message": f"Hi! {host_name} here from {business_name}. Free for a quick {duration_min}-min {meeting_type}? {booking_link}",
                "meeting_agenda": [
                    {"minute": 0, "topic": "Welcome + context setting"},
                    {"minute": 5, "topic": "Problem exploration"},
                    {"minute": 15, "topic": "Solution walkthrough"},
                    {"minute": 25, "topic": "Q&A + next steps"}
                ],
                "follow_up_sequence": [
                    {"timing": "Day -1", "channel": "email", "subject": f"Reminder: our {meeting_type} tomorrow", "body": "Looking forward to speaking. Join link in the original invite."},
                    {"timing": "Day 0", "channel": "whatsapp", "message": "Ready when you are!"},
                    {"timing": "Day +1", "channel": "email", "subject": "Thanks for the chat", "body": "Great speaking. Here's a quick summary + next steps."}
                ],
                "objection_handlers": [
                    {"objection": "No time right now", "response": "Totally understand. Would 3 weeks out work better?"},
                    {"objection": "We already have a solution", "response": "Great — happy to compare notes. Many teams use us alongside existing tools."}
                ]
            }

        kit_id = f"KIT-{secrets.token_hex(6).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_marketing_booking_kits (
                    kit_id         TEXT PRIMARY KEY,
                    email          TEXT NOT NULL,
                    host_name      TEXT,
                    business_name  TEXT,
                    meeting_type   TEXT,
                    duration_min   INTEGER,
                    context        TEXT,
                    kit_json       JSONB,
                    credits_used   INTEGER NOT NULL DEFAULT 0,
                    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                INSERT INTO charvak_marketing_booking_kits
                    (kit_id, email, host_name, business_name, meeting_type,
                     duration_min, context, kit_json, credits_used)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 60)
            """, (kit_id, email, host_name, business_name, meeting_type,
                  duration_min, context, json.dumps(kit)))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"generate_booking_kit persist failed: {e}")

        return {
            "status": "success",
            "kit_id": kit_id,
            "booking_link": booking_link,
            "booking_slug": slug,
            "host_name": host_name,
            "business_name": business_name,
            "meeting_type": meeting_type,
            "duration_min": duration_min,
            **kit,
        }

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