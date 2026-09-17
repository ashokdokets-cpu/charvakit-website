"""
Charvak Brand Engine
Company brand pages, reviews, promoted jobs
(DB-backed - Session D/2)
"""
import json
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.brand")


class BrandEngine:
    """Company brand pages and employer reviews (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Brand Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_brands (
                    brand_id        TEXT PRIMARY KEY,
                    company_name    TEXT,
                    industry        TEXT DEFAULT '',
                    description     TEXT DEFAULT '',
                    logo_url        TEXT DEFAULT '',
                    website         TEXT DEFAULT '',
                    location        TEXT DEFAULT '',
                    size            TEXT DEFAULT '',
                    culture_tags    JSONB DEFAULT '[]'::jsonb,
                    average_rating  NUMERIC(3,1) DEFAULT 0,
                    review_count    INTEGER DEFAULT 0,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_brands_company  ON charvak_brands(company_name)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_brands_industry ON charvak_brands(industry)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_brand_reviews (
                    review_id        TEXT PRIMARY KEY,
                    company_id       TEXT NOT NULL,
                    reviewer_name    TEXT,
                    reviewer_type    TEXT DEFAULT 'candidate',
                    rating           INTEGER DEFAULT 5,
                    title            TEXT DEFAULT '',
                    review           TEXT DEFAULT '',
                    would_recommend  BOOLEAN DEFAULT TRUE,
                    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_brand_reviews_company ON charvak_brand_reviews(company_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_brand_reviews_rating  ON charvak_brand_reviews(rating)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_brand_promoted_jobs (
                    promotion_id  TEXT PRIMARY KEY,
                    job_id        TEXT,
                    company_id    TEXT,
                    starts_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ends_at       TIMESTAMP,
                    views         INTEGER DEFAULT 0,
                    clicks        INTEGER DEFAULT 0
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_brand_promos_company ON charvak_brand_promoted_jobs(company_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_brand_promos_job     ON charvak_brand_promoted_jobs(job_id)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"brand tables init failed: {e}")

    # ============================================================
    # BRAND PAGES
    # ============================================================

    def create_brand_page(self, data: Dict) -> Dict:
        """Create a company brand page."""
        brand_id = f"BRAND-{secrets.token_hex(4).upper()}"

        company = {
            "brand_id": brand_id,
            "company_name": data.get("company_name"),
            "industry": data.get("industry", ""),
            "description": data.get("description", ""),
            "logo_url": data.get("logo_url", ""),
            "website": data.get("website", ""),
            "location": data.get("location", ""),
            "size": data.get("size", ""),
            "culture_tags": data.get("culture_tags", []),
            "average_rating": 0,
            "review_count": 0,
            "created_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_brands
                    (brand_id, company_name, industry, description, logo_url,
                     website, location, size, culture_tags, average_rating, review_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, 0, 0)
            ''', (
                brand_id, company["company_name"], company["industry"],
                company["description"], company["logo_url"], company["website"],
                company["location"], company["size"], json.dumps(company["culture_tags"]),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_brand_page failed: {e}")
            return {"status": "error", "message": "Could not create brand page"}

        logger.info(f"Brand page created: {brand_id} - {data.get('company_name')}")

        return {
            "status": "success",
            "brand_id": brand_id,
            "message": "Brand page created!",
            "brand_url": f"https://charvakit.com/companies/{brand_id}",
        }

    # ============================================================
    # REVIEWS
    # ============================================================

    def post_review(self, data: Dict) -> Dict:
        """Post an employer review (updates brand's aggregate rating)."""
        review_id = f"REV-{secrets.token_hex(4).upper()}"
        company_id = data.get("company_id")

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_brand_reviews
                    (review_id, company_id, reviewer_name, reviewer_type,
                     rating, title, review, would_recommend)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                review_id, company_id, data.get("reviewer_name"),
                data.get("reviewer_type", "candidate"),
                int(data.get("rating", 5)),
                data.get("title", ""),
                data.get("review", ""),
                bool(data.get("would_recommend", True)),
            ))

            cur.execute('''
                UPDATE charvak_brands SET
                    review_count = review_count + 1,
                    average_rating = COALESCE(
                        (SELECT ROUND(AVG(rating)::numeric, 1)
                         FROM charvak_brand_reviews WHERE company_id = %s),
                        0
                    )
                WHERE brand_id = %s
            ''', (company_id, company_id))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"post_review failed: {e}")
            return {"status": "error", "message": "Could not post review"}

        logger.info(f"Review posted: {review_id}")

        return {"status": "success", "review_id": review_id, "message": "Review posted!"}

    # ============================================================
    # BRAND PAGE READ
    # ============================================================

    def get_brand_page(self, brand_id: str) -> Dict:
        """Get company brand page with reviews."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT brand_id, company_name, industry, description, logo_url,
                       website, location, size, culture_tags, average_rating,
                       review_count, created_at
                FROM charvak_brands WHERE brand_id = %s
            ''', (brand_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Company not found"}

            def _d(x, default):
                if isinstance(x, type(default)) or x is None:
                    return x if x is not None else default
                try:
                    return json.loads(x)
                except Exception:
                    return default

            company = {
                "brand_id": row[0],
                "company_name": row[1],
                "industry": row[2] or "",
                "description": row[3] or "",
                "logo_url": row[4] or "",
                "website": row[5] or "",
                "location": row[6] or "",
                "size": row[7] or "",
                "culture_tags": _d(row[8], []),
                "average_rating": float(row[9]) if row[9] is not None else 0,
                "review_count": row[10],
                "created_at": row[11].isoformat() if hasattr(row[11], "isoformat") else str(row[11]),
            }

            cur.execute('''
                SELECT review_id, company_id, reviewer_name, reviewer_type,
                       rating, title, review, would_recommend, created_at
                FROM charvak_brand_reviews
                WHERE company_id = %s
                ORDER BY created_at DESC
            ''', (brand_id,))
            review_rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_brand_page failed: {e}")
            return {"status": "error", "message": "Could not load company"}

        company_reviews = [{
            "review_id": r[0],
            "company_id": r[1],
            "reviewer_name": r[2],
            "reviewer_type": r[3],
            "rating": r[4],
            "title": r[5] or "",
            "review": r[6] or "",
            "would_recommend": bool(r[7]),
            "created_at": r[8].isoformat() if hasattr(r[8], "isoformat") else str(r[8]),
        } for r in review_rows]

        recommendation_rate = (
            len([r for r in company_reviews if r["would_recommend"]]) / len(company_reviews) * 100
            if company_reviews else 0
        )

        return {
            "status": "success",
            "company": company,
            "reviews": company_reviews,
            "review_count": len(company_reviews),
            "recommendation_rate": recommendation_rate,
        }

    # ============================================================
    # PROMOTED JOBS
    # ============================================================

    def promote_job(self, job_id: str, company_id: str) -> Dict:
        """Promote a job posting."""
        promotion_id = f"PROMO-{secrets.token_hex(4).upper()}"
        ends_at = datetime.now() + timedelta(days=7)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_brand_promoted_jobs
                    (promotion_id, job_id, company_id, ends_at)
                VALUES (%s, %s, %s, %s)
            ''', (promotion_id, job_id, company_id, ends_at))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"promote_job failed: {e}")
            return {"status": "error", "message": "Could not promote job"}

        return {
            "status": "success",
            "promotion_id": promotion_id,
            "message": "Job promoted! It will appear in candidate feeds.",
            "duration": "7 days",
        }

    # ============================================================
    # LISTS + STATS
    # ============================================================

    def get_all_brands(self) -> Dict:
        """Get all company brand pages."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT brand_id, company_name, industry, description, logo_url,
                       website, location, size, culture_tags, average_rating,
                       review_count, created_at
                FROM charvak_brands
                ORDER BY created_at DESC
            ''')
            rows = cur.fetchall()

            def _d(x, default):
                if isinstance(x, type(default)) or x is None:
                    return x if x is not None else default
                try:
                    return json.loads(x)
                except Exception:
                    return default

            companies = [{
                "brand_id": r[0],
                "company_name": r[1],
                "industry": r[2] or "",
                "description": r[3] or "",
                "logo_url": r[4] or "",
                "website": r[5] or "",
                "location": r[6] or "",
                "size": r[7] or "",
                "culture_tags": _d(r[8], []),
                "average_rating": float(r[9]) if r[9] is not None else 0,
                "review_count": r[10],
                "created_at": r[11].isoformat() if hasattr(r[11], "isoformat") else str(r[11]),
            } for r in rows]

            cur.execute('SELECT COUNT(*) FROM charvak_brand_reviews')
            total_reviews = int(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_all_brands failed: {e}")
            return {"status": "error", "message": "Could not load brands"}

        return {
            "status": "success",
            "companies": companies,
            "count": len(companies),
            "total_reviews": total_reviews,
        }

    def get_stats(self) -> Dict:
        """Get brand engine statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_brands')
            total_companies = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_brand_reviews')
            total_reviews = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_brand_promoted_jobs')
            promoted_jobs = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COALESCE(AVG(average_rating), 0) FROM charvak_brands')
            average_rating = float(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_companies": total_companies,
                "total_reviews": total_reviews,
                "promoted_jobs": promoted_jobs,
                "average_rating": round(average_rating, 1) if total_companies else 0,
            },
        }


brand_engine = BrandEngine()