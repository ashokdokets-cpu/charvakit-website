"""
Seed client roles + screening questions from seed_data_1.json and seed_data_2.json.

Idempotent: if a role with the same (client_name, title) already exists,
the script updates it and replaces its screening questions.
"""
import os
import sys
import json
import pathlib
from dotenv import load_dotenv

load_dotenv(".env.local", override=True)

url = os.getenv("DATABASE_URL", "")
host = url.split("@")[1].split("/")[0] if "@" in url else "unknown"
is_prod = "render.com" in host or "singapore" in host

print(f"DB host: {host}")
if is_prod and os.getenv("CHARVAK_ALLOW_PROD") != "1":
    print("REFUSING: this is PROD. Set CHARVAK_ALLOW_PROD=1 to override.")
    sys.exit(1)

sys.path.insert(0, ".")
from client_staffing_engine import client_staffing_engine
import psycopg2


def load_seed_file(path):
    p = pathlib.Path(path)
    if not p.exists():
        print(f"  SKIP: {path} not found")
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def find_existing_role(conn, client_name, title):
    cur = conn.cursor()
    cur.execute(
        "SELECT role_id FROM charvak_client_roles WHERE client_name = %s AND title = %s LIMIT 1",
        (client_name, title),
    )
    row = cur.fetchone()
    cur.close()
    return row[0] if row else None


def update_role(conn, role_id, role):
    fields = [
        "client_type", "title", "location",
        "experience_min_years", "experience_max_years",
        "skills_required", "budget_min_inr", "budget_max_inr",
        "job_type", "priority", "jd_text", "status",
    ]
    set_parts = []
    params = []
    for f in fields:
        if f in role:
            set_parts.append(f"{f} = %s")
            params.append(role[f])
    if not set_parts:
        return
    set_parts.append("updated_at = CURRENT_TIMESTAMP")
    params.append(role_id)
    sql = f"UPDATE charvak_client_roles SET {', '.join(set_parts)} WHERE role_id = %s"
    cur = conn.cursor()
    cur.execute(sql, tuple(params))
    cur.close()


def insert_role(role):
    result = client_staffing_engine.create_role(role)
    if result.get("status") != "success":
        print(f"    FAIL create_role: {result.get('message')}")
        return None
    return result.get("role_id")


def set_questions(role_id, questions):
    result = client_staffing_engine.set_screening_questions(role_id, questions)
    if result.get("status") != "success":
        print(f"    FAIL set_questions: {result.get('message')}")
        return False
    return True


def seed(roles):
    conn = psycopg2.connect(url)
    created = 0
    updated = 0
    failed = 0

    for i, role in enumerate(roles, 1):
        client_name = role.get("client_name") or "?"
        title = role.get("title") or "?"
        print(f"\n[{i}] {title}  ({client_name})")

        role.setdefault("status", "sourcing")

        existing_id = find_existing_role(conn, client_name, title)
        if existing_id:
            update_role(conn, existing_id, role)
            role_id = existing_id
            print(f"    UPDATED: {role_id}")
            updated += 1
        else:
            role_id = insert_role(role)
            if not role_id:
                failed += 1
                continue
            print(f"    CREATED: {role_id}")
            created += 1

        questions = role.get("questions") or []
        if questions and set_questions(role_id, questions):
            print(f"    QUESTIONS: {len(questions)} set")

    conn.commit()
    conn.close()
    return created, updated, failed


def main():
    print("\n=== Loading seed files ===")
    roles_1 = load_seed_file("seed_data_1.json")
    roles_2 = load_seed_file("seed_data_2.json")
    print(f"  seed_data_1.json: {len(roles_1)} roles")
    print(f"  seed_data_2.json: {len(roles_2)} roles")

    all_roles = roles_1 + roles_2
    if not all_roles:
        print("No roles to seed.")
        return

    print(f"\n=== Seeding {len(all_roles)} roles ===")
    created, updated, failed = seed(all_roles)

    print()
    print("=== Summary ===")
    print(f"  Created: {created}")
    print(f"  Updated: {updated}")
    print(f"  Failed:  {failed}")
    print(f"  Total:   {created + updated}/{len(all_roles)}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
