"""
Charvak Events Engine
Career fairs, webinars, info sessions, RSVP management
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.events")


class EventStatus:
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventsEngine:
    """Complete events management system (DB-backed)."""

    def __init__(self):
        self._ensure_tables()
        logger.info("Events Engine ready (DB-backed)")

    def _ensure_tables(self):
        """Idempotent table creation for events tables."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_events (
                    event_id          TEXT PRIMARY KEY,
                    title             TEXT,
                    description       TEXT DEFAULT '',
                    event_type        TEXT DEFAULT 'webinar',
                    organizer_id      TEXT,
                    organizer_name    TEXT,
                    date              TEXT,
                    duration_minutes  INTEGER DEFAULT 60,
                    platform          TEXT DEFAULT 'zoom',
                    location          TEXT DEFAULT '',
                    link              TEXT DEFAULT '',
                    max_attendees     INTEGER DEFAULT 100,
                    target_audience   TEXT DEFAULT 'All',
                    rsvp_count        INTEGER DEFAULT 0,
                    status            TEXT NOT NULL DEFAULT 'upcoming',
                    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_status ON charvak_events(status)
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_type ON charvak_events(event_type)
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_events_date ON charvak_events(date)
            ''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_event_rsvps (
                    rsvp_id         TEXT PRIMARY KEY,
                    event_id        TEXT NOT NULL,
                    user_id         TEXT,
                    user_name       TEXT,
                    user_email      TEXT NOT NULL,
                    user_type       TEXT DEFAULT 'student',
                    checked_in      BOOLEAN DEFAULT FALSE,
                    checked_in_at   TIMESTAMP,
                    rsvp_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(event_id, user_email)
                )
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_rsvps_event_id ON charvak_event_rsvps(event_id)
            ''')
            cur.execute('''
                CREATE INDEX IF NOT EXISTS idx_rsvps_email ON charvak_event_rsvps(user_email)
            ''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"events tables init failed: {e}")

    # ============================================================
    # EVENT CREATION
    # ============================================================

    def create_event(self, data: Dict) -> Dict:
        """
        Create a career fair, webinar, or info session.

        data = {
            "title": str,
            "description": str,
            "event_type": "career_fair" / "webinar" / "info_session" / "workshop",
            "organizer_id": str,
            "organizer_name": str,
            "date": str (ISO format),
            "duration_minutes": int,
            "platform": "zoom" / "meet" / "teams" / "in_person",
            "location": str (for in-person),
            "link": str (for virtual),
            "max_attendees": int,
            "target_audience": str
        }
        """
        event_id = f"EVT-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_events (
                    event_id, title, description, event_type, organizer_id,
                    organizer_name, date, duration_minutes, platform, location,
                    link, max_attendees, target_audience, rsvp_count, status
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,%s)
            ''', (
                event_id,
                data.get("title"),
                data.get("description", ""),
                data.get("event_type", "webinar"),
                data.get("organizer_id"),
                data.get("organizer_name"),
                data.get("date"),
                int(data.get("duration_minutes", 60)),
                data.get("platform", "zoom"),
                data.get("location", ""),
                data.get("link", ""),
                int(data.get("max_attendees", 100)),
                data.get("target_audience", "All"),
                EventStatus.UPCOMING,
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_event failed: {e}")
            return {"status": "error", "message": "Could not create event"}

        logger.info(f"Event created: {event_id} - {data.get('title')}")

        return {
            "status": "success",
            "event_id": event_id,
            "message": "Event created! RSVP is open.",
            "event_url": f"https://charvakit.com/events/{event_id}",
        }

    # ============================================================
    # RSVP
    # ============================================================

    def rsvp_to_event(self, data: Dict) -> Dict:
        """
        RSVP to an event.

        data = {
            "event_id": str,
            "user_id": str,
            "user_name": str,
            "user_email": str,
            "user_type": "student" / "employer" / "alumni"
        }
        """
        event = self._find_event(data.get("event_id"))
        if not event:
            return {"status": "error", "message": "Event not found"}

        if event["rsvp_count"] >= event["max_attendees"]:
            return {"status": "error", "message": "Event is full"}

        rsvp_id = f"RSVP-{secrets.token_hex(4).upper()}"

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_event_rsvps (
                    rsvp_id, event_id, user_id, user_name, user_email,
                    user_type, checked_in
                ) VALUES (%s,%s,%s,%s,%s,%s,FALSE)
            ''', (
                rsvp_id,
                data.get("event_id"),
                data.get("user_id"),
                data.get("user_name"),
                data.get("user_email"),
                data.get("user_type", "student"),
            ))
            cur.execute('''
                UPDATE charvak_events
                SET rsvp_count = rsvp_count + 1
                WHERE event_id = %s
            ''', (data.get("event_id"),))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            # Unique violation on (event_id, user_email) -> friendly message
            msg = str(e).lower()
            if "unique" in msg or "duplicate" in msg:
                return {
                    "status": "error",
                    "message": "You are already registered for this event",
                }
            logger.error(f"rsvp_to_event failed: {e}")
            return {"status": "error", "message": "Could not RSVP"}

        logger.info(f"RSVP: {rsvp_id} for {event['event_id']}")

        return {
            "status": "success",
            "rsvp_id": rsvp_id,
            "message": f"RSVP confirmed for {event['title']}!",
            "confirmation": f"Details sent to {data.get('user_email')}",
        }

    # ============================================================
    # READS
    # ============================================================

    def rsvp_paid(self, data: Dict) -> Dict:
        """Paid RSVP - requires verified payment_id from Razorpay."""
        try:
            event_id = (data.get("event_id") or "").strip()
            user_email = (data.get("user_email") or "").strip().lower()
            user_name = (data.get("user_name") or "Guest").strip()
            user_id = (data.get("user_id") or "").strip()
            payment_id = (data.get("payment_id") or "").strip()

            if not event_id or not user_email:
                return {"status": "error", "message": "event_id and user_email required"}
            if not payment_id:
                return {"status": "error", "message": "payment_id required for paid RSVP"}

            # Verify the event exists and is a paid event
            event = self.get_event(event_id)
            if event.get("status") != "success":
                return {"status": "error", "message": "Event not found"}

            ev = event.get("event") or {}
            price_inr = int(ev.get("price_inr") or 0)
            if price_inr <= 0:
                return {"status": "error", "message": "This event has no paid tier"}

            from database import db
            conn = db.get_pooled_connection()
            cur = conn.cursor()

            # Idempotency: if this payment_id was already used for this event, return success
            cur.execute("""
                SELECT rsvp_id FROM charvak_event_rsvps
                WHERE event_id = %s AND payment_id = %s
            """, (event_id, payment_id))
            existing = cur.fetchone()
            if existing:
                cur.close()
                db.release_pooled_connection(conn)
                return {"status": "success", "message": "RSVP already recorded",
                        "rsvp_id": existing[0], "already_recorded": True}

            # Upsert RSVP
            rsvp_id = "RSVP-" + secrets.token_hex(6).upper()
            cur.execute("""
                INSERT INTO charvak_event_rsvps
                    (rsvp_id, event_id, user_id, user_name, user_email,
                     user_type, tier, paid, payment_id)
                VALUES (%s, %s, %s, %s, %s, 'student', 'pro', TRUE, %s)
                ON CONFLICT DO NOTHING
            """, (rsvp_id, event_id, user_id, user_name, user_email, payment_id))

            # Increment event rsvp_count
            cur.execute("""
                UPDATE charvak_events
                SET rsvp_count = COALESCE(rsvp_count, 0) + 1
                WHERE event_id = %s
            """, (event_id,))

            conn.commit()
            cur.close()
            db.release_pooled_connection(conn)

            logger.info(f"Paid RSVP: {user_email} for {event_id} payment={payment_id}")
            return {"status": "success", "message": "Paid RSVP confirmed", "rsvp_id": rsvp_id}
        except Exception as e:
            logger.error(f"rsvp_paid failed: {e}")
            return {"status": "error", "message": str(e)}
    def get_events(self, event_type: str = None) -> Dict:
        """Get all upcoming events."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            if event_type:
                cur.execute('''
                    SELECT event_id, title, description, event_type, organizer_id,
                           organizer_name, date, duration_minutes, platform,
                           location, link, max_attendees, target_audience,
                           rsvp_count, status, created_at, COALESCE(price_inr, 0)
                    FROM charvak_events
                    WHERE status = %s AND event_type = %s
                    ORDER BY date ASC
                ''', (EventStatus.UPCOMING, event_type))
            else:
                cur.execute('''
                    SELECT event_id, title, description, event_type, organizer_id,
                           organizer_name, date, duration_minutes, platform,
                           location, link, max_attendees, target_audience,
                           rsvp_count, status, created_at, COALESCE(price_inr, 0)
                    FROM charvak_events
                    WHERE status = %s
                    ORDER BY date ASC
                ''', (EventStatus.UPCOMING,))

            events = [self._row_to_event(r) for r in cur.fetchall()]

            cur.execute('SELECT DISTINCT event_type FROM charvak_events')
            types = [r[0] for r in cur.fetchall() if r[0]]
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_events failed: {e}")
            return {"status": "error", "message": "Could not load events"}

        return {
            "status": "success",
            "events": events,
            "count": len(events),
            "total_rsvps": sum(e["rsvp_count"] for e in events),
            "types": types,
        }

    def get_event(self, event_id: str) -> Dict:
        """Get event details."""
        event = self._find_event(event_id)
        if not event:
            return {"status": "error", "message": "Event not found"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT rsvp_id, event_id, user_id, user_name, user_email,
                       user_type, checked_in, checked_in_at, rsvp_at
                FROM charvak_event_rsvps
                WHERE event_id = %s
                ORDER BY rsvp_at ASC
            ''', (event_id,))
            event_rsvps = [self._row_to_rsvp(r) for r in cur.fetchall()]
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_event failed: {e}")
            return {"status": "error", "message": "Could not load event"}

        return {
            "status": "success",
            "event": event,
            "rsvps": event_rsvps,
            "rsvp_count": len(event_rsvps),
            "check_in_count": len([r for r in event_rsvps if r["checked_in"]]),
        }

    # ============================================================
    # ATTENDEE ACTIONS
    # ============================================================

    def check_in(self, rsvp_id: str) -> Dict:
        """Check in attendee."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_event_rsvps
                SET checked_in = TRUE, checked_in_at = CURRENT_TIMESTAMP
                WHERE rsvp_id = %s
            ''', (rsvp_id,))
            affected = cur.rowcount
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"check_in failed: {e}")
            return {"status": "error", "message": "Could not check in"}

        if affected == 0:
            return {"status": "error", "message": "RSVP not found"}
        return {"status": "success", "message": "Checked in!"}

    def cancel_event(self, event_id: str) -> Dict:
        """Cancel an event."""
        event = self._find_event(event_id)
        if not event:
            return {"status": "error", "message": "Event not found"}

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                UPDATE charvak_events SET status = %s WHERE event_id = %s
            ''', (EventStatus.CANCELLED, event_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"cancel_event failed: {e}")
            return {"status": "error", "message": "Could not cancel event"}

        return {"status": "success", "message": "Event cancelled"}

    # ============================================================
    # STATS + HELPERS
    # ============================================================

    def get_stats(self) -> Dict:
        """Get event statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM charvak_events')
            total_events = cur.fetchone()[0]
            cur.execute(
                'SELECT COUNT(*) FROM charvak_events WHERE status = %s',
                (EventStatus.UPCOMING,),
            )
            upcoming = cur.fetchone()[0]
            cur.execute('SELECT COUNT(*) FROM charvak_event_rsvps')
            total_rsvps = cur.fetchone()[0]
            cur.execute(
                'SELECT COUNT(*) FROM charvak_event_rsvps WHERE checked_in = TRUE'
            )
            total_check_ins = cur.fetchone()[0]
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": "Could not load stats"}

        return {
            "status": "success",
            "stats": {
                "total_events": total_events,
                "upcoming_events": upcoming,
                "total_rsvps": total_rsvps,
                "total_check_ins": total_check_ins,
            },
        }

    def _find_event(self, event_id: str) -> Optional[Dict]:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT event_id, title, description, event_type, organizer_id,
                       organizer_name, date, duration_minutes, platform,
                       location, link, max_attendees, target_audience,
                       rsvp_count, status, created_at, COALESCE(price_inr, 0)
                FROM charvak_events WHERE event_id = %s
            ''', (event_id,))
            row = cur.fetchone()
            cur.close(); conn.close()
            return self._row_to_event(row) if row else None
        except Exception as e:
            logger.error(f"_find_event failed: {e}")
            return None

    # ============================================================
    # ROW SERIALIZERS
    # ============================================================

    @staticmethod
    def _row_to_event(row) -> Dict:
        if not row:
            return {}
        # Handle both 16-col (old) and 17-col (with price_inr) rows
        if len(row) == 17:
            (event_id, title, description, event_type, organizer_id, organizer_name,
             date, duration_minutes, platform, location, link, max_attendees,
             target_audience, rsvp_count, status, created_at, price_inr) = row
        else:
            (event_id, title, description, event_type, organizer_id, organizer_name,
             date, duration_minutes, platform, location, link, max_attendees,
             target_audience, rsvp_count, status, created_at) = row
            price_inr = 0
        return {
            "event_id": event_id,
            "title": title,
            "description": description or "",
            "event_type": event_type,
            "organizer_id": organizer_id,
            "organizer_name": organizer_name,
            "date": date,
            "duration_minutes": duration_minutes,
            "platform": platform,
            "location": location or "",
            "link": link or "",
            "max_attendees": max_attendees,
            "target_audience": target_audience,
            "rsvp_count": rsvp_count,
            "status": status,
            "created_at": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
            "price_inr": int(price_inr or 0),
        }

    @staticmethod
    def _row_to_rsvp(row) -> Dict:
        if not row:
            return {}
        (rsvp_id, event_id, user_id, user_name, user_email,
         user_type, checked_in, checked_in_at, rsvp_at) = row
        return {
            "rsvp_id": rsvp_id,
            "event_id": event_id,
            "user_id": user_id,
            "user_name": user_name,
            "user_email": user_email,
            "user_type": user_type,
            "checked_in": bool(checked_in),
            "checked_in_at": checked_in_at.isoformat() if checked_in_at and hasattr(checked_in_at, "isoformat") else None,
            "rsvp_at": rsvp_at.isoformat() if hasattr(rsvp_at, "isoformat") else str(rsvp_at),
        }


events_engine = EventsEngine()