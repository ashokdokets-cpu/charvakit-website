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
        booking_link = f"https://www.charvakit.com/booking/{slug}"

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
            # Ensure new columns exist (auto-create on first use)
            cur.execute("ALTER TABLE charvak_marketing_booking_kits ADD COLUMN IF NOT EXISTS slug TEXT")
            cur.execute("ALTER TABLE charvak_marketing_booking_kits ADD COLUMN IF NOT EXISTS host_email TEXT")
            cur.execute("ALTER TABLE charvak_marketing_booking_kits ADD COLUMN IF NOT EXISTS booking_url TEXT")
            cur.execute("""
                INSERT INTO charvak_marketing_booking_kits
                    (kit_id, email, host_name, business_name, meeting_type,
                     duration_min, context, kit_json, credits_used,
                     slug, host_email, booking_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 60, %s, %s, %s)
            """, (kit_id, email, host_name, business_name, meeting_type,
                  duration_min, context, json.dumps(kit),
                  slug, email, booking_link))
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

    def get_kit_by_slug(self, slug: str) -> Dict:
        """Fetch a booking kit by its slug (public - used by /booking/{slug})."""
        if not slug:
            return {"status": "error", "message": "slug required"}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            # Ensure slug/host_email columns exist
            cur.execute("ALTER TABLE charvak_marketing_booking_kits ADD COLUMN IF NOT EXISTS slug TEXT")
            cur.execute("ALTER TABLE charvak_marketing_booking_kits ADD COLUMN IF NOT EXISTS host_email TEXT")
            cur.execute("ALTER TABLE charvak_marketing_booking_kits ADD COLUMN IF NOT EXISTS booking_url TEXT")
            cur.execute("""
                SELECT kit_id, email, host_name, business_name, meeting_type,
                       duration_min, context, kit_json, slug, booking_url, created_at
                FROM charvak_marketing_booking_kits
                WHERE slug = %s
                LIMIT 1
            """, (slug,))
            row = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_kit_by_slug failed: {e}")
            return {"status": "error", "message": "Could not load booking page"}

        if not row:
            return {"status": "error", "message": "Booking page not found"}

        kit_json = row[7] if isinstance(row[7], dict) else {}
        try:
            if isinstance(row[7], str):
                kit_json = json.loads(row[7])
        except Exception:
            kit_json = {}

        return {
            "status": "success",
            "kit_id": row[0],
            "email": row[1],
            "host_name": row[2],
            "business_name": row[3],
            "meeting_type": row[4],
            "duration_min": row[5],
            "context": row[6],
            "kit": kit_json,
            "slug": row[8],
            "booking_url": row[9],
            "created_at": row[10].isoformat() if hasattr(row[10], "isoformat") else str(row[10]),
        }

    def create_booking_request(self, slug: str, prospect: Dict) -> Dict:
        """
        Save a booking request and email both host + prospect.
        prospect = {name, email, preferred_time, notes}
        """
        import secrets
        if not slug:
            return {"status": "error", "message": "slug required"}
        name = (prospect.get("name") or "").strip()
        pemail = (prospect.get("email") or "").strip().lower()
        preferred = (prospect.get("preferred_time") or "").strip()
        notes = (prospect.get("notes") or "").strip()
        if len(name) < 2:
            return {"status": "error", "message": "Name is required"}
        if "@" not in pemail:
            return {"status": "error", "message": "Valid email is required"}

        kit = self.get_kit_by_slug(slug)
        if kit.get("status") != "success":
            return {"status": "error", "message": "Booking page not found"}

        request_id = f"REQ-{secrets.token_hex(6).upper()}"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_booking_requests (
                    request_id       TEXT PRIMARY KEY,
                    slug             TEXT NOT NULL,
                    kit_id           TEXT NOT NULL,
                    host_email       TEXT NOT NULL,
                    prospect_name    TEXT NOT NULL,
                    prospect_email   TEXT NOT NULL,
                    preferred_time   TEXT,
                    notes            TEXT,
                    status           TEXT NOT NULL DEFAULT 'pending',
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                INSERT INTO charvak_booking_requests
                    (request_id, slug, kit_id, host_email, prospect_name,
                     prospect_email, preferred_time, notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (request_id, slug, kit["kit_id"], kit["email"], name,
                  pemail, preferred, notes))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_booking_request persist failed: {e}")
            return {"status": "error", "message": "Could not save request"}

        # Email host
        try:
            from email_engine import email_engine
            host_subject = f"New booking request from {name}"
            host_body = f"""<h3>New Booking Request</h3>
<p><strong>Request ID:</strong> {request_id}</p>
<p><strong>From:</strong> {name} &lt;{pemail}&gt;</p>
<p><strong>Meeting:</strong> {kit['meeting_type']} ({kit['duration_min']} min)</p>
<p><strong>Preferred time:</strong> {preferred or '(not specified)'}</p>
<p><strong>Notes:</strong></p>
<pre style="white-space:pre-wrap;background:#f5f5f5;padding:12px;border-radius:6px;">{notes or '(none)'}</pre>
<hr>
<p>Reply directly to {pemail} to confirm the time.</p>
"""
            email_engine.send_email(kit["email"], host_subject, host_body)
            print(f"OK: host notification sent to {kit['email']}")
        except Exception as e:
            logger.warning(f"Host email failed (non-fatal): {e}")

        # Email prospect confirmation
        try:
            from email_engine import email_engine
            prospect_subject = f"Your booking request to {kit['business_name']}"
            prospect_body = f"""<p>Hi {name},</p>
<p>Thanks for requesting a {kit['meeting_type']} with {kit['host_name']} from {kit['business_name']}.</p>
<p><strong>Request ID:</strong> {request_id}</p>
<p><strong>Preferred time:</strong> {preferred or '(to be confirmed)'}</p>
<p>{kit['host_name']} will reach out shortly to confirm the exact time.</p>
<p>&mdash; The {kit['business_name']} team</p>
"""
            email_engine.send_email(pemail, prospect_subject, prospect_body)
            print(f"OK: confirmation sent to {pemail}")
        except Exception as e:
            logger.warning(f"Prospect email failed (non-fatal): {e}")

        return {
            "status": "success",
            "request_id": request_id,
            "message": "Request received. The host will confirm shortly.",
        }

    def list_requests_for_email(self, email: str) -> Dict:
        """Return all incoming booking requests for a host."""
        email = (email or "").strip().lower()
        if not email:
            return {"status": "error", "message": "email required"}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT request_id, slug, prospect_name, prospect_email,
                       preferred_time, notes, status, created_at
                FROM charvak_booking_requests
                WHERE host_email = %s
                ORDER BY created_at DESC
                LIMIT 100
            """, (email,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.warning(f"list_requests_for_email failed: {e}")
            return {"status": "success", "email": email, "count": 0, "requests": []}

        return {
            "status": "success",
            "email": email,
            "count": len(rows),
            "requests": [
                {
                    "request_id": r[0],
                    "slug": r[1],
                    "prospect_name": r[2],
                    "prospect_email": r[3],
                    "preferred_time": r[4],
                    "notes": r[5],
                    "status": r[6],
                    "created_at": r[7].isoformat() if hasattr(r[7], "isoformat") else str(r[7]),
                }
                for r in rows
            ],
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