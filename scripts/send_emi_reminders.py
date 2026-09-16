"""
Charvak EMI reminder runner.
Finds pending/overdue installments and sends the appropriate email per stage.
Dedupe via charvak_course_installments.last_reminder_stage.

Run manually:   python scripts/send_emi_reminders.py
Run on Render:  cron job, daily
"""
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from ai_courses_payments import ai_course_payments
from notification_engine import notification_engine
from email_engine import email_engine  # noqa: F401  (kept for parity with other scripts)


def _days_until(due_date_str):
    y, m, d = [int(x) for x in due_date_str.split("-")]
    return (date(y, m, d) - date.today()).days


def _stage_for(days_until):
    if days_until == 3:
        return "t_minus_3"
    if days_until == 0:
        return "due"
    if days_until == -1:
        return "overdue_1"
    if days_until == -3:
        return "overdue_3"
    if days_until == -7:
        return "overdue_7"
    return None


def _get_last_stage(enrollment_id, installment_num):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT last_reminder_stage FROM charvak_course_installments
        WHERE enrollment_id = %s AND installment_num = %s
    """, (enrollment_id, installment_num))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row[0] if row else None


def _set_last_stage(enrollment_id, installment_num, stage):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_course_installments
        SET last_reminder_stage = %s
        WHERE enrollment_id = %s AND installment_num = %s
    """, (stage, enrollment_id, installment_num))
    conn.commit()
    cur.close(); conn.close()


def _get_course_for(enrollment_id):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT course_name FROM charvak_enrollments WHERE enrollment_id = %s", (enrollment_id,))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row[0] if row else "your course"


def run():
    result = ai_course_payments.get_due_installments(days_ahead=7)
    if result.get("status") != "success":
        print("get_due_installments failed")
        return

    rows = result["installments"]
    print(f"Candidates: {len(rows)}")

    sent = {"t_minus_3": 0, "due": 0, "overdue_1": 0, "overdue_3": 0, "overdue_7": 0}
    skipped = 0

    for r in rows:
        try:
            days_until = _days_until(r["due_date"])
            stage = _stage_for(days_until)
            if not stage:
                skipped += 1
                continue
            if _get_last_stage(r["enrollment_id"], r["installment_num"]) == stage:
                skipped += 1
                continue

            course_name = _get_course_for(r["enrollment_id"])

            if stage in ("t_minus_3", "due"):
                notification_engine.notify_installment_due(
                    email=r["email"],
                    enrollment_id=r["enrollment_id"],
                    course_name=course_name,
                    installment_num=r["installment_num"],
                    total=r["total_installments"],
                    amount_inr=r["amount_inr"],
                    unlocks_weeks=f"{r['unlocks_from_week']}-{r['unlocks_to_week']}",
                    due_date=r["due_date"],
                    days_until=max(0, days_until),
                )
            else:
                days_overdue = abs(days_until)
                notification_engine.notify_installment_overdue(
                    email=r["email"],
                    enrollment_id=r["enrollment_id"],
                    course_name=course_name,
                    installment_num=r["installment_num"],
                    total=r["total_installments"],
                    amount_inr=r["amount_inr"],
                    unlocks_weeks=f"{r['unlocks_from_week']}-{r['unlocks_to_week']}",
                    days_overdue=days_overdue,
                )

            _set_last_stage(r["enrollment_id"], r["installment_num"], stage)
            sent[stage] = sent.get(stage, 0) + 1
        except Exception as e:
            print(f"  reminder failed for {r.get('email')}: {e}")

    print(f"Sent: {sent}")
    print(f"Skipped (no stage / already sent): {skipped}")


if __name__ == "__main__":
    run()
