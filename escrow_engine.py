"""
Charvak Escrow Engine (Dokets VouchAI)
Handles secure payment escrow for B2B transactions
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets
import json

logger = logging.getLogger("charvakit.escrow")

ESCROW_MODE = os.getenv("ESCROW_MODE", "test")
PLATFORM_FEE_PERCENT = 1.0  # Dokets VouchAI: 1% transaction fee


class EscrowStatus:
    AWAITING_DEPOSIT = "awaiting_deposit"
    FUNDS_HELD = "funds_held"
    WORK_IN_PROGRESS = "work_in_progress"
    WORK_DELIVERED = "work_delivered"
    UNDER_REVIEW = "under_review"
    DISPUTED = "disputed"
    RELEASED = "released"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class EscrowEngine:
    """Handles all escrow transactions via Dokets VouchAI."""
    
    def __init__(self):
        self.mode = ESCROW_MODE
        self._ensure_tables()
        logger.info(f"Escrow Engine ready (DB-backed): {'LIVE' if self.mode == 'live' else 'TEST'} mode | Fee: {PLATFORM_FEE_PERCENT}%")

    def _ensure_tables(self):
        """Idempotent table creation for escrow transactions."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_escrow_transactions (
                    escrow_id              TEXT PRIMARY KEY,
                    client_name            TEXT,
                    client_email           TEXT,
                    vendor_name            TEXT,
                    vendor_email           TEXT,
                    amount                 NUMERIC(12,2) NOT NULL,
                    currency               TEXT DEFAULT 'INR',
                    platform_fee           NUMERIC(12,2) DEFAULT 0,
                    vendor_payout          NUMERIC(12,2) DEFAULT 0,
                    description            TEXT DEFAULT '',
                    milestones             JSONB DEFAULT '[]'::jsonb,
                    status                 TEXT DEFAULT 'awaiting_deposit',
                    payment_method         TEXT DEFAULT 'Dokets VouchAI Escrow',
                    payment_details        JSONB,
                    delivery_data          JSONB,
                    dispute                JSONB,
                    duration_days          INTEGER DEFAULT 30,
                    payout_status          TEXT DEFAULT 'not_due',
                    payout_method          TEXT,
                    payout_reference       TEXT,
                    payout_amount          NUMERIC(12,2),
                    payout_at              TIMESTAMP,
                    created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    funded_at              TIMESTAMP,
                    delivered_at           TIMESTAMP,
                    released_at            TIMESTAMP,
                    expires_at             TIMESTAMP
                )
            """)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"escrow table init failed: {e}")


    # ============================================================
    # CREATE ESCROW TRANSACTION
    # ============================================================
    
    def create_escrow(self, data: Dict) -> Dict:
        """Create a new escrow transaction."""
        escrow_id = f"ESC-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        amount = float(data.get("amount", 0))
        fee_percent = float(data.get("platform_fee_percent", PLATFORM_FEE_PERCENT))
        platform_fee = round(amount * fee_percent / 100, 2)
        vendor_payout = round(amount - platform_fee, 2)
        currency = data.get("currency", "INR")
        duration_days = int(data.get("duration_days", 30))
        expires_at = datetime.now() + timedelta(days=duration_days)
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO charvak_escrow_transactions
                    (escrow_id, client_name, client_email, vendor_name, vendor_email,
                     amount, currency, platform_fee, vendor_payout, description,
                     milestones, status, payment_method, duration_days, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                        %s::jsonb, 'awaiting_deposit', 'Dokets VouchAI Escrow', %s, %s)
            """, (escrow_id, data.get("client_name"), data.get("client_email"),
                  data.get("vendor_name"), data.get("vendor_email"),
                  amount, currency, platform_fee, vendor_payout,
                  data.get("description", ""),
                  json.dumps(data.get("milestones", [])),
                  duration_days, expires_at))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Escrow created: {escrow_id} | {data.get('client_name')} -> {data.get('vendor_name')} | {amount} {currency}")
            return {
                "status": "success",
                "escrow_id": escrow_id,
                "amount": amount,
                "platform_fee": platform_fee,
                "vendor_receives": vendor_payout,
                "message": "Escrow created. Client must deposit funds to activate.",
                "payment_link": f"/invoice?service=Escrow+Deposit&client={data.get('client_name')}&amount={int(amount)}",
                "expires_at": expires_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"create_escrow failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # DEPOSIT FUNDS
    # ============================================================
    
    def deposit_funds(self, escrow_id: str, payment_details: Dict) -> Dict:
        """Client deposits funds into escrow."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT status, amount, currency, platform_fee FROM charvak_escrow_transactions WHERE escrow_id = %s", (escrow_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Escrow ID not found"}
            if row[0] != "awaiting_deposit":
                cur.close(); conn.close()
                return {"status": "error", "message": f"Cannot deposit. Current status: {row[0]}"}
            cur.execute("""
                UPDATE charvak_escrow_transactions
                SET status = 'funds_held', funded_at = CURRENT_TIMESTAMP,
                    payment_details = %s::jsonb
                WHERE escrow_id = %s
            """, (json.dumps(payment_details or {}), escrow_id))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Escrow funded: {escrow_id} | {row[1]} {row[2]}")
            return {
                "status": "success",
                "escrow_id": escrow_id,
                "amount_held": float(row[1]),
                "message": "Funds secured in escrow. Vendor can begin work.",
                "next_step": "Vendor delivers work -> Client reviews -> Funds released",
            }
        except Exception as e:
            logger.error(f"deposit_funds failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # DELIVER WORK
    # ============================================================
    
    def deliver_work(self, escrow_id: str, delivery_data: Dict) -> Dict:
        """Vendor marks work as delivered."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT status FROM charvak_escrow_transactions WHERE escrow_id = %s", (escrow_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Escrow ID not found"}
            if row[0] not in ("funds_held", "work_in_progress"):
                cur.close(); conn.close()
                return {"status": "error", "message": f"Cannot deliver. Current status: {row[0]}"}
            cur.execute("""
                UPDATE charvak_escrow_transactions
                SET status = 'work_delivered', delivered_at = CURRENT_TIMESTAMP,
                    delivery_data = %s::jsonb
                WHERE escrow_id = %s
            """, (json.dumps(delivery_data or {}), escrow_id))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Work delivered for escrow: {escrow_id}")
            return {
                "status": "success",
                "escrow_id": escrow_id,
                "message": "Work delivered. Awaiting client review.",
                "review_deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                "auto_release": "Funds will auto-release in 7 days if no dispute is raised",
            }
        except Exception as e:
            logger.error(f"deliver_work failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # RELEASE / APPROVE
    # ============================================================
    
    def release_funds(self, escrow_id: str) -> Dict:
        """Client approves work -> funds released. Marks pending manual payout."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT status, vendor_name, vendor_payout, platform_fee
                FROM charvak_escrow_transactions WHERE escrow_id = %s
            """, (escrow_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Escrow ID not found"}
            if row[0] != "work_delivered":
                cur.close(); conn.close()
                return {"status": "error", "message": f"Cannot release. Current status: {row[0]}"}
            cur.execute("""
                UPDATE charvak_escrow_transactions
                SET status = 'released',
                    released_at = CURRENT_TIMESTAMP,
                    payout_status = 'pending_manual',
                    payout_amount = %s
                WHERE escrow_id = %s
            """, (row[2], escrow_id))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Funds released: {escrow_id} | Vendor receives {row[2]} (pending manual payout)")
            return {
                "status": "success",
                "escrow_id": escrow_id,
                "amount_released": float(row[2]),
                "platform_fee": float(row[3]),
                "message": f"Funds released to {row[1]}. Transaction complete.",
                "payout_status": "pending_manual",
                "note": "Manual bank/UPI transfer required. Mark as paid in admin panel.",
            }
        except Exception as e:
            logger.error(f"release_funds failed: {e}")
            return {"status": "error", "message": str(e)}


    # ============================================================
    # DISPUTE
    # ============================================================
    
    def raise_dispute(self, escrow_id: str, dispute_data: Dict) -> Dict:
        """Raise a dispute on an escrow transaction."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT escrow_id FROM charvak_escrow_transactions WHERE escrow_id = %s", (escrow_id,))
            if not cur.fetchone():
                cur.close(); conn.close()
                return {"status": "error", "message": "Escrow ID not found"}
            dispute = {
                "raised_by": dispute_data.get("raised_by"),
                "reason": dispute_data.get("reason"),
                "details": dispute_data.get("details"),
                "raised_at": datetime.now().isoformat(),
                "status": "open",
            }
            cur.execute("""
                UPDATE charvak_escrow_transactions
                SET status = 'disputed', dispute = %s::jsonb
                WHERE escrow_id = %s
            """, (json.dumps(dispute), escrow_id))
            conn.commit()
            cur.close(); conn.close()
            logger.warning(f"Dispute raised: {escrow_id} by {dispute_data.get('raised_by')}")
            return {
                "status": "success",
                "escrow_id": escrow_id,
                "message": "Dispute registered. Our team will review within 48 hours.",
                "resolution_process": [
                    "AI-powered dispute analysis",
                    "Mediation by Charvak team if needed",
                    "Evidence review from both parties",
                    "Final decision within 7 business days",
                ],
            }
        except Exception as e:
            logger.error(f"raise_dispute failed: {e}")
            return {"status": "error", "message": str(e)}
    def resolve_dispute(self, escrow_id: str, resolution: Dict) -> Dict:
        """Admin resolves a dispute."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT status, dispute FROM charvak_escrow_transactions WHERE escrow_id = %s", (escrow_id,))
            row = cur.fetchone()
            if not row or row[0] != "disputed":
                cur.close(); conn.close()
                return {"status": "error", "message": "Escrow ID not found or not in dispute"}
            dispute = row[1] if isinstance(row[1], dict) else json.loads(row[1] or "{}")
            dispute["status"] = "resolved"
            dispute["resolution"] = resolution
            dispute["resolved_at"] = datetime.now().isoformat()
            decision = resolution.get("decision")
            new_status = "released" if decision == "release_to_vendor" else ("refunded" if decision == "refund_to_client" else "released")
            cur.execute("""
                UPDATE charvak_escrow_transactions
                SET status = %s, dispute = %s::jsonb
                WHERE escrow_id = %s
            """, (new_status, json.dumps(dispute), escrow_id))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Dispute resolved: {escrow_id} -> {decision}")
            return {
                "status": "success",
                "escrow_id": escrow_id,
                "resolution": decision,
                "message": "Dispute resolved",
            }
        except Exception as e:
            logger.error(f"resolve_dispute failed: {e}")
            return {"status": "error", "message": str(e)}




    # ============================================================
    # QUERY
    # ============================================================
    
    def get_escrow(self, escrow_id: str) -> Dict:
        """Get escrow transaction details."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT escrow_id, client_name, client_email, vendor_name, vendor_email,
                       amount, currency, platform_fee, vendor_payout, description,
                       milestones, status, payment_method, payment_details,
                       delivery_data, dispute, duration_days,
                       payout_status, payout_method, payout_reference, payout_amount,
                       payout_at, created_at, funded_at, delivered_at, released_at, expires_at
                FROM charvak_escrow_transactions WHERE escrow_id = %s
            """, (escrow_id,))
            r = cur.fetchone()
            cur.close(); conn.close()
            if not r:
                return {"status": "error", "message": "Escrow ID not found"}
            return {"status": "success", "transaction": {
                "escrow_id": r[0],
                "client_name": r[1], "client_email": r[2],
                "vendor_name": r[3], "vendor_email": r[4],
                "amount": float(r[5] or 0), "currency": r[6],
                "platform_fee": float(r[7] or 0), "vendor_payout": float(r[8] or 0),
                "description": r[9] or "",
                "milestones": r[10] if isinstance(r[10], list) else json.loads(r[10] or "[]"),
                "status": r[11], "payment_method": r[12],
                "payment_details": r[13] if isinstance(r[13], dict) else (json.loads(r[13]) if r[13] else None),
                "delivery_data": r[14] if isinstance(r[14], dict) else (json.loads(r[14]) if r[14] else None),
                "dispute": r[15] if isinstance(r[15], dict) else (json.loads(r[15]) if r[15] else None),
                "duration_days": r[16],
                "payout_status": r[17], "payout_method": r[18],
                "payout_reference": r[19],
                "payout_amount": float(r[20]) if r[20] else None,
                "payout_at": r[21].isoformat() if r[21] else None,
                "created_at": r[22].isoformat() if r[22] else None,
                "funded_at": r[23].isoformat() if r[23] else None,
                "delivered_at": r[24].isoformat() if r[24] else None,
                "released_at": r[25].isoformat() if r[25] else None,
                "expires_at": r[26].isoformat() if r[26] else None,
            }}
        except Exception as e:
            logger.error(f"get_escrow failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_user_escrows(self, email: str) -> Dict:
        """Get all escrows for a user (client or vendor)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT escrow_id, client_name, client_email, vendor_name, vendor_email,
                       amount, currency, platform_fee, vendor_payout, description,
                       milestones, status, payment_method,
                       payout_status, payout_amount,
                       created_at, funded_at, delivered_at, released_at
                FROM charvak_escrow_transactions
                WHERE client_email = %s OR vendor_email = %s
                ORDER BY created_at DESC
            """, (email, email))
            rows = cur.fetchall()
            cur.close(); conn.close()
            escrows = []
            for r in rows:
                escrows.append({
                    "escrow_id": r[0],
                    "client_name": r[1], "client_email": r[2],
                    "vendor_name": r[3], "vendor_email": r[4],
                    "amount": float(r[5] or 0), "currency": r[6],
                    "platform_fee": float(r[7] or 0), "vendor_payout": float(r[8] or 0),
                    "description": r[9] or "",
                    "milestones": r[10] if isinstance(r[10], list) else json.loads(r[10] or "[]"),
                    "status": r[11], "payment_method": r[12],
                    "payout_status": r[13],
                    "payout_amount": float(r[14]) if r[14] else None,
                    "created_at": r[15].isoformat() if r[15] else None,
                    "funded_at": r[16].isoformat() if r[16] else None,
                    "delivered_at": r[17].isoformat() if r[17] else None,
                    "released_at": r[18].isoformat() if r[18] else None,
                })
            active = [e for e in escrows if e["status"] not in ("released", "refunded", "cancelled")]
            completed = [e for e in escrows if e["status"] == "released"]
            return {
                "status": "success",
                "escrows": escrows,
                "count": len(escrows),
                "active": len(active),
                "completed": len(completed),
            }
        except Exception as e:
            logger.error(f"get_user_escrows failed: {e}")
            return {"status": "error", "message": str(e), "escrows": [], "count": 0}

    def get_stats(self) -> Dict:
        """Get escrow system statistics."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM charvak_escrow_transactions")
            total = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_escrow_transactions WHERE status NOT IN ('released','refunded','cancelled')")
            active = cur.fetchone()[0] or 0
            cur.execute("SELECT COALESCE(SUM(amount), 0) FROM charvak_escrow_transactions WHERE status IN ('funds_held','work_in_progress','work_delivered')")
            total_held = float(cur.fetchone()[0] or 0)
            cur.execute("SELECT COALESCE(SUM(platform_fee), 0) FROM charvak_escrow_transactions WHERE status = 'released'")
            total_fees = float(cur.fetchone()[0] or 0)
            cur.execute("SELECT COUNT(*) FROM charvak_escrow_transactions WHERE status = 'disputed'")
            disputed = cur.fetchone()[0] or 0
            cur.execute("SELECT COUNT(*) FROM charvak_escrow_transactions WHERE payout_status = 'pending_manual'")
            pending_payouts = cur.fetchone()[0] or 0
            cur.close(); conn.close()
            return {
                "status": "success",
                "stats": {
                    "total_transactions": total,
                    "active_escrows": active,
                    "funds_held": round(total_held, 2),
                    "platform_fees_earned": round(total_fees, 2),
                    "disputed": disputed,
                    "pending_payouts": pending_payouts,
                    "fee_percentage": PLATFORM_FEE_PERCENT,
                },
            }
        except Exception as e:
            logger.error(f"get_stats failed: {e}")
            return {"status": "error", "message": str(e)}

    # ============================================================
    # MANUAL PAYOUT (admin actions)
    # ============================================================

    def get_pending_payouts(self) -> Dict:
        """Admin: list escrows where funds are released but payout not yet done."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT escrow_id, client_name, vendor_name, vendor_email,
                       vendor_payout, currency, released_at, payout_amount,
                       description
                FROM charvak_escrow_transactions
                WHERE payout_status = 'pending_manual'
                ORDER BY released_at ASC
            """)
            rows = cur.fetchall()
            cur.close(); conn.close()
            pending = []
            total_due = 0.0
            for r in rows:
                pending.append({
                    "escrow_id": r[0],
                    "client_name": r[1],
                    "vendor_name": r[2],
                    "vendor_email": r[3],
                    "amount": float(r[4] or 0),
                    "currency": r[5],
                    "released_at": r[6].isoformat() if r[6] else None,
                    "payout_amount": float(r[7]) if r[7] else 0.0,
                    "description": r[8] or "",
                })
                total_due += float(r[7] or r[4] or 0)
            return {
                "status": "success",
                "pending": pending,
                "count": len(pending),
                "total_due": round(total_due, 2),
            }
        except Exception as e:
            logger.error(f"get_pending_payouts failed: {e}")
            return {"status": "error", "message": str(e), "pending": [], "count": 0}

    def mark_payout_paid(self, escrow_id: str, method: str = "bank", reference: str = "", notes: str = "") -> Dict:
        """Admin: mark a manual payout as completed (bank/UPI transfer done)."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT payout_status, payout_amount, vendor_payout, vendor_name, vendor_email
                FROM charvak_escrow_transactions WHERE escrow_id = %s
            """, (escrow_id,))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Escrow ID not found"}
            if row[0] == "paid":
                cur.close(); conn.close()
                return {"status": "already_paid", "message": "Payout already marked as paid"}
            cur.execute("""
                UPDATE charvak_escrow_transactions
                SET payout_status = 'paid',
                    payout_method = %s,
                    payout_reference = %s,
                    payout_at = CURRENT_TIMESTAMP
                WHERE escrow_id = %s
            """, (method, reference, escrow_id))
            conn.commit()
            cur.close(); conn.close()
            logger.info(f"Payout marked paid: {escrow_id} -> {row[4]} ({method} ref {reference})")
            return {
                "status": "success",
                "escrow_id": escrow_id,
                "vendor_name": row[3],
                "vendor_email": row[4],
                "amount": float(row[2] or 0),
                "method": method,
                "reference": reference,
                "message": "Payout marked as paid",
            }
        except Exception as e:
            logger.error(f"mark_payout_paid failed: {e}")
            return {"status": "error", "message": str(e)}



# ============================================================
# SINGLETON
# ============================================================
escrow_engine = EscrowEngine()
