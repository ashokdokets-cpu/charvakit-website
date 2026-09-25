"""
Voice-to-Web Pro Engine
Complete management for Pro features: Custom domain, No branding, AI SEO, Updates, Priority Support
(DB-backed - Session C2, 2026-09-25)
"""
import json
import logging
from datetime import datetime
from typing import Dict, Optional, List

logger = logging.getLogger("charvakit.voice_to_web")


class VoiceToWebEngine:
    def __init__(self):
        self._ensure_tables()
        logger.info("Voice-to-Web Pro Engine ready (DB-backed)")

    # ============================================================
    # TABLE INIT (idempotent — mirrors migrations/20260925_voice_to_web.sql)
    # ============================================================

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_voice_to_web_sites (
                    website_id       TEXT PRIMARY KEY,
                    email            TEXT NOT NULL,
                    business_name    TEXT NOT NULL,
                    plan             TEXT DEFAULT 'free',
                    transcript       TEXT DEFAULT '',
                    custom_domain    TEXT,
                    branding         TEXT DEFAULT 'charvak',
                    seo_enabled      BOOLEAN DEFAULT FALSE,
                    updates_enabled  BOOLEAN DEFAULT FALSE,
                    priority_support BOOLEAN DEFAULT FALSE,
                    status           TEXT DEFAULT 'live',
                    url              TEXT,
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_v2w_sites_email ON charvak_voice_to_web_sites(email)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_v2w_sites_plan  ON charvak_voice_to_web_sites(plan)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_voice_to_web_domains (
                    website_id     TEXT PRIMARY KEY REFERENCES charvak_voice_to_web_sites(website_id) ON DELETE CASCADE,
                    domain         TEXT NOT NULL,
                    status         TEXT DEFAULT 'pending_setup',
                    dns_configured BOOLEAN DEFAULT FALSE,
                    ssl_active     BOOLEAN DEFAULT FALSE,
                    setup_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_voice_to_web_updates (
                    update_id            TEXT PRIMARY KEY,
                    website_id           TEXT NOT NULL REFERENCES charvak_voice_to_web_sites(website_id) ON DELETE CASCADE,
                    type                 TEXT,
                    details              TEXT,
                    email                TEXT DEFAULT '',
                    status               TEXT DEFAULT 'queued',
                    priority             TEXT DEFAULT 'normal',
                    requested_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    estimated_completion TEXT DEFAULT '24 hours'
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_v2w_updates_site ON charvak_voice_to_web_updates(website_id)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_voice_to_web_tickets (
                    ticket_id     TEXT PRIMARY KEY,
                    email         TEXT NOT NULL,
                    issue         TEXT NOT NULL,
                    website_id    TEXT REFERENCES charvak_voice_to_web_sites(website_id) ON DELETE SET NULL,
                    priority      TEXT DEFAULT 'normal',
                    status        TEXT DEFAULT 'open',
                    response_time TEXT DEFAULT '24 hours',
                    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_v2w_tickets_site  ON charvak_voice_to_web_tickets(website_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_v2w_tickets_email ON charvak_voice_to_web_tickets(email)''')

            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_voice_to_web_seo (
                    website_id       TEXT PRIMARY KEY REFERENCES
charvak_voice_to_web_sites(website_id) ON DELETE CASCADE,
                    meta_title       TEXT,
                    meta_description TEXT,
                    keywords         JSONB DEFAULT '[]'::jsonb,
                    og_tags          BOOLEAN DEFAULT TRUE,
                    twitter_cards    BOOLEAN DEFAULT TRUE,
                    sitemap          BOOLEAN DEFAULT TRUE,
                    robots_txt       BOOLEAN DEFAULT TRUE,
                    structured_data  JSONB DEFAULT '{}'::jsonb,
                    enabled_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Option 2: store generated HTML + slug (idempotent)
            cur.execute('''ALTER TABLE charvak_voice_to_web_sites
                ADD COLUMN IF NOT EXISTS html_content TEXT''')
            cur.execute('''ALTER TABLE charvak_voice_to_web_sites
                ADD COLUMN IF NOT EXISTS slug TEXT''')
            cur.execute('''CREATE UNIQUE INDEX IF NOT EXISTS idx_v2w_sites_slug
                ON charvak_voice_to_web_sites(slug) WHERE slug IS NOT NULL''')

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"voice_to_web tables init failed: {e}")

    # ============================================================
    # WEBSITES
    # ============================================================


    def create_website(self, email: str, business_name: str, plan: str = "free",
                       transcript: str = "", html_content: str = "") -> Dict:
        """Create website from voice data. Stores generated HTML + slug."""
        import re
        website_id = f"V2W-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        is_pro = plan == "pro"

        # Build a human-readable, collision-safe slug from business_name.
        base = re.sub(r'[^a-z0-9]+', '-', (business_name or '').lower()).strip('-') or 'site'
        base = base[:60]

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            slug = base
            n = 1
            while True:
                cur.execute(
                    "SELECT 1 FROM charvak_voice_to_web_sites WHERE slug = %s",
                    (slug,),
                )
                if not cur.fetchone():
                    break
                n += 1
                slug = f"{base}-{n}"

            url = f"/sites/{slug}"

            cur.execute('''
                INSERT INTO charvak_voice_to_web_sites
                    (website_id, email, business_name, plan, transcript,
                     custom_domain, branding, seo_enabled, updates_enabled,
                     priority_support, status, url, html_content, slug)
                VALUES (%s, %s, %s, %s, %s, NULL, %s, %s, %s, %s, 'live', %s, %s, %s)
            ''', (
                website_id, email, business_name, plan, transcript,
                "none" if is_pro else "charvak",
                is_pro, is_pro, is_pro, url, html_content, slug,
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_website failed: {e}")
            return {"status": "error", "message": "Could not create website"}

        return {
            "status": "success",
            "website_id": website_id,
            "slug": slug,
            "url": url,
            "message": f"Website created for {business_name}",
        }

    # ============================================================
    # CUSTOM DOMAINS
    # ============================================================

    def setup_custom_domain(self, website_id: str, domain: str) -> Dict:
        """Setup custom domain for Pro users."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT plan FROM charvak_voice_to_web_sites WHERE website_id = %s
            ''', (website_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Website not found"}
            # Credits charged by the route. No plan gate.

            cur.execute('''
                INSERT INTO charvak_voice_to_web_domains
                    (website_id, domain, status, dns_configured, ssl_active)
                VALUES (%s, %s, 'pending_setup', FALSE, FALSE)
                ON CONFLICT (website_id) DO UPDATE
                SET domain = EXCLUDED.domain,
                    status = 'pending_setup',
                    dns_configured = FALSE,
                    ssl_active = FALSE,
                    setup_at = CURRENT_TIMESTAMP
            ''', (website_id, domain))

            cur.execute('''
                UPDATE charvak_voice_to_web_sites
                SET custom_domain = %s, url = %s
                WHERE website_id = %s
            ''', (domain, f"https://{domain}", website_id))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"setup_custom_domain failed: {e}")
            return {"status": "error", "message": "Could not setup domain"}

        return {
            "status": "success",
            "domain": domain,
            "dns_instructions": [
                f"1. Login to your domain registrar ({domain.split('.')[-1]})",
                f"2. Add CNAME record: www -> charvakit.com",
                f"3. Add A record: @ -> 76.76.21.21",
                "4. Wait for DNS propagation (up to 24 hours)",
            ],
            "message": f"Custom domain {domain} setup initiated",
        }

    # ============================================================
    # AI SEO
    # ============================================================

    def enable_ai_seo(self, website_id: str, business_name: str, description: str = "") -> Dict:
        """Enable AI SEO for Pro users."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT plan FROM charvak_voice_to_web_sites WHERE website_id = %s
            ''', (website_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Website not found"}
            # Credits charged by the route. No plan gate.

            meta_title = f"{business_name} - Professional Services"
            meta_description = (
                description[:160] if description
                else f"{business_name} - Professional services. Contact us today!"
            )
            keywords = [business_name, "services", "business", "professional"]
            structured_data = {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": business_name,
            }

            cur.execute('''
                INSERT INTO charvak_voice_to_web_seo
                    (website_id, meta_title, meta_description, keywords,
                     og_tags, twitter_cards, sitemap, robots_txt, structured_data)
                VALUES (%s, %s, %s, %s::jsonb, TRUE, TRUE, TRUE, TRUE, %s::jsonb)
                ON CONFLICT (website_id) DO UPDATE
                SET meta_title = EXCLUDED.meta_title,
                    meta_description = EXCLUDED.meta_description,
                    keywords = EXCLUDED.keywords,
                    structured_data = EXCLUDED.structured_data,
                    enabled_at = CURRENT_TIMESTAMP
            ''', (
                website_id, meta_title, meta_description,
                json.dumps(keywords), json.dumps(structured_data),
            ))

            cur.execute('''
                UPDATE charvak_voice_to_web_sites
                SET seo_enabled = TRUE
                WHERE website_id = %s
            ''', (website_id,))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"enable_ai_seo failed: {e}")
            return {"status": "error", "message": "Could not enable SEO"}

        return {
            "status": "success",
            "seo_config": {
                "meta_title": meta_title,
                "meta_description": meta_description,
                "keywords": keywords,
                "og_tags": True,
                "twitter_cards": True,
                "sitemap": True,
                "robots_txt": True,
                "structured_data": structured_data,
            },
            "message": "AI SEO enabled for your website",
        }

    # ============================================================
    # UPDATES
    # ============================================================

    def request_update(self, website_id: str, update_type: str, details: str, email: str = "") -> Dict:
        """Request on-demand update for Pro users."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT plan FROM charvak_voice_to_web_sites WHERE website_id = %s
            ''', (website_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Website not found"}
            # Credits charged by the route. No plan gate.

            update_id = f"UPD-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

            cur.execute('''
                INSERT INTO charvak_voice_to_web_updates
                    (update_id, website_id, type, details, email,
                     status, priority, estimated_completion)
                VALUES (%s, %s, %s, %s, %s, 'queued', 'high', '24 hours')
            ''', (update_id, website_id, update_type, details, email))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"request_update failed: {e}")
            return {"status": "error", "message": "Could not queue update"}

        return {
            "status": "success",
            "update_id": update_id,
            "message": "Update requested. Estimated completion: 24 hours",
        }

    # ============================================================
    # SUPPORT TICKETS
    # ============================================================

    def create_support_ticket(self, email: str, issue: str, website_id: str = None) -> Dict:
        """Create priority support ticket for Pro users."""
        is_priority = False
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            if website_id:
                cur.execute('''
                    SELECT plan FROM charvak_voice_to_web_sites WHERE website_id = %s
                ''', (website_id,))
                row = cur.fetchone()
                is_priority = bool(row and row[0] == "pro")

            ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            priority = "high" if is_priority else "normal"
            response_time = "1 hour" if is_priority else "24 hours"

            cur.execute('''
                INSERT INTO charvak_voice_to_web_tickets
                    (ticket_id, email, issue, website_id, priority, status, response_time)
                VALUES (%s, %s, %s, %s, %s, 'open', %s)
            ''', (ticket_id, email, issue, website_id, priority, response_time))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_support_ticket failed: {e}")
            return {"status": "error", "message": "Could not create ticket"}

        return {
            "status": "success",
            "ticket_id": ticket_id,
            "response_time": "1 hour" if is_priority else "24 hours",
            "message": f"Support ticket created. Response within { '1 hour' if is_priority else '24 hours' }",
        }

    # ============================================================
    # READS
    # ============================================================

    def get_website_status(self, website_id: str) -> Dict:
        """Get website status."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT website_id, email, business_name, plan, transcript,
                       custom_domain, branding, seo_enabled, updates_enabled,
                       priority_support, status, url, created_at
                FROM charvak_voice_to_web_sites WHERE website_id = %s
            ''', (website_id,))
            w = cur.fetchone()
            if not w:
                cur.close(); conn.close()
                return {"status": "error", "message": "Website not found"}

            website = {
                "website_id": w[0], "email": w[1], "business_name": w[2],
                "plan": w[3], "transcript": w[4], "custom_domain": w[5],
                "branding": w[6], "seo_enabled": w[7], "updates_enabled": w[8],
                "priority_support": w[9], "status": w[10], "url": w[11],
                "created_at": w[12].isoformat() if w[12] else None,
            }

            cur.execute('''
                SELECT domain, status, dns_configured, ssl_active, setup_at
                FROM charvak_voice_to_web_domains WHERE website_id = %s
            ''', (website_id,))
            d = cur.fetchone()
            domain = {
                "domain": d[0], "status": d[1], "dns_configured": d[2],
                "ssl_active": d[3],
                "setup_at": d[4].isoformat() if d[4] else None,
            } if d else None

            cur.execute('''
                SELECT meta_title, meta_description, keywords, og_tags,
                       twitter_cards, sitemap, robots_txt, structured_data, enabled_at
                FROM charvak_voice_to_web_seo WHERE website_id = %s
            ''', (website_id,))
            s = cur.fetchone()
            if s:
                seo = {
                    "meta_title": s[0], "meta_description": s[1],
                    "keywords": s[2] if isinstance(s[2], list) else json.loads(s[2] or "[]"),
                    "og_tags": s[3], "twitter_cards": s[4],
                    "sitemap": s[5], "robots_txt": s[6],
                    "structured_data": s[7] if isinstance(s[7], dict) else json.loads(s[7] or "{}"),
                    "enabled_at": s[8].isoformat() if s[8] else None,
                }
            else:
                seo = {"enabled": website["seo_enabled"]}

            cur.execute('''
                SELECT update_id, type, details, email, status, priority,
                       requested_at, estimated_completion
                FROM charvak_voice_to_web_updates
                WHERE website_id = %s ORDER BY requested_at DESC
            ''', (website_id,))
            updates = [
                {
                    "update_id": u[0], "type": u[1], "details": u[2],
                    "email": u[3], "status": u[4], "priority": u[5],
                    "requested_at": u[6].isoformat() if u[6] else None,
                    "estimated_completion": u[7],
                }
                for u in cur.fetchall()
            ]

            cur.execute('''
                SELECT ticket_id, email, issue, priority, status, response_time, created_at
                FROM charvak_voice_to_web_tickets
                WHERE website_id = %s ORDER BY created_at DESC
            ''', (website_id,))
            tickets = [
                {
                    "ticket_id": t[0], "email": t[1], "issue": t[2],
                    "priority": t[3], "status": t[4], "response_time": t[5],
                    "created_at": t[6].isoformat() if t[6] else None,
                }
                for t in cur.fetchall()
            ]

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_website_status failed: {e}")
            return {"status": "error", "message": "Could not load website"}

        return {
            "status": "success",
            "website": website,
            "domain": domain,
            "seo": seo,
            "updates": updates,
            "support_tickets": tickets,
        }

    def get_stats(self) -> Dict:
        """Get engine statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_voice_to_web_sites')
            total_websites = int(cur.fetchone()[0] or 0)

            cur.execute('''SELECT COUNT(*) FROM charvak_voice_to_web_sites WHERE plan = 'pro' ''')
            pro_websites = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_voice_to_web_domains')
            custom_domains = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_voice_to_web_updates')
            total_updates = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_voice_to_web_tickets')
            support_tickets = int(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "total_websites": total_websites,
            "pro_websites": pro_websites,
            "custom_domains": custom_domains,
            "total_updates": total_updates,
            "support_tickets": support_tickets,
        }


voice_to_web_engine = VoiceToWebEngine()