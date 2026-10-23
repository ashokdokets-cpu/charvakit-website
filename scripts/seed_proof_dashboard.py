"""
Session 81 — Seed demo institutions for Proof Dashboard testing.
Creates 3 institutions, 50 students each, 150 total certs, 200 cert views.
Idempotent — safe to re-run.
"""
import os
from dotenv import load_dotenv
load_dotenv()

import psycopg2
import secrets
from datetime import datetime, timedelta
import random

url = os.getenv("DATABASE_URL", "")
is_local = "localhost" in url or "127.0.0.1" in url
print(f"Target: {'LOCAL' if is_local else 'PROD'} database")

conn = psycopg2.connect(url)
cur = conn.cursor()

# ---------- 3 institutions ----------
INSTITUTIONS = [
    {"university_id": "UNI-AMRITA-001", "name": "Amrita Vishwa Vidyapeetham",
     "admin_email": "cdc@amrita.edu.in", "location": "Coimbatore, TN",
     "type": "Deemed University"},
    {"university_id": "UNI-VIT-001", "name": "VIT Vellore",
     "admin_email": "cdc@vit.ac.in", "location": "Vellore, TN",
     "type": "Deemed University"},
    {"university_id": "UNI-NITT-001", "name": "NIT Tiruchirappalli",
     "admin_email": "cdc@nitt.edu", "location": "Tiruchirappalli, TN",
     "type": "NIT"},
]

ROLES = [
    "Software Engineer", "Data Analyst", "Product Manager",
    "Business Analyst", "ML Engineer", "DevOps Engineer",
    "Full-Stack Engineer", "Backend Engineer",
]

FIRST_NAMES = ["Priya", "Arjun", "Meera", "Rahul", "Sneha", "Vikram",
               "Ananya", "Karthik", "Divya", "Sanjay", "Kavya", "Naveen",
               "Isha", "Amit", "Ritu", "Rohan", "Pooja", "Yash",
               "Neha", "Sameer", "Aditi", "Varun", "Tara", "Nikhil",
               "Shreya", "Manish", "Aisha", "Kiran", "Pranav", "Deepa"]

LAST_NAMES = ["Sharma", "Kumar", "Iyer", "Reddy", "Nair", "Patel",
              "Rao", "Singh", "Gupta", "Menon", "Pillai", "Verma"]

print("\n=== 1. Seeding institutions ===")
for inst in INSTITUTIONS:
    cur.execute("""
        INSERT INTO charvak_universities
            (university_id, name, admin_email, location, type, student_count, created_at)
        VALUES (%s, %s, %s, %s, %s, 50, NOW())
        ON CONFLICT (university_id) DO UPDATE SET
            name = EXCLUDED.name,
            location = EXCLUDED.location
    """, (inst["university_id"], inst["name"], inst["admin_email"],
          inst["location"], inst["type"]))
    print(f"  {inst['university_id']} -> {inst['name']}")

conn.commit()

# ---------- 50 students per institution ----------
print("\n=== 2. Seeding students (50 per institution) ===")
student_count = 0
for inst in INSTITUTIONS:
    for i in range(50):
        student_id = f"{inst['university_id']}-S{i+1:03d}"
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}{i+1}@{inst['university_id'].lower().replace('uni-','').replace('-001','')}.edu.in"
        grad_year = 2026 if i < 30 else 2027
        status = "final_year" if i < 30 else "pre_final"
        placement_status = random.choice(["not_placed"] * 7 + ["placed"] * 3)

        cur.execute("""
            INSERT INTO charvak_university_students
                (student_id, university_id, name, email, graduation_year, status, placement_status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (student_id) DO UPDATE SET
                email = EXCLUDED.email
        """, (student_id, inst["university_id"], f"{first} {last}", email,
              grad_year, status, placement_status))
        student_count += 1

conn.commit()
print(f"  Seeded {student_count} students across {len(INSTITUTIONS)} institutions")

# ---------- Certs: 30-45 per institution (random 60-90% coverage) ----------
print("\n=== 3. Seeding readiness certificates ===")
cert_count = 0
cert_ids_by_inst = {}
for inst in INSTITUTIONS:
    cur.execute("""
        SELECT email, name FROM charvak_university_students
        WHERE university_id = %s ORDER BY student_id LIMIT 50
    """, (inst["university_id"],))
    students = cur.fetchall()

    cert_ids_by_inst[inst["university_id"]] = []

    # Random 60-90% have certs (per institution)
    coverage_pct = random.randint(60, 90)
    n_with_cert = int(len(students) * coverage_pct / 100)
    students_with_cert = random.sample(students, n_with_cert)

    for student_email, student_name in students_with_cert:
        cert_id = f"RDC-{secrets.token_hex(6).upper()}"
        role = random.choice(ROLES)
        industry = random.choice(["IT / Tech", "FinTech / Payments", "HealthTech / Digital Health"])
        level = random.choice(["junior", "mid", "senior"])
        score = random.randint(45, 92)
        benchmark = random.randint(65, 75)
        verdict = "Above benchmark - role ready" if score >= benchmark else "Below benchmark - skill gaps to close"
        cert_hash = secrets.token_hex(8)

        # Spread certs across last 90 days
        days_ago = random.randint(1, 90)
        created_at = datetime.now() - timedelta(days=days_ago)

        cur.execute("""
            INSERT INTO charvak_readiness_certificates
                (certificate_id, assessment_id, email, display_name, role, industry, level,
                 readiness_score, percentile, benchmark_score, verdict,
                 payload_json, certificate_hash, source, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    '{}'::jsonb, %s, 'written', %s)
            ON CONFLICT (certificate_id) DO NOTHING
        """, (cert_id, f"CAR-SEED-{cert_count}", student_email, student_name,
              role, industry, level, score, random.randint(10, 95),
              benchmark, verdict, cert_hash, created_at))

        cert_ids_by_inst[inst["university_id"]].append(cert_id)
        cert_count += 1

conn.commit()
print(f"  Seeded {cert_count} certificates")

# ---------- 200 cert views across the institutions ----------
print("\n=== 4. Seeding cert views ===")
view_count = 0
for inst in INSTITUTIONS:
    certs = cert_ids_by_inst[inst["university_id"]]
    if not certs:
        continue

    # 50-80 views per institution, weighted to employer views
    n_views = random.randint(50, 80)
    for _ in range(n_views):
        cert_id = random.choice(certs)
        viewer_type = random.choices(
            ["anonymous", "employer", "dean", "admin"],
            weights=[40, 45, 10, 5]
        )[0]
        ip_hash = secrets.token_hex(16)
        days_ago = random.randint(0, 30)
        viewed_at = datetime.now() - timedelta(days=days_ago)

        cur.execute("""
            INSERT INTO charvak_certificate_views
                (view_id, certificate_id, viewer_ip_hash, viewer_type,
                 user_agent, referrer, university_id, viewed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (f"CV-SEED-{secrets.token_hex(6)}", cert_id, ip_hash,
              viewer_type, "Seed/1.0", "seed", inst["university_id"], viewed_at))
        view_count += 1

conn.commit()
print(f"  Seeded {view_count} cert views")

# ---------- Summary ----------
print("\n=== SUMMARY ===")
cur.execute("SELECT COUNT(*) FROM charvak_universities")
print(f"  Institutions: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM charvak_university_students")
print(f"  Students: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM charvak_readiness_certificates WHERE certificate_id LIKE 'RDC-%' AND assessment_id LIKE 'CAR-SEED-%'")
print(f"  Seeded certs: {cur.fetchone()[0]}")
cur.execute("SELECT COUNT(*) FROM charvak_certificate_views WHERE view_id LIKE 'CV-SEED-%'")
print(f"  Seeded views: {cur.fetchone()[0]}")

print("\n=== Sample: Amrita proof dashboard data (JSON) ===")
cur.close()
conn.close()

# Quick sanity: call get_proof_dashboard
from university_engine import university_engine
result = university_engine.get_proof_dashboard("UNI-AMRITA-001")
import json
print(json.dumps(result, indent=2)[:2000])