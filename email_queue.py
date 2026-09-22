"""
Charvak Email Queue — delayed email delivery for onboarding sequences.

Usage:
    from email_queue import email_queue
    email_queue.enqueue(email, "nudge_first_assessment", when_hours=24)
"""
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("charvakit.email_queue")


class EmailQueue:
    def __init__(self):
        logger.info("Email Queue ready")

    def _ensure_table(self):
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_email_queue (
                    queue_id      SERIAL PRIMARY KEY,
                    email         TEXT NOT NULL,
                    template      TEXT NOT NULL,
                    payload       JSONB DEFAULT '{}'::jsonb,
                    scheduled_at  TIMESTAMP NOT NULL,
                    sent_at       TIMESTAMP,
                    status        TEXT DEFAULT 'pending',
                    error         TEXT,
                    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.error(f"_ensure_table failed: {e}")

    def enqueue(self, email, template, when_hours=24, payload=None):
        """Queue an email to be sent after when_hours."""
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            scheduled = datetime.utcnow() + timedelta(hours=when_hours)
            cur.execute("""
                INSERT INTO charvak_email_queue (email, template, payload, scheduled_at)
                VALUES (%s, %s, %s::jsonb, %s)
                RETURNING queue_id
            """, (email, template, json.dumps(payload or {}), scheduled))
            qid = cur.fetchone()[0]
            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)
            logger.info(f"Queued {template} for {email} at {scheduled}")
            return {"status": "success", "queue_id": qid}
        except Exception as e:
            logger.error(f"enqueue failed: {e}")
            return {"status": "error", "message": str(e)}

    def process_pending(self, batch=50):
        """Send all due emails. Returns counts."""
        sent = 0
        failed = 0
        try:
            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT queue_id, email, template, payload
                FROM charvak_email_queue
                WHERE sent_at IS NULL
                  AND status = 'pending'
                  AND scheduled_at <= NOW()
                ORDER BY scheduled_at
                LIMIT %s
            """, (batch,))
            rows = cur.fetchall()
            cur.close()
            db.release_pooled_connection(conn)
        except Exception as e:
            logger.error(f"process_pending fetch failed: {e}")
            return {"sent": 0, "failed": 0, "error": str(e)}

        for qid, email, template, payload in rows:
            try:
                ok = self._send_template(email, template, payload or {})
                conn = db.get_pooled_connection()
                cur = conn.cursor()
                if ok:
                    cur.execute("""
                        UPDATE charvak_email_queue
                        SET sent_at = NOW(), status = 'sent'
                        WHERE queue_id = %s
                    """, (qid,))
                    sent += 1
                else:
                    cur.execute("""
                        UPDATE charvak_email_queue
                        SET status = 'failed', error = 'send failed'
                        WHERE queue_id = %s
                    """, (qid,))
                    failed += 1
                conn.commit()
                cur.close()
                db.release_pooled_connection(conn)
            except Exception as e:
                logger.error(f"process qid={qid} failed: {e}")
                failed += 1

        return {"sent": sent, "failed": failed}

    def _send_template(self, email, template, payload):
        """Dispatch by template name."""
        from email_engine import email_engine

        try:
            if template == "nudge_first_assessment":
                subject = "Ready for your first practice test, {name}?"
                body = """
                <div style="font-family:sans-serif;max-width:600px;">
                  <h2 style="color:#3ba591;">Take your first practice test</h2>
                  <p>Hi there,</p>
                  <p>You signed up yesterday — ready to try a practice test?
                     It takes about 5 minutes and gives you instant AI feedback.</p>
                  <p><a href="https://www.charvakit.com/exam-prep"
                        style="background:#3ba591;color:#fff;padding:12px 24px;
                               text-decoration:none;border-radius:6px;display:inline-block;">
                     Start practicing</a></p>
                  <p style="color:#888;font-size:12px;margin-top:32px;">
                     Charvak IT Consulting &middot; <a href="https://www.charvakit.com">charvakit.com</a>
                  </p>
                </div>
                """
                return email_engine.send_email(email, subject, body).get("status") == "success"
            elif template == "cta_credits_expire":
                subject = "Your 50 free credits are waiting"
                body = """
                <div style="font-family:sans-serif;max-width:600px;">
                  <h2 style="color:#3ba591;">Still deciding? Your credits are ready.</h2>
                  <p>You have 50 free credits waiting on Charvak.
                     Try a skill assessment, run a resume review, or practice an exam.</p>
                  <p><a href="https://www.charvakit.com/welcome"
                        style="background:#3ba591;color:#fff;padding:12px 24px;
                               text-decoration:none;border-radius:6px;display:inline-block;">
                     Explore Charvak</a></p>
                  <p style="color:#888;font-size:12px;margin-top:32px;">
                     Charvak IT Consulting &middot; <a href="https://www.charvakit.com">charvakit.com</a>
                  </p>
                </div>
                """
                return email_engine.send_email(email, subject, body).get("status") == "success"
            else:
                logger.warning(f"Unknown template: {template}")
                return False
        except Exception as e:
            logger.error(f"_send_template({template}) failed: {e}")
            return False


email_queue = EmailQueue()
