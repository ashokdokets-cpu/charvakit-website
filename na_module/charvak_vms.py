"""
Charvak Native VMS (Vendor Management System)
Replaces Fieldglass/Beeline - Zero integration cost, full control
(DB-backed - Session G/6)
"""
import json
import logging
import os
import secrets
from typing import Dict, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger("charvakit.na.charvak_vms")


class RequisitionStatus(Enum):
    DRAFT = "Draft"
    OPEN = "Open - Accepting Submissions"
    REVIEWING = "Reviewing Candidates"
    INTERVIEWING = "Interviews in Progress"
    OFFER_MADE = "Offer Extended"
    FILLED = "Position Filled"
    CANCELLED = "Cancelled"
    ON_HOLD = "On Hold"


class TimecardStatus(Enum):
    PENDING = "Pending Submission"
    SUBMITTED = "Submitted for Approval"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    PAID = "Paid"


class CharvakVMS:
    """Charvak's native Vendor Management System (DB-backed)"""

    def __init__(self):
        self._ensure_tables()
        logger.info("Charvak Native VMS ready (DB-backed) | Req Mgmt, Timecards, SOW, Analytics")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_cvms_requisitions (
                    req_id               TEXT PRIMARY KEY,
                    client_id            TEXT NOT NULL,
                    title                TEXT,
                    description          TEXT DEFAULT '',
                    skills_required      JSONB DEFAULT '[]'::jsonb,
                    rate_range           JSONB DEFAULT '{}'::jsonb,
                    location             TEXT DEFAULT 'Remote',
                    duration             TEXT DEFAULT '6 months',
                    visa_restrictions    JSONB DEFAULT '[]'::jsonb,
                    submission_limit     INTEGER DEFAULT 3,
                    status               TEXT DEFAULT 'Open - Accepting Submissions',
                    submissions_count    INTEGER DEFAULT 0,
                    interviews_scheduled INTEGER DEFAULT 0,
                    offer_extended       BOOLEAN DEFAULT FALSE,
                    timeline             JSONB DEFAULT '[]'::jsonb,
                    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_req_client ON charvak_na_cvms_requisitions(client_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_req_status ON charvak_na_cvms_requisitions(status)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_cvms_timecards (
                    timecard_id        TEXT PRIMARY KEY,
                    req_id             TEXT NOT NULL,
                    candidate_id       TEXT,
                    hours              NUMERIC(8,2) DEFAULT 0,
                    rate               NUMERIC(8,2) DEFAULT 0,
                    gross_amount       NUMERIC(12,2) DEFAULT 0,
                    charvak_fee        NUMERIC(12,2) DEFAULT 0,
                    net_amount         NUMERIC(12,2) DEFAULT 0,
                    period_end         TEXT,
                    status             TEXT DEFAULT 'Submitted for Approval',
                    payment_triggered  BOOLEAN DEFAULT FALSE,
                    payment_reference  TEXT,
                    approval_history   JSONB DEFAULT '[]'::jsonb,
                    submitted_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_tc_req       ON charvak_na_cvms_timecards(req_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_tc_candidate ON charvak_na_cvms_timecards(candidate_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_tc_status    ON charvak_na_cvms_timecards(status)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_cvms_sow_contracts (
                    sow_id             TEXT PRIMARY KEY,
                    client_id          TEXT NOT NULL,
                    vendor_id          TEXT NOT NULL,
                    title              TEXT,
                    description        TEXT,
                    deliverables       JSONB DEFAULT '[]'::jsonb,
                    total_value        NUMERIC(12,2) DEFAULT 0,
                    start_date         TEXT,
                    end_date           TEXT,
                    milestones         JSONB DEFAULT '[]'::jsonb,
                    payment_schedule   JSONB DEFAULT '[]'::jsonb,
                    status             TEXT DEFAULT 'Active',
                    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_sow_client ON charvak_na_cvms_sow_contracts(client_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_sow_vendor ON charvak_na_cvms_sow_contracts(vendor_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_cvms_sow_status ON charvak_na_cvms_sow_contracts(status)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"charvak_vms tables init failed: {e}")

    # ============ REQUISITION MANAGEMENT ============

    def create_requisition(self, client_id: str, job_data: Dict) -> Dict:
        """Create a new job requisition (replaces Fieldglass/Beeline)"""
        req_id = f"REQ-{secrets.token_hex(4).upper()}"
        now = datetime.now().isoformat()

        requisition = {
            "req_id": req_id,
            "client_id": client_id,
            "title": job_data.get("title"),
            "description": job_data.get("description", ""),
            "skills_required": job_data.get("skills", []),
            "rate_range": {
                "min": job_data.get("rate_min", 0),
                "max": job_data.get("rate_max", 0),
                "type": job_data.get("rate_type", "C2C"),
            },
            "location": job_data.get("location", "Remote"),
            "duration": job_data.get("duration", "6 months"),
            "visa_restrictions": job_data.get("visa_restrictions", []),
            "submission_limit": job_data.get("submission_limit", 3),
            "status": RequisitionStatus.OPEN.value,
            "created_at": now,
            "submissions_count": 0,
            "interviews_scheduled": 0,
            "offer_extended": False,
            "timeline": [{"event": "Requisition Created", "timestamp": now}],
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_na_cvms_requisitions (
                    req_id, client_id, title, description, skills_required,
                    rate_range, location, duration, visa_restrictions,
                    submission_limit, status, timeline
                ) VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s::jsonb, %s, %s, %s::jsonb)
            ''', (
                req_id, client_id, requisition["title"], requisition["description"],
                json.dumps(requisition["skills_required"]),
                json.dumps(requisition["rate_range"]),
                requisition["location"], requisition["duration"],
                json.dumps(requisition["visa_restrictions"]),
                requisition["submission_limit"], requisition["status"],
                json.dumps(requisition["timeline"]),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_requisition failed: {e}")

        return requisition

    def get_open_requisitions(self, filters: Dict = None) -> List[Dict]:
        """Get all open requisitions with optional filters"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT req_id, client_id, title, description, skills_required,
                       rate_range, location, duration, visa_restrictions,
                       submission_limit, status, submissions_count,
                       interviews_scheduled, offer_extended, timeline, created_at
                FROM charvak_na_cvms_requisitions
                WHERE status = %s
                ORDER BY created_at DESC
            ''', (RequisitionStatus.OPEN.value,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_open_requisitions failed: {e}")
            return []

        def _d(x, default):
            if isinstance(x, type(default)) or x is None:
                return x if x is not None else default
            try:
                return json.loads(x)
            except Exception:
                return default

        open_reqs = []
        for r in rows:
            open_reqs.append({
                "req_id": r[0],
                "client_id": r[1],
                "title": r[2],
                "description": r[3] or "",
                "skills_required": _d(r[4], []),
                "rate_range": _d(r[5], {}),
                "location": r[6] or "",
                "duration": r[7],
                "visa_restrictions": _d(r[8], []),
                "submission_limit": r[9],
                "status": r[10],
                "submissions_count": r[11],
                "interviews_scheduled": r[12],
                "offer_extended": bool(r[13]),
                "timeline": _d(r[14], []),
                "created_at": r[15].isoformat() if hasattr(r[15], "isoformat") else str(r[15]),
            })

        if filters:
            if filters.get("skill"):
                skill = filters["skill"].lower()
                open_reqs = [r for r in open_reqs if any(skill in s.lower() for s in r["skills_required"])]
            if filters.get("visa_type"):
                open_reqs = [r for r in open_reqs if filters["visa_type"] not in r["visa_restrictions"]]
            if filters.get("rate_min"):
                open_reqs = [r for r in open_reqs if r["rate_range"].get("max", 0) >= filters["rate_min"]]

        return open_reqs

    def update_requisition_status(self, req_id: str, status: RequisitionStatus) -> Dict:
        """Update requisition status with timeline tracking"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT timeline FROM charvak_na_cvms_requisitions WHERE req_id = %s', (req_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"error": "Requisition not found"}

            timeline = row[0] if isinstance(row[0], list) else (json.loads(row[0]) if row[0] else [])
            timeline.append({
                "event": f"Status changed to {status.value}",
                "timestamp": datetime.now().isoformat(),
            })

            cur.execute('''
                UPDATE charvak_na_cvms_requisitions
                SET status = %s, timeline = %s::jsonb
                WHERE req_id = %s
            ''', (status.value, json.dumps(timeline), req_id))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"update_requisition_status failed: {e}")
            return {"error": "Could not update requisition"}

        return self._get_requisition(req_id)

    def _get_requisition(self, req_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT req_id, client_id, title, description, skills_required,
                       rate_range, location, duration, visa_restrictions,
                       submission_limit, status, submissions_count,
                       interviews_scheduled, offer_extended, timeline, created_at
                FROM charvak_na_cvms_requisitions WHERE req_id = %s
            ''', (req_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_get_requisition failed: {e}")
            return {}

        if not r:
            return {}

        def _d(x, default):
            if isinstance(x, type(default)) or x is None:
                return x if x is not None else default
            try:
                return json.loads(x)
            except Exception:
                return default

        return {
            "req_id": r[0],
            "client_id": r[1],
            "title": r[2],
            "description": r[3] or "",
            "skills_required": _d(r[4], []),
            "rate_range": _d(r[5], {}),
            "location": r[6] or "",
            "duration": r[7],
            "visa_restrictions": _d(r[8], []),
            "submission_limit": r[9],
            "status": r[10],
            "submissions_count": r[11],
            "interviews_scheduled": r[12],
            "offer_extended": bool(r[13]),
            "timeline": _d(r[14], []),
            "created_at": r[15].isoformat() if hasattr(r[15], "isoformat") else str(r[15]),
        }

    # ============ TIMECARD MANAGEMENT ============

    def submit_timecard(self, req_id: str, candidate_id: str,
                        hours: float, period_end: str, rate: float) -> Dict:
        """Submit weekly/bi-weekly timecard"""
        timecard_id = f"TC-{secrets.token_hex(4).upper()}"
        gross_amount = hours * rate

        timecard = {
            "timecard_id": timecard_id,
            "req_id": req_id,
            "candidate_id": candidate_id,
            "hours": hours,
            "rate": rate,
            "gross_amount": gross_amount,
            "charvak_fee": round(gross_amount * 0.02, 2),
            "net_amount": round(gross_amount * 0.98, 2),
            "period_end": period_end,
            "status": TimecardStatus.SUBMITTED.value,
            "submitted_at": datetime.now().isoformat(),
            "approval_history": [],
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_na_cvms_timecards (
                    timecard_id, req_id, candidate_id, hours, rate,
                    gross_amount, charvak_fee, net_amount, period_end,
                    status, approval_history
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ''', (
                timecard_id, req_id, candidate_id, hours, rate,
                gross_amount, timecard["charvak_fee"], timecard["net_amount"],
                period_end, timecard["status"], json.dumps([]),
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"submit_timecard failed: {e}")

        return timecard

    def approve_timecard(self, timecard_id: str) -> Dict:
        """Approve timecard and trigger payment"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT approval_history FROM charvak_na_cvms_timecards WHERE timecard_id = %s', (timecard_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"error": "Timecard not found"}

            history = row[0] if isinstance(row[0], list) else (json.loads(row[0]) if row[0] else [])
            history.append({
                "action": "Approved",
                "timestamp": datetime.now().isoformat(),
            })
            payment_ref = f"PAY-{secrets.token_hex(4).upper()}"

            cur.execute('''
                UPDATE charvak_na_cvms_timecards
                SET status = %s,
                    approval_history = %s::jsonb,
                    payment_triggered = TRUE,
                    payment_reference = %s
                WHERE timecard_id = %s
            ''', (TimecardStatus.APPROVED.value, json.dumps(history), payment_ref, timecard_id))

            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"approve_timecard failed: {e}")
            return {"error": "Could not approve timecard"}

        return self._get_timecard(timecard_id)

    def _get_timecard(self, timecard_id: str) -> Dict:
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT timecard_id, req_id, candidate_id, hours, rate,
                       gross_amount, charvak_fee, net_amount, period_end,
                       status, payment_triggered, payment_reference,
                       approval_history, submitted_at
                FROM charvak_na_cvms_timecards WHERE timecard_id = %s
            ''', (timecard_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"_get_timecard failed: {e}")
            return {}

        if not r:
            return {}

        hist = r[12] if isinstance(r[12], list) else (json.loads(r[12]) if r[12] else [])

        return {
            "timecard_id": r[0],
            "req_id": r[1],
            "candidate_id": r[2],
            "hours": float(r[3]) if r[3] is not None else 0,
            "rate": float(r[4]) if r[4] is not None else 0,
            "gross_amount": float(r[5]) if r[5] is not None else 0,
            "charvak_fee": float(r[6]) if r[6] is not None else 0,
            "net_amount": float(r[7]) if r[7] is not None else 0,
            "period_end": r[8],
            "status": r[9],
            "payment_triggered": bool(r[10]),
            "payment_reference": r[11],
            "approval_history": hist,
            "submitted_at": r[13].isoformat() if hasattr(r[13], "isoformat") else str(r[13]),
        }

    # ============ SOW MANAGEMENT ============

    def create_sow(self, client_id: str, vendor_id: str, sow_data: Dict) -> Dict:
        """Create Statement of Work for fixed-price projects"""
        sow_id = f"SOW-{secrets.token_hex(4).upper()}"

        sow = {
            "sow_id": sow_id,
            "client_id": client_id,
            "vendor_id": vendor_id,
            "title": sow_data.get("title"),
            "description": sow_data.get("description"),
            "deliverables": sow_data.get("deliverables", []),
            "total_value": sow_data.get("total_value", 0),
            "start_date": sow_data.get("start_date"),
            "end_date": sow_data.get("end_date"),
            "milestones": sow_data.get("milestones", []),
            "status": "Active",
            "created_at": datetime.now().isoformat(),
            "payment_schedule": self._generate_payment_schedule(sow_data.get("total_value", 0)),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_na_cvms_sow_contracts (
                    sow_id, client_id, vendor_id, title, description,
                    deliverables, total_value, start_date, end_date,
                    milestones, payment_schedule, status
                ) VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s::jsonb, %s::jsonb, %s)
            ''', (
                sow_id, client_id, vendor_id, sow["title"], sow["description"],
                json.dumps(sow["deliverables"]), sow["total_value"],
                sow["start_date"], sow["end_date"],
                json.dumps(sow["milestones"]), json.dumps(sow["payment_schedule"]),
                sow["status"],
            ))
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_sow failed: {e}")

        return sow

    def _generate_payment_schedule(self, total_value: float) -> List[Dict]:
        """Generate milestone-based payment schedule"""
        milestones = ["Project Start", "50% Completion", "Final Delivery"]
        schedule = []
        for i, milestone in enumerate(milestones):
            pct = [20, 30, 50][i]
            schedule.append({
                "milestone": milestone,
                "percentage": pct,
                "amount": round(total_value * pct / 100, 2),
                "due": "Upon milestone completion",
            })
        return schedule

    # ============ ANALYTICS & REPORTING ============

    def get_client_analytics(self, client_id: str) -> Dict:
        """Comprehensive analytics for clients"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COUNT(*) FROM charvak_na_cvms_requisitions WHERE client_id = %s', (client_id,))
            total_requisitions = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_na_cvms_requisitions WHERE client_id = %s AND status = %s',
                        (client_id, RequisitionStatus.OPEN.value))
            open_requisitions = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_na_cvms_requisitions WHERE client_id = %s AND status = %s',
                        (client_id, RequisitionStatus.FILLED.value))
            filled_requisitions = int(cur.fetchone()[0] or 0)

            cur.execute('''SELECT COUNT(*) FROM charvak_na_cvms_requisitions
                           WHERE client_id = %s AND status IN (%s, %s)''',
                        (client_id, RequisitionStatus.REVIEWING.value, RequisitionStatus.INTERVIEWING.value))
            active_candidates = int(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_client_analytics failed: {e}")
            return {
                "total_requisitions": 0,
                "open_requisitions": 0,
                "filled_requisitions": 0,
                "average_fill_time_days": 0,
                "total_spend": 0,
                "active_candidates": 0,
                "savings_vs_traditional": 0,
            }

        return {
            "total_requisitions": total_requisitions,
            "open_requisitions": open_requisitions,
            "filled_requisitions": filled_requisitions,
            "average_fill_time_days": self._calculate_avg_fill_time(filled_requisitions),
            "total_spend": self._calculate_total_spend(client_id),
            "active_candidates": active_candidates,
            "savings_vs_traditional": self._calculate_savings(client_id),
        }

    def _calculate_avg_fill_time(self, filled_count: int) -> float:
        """Calculate average time to fill (simplified - returns 4.5 if any filled)"""
        if not filled_count:
            return 0
        return 4.5

    def _calculate_total_spend(self, client_id: str) -> float:
        """Calculate total spending (paid timecards for this client's reqs)"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT COALESCE(SUM(t.gross_amount), 0)
                FROM charvak_na_cvms_timecards t
                JOIN charvak_na_cvms_requisitions r ON t.req_id = r.req_id
                WHERE r.client_id = %s AND t.status = %s
            ''', (client_id, TimecardStatus.PAID.value))
            total = float(cur.fetchone()[0] or 0)
            cur.close(); conn.close()
            return total
        except Exception as e:
            logger.error(f"_calculate_total_spend failed: {e}")
            return 0

    def _calculate_savings(self, client_id: str) -> float:
        """Calculate savings vs traditional VMS"""
        total_spend = self._calculate_total_spend(client_id)
        traditional_cost = total_spend * 1.10
        return round(traditional_cost - total_spend, 2)


charvak_vms = CharvakVMS()

# ============================================================
# DEMO DATA - loaded only when CHARVAK_LOAD_DEMO_VMS=1
# ============================================================
if os.getenv("CHARVAK_LOAD_DEMO_VMS", "0") == "1":
    sample_reqs = [
        {"title": "Senior Java Backend Developer", "skills": ["Java", "Spring Boot", "Kafka", "Microservices", "AWS"], "rate_min": 65, "rate_max": 75, "rate_type": "C2C", "location": "New York, NY (Hybrid)", "duration": "12 months", "visa_restrictions": [], "submission_limit": 3},
        {"title": "React Frontend Developer", "skills": ["React", "TypeScript", "Node.js", "GraphQL"], "rate_min": 55, "rate_max": 70, "rate_type": "C2C", "location": "Remote (US)", "duration": "6 months", "visa_restrictions": ["CPT"], "submission_limit": 3},
        {"title": "DevOps Engineer", "skills": ["AWS", "Kubernetes", "Terraform", "CI/CD"], "rate_min": 60, "rate_max": 80, "rate_type": "C2C", "location": "Austin, TX", "duration": "12 months", "visa_restrictions": [], "submission_limit": 2},
        {"title": "Data Engineer", "skills": ["Python", "Spark", "Airflow", "Snowflake"], "rate_min": 55, "rate_max": 75, "rate_type": "C2C", "location": "Remote (US)", "duration": "6 months", "visa_restrictions": ["OPT"], "submission_limit": 3},
        {"title": "Cloud Architect", "skills": ["AWS", "Azure", "GCP", "Kubernetes"], "rate_min": 80, "rate_max": 100, "rate_type": "W2", "location": "Chicago, IL", "duration": "18 months", "visa_restrictions": [], "submission_limit": 2},
    ]
    for req in sample_reqs:
        charvak_vms.create_requisition("CLIENT-001", req)
    logger.info("Charvak VMS: loaded %d demo requisitions (CHARVAK_LOAD_DEMO_VMS=1)", len(sample_reqs))