"""
Admin metrics for AI Internship enrollments (Phase 5).

Read-only aggregations over charvak_ai_internship_enrollments:
- Summary KPIs (revenue, counts)
- Tier distribution (for Chart.js doughnut)
- Per-enrollment table data (joined to tiers + programs)

No writes, no state. Admin-only via the calling route.
"""
from typing import Dict, List, Optional
from datetime import datetime

from database import db
import logging

# Hoist this import to module level. The previous pattern — importing
# ai_internship_engine lazily inside _program_name() — caused a re-entrancy
# deadlock: _program_name was called while we held a pool connection, and
# ai_internship_engine's module-level _ensure_tables() needed a pool connection
# that never freed. Module-level import runs once at startup, before any
# request holds a connection.
_internship_engine_programs = None
try:
    from ai_internship_engine import ai_internship_engine as _ie
    _internship_engine_programs = getattr(_ie, 'programs', None)
except Exception as _e:
    logger.warning(f'admin_internship_metrics: could not import ai_internship_engine: {_e}')

logger = logging.getLogger(__name__)

TEST_EMAIL_SUFFIXES = ("@charvak.local", "@test.local", "@example.com")


def _is_test_email(email: str) -> bool:
    if not email:
        return False
    e = email.lower()
    return any(e.endswith(s) for s in TEST_EMAIL_SUFFIXES)


def _program_name(program_id: str, custom_map: Dict[str, str]) -> str:
    """Resolve a program_id to a human name. Falls back to the raw id."""
    if not program_id:
        return "—"
    if program_id in custom_map:
        return custom_map[program_id]
    # Static catalog — resolved via the module-level hoisted reference.
    # No lazy import here: doing it inline caused a pool re-entrancy deadlock.
    if _internship_engine_programs:
        prog = _internship_engine_programs.get(program_id)
        if prog and isinstance(prog, dict):
            return prog.get("name") or program_id
    return program_id


def get_enrollment_overview(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    hide_test: bool = True,
) -> Dict:
    """
    Return summary + tier distribution + full enrollment list.

    Args:
        date_from: ISO date string (YYYY-MM-DD), inclusive. Optional.
        date_to:   ISO date string (YYYY-MM-DD), inclusive. Optional.
        hide_test: Filter out @charvak.local / @test.local / @example.com rows.
    """
    conn = db.get_pooled_connection()
    try:
        cur = conn.cursor()

        # --- Build WHERE clause safely (params, never concat) ---
        where_parts = []
        params: List = []
        if date_from:
            where_parts.append("e.start_date >= %s")
            params.append(date_from)
        if date_to:
            where_parts.append("e.start_date <= %s")
            params.append(date_to + " 23:59:59")
        where_sql = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""

        # --- Main query: enrollments joined to tiers ---
        cur.execute(f"""
            SELECT
                e.enrollment_id,
                e.email,
                e.program_id,
                e.tier_key,
                e.amount_paid_inr,
                e.razorpay_payment_id,
                e.status,
                e.current_day,
                e.total_days,
                e.start_date,
                t.tier_name,
                t.price_inr AS tier_price_inr
            FROM charvak_ai_internship_enrollments e
            LEFT JOIN charvak_ai_internship_tiers t ON t.tier_key = e.tier_key
            {where_sql}
            ORDER BY e.start_date DESC NULLS LAST
        """, params)
        rows = cur.fetchall()

        # --- Custom program name map (only fetch what we need) ---
        custom_ids = [r[2] for r in rows if r[2] and r[2].startswith("PROG-")]
        custom_map: Dict[str, str] = {}
        if custom_ids:
            cur.execute(
                "SELECT program_id, name FROM charvak_ai_internship_custom_programs WHERE program_id = ANY(%s)",
                (custom_ids,)
            )
            for r in cur.fetchall():
                custom_map[r[0]] = r[1]

        # --- Build enrollment list ---
        enrollments = []
        for r in rows:
            (enrollment_id, email, program_id, tier_key, amount_paid_inr,
             razorpay_payment_id, status, current_day, total_days,
             start_date, tier_name, tier_price_inr) = r

            if hide_test and _is_test_email(email):
                continue

            enrollments.append({
                "enrollment_id": enrollment_id,
                "email": email,
                "program_id": program_id,
                "program_name": _program_name(program_id, custom_map),
                "tier_key": tier_key,
                "tier_name": tier_name or tier_key or "—",
                "amount_paid_inr": amount_paid_inr or 0,
                "razorpay_payment_id": razorpay_payment_id,
                "status": status,
                "current_day": current_day,
                "total_days": total_days,
                "start_date": start_date.isoformat() if start_date else None,
            })

        # --- Summary + tier distribution (computed from filtered list) ---
        total_revenue = sum(e["amount_paid_inr"] for e in enrollments)
        active_count = sum(1 for e in enrollments if e["status"] == "active")
        abandoned_count = sum(1 for e in enrollments if e["status"] == "abandoned")
        completed_count = sum(1 for e in enrollments if e["status"] == "completed")
        paid_count = sum(1 for e in enrollments if e["amount_paid_inr"] > 0)

        # Tier distribution (only tiers with at least one enrollment)
        tier_dist: Dict[str, Dict] = {}
        for e in enrollments:
            key = e["tier_key"] or "unknown"
            if key not in tier_dist:
                tier_dist[key] = {
                    "tier_key": key,
                    "tier_name": e["tier_name"],
                    "count": 0,
                    "revenue_inr": 0,
                }
            tier_dist[key]["count"] += 1
            tier_dist[key]["revenue_inr"] += e["amount_paid_inr"]

        return {
            "status": "success",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "filters": {
                "date_from": date_from,
                "date_to": date_to,
                "hide_test": hide_test,
            },
            "summary": {
                "total_revenue_inr": total_revenue,
                "total_enrollments": len(enrollments),
                "active_count": active_count,
                "abandoned_count": abandoned_count,
                "completed_count": completed_count,
                "paid_count": paid_count,
            },
            "tier_distribution": sorted(tier_dist.values(), key=lambda x: -x["count"]),
            "enrollments": enrollments,
        }
    except Exception as e:
        logger.exception(f"get_enrollment_overview failed: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()


def to_csv(overview: Dict) -> str:
    """Render the enrollment list from get_enrollment_overview as CSV."""
    import csv
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "enrollment_id", "email", "program", "tier", "amount_inr",
        "razorpay_payment_id", "status", "day", "start_date"
    ])
    for e in overview.get("enrollments", []):
        w.writerow([
            e["enrollment_id"],
            e["email"],
            e["program_name"],
            e["tier_name"],
            e["amount_paid_inr"],
            e["razorpay_payment_id"] or "",
            e["status"],
            f'{e["current_day"] or 0}/{e["total_days"] or 0}',
            e["start_date"] or "",
        ])
    return buf.getvalue()


admin_internship_metrics = None  # module-level functions only, but expose a stable name
