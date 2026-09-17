"""
Charvak Messaging Engine
Direct messaging: Employer <-> Candidate InMail system
(DB-backed - Session D/5)
"""
import json
import logging
import secrets
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.messaging")


class MessageStatus:
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    REPLIED = "replied"


class MessagingEngine:
    """Complete messaging system for employers and candidates (DB-backed)."""

    def __init__(self):
        self.templates = self._seed_templates()
        self._ensure_tables()
        logger.info("Messaging Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_messages (
                    message_id        TEXT PRIMARY KEY,
                    sender_id         TEXT NOT NULL,
                    sender_type       TEXT,
                    recipient_id      TEXT NOT NULL,
                    recipient_type    TEXT,
                    subject           TEXT DEFAULT 'New Message',
                    body              TEXT DEFAULT '',
                    job_id            TEXT,
                    application_id    TEXT,
                    status            TEXT DEFAULT 'sent',
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read_at           TIMESTAMP,
                    conversation_key  TEXT NOT NULL
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_messages_sender    ON charvak_messages(sender_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_messages_recipient ON charvak_messages(recipient_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_messages_convo     ON charvak_messages(conversation_key)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_messages_status    ON charvak_messages(status)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_messages_created   ON charvak_messages(created_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"messaging tables init failed: {e}")

    @staticmethod
    def _convo_key(a: str, b: str) -> str:
        """Normalized conversation key - sorted so A:B and B:A collide."""
        return ":".join(sorted([a or "", b or ""]))

    # ============================================================
    # TEMPLATES (static)
    # ============================================================

    def _seed_templates(self) -> List[Dict]:
        return [
            {"id": "TPL-001", "name": "Interview Invitation", "body": "Hi {{name}}, we reviewed your profile and would love to invite you for an interview for the {{role}} position at {{company}}. Are you available this week?"},
            {"id": "TPL-002", "name": "Job Opportunity", "body": "Hi {{name}}, I came across your profile and think you'd be a great fit for our {{role}} position. Interested?"},
            {"id": "TPL-003", "name": "Application Update", "body": "Hi {{name}}, thank you for applying to {{company}}. Your application is under review. We'll update you within 48 hours."},
            {"id": "TPL-004", "name": "Offer Extension", "body": "Hi {{name}}, congratulations! We'd like to extend an offer for the {{role}} position. Let's discuss details."},
            {"id": "TPL-005", "name": "Rejection - Soft", "body": "Hi {{name}}, thank you for your interest. While your profile is impressive, we've decided to move forward with other candidates. We'll keep you in mind for future roles."},
        ]

    def _find_template(self, template_id: str) -> Optional[Dict]:
        for template in self.templates:
            if template["id"] == template_id:
                return template
        return None

    def get_templates(self) -> Dict:
        return {"status": "success", "templates": self.templates, "count": len(self.templates)}

    # ============================================================
    # SEND
    # ============================================================

    def send_message(self, data: Dict) -> Dict:
        """Send a message."""
        message_id = f"MSG-{secrets.token_hex(4).upper()}"

        body = data.get("body", "")
        if data.get("template_id"):
            template = self._find_template(data["template_id"])
            if template:
                body = template["body"].replace("{{name}}", data.get("recipient_name", ""))
                body = body.replace("{{role}}", data.get("role", ""))
                body = body.replace("{{company}}", data.get("company", ""))

        sender_id = data.get("sender_id")
        recipient_id = data.get("recipient_id")
        convo_key = self._convo_key(sender_id, recipient_id)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_messages (
                    message_id, sender_id, sender_type, recipient_id, recipient_type,
                    subject, body, job_id, application_id, status, conversation_key
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                message_id,
                sender_id, data.get("sender_type"),
                recipient_id, data.get("recipient_type"),
                data.get("subject", "New Message"),
                body,
                data.get("job_id"),
                data.get("application_id"),
                MessageStatus.SENT,
                convo_key,
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"send_message failed: {e}")
            return {"status": "error", "message": "Could not send message"}

        logger.info(f"Message sent: {message_id} from {sender_id} to {recipient_id}")

        return {
            "status": "success",
            "message_id": message_id,
            "message": "Message sent successfully",
        }

    # ============================================================
    # SERIALIZER
    # ============================================================

    @staticmethod
    def _row_to_message(r) -> Dict:
        return {
            "message_id": r[0],
            "sender_id": r[1],
            "sender_type": r[2],
            "recipient_id": r[3],
            "recipient_type": r[4],
            "subject": r[5],
            "body": r[6],
            "job_id": r[7],
            "application_id": r[8],
            "status": r[9],
            "created_at": r[10].isoformat() if hasattr(r[10], "isoformat") else str(r[10]),
            "read_at": r[11].isoformat() if r[11] and hasattr(r[11], "isoformat") else None,
            "conversation_key": r[12],
        }

    _MSG_COLS = """message_id, sender_id, sender_type, recipient_id, recipient_type,
                   subject, body, job_id, application_id, status, created_at,
                   read_at, conversation_key"""

    # ============================================================
    # INBOX
    # ============================================================

    def get_inbox(self, user_id: str) -> Dict:
        """Get user's inbox - one entry per conversation partner."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Find all conversations this user participates in
            cur.execute('''
                SELECT conversation_key,
                       MIN(created_at) AS first_at,
                       MAX(created_at) AS last_at,
                       COUNT(*) AS msg_count
                FROM charvak_messages
                WHERE sender_id = %s OR recipient_id = %s
                GROUP BY conversation_key
                ORDER BY last_at DESC
            ''', (user_id, user_id))
            convo_rows = cur.fetchall()

            conversations = []
            for ck, first_at, last_at, msg_count in convo_rows:
                # Participants
                cur.execute('''
                    SELECT DISTINCT sender_id, recipient_id
                    FROM charvak_messages WHERE conversation_key = %s
                ''', (ck,))
                participants = set()
                for r in cur.fetchall():
                    participants.add(r[0])
                    participants.add(r[1])

                # Last message
                cur.execute(f'''
                    SELECT {self._MSG_COLS}
                    FROM charvak_messages WHERE conversation_key = %s
                    ORDER BY created_at DESC LIMIT 1
                ''', (ck,))
                last_msg = self._row_to_message(cur.fetchone())

                # Unread count for this user
                cur.execute('''
                    SELECT COUNT(*) FROM charvak_messages
                    WHERE conversation_key = %s AND recipient_id = %s AND status != %s
                ''', (ck, user_id, MessageStatus.READ))
                unread_count = int(cur.fetchone()[0] or 0)

                conversations.append({
                    "conversation_key": ck,
                    "participants": list(participants),
                    "last_message": last_msg,
                    "message_count": int(msg_count),
                    "unread_count": unread_count,
                    "updated_at": last_at.isoformat() if hasattr(last_at, "isoformat") else str(last_at),
                })

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_inbox failed: {e}")
            return {"status": "error", "message": "Could not load inbox"}

        # Already sorted by last_at DESC in SQL
        return {
            "status": "success",
            "conversations": conversations,
            "count": len(conversations),
            "total_unread": sum(c["unread_count"] for c in conversations),
        }

    # ============================================================
    # CONVERSATION
    # ============================================================

    def get_conversation(self, user_id: str, other_user_id: str) -> Dict:
        """Get full conversation between two users (marks incoming as read)."""
        convo_key = self._convo_key(user_id, other_user_id)

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # Ensure conversation exists
            cur.execute('SELECT 1 FROM charvak_messages WHERE conversation_key = %s LIMIT 1', (convo_key,))
            if not cur.fetchone():
                cur.close(); conn.close()
                return {"status": "error", "message": "Conversation not found"}

            # Mark incoming as read (side effect on read - preserves original behavior)
            cur.execute('''
                UPDATE charvak_messages
                SET status = %s, read_at = NOW()
                WHERE conversation_key = %s AND recipient_id = %s AND status != %s
            ''', (MessageStatus.READ, convo_key, user_id, MessageStatus.READ))

            # Fetch all messages
            cur.execute(f'''
                SELECT {self._MSG_COLS}
                FROM charvak_messages WHERE conversation_key = %s
                ORDER BY created_at ASC
            ''', (convo_key,))
            messages = [self._row_to_message(r) for r in cur.fetchall()]

            # Fetch conversation meta
            cur.execute('''
                SELECT MIN(created_at), MAX(created_at) FROM charvak_messages WHERE conversation_key = %s
            ''', (convo_key,))
            first_at, last_at = cur.fetchone()

            cur.execute('''
                SELECT DISTINCT sender_id, recipient_id
                FROM charvak_messages WHERE conversation_key = %s
            ''', (convo_key,))
            participants = set()
            for r in cur.fetchall():
                participants.add(r[0])
                participants.add(r[1])

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_conversation failed: {e}")
            return {"status": "error", "message": "Conversation not found"}

        conversation = {
            "key": convo_key,
            "participants": list(participants),
            "messages": messages,
            "last_message": messages[-1] if messages else None,
            "created_at": first_at.isoformat() if hasattr(first_at, "isoformat") else str(first_at),
            "updated_at": last_at.isoformat() if hasattr(last_at, "isoformat") else str(last_at),
        }

        return {"status": "success", "conversation": conversation}

    # ============================================================
    # MARK READ
    # ============================================================

    def mark_read(self, message_id: str) -> Dict:
        """Mark a single message as read."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_messages
                SET status = %s, read_at = NOW()
                WHERE message_id = %s
            ''', (MessageStatus.READ, message_id))
            affected = cur.rowcount
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"mark_read failed: {e}")
            return {"status": "error", "message": "Message not found"}

        if affected == 0:
            return {"status": "error", "message": "Message not found"}
        return {"status": "success", "message": "Marked as read"}

    # ============================================================
    # STATS
    # ============================================================

    def get_stats(self) -> Dict:
        """Get messaging statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_messages')
            total_messages = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(DISTINCT conversation_key) FROM charvak_messages')
            total_conversations = int(cur.fetchone()[0] or 0)

            # unread_messages: status in ('sent', 'delivered') - NOT replied, NOT read
            cur.execute('''
                SELECT COUNT(*) FROM charvak_messages
                WHERE status IN (%s, %s)
            ''', (MessageStatus.SENT, MessageStatus.DELIVERED))
            unread_messages = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_messages WHERE status = %s', (MessageStatus.READ,))
            read_messages = int(cur.fetchone()[0] or 0)

            # active conversations = conversations with >1 message
            cur.execute('''
                SELECT COUNT(*) FROM (
                    SELECT conversation_key FROM charvak_messages
                    GROUP BY conversation_key HAVING COUNT(*) > 1
                ) AS active
            ''')
            active_conversations = int(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_messages": total_messages,
                "total_conversations": total_conversations,
                "unread_messages": unread_messages,
                "read_messages": read_messages,
                "active_conversations": active_conversations,
            },
        }


messaging_engine = MessagingEngine()