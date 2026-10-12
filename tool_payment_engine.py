"""
tool_payment_engine.py - Session 43-A1.6 (currency-aware)

One-off tool runs paid via Razorpay (INR) or PayPal (multi-currency).
Bypasses the credits system entirely.

Pricing:
  - Base: Rs 99 (India, tier_1)
  - Tier multipliers: tier_1 = 1.0x, tier_2 = 1.5x, tier_3 = 3.0x
  - Currency rates come from global_config.CURRENCIES
  - Country -> currency from global_config.COUNTRY_TO_CURRENCY

Gateway routing:
  - INR -> Razorpay
  - All other currencies -> PayPal
  - PayPal fallback: NGN, BRL, ZAR are charged in USD

Self-healing DDL. Idempotent on razorpay_payment_id / paypal_order_id.
"""

import json
import secrets
from datetime import datetime

import global_config
from payment_engine import payment_engine


# ============================================================
# Tool registry
# ============================================================

PAID_TOOLS = {
    "resume_roast":     "Resume Roast",
    "ghost_bounty":     "Ghost-Bounty",
    "ref_check":        "Ref-Check",
    "role_mirror":      "Role-Mirror",
    "bounty_swap":      "Bounty-Swap",
    "micro_trial":      "Micro-Trial",
    "offer_matcher":    "Offer-Matcher",
    "ghost_job_shield": "Ghost-Job Shield",
    "counter_offer":    "Counter-Offer",
    "ref_swap":         "Ref-Swap",
    "ghost_tracker":    "Ghost-Tracker",
    "pitch_roast":      "Pitch-Roast",
}


# ============================================================
# Pricing
# ============================================================

BASE_PRICE_INR = 99

# PayPal-supported currencies (from global_config.CURRENCIES)
PAYPAL_SUPPORTED = {"USD", "EUR", "GBP", "AUD", "CAD", "SGD", "JPY", "CNY", "AED"}

# Currencies that use whole-number pricing (no decimals)
WHOLE_NUMBER_CURRENCIES = {"JPY", "NGN", "CNY", "AED"}


def _tier_for_country(country_code: str) -> str:
    """Return 'tier_1' | 'tier_2' | 'tier_3'."""
    cc = (country_code or "").strip().upper()
    for tier_name, tier_data in global_config.PRICING_TIERS.items():
        if cc in tier_data.get("countries", []):
            return tier_name
    return "tier_3"  # default to global standard


def _fmt_amount(amount: float, currency: str) -> str:
    """Format an amount for display based on currency conventions."""
    if currency in WHOLE_NUMBER_CURRENCIES or currency == "INR":
        return str(int(round(amount)))
    return f"{amount:.2f}"


# ============================================================
# Explicit tool price table — set by hand per market, not computed.
# Keyed by (currency, tier). One number per market per tier.
#
# Rationale: purchasing power per market beats raw FX conversion.
# Updating a price = editing one line. No arithmetic surprises.
# ============================================================

TOOL_PRICE_TABLE = {
    # India
    ("INR", "tier_1"): 99,
    ("INR", "tier_2"): 149,
    ("INR", "tier_3"): 299,

    # United States
    ("USD", "tier_1"): 1.99,
    ("USD", "tier_2"): 2.99,
    ("USD", "tier_3"): 4.99,

    # Eurozone
    ("EUR", "tier_1"): 1.99,
    ("EUR", "tier_2"): 2.99,
    ("EUR", "tier_3"): 4.49,

    # United Kingdom
    ("GBP", "tier_1"): 1.49,
    ("GBP", "tier_2"): 2.49,
    ("GBP", "tier_3"): 3.99,

    # UAE
    ("AED", "tier_1"): 7,
    ("AED", "tier_2"): 11,
    ("AED", "tier_3"): 17,

    # Singapore
    ("SGD", "tier_1"): 2.49,
    ("SGD", "tier_2"): 3.99,
    ("SGD", "tier_3"): 5.99,

    # Australia
    ("AUD", "tier_1"): 2.99,
    ("AUD", "tier_2"): 4.49,
    ("AUD", "tier_3"): 6.49,

    # Canada
    ("CAD", "tier_1"): 2.49,
    ("CAD", "tier_2"): 3.99,
    ("CAD", "tier_3"): 5.99,

    # Japan
    ("JPY", "tier_1"): 300,
    ("JPY", "tier_2"): 450,
    ("JPY", "tier_3"): 700,

    # China
    ("CNY", "tier_1"): 14,
    ("CNY", "tier_2"): 21,
    ("CNY", "tier_3"): 32,

    # Brazil — but PayPal doesn't support BRL, charged in USD
    # Local amounts provided for reference; USD fallback used.
    ("BRL", "tier_1"): 9.99,
    ("BRL", "tier_2"): 14.99,
    ("BRL", "tier_3"): 22.99,

    # Nigeria — same as above
    ("NGN", "tier_1"): 1499,
    ("NGN", "tier_2"): 2499,
    ("NGN", "tier_3"): 3999,

    # South Africa — same as above
    ("ZAR", "tier_1"): 34.99,
    ("ZAR", "tier_2"): 54.99,
    ("ZAR", "tier_3"): 84.99,
}


def _lookup_tool_price(currency: str, tier: str) -> float:
    """
    Look up the tool price for (currency, tier).
    Falls back to (USD, tier) if the specific combo is missing.
    """
    if (currency, tier) in TOOL_PRICE_TABLE:
        return TOOL_PRICE_TABLE[(currency, tier)]
    if (currency, "tier_1") in TOOL_PRICE_TABLE:
        # Fall back to same currency tier_1 as last resort
        return TOOL_PRICE_TABLE[(currency, "tier_1")]
    # Ultimate fallback
    return 1.99


def resolve_tool_price(country_code: str) -> dict:
    """
    Return the localized tool price.

    Uses TOOL_PRICE_TABLE (explicit per-market prices), not conversion math.

    Returns:
      {
        currency, amount, symbol, gateway, tier, amount_display
      }
    """
    cc = (country_code or "").strip().upper()
    tier = _tier_for_country(cc)

    # Look up local currency
    currency = global_config.COUNTRY_TO_CURRENCY.get(cc, "USD")

    # Determine gateway
    if currency == "INR":
        gateway = "razorpay"
        charge_currency = "INR"
    else:
        gateway = "paypal"
        # Fall back to USD for currencies PayPal doesn't support
        if currency not in PAYPAL_SUPPORTED:
            charge_currency = "USD"
        else:
            charge_currency = currency

    # Look up price for (charge_currency, tier)
    amount = _lookup_tool_price(charge_currency, tier)
    display = _fmt_amount(amount, charge_currency)

    return {
        "currency": charge_currency,
        "amount": amount,
        "symbol": global_config.CURRENCIES[charge_currency]["symbol"],
        "gateway": gateway,
        "tier": tier,
        "amount_display": f"{global_config.CURRENCIES[charge_currency]['symbol']}{display}",
        "original_currency": currency,  # for logging/debug
    }


# ============================================================
# Table (self-healing)
# ============================================================

def _ensure_table():
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS charvak_tool_purchases (
            purchase_id            TEXT PRIMARY KEY,
            email                  TEXT,
            user_id                TEXT,
            tool_slug              TEXT NOT NULL,
            tool_name              TEXT,
            currency               TEXT NOT NULL DEFAULT 'INR',
            amount_local           NUMERIC(12,2) NOT NULL,
            amount_inr             INTEGER NOT NULL,
            tier                   TEXT,
            gateway                TEXT NOT NULL,
            razorpay_order_id      TEXT UNIQUE,
            razorpay_payment_id    TEXT UNIQUE,
            paypal_order_id        TEXT UNIQUE,
            status                 TEXT NOT NULL DEFAULT 'pending',
            result_json            JSONB,
            error_message          TEXT,
            created_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at           TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_tool_purchases_email
        ON charvak_tool_purchases (email, created_at DESC)
    """)
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_tool_purchases_tool
        ON charvak_tool_purchases (tool_slug, created_at DESC)
    """)
    conn.commit()
    cur.close()
    conn.close()


# ============================================================
# Order creation
# ============================================================

def create_order(tool_slug: str, country_code: str) -> dict:
    """Create a Razorpay or PayPal order for a specific tool."""
    tool_slug = (tool_slug or "").strip().lower()
    if tool_slug not in PAID_TOOLS:
        return {"status": "error", "message": f"Unknown tool: {tool_slug}"}

    price = resolve_tool_price(country_code)
    tool_name = PAID_TOOLS[tool_slug]

    # Pre-allocate the purchase_id up front so we can use it in the
    # gateway's notes/custom_id
    purchase_id = f"TPUR-{secrets.token_hex(6).upper()}"
    receipt = f"tool_{tool_slug}_{secrets.token_hex(4)}"

    if price["gateway"] == "razorpay":
        # Razorpay uses paise (INR * 100)
        amount_paise = int(round(price["amount"] * 100))
        order = payment_engine.create_razorpay_order(
            amount_inr=amount_paise,
            receipt=receipt,
            notes={
                "type": "tool_purchase",
                "purchase_id": purchase_id,
                "tool_slug": tool_slug,
                "tool_name": tool_name,
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
        # PayPal: pass the INR equivalent; the engine converts internally
        # via its INR_RATES and returns the actual charged amount.
        tier_multiplier = global_config.PRICING_TIERS[price["tier"]]["multiplier"]
        inr_equivalent = BASE_PRICE_INR * tier_multiplier

        order = payment_engine.create_paypal_order(
            amount_inr=inr_equivalent,
            target_currency=price["currency"],
            description=f"{tool_name} - one-off tool run",
            custom_id=purchase_id,
        )
        if order.get("status") != "success":
            return order
        order_id = order.get("order_id")
        pre_gateway = "paypal"
        pre_razorpay_order_id = None
        pre_paypal_order_id = order_id

    # Persist the pre-registration row
    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO charvak_tool_purchases
            (purchase_id, tool_slug, tool_name, currency, amount_local,
             amount_inr, tier, gateway, razorpay_order_id, paypal_order_id,
             status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')
    """, (
        purchase_id, tool_slug, tool_name,
        price["currency"], price["amount"],
        int(round(BASE_PRICE_INR * global_config.PRICING_TIERS[price["tier"]]["multiplier"])),
        price["tier"], pre_gateway,
        pre_razorpay_order_id, pre_paypal_order_id,
    ))
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "purchase_id": purchase_id,
        "order_id": order_id,
        "gateway": pre_gateway,
        "currency": price["currency"],
        "amount": price["amount"],
        "amount_display": price["amount_display"],
        "symbol": price["symbol"],
        "key_id": order.get("key_id"),
        "tool_slug": tool_slug,
        "tool_name": tool_name,
    }


# ============================================================
# Verification — Razorpay
# ============================================================

def verify_and_claim_razorpay(
    tool_slug: str,
    razorpay_payment_id: str,
    razorpay_order_id: str,
    razorpay_signature: str,
    email: str,
    user_id: str = None,
) -> dict:
    """Verify a Razorpay INR payment and claim it."""
    tool_slug = (tool_slug or "").strip().lower()
    if tool_slug not in PAID_TOOLS:
        return {"status": "error", "message": f"Unknown tool: {tool_slug}"}

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
        SELECT purchase_id, status FROM charvak_tool_purchases
        WHERE razorpay_payment_id = %s
    """, (razorpay_payment_id,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        conn.close()
        return {
            "status": "success",
            "already_claimed": True,
            "purchase_id": existing[0],
            "purchase_status": existing[1],
            "email": email,
            "tool_slug": tool_slug,
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

    # Fetch payment to confirm captured + amount
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
        SELECT purchase_id, amount_local FROM charvak_tool_purchases
        WHERE razorpay_order_id = %s
    """, (razorpay_order_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return {"status": "error", "message": "Pre-registration not found"}

    purchase_id, expected_amount = row
    expected_paise = int(round(float(expected_amount) * 100))
    if int(fetched.get("amount", 0)) != expected_paise:
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": f"Amount mismatch: paid {fetched.get('amount')} expected {expected_paise}",
        }

    # Update row
    cur.execute("""
        UPDATE charvak_tool_purchases
        SET email = %s, user_id = %s, razorpay_payment_id = %s,
            status = 'captured', completed_at = NOW()
        WHERE purchase_id = %s
    """, (email, user_id, razorpay_payment_id, purchase_id))
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "already_claimed": False,
        "purchase_id": purchase_id,
        "email": email,
        "tool_slug": tool_slug,
    }


# ============================================================
# Verification — PayPal
# ============================================================

def verify_and_claim_paypal(
    tool_slug: str,
    paypal_order_id: str,
    email: str,
    user_id: str = None,
) -> dict:
    """Verify a PayPal order and claim it. Fetches from PayPal API."""
    tool_slug = (tool_slug or "").strip().lower()
    if tool_slug not in PAID_TOOLS:
        return {"status": "error", "message": f"Unknown tool: {tool_slug}"}

    email = (email or "").strip().lower()
    if not email:
        return {"status": "error", "message": "email required"}
    if not paypal_order_id:
        return {"status": "error", "message": "paypal_order_id required"}

    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()

    # Idempotency
    cur.execute("""
        SELECT purchase_id, status FROM charvak_tool_purchases
        WHERE paypal_order_id = %s
    """, (paypal_order_id,))
    existing = cur.fetchone()
    if existing:
        cur.close()
        conn.close()
        return {
            "status": "success",
            "already_claimed": True,
            "purchase_id": existing[0],
            "purchase_status": existing[1],
            "email": email,
            "tool_slug": tool_slug,
        }

    # Fetch from PayPal
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
            "message": f"PayPal order status is {fetched.get('status_field')}, expected COMPLETED",
        }

    # Find pre-registered row
    cur.execute("""
        SELECT purchase_id, amount_local, currency
        FROM charvak_tool_purchases
        WHERE paypal_order_id = %s
    """, (paypal_order_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return {"status": "error", "message": "Pre-registration not found"}

    purchase_id, expected_amount, expected_currency = row
    paid_amount = float(fetched.get("amount", 0))
    paid_currency = (fetched.get("currency") or "").upper()

    if paid_currency != expected_currency.upper():
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": f"Currency mismatch: paid {paid_currency} expected {expected_currency}",
        }

    # Allow small FX tolerance (2%)
    expected_f = float(expected_amount)
    if abs(paid_amount - expected_f) > max(expected_f * 0.02, 0.01):
        cur.close()
        conn.close()
        return {
            "status": "error",
            "message": f"Amount mismatch: paid {paid_amount} expected {expected_f}",
        }

    cur.execute("""
        UPDATE charvak_tool_purchases
        SET email = %s, user_id = %s, status = 'captured', completed_at = NOW()
        WHERE purchase_id = %s
    """, (email, user_id, purchase_id))
    conn.commit()
    cur.close()
    conn.close()

    return {
        "status": "success",
        "already_claimed": False,
        "purchase_id": purchase_id,
        "email": email,
        "tool_slug": tool_slug,
    }


# ============================================================
# Result recording
# ============================================================

def record_result(purchase_id: str, result: dict = None, error: str = None):
    """Attach the tool run result (or error) to the purchase record."""
    _ensure_table()
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    if result is not None:
        cur.execute("""
            UPDATE charvak_tool_purchases
            SET result_json = %s, status = 'completed', completed_at = NOW()
            WHERE purchase_id = %s
        """, (json.dumps(result), purchase_id))
    else:
        cur.execute("""
            UPDATE charvak_tool_purchases
            SET error_message = %s, status = 'captured_but_failed'
            WHERE purchase_id = %s
        """, (error or "unknown error", purchase_id))
    conn.commit()
    cur.close()
    conn.close()