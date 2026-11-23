"""
Follow-Up Reminder Engine - Session 123 Option A
Sends Day 3 / Day 7 / Day 14 reminders for applied jobs.
"""
import os
import logging
from datetime import datetime, timezone
from database import db

logger = logging.getLogger("charvakit.followup")


class FollowUpEngine:
    def get_due_reminders(self, db_url_override=None) -> list:
        """Find applications that need a reminder today."""
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT sj.save_id, sj.student_id, sj.job_id, sj.applied_at,
                       sj.followup_3day_at, sj.followup_7day_at, sj.followup_14day_at,
                       sj.followup_3day_sent_at, sj.followup_7day_sent_at, sj.followup_14day_sent_at,
                       j.title, j.company, j.location,
                       s.email, s.name
                FROM charvak_saved_jobs sj
                JOIN charvak_jobs j ON j.job_id = sj.job_id
                JOIN charvak_students s ON s.student_id = sj.student_id
                WHERE sj.status = 'applied'
                  AND sj.applied_at IS NOT NULL
                  AND (
                    (sj.followup_3day_at <= NOW() AND sj.followup_3day_sent_at IS NULL)
                    OR (sj.followup_7day_at <= NOW() AND sj.followup_7day_sent_at IS NULL)
                    OR (sj.followup_14day_at <= NOW() AND sj.followup_14day_sent_at IS NULL)
                  )
            """)
            rows = cur.fetchall()
            results = []
            for r in rows:
                # Determine which reminder is due
                reminder_type = None
                if r[7] is None and r[4] and r[4] <= datetime.now(timezone.utc):
                    reminder_type = "3day"
                elif r[8] is None and r[5] and r[5] <= datetime.now(timezone.utc):
                    reminder_type = "7day"
                elif r[9] is None and r[6] and r[6] <= datetime.now(timezone.utc):
                    reminder_type = "14day"

                if not reminder_type:
                    continue

                results.append({
                    "save_id": r[0], "student_id": r[1], "job_id": r[2],
                    "applied_at": r[3],
                    "reminder_type": reminder_type,
                    "title": r[10], "company": r[11], "location": r[12],
                    "email": r[13], "name": r[14],
                })
            return results
        finally:
            cur.close()
            conn.close()

    def build_followup_email(self, reminder: dict) -> tuple:
        """Build subject + body for a follow-up reminder."""
        title = reminder["title"]
        company = reminder["company"]
        rtype = reminder["reminder_type"]

        templates = {
            "3day": {
                "subject": f"Quick nudge: Follow up on your {company} application",
                "body": f"""<p>Hi {reminder['name'] or 'there'},</p>
<p>You applied to <strong>{title}</strong> at <strong>{company}</strong> 3 days ago.
It's a good time to send a short follow-up.</p>
<p><strong>Suggested message:</strong></p>
<blockquote style="background:#f0f9ff;padding:15px;border-left:3px solid #0a3d62;margin:15px 0;">
Hi [Hiring Manager],<br><br>
I applied for the {title} role at {company} on [date]. I'm very excited about the opportunity and wanted to ensure my application reached you. I'd be happy to provide any additional information you need.<br><br>
Thanks,<br>
{reminder['name'] or 'Your name'}
</blockquote>
<p>Reply to the original email you sent, or use this template in a fresh message.</p>
<p>— Charvak Career Team</p>"""
            },
            "7day": {
                "subject": f"Week 1 check-in: {company} application",
                "body": f"""<p>Hi {reminder['name'] or 'there'},</p>
<p>It's been 7 days since you applied to <strong>{title}</strong> at <strong>{company}</strong>.
Try a different angle — mention a recent project or news about the company.</p>
<p><strong>Suggested message:</strong></p>
<blockquote style="background:#f0f9ff;padding:15px;border-left:3px solid #0a3d62;margin:15px 0;">
Hi [Hiring Manager],<br><br>
Following up on my {title} application. I recently [added relevant project/skill], which I believe aligns well with {company}'s work. Would love to discuss further.<br><br>
Thanks,<br>
{reminder['name'] or 'Your name'}
</blockquote>
<p>— Charvak Career Team</p>"""
            },
            "14day": {
                "subject": f"Final follow-up: {company} application",
                "body": f"""<p>Hi {reminder['name'] or 'there'},</p>
<p>Two weeks since you applied to <strong>{title}</strong> at <strong>{company}</strong>.
If you haven't heard back, this is a good time to either send a final follow-up or move on.</p>
<p><strong>Suggested final follow-up:</strong></p>
<blockquote style="background:#f0f9ff;padding:15px;border-left:3px solid #0a3d62;margin:15px 0;">
Hi [Hiring Manager],<br><br>
I wanted to follow up one last time on the {title} role. If the position has been filled or you've moved forward with other candidates, I understand — I'd just appreciate knowing either way.<br><br>
Thanks for your time,<br>
{reminder['name'] or 'Your name'}
</blockquote>
<p>After this, you can mark the application as "Rejected" or "Offer" in your tracker and move on.</p>
<p>— Charvak Career Team</p>"""
            },
        }

        return templates[rtype]["subject"], templates[rtype]["body"]

    def send_reminder(self, reminder: dict) -> bool:
        """Send the email and mark as sent."""
        subject, body = self.build_followup_email(reminder)

        # Send email using existing EmailEngine
        try:
            from email_engine import EmailEngine
            engine = EmailEngine()
            if hasattr(engine, 'send_email'):
                engine.send_email(to_email=reminder["email"], subject=subject, body=body)
            else:
                # Fallback: log only
                logger.info(f"[FOLLOWUP] {reminder['email']} — {subject}")
        except Exception as e:
            logger.error(f"Failed to send followup: {e}")
            return False

        # Mark as sent
        conn = db.get_connection()
        cur = conn.cursor()
        try:
            rtype = reminder["reminder_type"]
            col = f"followup_{rtype}_sent_at"
            cur.execute(f"""
                UPDATE charvak_saved_jobs
                SET {col} = NOW()
                WHERE save_id = %s
            """, (reminder["save_id"],))
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to mark reminder as sent: {e}")
            return False
        finally:
            cur.close()
            conn.close()

    def process_due_reminders(self) -> dict:
        """Main entry point — find, send, mark."""
        reminders = self.get_due_reminders()
        logger.info(f"Found {len(reminders)} due reminders")

        sent = 0
        failed = 0
        for r in reminders:
            if self.send_reminder(r):
                sent += 1
            else:
                failed += 1

        return {
            "status": "success",
            "processed": len(reminders),
            "sent": sent,
            "failed": failed,
        }


followup_engine = FollowUpEngine()