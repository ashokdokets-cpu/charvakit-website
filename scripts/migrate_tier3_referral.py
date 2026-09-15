"""
Tier 3 Session 2 — Referral System persistence
Creates 3 tables:
  - charvak_referrals          (referral codes + referrer info + stats)
  - charvak_referral_clicks    (click log)
  - charvak_referral_bounties  (bounties: signup/converted/paid)
Idempotent.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
import psycopg2

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

print("Creating tables...\n")

# 1. charvak_referrals
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_referrals (
        referral_code TEXT PRIMARY KEY,
        referral_link TEXT NOT NULL,
        referrer_name TEXT,
        referrer_email TEXT NOT NULL,
        user_type TEXT DEFAULT 'candidate',
        clicks INTEGER DEFAULT 0,
        signups INTEGER DEFAULT 0,
        conversions INTEGER DEFAULT 0,
        total_earned INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_referrals_email ON charvak_referrals(referrer_email)")
print("  [OK] charvak_referrals")

# 2. charvak_referral_clicks
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_referral_clicks (
        id SERIAL PRIMARY KEY,
        referral_code TEXT NOT NULL,
        source TEXT DEFAULT 'direct',
        clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_clicks_code ON charvak_referral_clicks(referral_code)")
print("  [OK] charvak_referral_clicks")

# 3. charvak_referral_bounties
cur.execute("""
    CREATE TABLE IF NOT EXISTS charvak_referral_bounties (
        bounty_id TEXT PRIMARY KEY,
        referral_code TEXT NOT NULL,
        referrer_email TEXT NOT NULL,
        new_user_email TEXT,
        amount_inr INTEGER DEFAULT 500,
        status TEXT DEFAULT 'signed_up',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        paid_at TIMESTAMP
    )
""")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_bounties_ref ON charvak_referral_bounties(referral_code)")
cur.execute("CREATE INDEX IF NOT EXISTS idx_charvak_bounties_email ON charvak_referral_bounties(referrer_email)")
print("  [OK] charvak_referral_bounties")

conn.commit()

# Verify
print("\nVerifying:")
for table in ['charvak_referrals', 'charvak_referral_clicks', 'charvak_referral_bounties']:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]} rows")

cur.close()
conn.close()
print("\nMigration complete.")