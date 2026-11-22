"""
Role Category Classifier - Session 121
Classifies jobs into tech, sales_marketing, finance, healthcare, hospitality, campus, other.
"""
import os
import sys
import logging

logger = logging.getLogger("charvakit.role_classifier")


# Priority-ordered keyword map — first match wins
ROLE_KEYWORDS = [
    # Campus / fresher (highest priority — overrides tech)
    ("campus", ["fresher", "graduate trainee", "campus placement", "trainee engineer",
                "graduate engineer trainee", "get", "management trainee", "intern"]),

    # Tech
    ("tech", ["software", "developer", "engineer", "data analyst", "data scientist",
              "data engineer", "python", "java", "devops", "ml engineer", "machine learning",
              "ai ", "frontend", "backend", "full stack", "fullstack", "react", "node",
              "qa ", "quality assurance", "sde", "sre", "cloud", "aws", "azure",
              "programmer", "architect", "cto", "technical lead", "systems engineer",
              "database", "dba", "cybersecurity", "security engineer", "ui/ux",
              "product manager", "product owner", "scrum", "agile coach"]),

    # Sales / Marketing
    ("sales_marketing", ["sales", "marketing", "business development", "growth",
                         "account executive", "account manager", "relationship manager",
                         "brand", "content", "seo", "digital marketing", "social media",
                         "inside sales", "field sales", "channel partner", "customer success"]),

    # Finance
    ("finance", ["finance", "financial", "accountant", "accounting", "audit",
                 "tax ", "taxation", "banking", "banker", "loan", "credit",
                 "treasury", "cfa", "ca ", "chartered accountant", "cfo", "investment",
                 "wealth manager", "insurance", "underwriter", "risk analyst"]),

    # Healthcare
    ("healthcare", ["nurse", "nursing", "pharma", "pharmacist", "medical",
                    "hospital", "doctor", "surgeon", "clinical", "patient",
                    "healthcare", "health", "diagnostic", "lab technician",
                    "physiotherapist", "radiolog", "bsc graduate"]),

    # Hospitality
    ("hospitality", ["hotel", "hospitality", "housekeeping", "f&b", "food and beverage",
                     "chef", "waiter", "hostess", "front desk", "concierge", "resort"]),

    # Admin / Operations
    ("admin_ops", ["administrator", "admin", "operations", "office assistant",
                   "executive assistant", "receptionist", "data entry",
                   "back office", "coordinator", "logistics", "supply chain",
                   "warehouse", "procurement", "inventory"]),
]


def classify_role(title: str) -> str:
    """Classify a job title into a category. Returns 'other' if no match."""
    if not title:
        return "other"
    title_lower = title.lower()

    for category, keywords in ROLE_KEYWORDS:
        for kw in keywords:
            if kw in title_lower:
                return category

    return "other"


def classify_all_jobs(db_url: str, dry_run: bool = False) -> dict:
    """Classify all jobs in the DB and update role_category."""
    import psycopg2
    conn = psycopg2.connect(db_url)
    conn.autocommit = False
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT job_id, title FROM charvak_jobs
            WHERE role_category IS NULL OR role_category = 'other'
        """)
        rows = cur.fetchall()
        print(f"Found {len(rows)} jobs needing classification")

        counts = {}
        updates = []

        for job_id, title in rows:
            cat = classify_role(title)
            counts[cat] = counts.get(cat, 0) + 1
            updates.append((cat, job_id))

        print(f"\n=== Classification breakdown ===")
        for cat, cnt in sorted(counts.items(), key=lambda x: -x[1]):
            print(f"  {cat:20} {cnt}")

        if not dry_run:
            for cat, job_id in updates:
                cur.execute(
                    "UPDATE charvak_jobs SET role_category = %s WHERE job_id = %s",
                    (cat, job_id)
                )
            conn.commit()
            print(f"\n✅ Updated {len(updates)} jobs in database")
        else:
            print("\n🔍 DRY RUN — no updates applied")

    finally:
        cur.close()
        conn.close()

    return counts


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # Force production
    for key in ["DATABASE_URL"]:
        if key in os.environ: del os.environ[key]
    load_dotenv(".env", override=True)

    db_url = os.getenv("DATABASE_URL")
    if "localhost" in db_url:
        print("❌ .env points to localhost")
        sys.exit(1)

    print(f"✅ Using PRODUCTION DB: {db_url.split('@')[-1].split('/')[0]}\n")
    counts = classify_all_jobs(db_url, dry_run=False)

    # Verify
    import psycopg2
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    cur.execute("""
        SELECT role_category, COUNT(*) FROM charvak_jobs
        WHERE status = 'active'
        GROUP BY role_category
        ORDER BY COUNT(*) DESC
    """)
    print("\n=== Role categories in production ===")
    for cat, cnt in cur.fetchall():
        print(f"  {cat:20} {cnt}")
    cur.close(); conn.close()