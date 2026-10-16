"""
State-PSC Free-Mock Funnel Engine (Session 44-A3)

Provides:
  - Free-tier question serving (15 questions, no login)
  - Rs 49 currency-aware unlock order creation
  - Payment verification + full-mock serving

Reuses:
  - exam_prep_engine.get_free_mock_questions() for the free tier
  - exam_prep_engine.generate_questions() for the paid full mock
  - payment_engine.resolve_public_price("state_psc_full_mock", cc)
  - payment_engine Razorpay + PayPal order creation
"""

import os
import hmac
import time
import base64
import hashlib
import logging
import secrets
from typing import Dict, Optional

from exam_prep_engine import exam_prep_engine
from payment_engine import payment_engine
from database import db

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-not-secret-not-used-for-prod")

# The 10 supported state-PSC exams for the free funnel
SUPPORTED_EXAMS = {
    # Tier 1 (shipped 2026-10-16 in Session 44-A3)
    "uppsc_pcs", "mpsc_rajyaseva", "rpsc_ras", "wbpsc_wbcs",
    "tnpsc_group1", "kpsc_kas", "mppsc_sse", "gpsc_class12",
    "apsc_cce", "kpsc_kerala",
    # Tier 2 (extended 2026-10-16 after bank seeding verified)
    "opsc_ocs", "cgpsc_sse", "jpsc_ccs", "ukpsc_pcs", "hpsc_hcs",
    "ppsc_pcs", "mpsc_manipur", "jkpsc_kas", "tnpsc_group2", "tpsc_tcs",
}

# Full mock size (questions)
FULL_MOCK_QUESTIONS = 100
FULL_MOCK_SECTIONS_PER = 34  # 3 sections * 34 = 102, capped at 100


# ---------------------------------------------------------------
# Table (self-healing DDL)
# ---------------------------------------------------------------

def _ensure_table() -> None:
    """Self-healing DDL for charvak_state_psc_unlocks."""
    conn = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS charvak_state_psc_unlocks (
                unlock_id        TEXT PRIMARY KEY,
                exam_id          TEXT NOT NULL,
                email            TEXT NOT NULL,
                country_code     TEXT,
                currency         TEXT,
                amount_local     NUMERIC,
                gateway          TEXT,
                razorpay_order_id    TEXT,
                razorpay_payment_id  TEXT,
                paypal_order_id      TEXT,
                status           TEXT DEFAULT 'pending',
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (exam_id, email)
            )
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_state_psc_unlocks_email
            ON charvak_state_psc_unlocks (email, created_at DESC)
        """)
        conn.commit()
        cur.close()
    except Exception as e:
        logger.warning(f"_ensure_table skipped: {e}")
    finally:
        if conn:
            try: conn.close()
            except Exception: pass


# ---------------------------------------------------------------
# Free-tier signed token (HMAC, stateless)
# ---------------------------------------------------------------

def make_free_token(exam_id: str) -> str:
    payload = f"{exam_id}|{int(time.time())}"
    sig = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()[:24]
    raw = f"{payload}|{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def verify_free_token(token: str, expected_exam_id: str, max_age_s: int = 3600) -> bool:
    try:
        padded = token + "=" * (-len(token) % 4)
        raw = base64.urlsafe_b64decode(padded.encode()).decode()
        exam_id, ts_s, sig = raw.rsplit("|", 2)
        if exam_id != expected_exam_id:
            return False
        if abs(int(time.time()) - int(ts_s)) > max_age_s:
            return False
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{exam_id}|{ts_s}".encode(),
            hashlib.sha256,
        ).hexdigest()[:24]
        return hmac.compare_digest(sig, expected_sig)
    except Exception:
        return False


# ---------------------------------------------------------------
# Free tier
# ---------------------------------------------------------------

def get_free_questions(exam_id: str) -> Dict:
    """Return 15 questions + a signed token. Never raises."""
    if exam_id not in SUPPORTED_EXAMS:
        return {"status": "error", "message": "Exam not supported for free mock"}

    fetch = exam_prep_engine.get_free_mock_questions(exam_id, sections=3, per_section=5)
    # Session 44-A3b: pass through warming_up status (lazy seeding in progress)
    if fetch.get("status") in ("error", "warming_up"):
        return fetch
    if fetch.get("status") != "success":
        return fetch

    safe_questions = []
    for q in fetch.get("questions", []):
        safe_questions.append({
            "question_text": q.get("question_text"),
            "options": q.get("options") or [],
            "topic": q.get("topic"),
        })

    return {
        "status": "success",
        "exam_id": exam_id,
        "exam": fetch.get("exam"),
        "sections_used": fetch.get("sections_used"),
        "total": len(safe_questions),
        "questions": safe_questions,
        "free_token": make_free_token(exam_id),
    }


def score_free_answers(exam_id: str, answers: list) -> Dict:
    """Score the free-tier answers. Answers is a list of selected indexes."""
    fetch = exam_prep_engine.get_free_mock_questions(exam_id, sections=3, per_section=5)
    # Session 44-A3b: pass through warming_up status (lazy seeding in progress)
    if fetch.get("status") in ("error", "warming_up"):
        return fetch
    if fetch.get("status") != "success":
        return fetch

    server_qs = fetch.get("questions", [])
    total = len(server_qs)
    correct = 0
    per_topic = {}
    for i, sq in enumerate(server_qs):
        topic = sq.get("topic") or "General"
        per_topic.setdefault(topic, {"correct": 0, "total": 0})
        per_topic[topic]["total"] += 1
        try:
            user_sel = int(answers[i]) if i < len(answers) and answers[i] is not None else -1
        except Exception:
            user_sel = -1
        if user_sel == int(sq.get("correct_index", -1)):
            correct += 1
            per_topic[topic]["correct"] += 1

    pct = int(round(100 * correct / total)) if total else 0
    return {
        "status": "success",
        "score_pct": pct,
        "correct": correct,
        "total": total,
        "per_topic": per_topic,
        "passed": pct >= 60,
        "exam": fetch.get("exam"),
    }


# ---------------------------------------------------------------
# Paid tier — order creation
# ---------------------------------------------------------------

def create_unlock_order(exam_id: str, email: str, country_code: str) -> Dict:
    """Create a Razorpay or PayPal order for the full-mock unlock."""
    if exam_id not in SUPPORTED_EXAMS:
        return {"status": "error", "message": "Exam not supported"}
    email = (email or "").strip().lower()
    if not email or "@" not in email:
        return {"status": "error", "message": "Valid email required"}

    price = payment_engine.resolve_public_price("state_psc_full_mock", country_code)
    if price.get("status") != "success":
        return price

    gateway = price.get("gateway")
    currency = price.get("currency")
    amount_local = price.get("amount_local")
    amount_inr = price.get("amount_inr", 0)
    amount_paise = price.get("razorpay_paise", 0)

    _ensure_table()
    unlock_id = f"SPSC-{secrets.token_hex(8).upper()}"

    # Persist pending order
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO charvak_state_psc_unlocks
              (unlock_id, exam_id, email, country_code, currency, amount_local, gateway, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            ON CONFLICT (exam_id, email) DO UPDATE
              SET country_code = EXCLUDED.country_code,
                  currency = EXCLUDED.currency,
                  amount_local = EXCLUDED.amount_local,
                  gateway = EXCLUDED.gateway,
                  status = CASE
                    WHEN charvak_state_psc_unlocks.status = 'paid' THEN 'paid'
                    ELSE 'pending'
                  END
        """, (unlock_id, exam_id, email, country_code, currency, amount_local, gateway))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"state_psc unlock persist failed: {e}")

    # Reuse the existing payment engines
    try:
        if gateway == "razorpay":
            order = payment_engine.create_razorpay_order(
                amount_inr=amount_inr,
                receipt=f"spsc_{secrets.token_hex(6)}",
                notes={
                    "plan": "state_psc_full_mock",
                    "tool": "state_psc_full_mock",
                    "email": email,
                    "exam_id": exam_id,
                    "unlock_id": unlock_id,
                    "amount_inr": amount_inr,
                },
            )
            if order.get("status") != "success":
                return order
            return {
                "status": "success",
                "unlock_id": unlock_id,
                "gateway": "razorpay",
                "currency": currency,
                "amount_local": amount_local,
                "amount_paise": amount_paise,
                "razorpay_order_id": order.get("order_id"),
                "razorpay_key_id": order.get("key_id"),
            }
        elif gateway == "paypal":
            order = payment_engine.create_paypal_order(
                amount=amount_local,
                currency=currency,
                custom_id=f"state_psc|{email}|{exam_id}|{unlock_id}",
            )
            if order.get("status") != "success":
                return order
            return {
                "status": "success",
                "unlock_id": unlock_id,
                "gateway": "paypal",
                "currency": currency,
                "amount_local": amount_local,
                "paypal_order_id": order.get("paypal_order_id"),
            }
        else:
            return {"status": "error", "message": f"Unknown gateway: {gateway}"}
    except Exception as e:
        logger.error(f"state_psc create_order failed: {e}")
        return {"status": "error", "message": str(e)}


# ---------------------------------------------------------------
# Paid tier — verify payment + serve full mock
# ---------------------------------------------------------------

def _mark_paid(unlock_id: str, gateway: str, razorpay_payment_id: str = None,
               razorpay_order_id: str = None, paypal_order_id: str = None) -> None:
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            UPDATE charvak_state_psc_unlocks
            SET status = 'paid',
                razorpay_payment_id = COALESCE(%s, razorpay_payment_id),
                razorpay_order_id = COALESCE(%s, razorpay_order_id),
                paypal_order_id = COALESCE(%s, paypal_order_id),
                gateway = %s
            WHERE unlock_id = %s
        """, (razorpay_payment_id, razorpay_order_id, paypal_order_id, gateway, unlock_id))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"state_psc mark_paid failed: {e}")


def verify_and_serve(exam_id: str, email: str, gateway: str,
                     razorpay_payment_id: str = None,
                     razorpay_order_id: str = None,
                     razorpay_signature: str = None,
                     paypal_order_id: str = None) -> Dict:
    """Verify payment, mark as paid, return the full 100-question mock."""
    email = (email or "").strip().lower()
    if exam_id not in SUPPORTED_EXAMS:
        return {"status": "error", "message": "Exam not supported"}

    _ensure_table()

    # Find the pending order
    row = None
    try:
        conn = db.get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT unlock_id, status, currency, amount_local, razorpay_order_id, paypal_order_id
            FROM charvak_state_psc_unlocks
            WHERE exam_id = %s AND email = %s
            LIMIT 1
        """, (exam_id, email))
        row = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"state_psc lookup failed: {e}")

    if not row:
        return {"status": "error", "message": "No pending unlock order found"}

    unlock_id, status, currency, amount_local, stored_rzp_order, stored_pp_order = row

    # Verify Razorpay
    if gateway == "razorpay":
        if status == "paid":
            pass  # Idempotent — already unlocked
        else:
            if not (razorpay_payment_id and razorpay_order_id and razorpay_signature):
                return {"status": "error", "message": "Missing Razorpay fields"}
            verify = payment_engine.verify_razorpay_payment(
                razorpay_order_id, razorpay_payment_id, razorpay_signature
            )
            if not verify.get("verified"):
                return {"status": "error", "message": "Signature verification failed"}
            # Also confirm captured via Razorpay API
            fetched = payment_engine.fetch_razorpay_payment(razorpay_payment_id)
            if fetched.get("status_field") != "captured":
                return {"status": "error", "message": "Payment not captured"}
            _mark_paid(unlock_id, "razorpay",
                       razorpay_payment_id=razorpay_payment_id,
                       razorpay_order_id=razorpay_order_id)

    elif gateway == "paypal":
        if status == "paid":
            pass
        else:
            if not paypal_order_id:
                return {"status": "error", "message": "Missing PayPal order id"}
            fetched = payment_engine.fetch_paypal_order(paypal_order_id)
            if fetched.get("status_field") != "COMPLETED":
                return {"status": "error", "message": "PayPal payment not completed"}
            _mark_paid(unlock_id, "paypal", paypal_order_id=paypal_order_id)
    else:
        return {"status": "error", "message": f"Unknown gateway: {gateway}"}

    # Serve the full mock
    sections = (exam_prep_engine.get_exam_details(exam_id).get("exam") or {}).get("sections") or []
    # Take up to 3 sections * ~34 questions = ~100 questions
    full_qs = []
    for sec in sections[:3]:
        try:
            batch = exam_prep_engine.generate_questions(exam_id, sec, count=FULL_MOCK_SECTIONS_PER)
            for q in (batch.get("questions") or []):
                q["topic"] = sec
                full_qs.append({
                    "question_text": q.get("question_text") or q.get("question"),
                    "options": q.get("options") or [],
                    "correct_index": int(q.get("correct_index", q.get("correct", 0)) or 0),
                    "topic": sec,
                })
        except Exception as e:
            logger.warning(f"full mock section fetch failed: {e}")

    full_qs = full_qs[:FULL_MOCK_QUESTIONS]
    return {
        "status": "success",
        "exam_id": exam_id,
        "unlock_id": unlock_id,
        "total": len(full_qs),
        "questions": full_qs,
    }


# ---------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------

state_psc_funnel_engine = None  # stateless — module-level functions suffice


def __getattr__(name):
    """Lazy compat: allows `state_psc_funnel_engine.foo` if someone expects a singleton."""
    import sys
    return sys.modules[__name__]