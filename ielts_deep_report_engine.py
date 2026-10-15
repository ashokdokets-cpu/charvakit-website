"""
ielts_deep_report_engine.py — Session 43-A1.7

IELTS Deep Report micro-paywall.

Free tier (existing): band score + sub-bands + basic feedback
Paid tier (Rs 99): deep diagnostic report + PDF + email

Reuses:
  - payment_engine: Razorpay + PayPal
  - global_config: currencies, tiers
  - pdf_engine: PDF rendering
  - ielts_engine: sessions storage (essay/transcripts)
  - enhanced_email: SendGrid attachment

Self-healing DDL. Idempotent on razorpay_payment_id / paypal_order_id.
"""

import json
import os
import secrets
import logging
from datetime import datetime

import global_config
import payment_engine as pe_module
from payment_engine import payment_engine
from global_config import OPENAI_MODEL

logger = logging.getLogger("charvakit.ielts_deep_report")


# ============================================================
# Pricing (same tiers as tool_payment_engine)
# ============================================================

# See tool_payment_engine.TOOL_PRICE_TABLE — we mirror the same
# tier_1 / tier_2 / tier_3 pricing for the IELTS deep report.
DEEP_REPORT_PRICE_TABLE = {
    ("INR", "tier_1"): 99,
    ("INR", "tier_2"): 149,
    ("INR", "tier_3"): 299,

    ("USD", "tier_1"): 1.99,
    ("USD", "tier_2"): 2.99,
    ("USD", "tier_3"): 4.99,

    ("EUR", "tier_1"): 1.99,
    ("EUR", "tier_2"): 2.99,
    ("EUR", "tier_3"): 4.49,

    ("GBP", "tier_1"): 1.49,
    ("GBP", "tier_2"): 2.49,
    ("GBP", "tier_3"): 3.99,

    ("AED", "tier_1"): 7,
    ("AED", "tier_2"): 11,
    ("AED", "tier_3"): 17,

    ("SGD", "tier_1"): 2.49,
    ("SGD", "tier_2"): 3.99,
    ("SGD", "tier_3"): 5.99,

    ("AUD", "tier_1"): 2.99,
    ("AUD", "tier_2"): 4.49,
    ("AUD", "tier_3"): 6.49,

    ("CAD", "tier_1"): 2.49,
    ("CAD", "tier_2"): 3.99,
    ("CAD", "tier_3"): 5.99,

    ("JPY", "tier_1"): 300,
    ("JPY", "tier_2"): 450,
    ("JPY", "tier_3"): 700,

    ("CNY", "tier_1"): 14,
    ("CNY", "tier_2"): 21,
    ("CNY", "tier_3"): 32,
}

PAYPAL_SUPPORTED = {"USD", "EUR", "GBP", "AUD", "CAD", "SGD", "JPY", "CNY", "AED"}
WHOLE_NUMBER_CURRENCIES = {"JPY", "NGN", "CNY", "AED"}


def _tier_for_country(country_code: str) -> str:
    cc = (country_code or "").strip().upper()
    for tier_name, tier_data in global_config.PRICING_TIERS.items():
        if cc in tier_data.get("countries", []):
            return tier_name
    return "tier_3"


def _fmt_amount(amount: float, currency: str) -> str:
    if currency in WHOLE_NUMBER_CURRENCIES or currency == "INR":
        return str(int(round(amount)))
    return f"{amount:.2f}"


def _lookup_price(currency: str, tier: str) -> float:
    if (currency, tier) in DEEP_REPORT_PRICE_TABLE:
        return DEEP_REPORT_PRICE_TABLE[(currency, tier)]
    return DEEP_REPORT_PRICE_TABLE.get((currency, "tier_1"), 1.99)


def resolve_price(country_code: str) -> dict:
    """Return the localized deep-report price."""
    cc = (country_code or "").strip().upper()
    tier = _tier_for_country(cc)
    currency = global_config.COUNTRY_TO_CURRENCY.get(cc, "USD")

    if currency == "INR":
        gateway = "razorpay"
        charge_currency = "INR"
    else:
        gateway = "paypal"
        charge_currency = currency if currency in PAYPAL_SUPPORTED else "USD"

    amount = _lookup_price(charge_currency, tier)
    return {
        "currency": charge_currency,
        "amount": amount,
        "symbol": global_config.CURRENCIES[charge_currency]["symbol"],
        "gateway": gateway,
        "tier": tier,
        "amount_display": f"{global_config.CURRENCIES[charge_currency]['symbol']}{_fmt_amount(amount, charge_currency)}",
    }


# ============================================================
# Table (self-healing)
# ============================================================

def _ensure_table():
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        ALTER TABLE charvak_ielts_sessions
        ADD COLUMN IF NOT EXISTS responses_json JSONB
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS charvak_ielts_deep_reports (
            report_id         TEXT PRIMARY KEY,
            session_id        TEXT NOT NULL,
            email             TEXT NOT NULL,
            test_type         TEXT NOT NULL,
            currency          TEXT NOT NULL DEFAULT 'INR',
            amount_local      NUMERIC(12,2) NOT NULL DEFAULT 99,
            tier              TEXT,
            gateway           TEXT NOT NULL,
            razorpay_order_id    TEXT UNIQUE,
            razorpay_payment_id  TEXT UNIQUE,
            paypal_order_id      TEXT UNIQUE,
            status            TEXT NOT NULL DEFAULT 'pending',
            report_json       JSONB,
            pdf_generated_at  TIMESTAMP,
            email_sent_at     TIMESTAMP,
            error_message     TEXT,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at      TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ielts_deep_reports_email
        ON charvak_ielts_deep_reports (email, created_at DESC)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_ielts_deep_reports_session
        ON charvak_ielts_deep_reports (session_id)
    """)
    conn.commit()
    cur.close()
    conn.close()


# ============================================================
# Order creation
# ============================================================

def create_order(session_id: str, test_type: str, email: str, country_code: str) -> dict:
    """
    Create a Razorpay or PayPal order for the IELTS Deep Report.
    Validates that the session exists and belongs to the caller.
    """
    test_type = (test_type or "").strip().lower()
    if test_type not in ("writing", "speaking"):
        return {"status": "error", "message": "test_type must be 'writing' or 'speaking'"}

    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}

    if not session_id:
        return {"status": "error", "message": "session_id required"}

    # Load the session to verify ownership + confirm responses exist
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT email, test_type, responses_json
        FROM charvak_ielts_sessions
        WHERE session_id = %s
    """, (session_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return {"status": "error", "message": "Session not found"}
    if (row[0] or "").strip().lower() != email:
        return {"status": "error", "message": "Session belongs to a different user"}
    if (row[1] or "").strip().lower() != test_type:
        return {"status": "error", "message": f"Session is {row[1]}, not {test_type}"}
    if not row[2]:
        return {"status": "error", "message": "Session has no stored responses (free eval may not have completed)"}

    price = resolve_price(country_code)
    report_id = f"IELTS-{test_type.upper()[:1]}-{secrets.token_hex(6).upper()}"
    receipt = f"ielts_{test_type}_{secrets.token_hex(4)}"

    if price["gateway"] == "razorpay":
        amount_paise = int(round(price["amount"] * 100))
        order = payment_engine.create_razorpay_order(
            amount_inr=amount_paise,
            receipt=receipt,
            notes={
                "type": "ielts_deep_report",
                "report_id": report_id,
                "session_id": session_id,
                "test_type": test_type,
                "email": email,
                "currency": price["currency"],
                "amount_local": price["amount"],
                "tier": price["tier"],
            },
        )
        if order.get("status") != "success":
            return order
        order_id = order.get("order_id")
        pre_gateway = "razorpay"
        pre_razorpay_order_id = order_id
        pre_paypal_order_id = None
    else:
        # PayPal amount must be in the target currency; pass INR-equivalent
        # and let payment_engine convert.
        inr_equivalent = 99 * global_config.PRICING_TIERS[price["tier"]]["multiplier"]
        order = payment_engine.create_paypal_order(
            amount_inr=inr_equivalent,
            target_currency=price["currency"],
            description="IELTS Deep Report - " + test_type,
            custom_id=report_id,
        )
        if order.get("status") != "success":
            return order
        order_id = order.get("order_id")
        pre_gateway = "paypal"
        pre_razorpay_order_id = None
        pre_paypal_order_id = order_id

    # Persist pre-registration
    _ensure_table()
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO charvak_ielts_deep_reports
            (report_id, session_id, email, test_type, currency,
             amount_local, tier, gateway, razorpay_order_id, paypal_order_id,
             status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
    """, (
        report_id, session_id, email, test_type,
        price["currency"], price["amount"], price["tier"], pre_gateway,
        pre_razorpay_order_id, pre_paypal_order_id,
    ))
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "report_id": report_id,
        "order_id": order_id,
        "gateway": pre_gateway,
        "currency": price["currency"],
        "amount": price["amount"],
        "amount_display": price["amount_display"],
        "symbol": price["symbol"],
        "key_id": order.get("key_id"),
        "test_type": test_type,
    }


# ============================================================
# AI report generation
# ============================================================

def generate_report(session_id: str, test_type: str) -> dict:
    """
    Run ONE OpenAI call that produces the full deep report.
    Reads the essay/transcripts from charvak_ielts_sessions.responses_json.
    """
    from ielts_engine import ielts_engine as ie

    try:
        stored = ie.get_responses(session_id)
    except ValueError as e:
        return {"status": "error", "message": str(e)}

    if test_type == "writing":
        return _generate_writing_report(stored)
    elif test_type == "speaking":
        return _generate_speaking_report(stored)
    return {"status": "error", "message": "Unknown test_type"}


def _generate_writing_report(stored: dict) -> dict:
    """Deep diagnostic for an IELTS Writing essay."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        return {"status": "error", "message": f"OpenAI unavailable: {e}"}

    essay = stored.get("essay", "")
    task = stored.get("task", 2)
    prompt = stored.get("prompt", "")
    evaluation = stored.get("evaluation", {})

    prompt_text = f"""You are a senior IELTS examiner. Produce a deep diagnostic report for the essay below.

TASK: IELTS Writing Task {task}
PROMPT: {prompt}

STUDENT ESSAY:
\"\"\"{essay}\"\"\"

PREVIOUS FREE-TIER EVALUATION:
{json.dumps(evaluation, indent=2)}

Return ONLY valid JSON matching this exact shape:
{{
  "band": <float 0-9, the overall band the AI gave>,
  "summary": "<2-3 sentence overall assessment>",
  "sub_band_reasoning": {{
    "task_response": "<why this band, quote specific sentences>",
    "coherence_cohesion": "<why this band, quote specific transitions>",
    "lexical_resource": "<why this band, quote specific vocabulary>",
    "grammatical_range_accuracy": "<why this band, quote specific errors>"
  }},
  "grammar_corrections": [
    {{"original": "<exact sentence from essay>", "corrected": "<fixed version>", "rule": "<rule name>", "explanation": "<1 sentence>"}}
  ],
  "vocabulary_upgrades": [
    {{"original": "<word or phrase>", "better": ["<synonym 1>", "<synonym 2>"], "context": "<when to use which>"}}
  ],
  "example_high_band_rewrite": {{
    "paragraph_1": "<a Band 8+ version of the first body paragraph>",
    "paragraph_2": "<a Band 8+ version of a later paragraph>"
  }},
  "common_pitfalls": ["<3-5 specific issues in THIS essay>"],
  "exercises": [
    {{"topic": "<what to practice>", "task": "<specific exercise>", "rationale": "<why>"}}
  ]
}}

Rules:
- grammar_corrections: 5-10 entries, only real errors from the essay
- vocabulary_upgrades: 5-8 entries, only upgradeable words
- example_high_band_rewrite: 2 paragraphs, paraphrased but same thesis
- common_pitfalls: specific to THIS essay, not generic
- exercises: exactly 3 items
- Be honest but constructive. Never inflate the band.
"""

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a senior IELTS examiner producing a JSON deep-diagnostic report."},
                {"role": "user", "content": prompt_text},
            ],
            response_format={"type": "json_object"},
            max_tokens=4000,
            temperature=0.3,
        )
        raw = resp.choices[0].message.content
        report = json.loads(raw)
        return {"status": "success", "report": report}
    except Exception as e:
        logger.error(f"writing deep report failed: {e}")
        return {"status": "error", "message": f"Could not generate report: {e}"}


def _generate_speaking_report(stored: dict) -> dict:
    """Deep diagnostic for an IELTS Speaking session."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    except Exception as e:
        return {"status": "error", "message": f"OpenAI unavailable: {e}"}

    responses = stored.get("responses", [])
    topic = stored.get("topic", "")
    evaluation = stored.get("evaluation", {})

    transcript_block = "\n\n".join(
        f"Part {r.get('part', '?')} — Q: {r.get('question', '')}\nA: {r.get('transcript', '')}"
        for r in responses
    )

    prompt_text = f"""You are a senior IELTS Speaking examiner. Produce a deep diagnostic report for the session below.

TOPIC: {topic}

CANDIDATE RESPONSES:
{transcript_block}

PREVIOUS FREE-TIER EVALUATION:
{json.dumps(evaluation, indent=2)}

Return ONLY valid JSON matching this exact shape:
{{
  "band": <float 0-9, the overall band the AI gave>,
  "summary": "<2-3 sentence overall assessment>",
  "sub_band_reasoning": {{
    "fluency_coherence": "<why this band, quote specific moments>",
    "lexical_resource": "<why this band, quote specific vocabulary>",
    "grammatical_range_accuracy": "<why this band, quote specific errors>",
    "pronunciation": "<why this band, based on transcript clarity>"
  }},
  "response_by_response": [
    {{"part": <int>, "question": "<question>", "strength": "<what worked>", "improvement": "<what to fix>"}}
  ],
  "vocabulary_upgrades": [
    {{"original": "<word or phrase>", "better": ["<synonym 1>", "<synonym 2>"], "context": "<when to use which>"}}
  ],
  "example_high_band_answer": {{
    "part": <int>,
    "question": "<which question>",
    "band_8_answer": "<a Band 8+ version of the answer>"
  }},
  "pronunciation_notes": [
    {{"sounds": "<specific sounds or words>", "tip": "<how to improve>"}}
  ],
  "common_pitfalls": ["<3-5 specific issues in THIS session>"],
  "exercises": [
    {{"topic": "<what to practice>", "task": "<specific exercise>", "rationale": "<why>"}}
  ]
}}

Rules:
- response_by_response: one entry per candidate response
- vocabulary_upgrades: 5-8 entries
- pronunciation_notes: 3-5 entries, focused on transcript-observable issues
- exercises: exactly 3 items
- Never inflate the band.
"""

    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a senior IELTS examiner producing a JSON deep-diagnostic report."},
                {"role": "user", "content": prompt_text},
            ],
            response_format={"type": "json_object"},
            max_tokens=4000,
            temperature=0.3,
        )
        raw = resp.choices[0].message.content
        report = json.loads(raw)
        return {"status": "success", "report": report}
    except Exception as e:
        logger.error(f"speaking deep report failed: {e}")
        return {"status": "error", "message": f"Could not generate report: {e}"}


# ============================================================
# Verification — Razorpay
# ============================================================

def verify_and_claim_razorpay(
    report_id: str,
    razorpay_payment_id: str,
    razorpay_order_id: str,
    razorpay_signature: str,
    email: str,
) -> dict:
    """Verify a Razorpay payment for the deep report. Idempotent."""
    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}
    if not razorpay_payment_id or not razorpay_order_id or not razorpay_signature:
        return {"status": "error", "message": "Payment details incomplete"}

    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()

    # Idempotency
    cur.execute("""
        SELECT report_id, status FROM charvak_ielts_deep_reports
        WHERE razorpay_payment_id = %s
    """, (razorpay_payment_id,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        conn.close()
        return {
            "status": "success",
            "already_claimed": True,
            "report_id": existing[0],
            "report_status": existing[1],
        }

    # Verify signature
    verify = payment_engine.verify_razorpay_payment(
        payment_id=razorpay_payment_id,
        order_id=razorpay_order_id,
        signature=razorpay_signature,
    )
    if verify.get("status") != "success" or not verify.get("verified"):
        cur.close()
        conn.close()
        return {"status": "error", "message": "Signature verification failed"}

    # Fetch payment
    fetched = payment_engine.fetch_razorpay_payment(razorpay_payment_id)
    if fetched.get("status") != "success":
        cur.close()
        conn.close()
        return {"status": "error", "message": "Could not fetch payment from Razorpay"}
    if fetched.get("status_field") != "captured":
        cur.close()
        conn.close()
        return {"status": "error", "message": "Payment not captured"}

    # Find pre-registered row
    cur.execute("""
        SELECT report_id, amount_local FROM charvak_ielts_deep_reports
        WHERE razorpay_order_id = %s
    """, (razorpay_order_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return {"status": "error", "message": "Pre-registration not found"}

    pre_report_id, expected_amount = row
    expected_paise = int(round(float(expected_amount) * 100))
    if int(fetched.get("amount", 0)) != expected_paise:
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": f"Amount mismatch: paid {fetched.get('amount')} expected {expected_paise}",
        }

    cur.execute("""
        UPDATE charvak_ielts_deep_reports
        SET email = %s, razorpay_payment_id = %s,
            status = 'captured', completed_at = NOW()
        WHERE report_id = %s
    """, (email, razorpay_payment_id, pre_report_id))
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "already_claimed": False,
        "report_id": pre_report_id,
    }


# ============================================================
# Verification — PayPal
# ============================================================

def verify_and_claim_paypal(
    report_id: str,
    paypal_order_id: str,
    email: str,
) -> dict:
    """Verify a PayPal order for the deep report. Idempotent."""
    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}
    if not paypal_order_id:
        return {"status": "error", "message": "paypal_order_id required"}

    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT report_id, status FROM charvak_ielts_deep_reports
        WHERE paypal_order_id = %s
    """, (paypal_order_id,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        conn.close()
        return {
            "status": "success",
            "already_claimed": True,
            "report_id": existing[0],
            "report_status": existing[1],
        }

    fetched = payment_engine.fetch_paypal_order(paypal_order_id)
    if fetched.get("status") != "success":
        cur.close()
        conn.close()
        return {"status": "error", "message": "Could not fetch PayPal order"}
    if fetched.get("status_field") != "COMPLETED":
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": f"PayPal status is {fetched.get('status_field')}, expected COMPLETED",
        }

    cur.execute("""
        SELECT report_id, amount_local, currency
        FROM charvak_ielts_deep_reports
        WHERE paypal_order_id = %s
    """, (paypal_order_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return {"status": "error", "message": "Pre-registration not found"}

    pre_report_id, expected_amount, expected_currency = row
    paid_amount = float(fetched.get("amount", 0))
    paid_currency = (fetched.get("currency") or "").upper()

    if paid_currency != expected_currency.upper():
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": f"Currency mismatch: paid {paid_currency} expected {expected_currency}",
        }

    expected_f = float(expected_amount)
    if abs(paid_amount - expected_f) > max(expected_f * 0.02, 0.01):
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": f"Amount mismatch: paid {paid_amount} expected {expected_f}",
        }

    cur.execute("""
        UPDATE charvak_ielts_deep_reports
        SET email = %s, status = 'captured', completed_at = NOW()
        WHERE report_id = %s
    """, (email, pre_report_id))
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "already_claimed": False,
        "report_id": pre_report_id,
    }


# ============================================================
# Persistence + retrieval
# ============================================================

def save_report(report_id: str, report: dict) -> dict:
    """Persist the generated report JSON and mark the row complete."""
    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_ielts_deep_reports
        SET report_json = %s, status = 'completed', completed_at = NOW()
        WHERE report_id = %s
    """, (json.dumps(report), report_id))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "success"}


def get_report(report_id: str) -> dict:
    """Load a saved deep report. Raises ValueError on missing."""
    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT report_id, session_id, email, test_type, report_json,
               currency, amount_local, gateway, status, created_at
        FROM charvak_ielts_deep_reports
        WHERE report_id = %s
    """, (report_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise ValueError(f"report not found: {report_id}")
    if not row[4]:
        raise ValueError("report not yet generated")

    report_json = row[4] if isinstance(row[4], dict) else json.loads(row[4])
    return {
        "report_id": row[0],
        "session_id": row[1],
        "email": row[2],
        "test_type": row[3],
        "report": report_json,
        "currency": row[5],
        "amount_local": float(row[6]) if row[6] is not None else None,
        "gateway": row[7],
        "status": row[8],
        "created_at": row[9],
    }


def mark_pdf_generated(report_id: str):
    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_ielts_deep_reports
        SET pdf_generated_at = NOW()
        WHERE report_id = %s
    """, (report_id,))
    conn.commit()
    cur.close()
    conn.close()


def mark_email_sent(report_id: str):
    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_ielts_deep_reports
        SET email_sent_at = NOW()
        WHERE report_id = %s
    """, (report_id,))
    conn.commit()
    cur.close()
    conn.close()


def record_error(report_id: str, error: str):
    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE charvak_ielts_deep_reports
        SET error_message = %s, status = 'captured_but_failed'
        WHERE report_id = %s
    """, (error, report_id))
    conn.commit()
    cur.close()
    conn.close()