"""
Charvak Course Payments - DB-backed EMI + access control.
Replaces the in-memory payment_enrollment.py flow.

Tables:
  charvak_course_prices        - Tier-1 fixed regional prices
  charvak_course_payments      - one row per gateway payment (idempotent)
  charvak_course_installments  - India EMI schedule (block-unlock model)
"""
import logging
import secrets
from datetime import datetime, timedelta, date, timezone

logger = logging.getLogger("charvakit.course_payments")

# Markets that offer EMI. Single flag so enabling more later is one line.
EMI_COUNTRIES = {"IN"}

# Markets with a fixed local price card. Rest of world converts from INR.
TIER1_MARKETS = {"IN", "US", "GB", "EU", "AE", "SG", "AU"}

# Multipliers applied to the base price / duration for level variants.
LEVEL_MULTIPLIERS = {
    "beginner":     {"price": 0.60, "weeks": 0.70},
    "intermediate": {"price": 1.00, "weeks": 1.00},
    "advanced":     {"price": 1.60, "weeks": 1.30},
}

# Country -> currency
CURRENCY_BY_COUNTRY = {
    "IN": "INR", "US": "USD", "GB": "GBP", "EU": "EUR",
    "AE": "AED", "SG": "SGD", "AU": "AUD",
    "CA": "CAD", "JP": "JPY", "HK": "HKD", "NZ": "NZD",
    "CH": "CHF", "SE": "SEK", "NO": "NOK", "DK": "DKK",
    "PL": "PLN", "MX": "MXN", "BR": "BRL",
    "DE": "EUR", "FR": "EUR", "ES": "EUR", "IT": "EUR",
    "NL": "EUR", "IE": "EUR", "PT": "EUR", "AT": "EUR",
    "BE": "EUR", "FI": "EUR", "GR": "EUR",
}

DEFAULT_CURRENCY = "USD"

# India Standard Time - EMI due dates use this since EMI is India-only.
IST = timezone(timedelta(hours=5, minutes=30))


def _ist_today():
    return datetime.now(IST).date()


class AICoursePayments:
    def __init__(self):
        self._ensure_tables()
        logger.info("AICoursePayments ready (DB-backed)")

    # ------------------------------------------------------------------
    # Schema safety net (migration also creates these; this is idempotent)
    # ------------------------------------------------------------------
    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_course_prices (
                    course_name     TEXT NOT NULL,
                    country_code    TEXT NOT NULL,
                    currency        TEXT NOT NULL,
                    amount_local    NUMERIC(10,2) NOT NULL,
                    razorpay_paise  INTEGER,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (course_name, country_code)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_course_payments (
                    payment_id          TEXT PRIMARY KEY,
                    enrollment_id       TEXT,
                    email               TEXT NOT NULL,
                    course_name         TEXT NOT NULL,
                    country_code        TEXT,
                    currency            TEXT NOT NULL,
                    amount_local        NUMERIC(10,2) NOT NULL,
                    amount_inr          INTEGER NOT NULL,
                    payment_type        TEXT NOT NULL,
                    installment_num     INTEGER,
                    razorpay_payment_id TEXT UNIQUE,
                    razorpay_order_id   TEXT,
                    paypal_order_id     TEXT,
                    gateway             TEXT NOT NULL,
                    status              TEXT NOT NULL DEFAULT 'pending',
                    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charvak_course_installments (
                    installment_id      TEXT PRIMARY KEY,
                    enrollment_id       TEXT NOT NULL,
                    email               TEXT NOT NULL,
                    installment_num     INTEGER NOT NULL,
                    total_installments  INTEGER NOT NULL,
                    amount_inr          INTEGER NOT NULL,
                    unlocks_from_week   INTEGER NOT NULL,
                    unlocks_to_week     INTEGER NOT NULL,
                    due_week            INTEGER NOT NULL,
                    due_date            DATE NOT NULL,
                    status              TEXT NOT NULL DEFAULT 'pending',
                    paid_at             TIMESTAMP,
                    payment_id          TEXT,
                    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(enrollment_id, installment_num)
                )
            """)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"course payment tables init failed: {e}")
    # ------------------------------------------------------------------
    # Price resolution
    # ------------------------------------------------------------------
    def resolve_price(self, course_name, country_code, level="intermediate"):
        """
        Returns:
          {status, course_name, country_code, level, currency, amount_local,
           amount_inr, razorpay_paise, duration_weeks, source}
        source is 'inr' | 'tier1' | 'converted'
        level: beginner | intermediate | advanced (default intermediate)
        """
        country_code = (country_code or "US").upper()
        level = (level or "intermediate").lower()
        if level not in LEVEL_MULTIPLIERS:
            level = "intermediate"
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            # 1) Try charvak_course_levels for the specific (course, level)
            cur.execute("""
                SELECT price_inr, duration_weeks FROM charvak_course_levels
                WHERE course_name = %s AND level = %s AND status = 'active'
            """, (course_name, level))
            lvl_row = cur.fetchone()

            # 2) Fallback: base catalog row (its duration_weeks)
            cur.execute(
                "SELECT price_inr, duration_weeks FROM charvak_courses WHERE course_name = %s",
                (course_name,)
            )
            base_row = cur.fetchone()
            if not base_row and not lvl_row:
                cur.close(); conn.close()
                return {"status": "error", "message": "Course not found"}

            if lvl_row:
                price_inr = int(lvl_row[0] or 0)
                duration_weeks = int(lvl_row[1] or 8)
            else:
                # Backward compat: no level row -> base price scaled by multiplier
                base_price = int(base_row[0] or 0)
                base_weeks = int(base_row[1] or 8)
                mul = LEVEL_MULTIPLIERS.get(level, LEVEL_MULTIPLIERS["intermediate"])
                price_inr = int(round(base_price * mul["price"]))
                duration_weeks = max(1, int(round(base_weeks * mul["weeks"])))

            if country_code == "IN":
                cur.close(); conn.close()
                return {
                    "status": "success",
                    "course_name": course_name,
                    "country_code": "IN",
                    "level": level,
                    "currency": "INR",
                    "amount_local": float(price_inr),
                    "amount_inr": price_inr,
                    "razorpay_paise": price_inr * 100,
                    "duration_weeks": duration_weeks,
                    "source": "inr",
                }

            # Tier-1: read base regional price, apply level multiplier
            cur.execute("""
                SELECT currency, amount_local, razorpay_paise
                FROM charvak_course_prices
                WHERE course_name = %s AND country_code = %s
            """, (course_name, country_code))
            t1 = cur.fetchone()
            if t1:
                cur.close(); conn.close()
                base_local = float(t1[1])
                mul = LEVEL_MULTIPLIERS.get(level, LEVEL_MULTIPLIERS["intermediate"])
                # Intermediate uses the fixed regional price verbatim;
                # Beginner/Advanced scale then round to X.99
                if level == "intermediate":
                    amount_local = base_local
                else:
                    amount_local = base_local * mul["price"]
                    # Round to nearest whole, then subtract 0.01 for .99 ending
                    amount_local = max(0.99, round(amount_local) - 0.01)
                return {
                    "status": "success",
                    "course_name": course_name,
                    "country_code": country_code,
                    "level": level,
                    "currency": t1[0],
                    "amount_local": round(amount_local, 2),
                    "amount_inr": price_inr,
                    "razorpay_paise": int(round(amount_local * 100)),
                    "duration_weeks": duration_weeks,
                    "source": "tier1",
                }

            # Rest of world: convert from the level-specific INR price
            currency = CURRENCY_BY_COUNTRY.get(country_code, DEFAULT_CURRENCY)
            from payment_engine import payment_engine
            rate = payment_engine.INR_RATES.get(currency, payment_engine.INR_RATES["USD"])
            amount_local = round(price_inr * rate, 2)
            if amount_local < 1:
                amount_local = 1.0
            cur.close(); conn.close()
            return {
                "status": "success",
                "course_name": course_name,
                "country_code": country_code,
                "level": level,
                "currency": currency,
                "amount_local": amount_local,
                "amount_inr": price_inr,
                "razorpay_paise": int(amount_local * 100),
                "duration_weeks": duration_weeks,
                "source": "converted",
            }
        except Exception as e:
            logger.error(f"resolve_price failed: {e}")
            return {"status": "error", "message": str(e)}
    def compute_emi_schedule(self, price_inr, duration_weeks):
        """
        2 blocks for <= 8 weeks, 3 blocks for > 8 weeks.
        Remainder weeks go to the LAST block (earlier blocks stay smallest).
        Earlier installments carry the rounded-up amount.
        Returns {num_installments, blocks:[{num,from,to,amount_inr,due_week}]}
        """
        n = 2 if duration_weeks <= 8 else 3

        base = duration_weeks // n
        rem = duration_weeks % n
        sizes = [base] * n
        sizes[-1] += rem
        sizes = [max(1, s) for s in sizes]

        base_amt = price_inr // n
        rem_amt = price_inr % n
        amounts = [base_amt + 1] * rem_amt + [base_amt] * (n - rem_amt)

        blocks = []
        start = 1
        for i in range(n):
            to = start + sizes[i] - 1
            blocks.append({
                "num": i + 1,
                "from": start,
                "to": to,
                "amount_inr": amounts[i],
                "due_week": start,
            })
            start = to + 1

        return {"num_installments": n, "blocks": blocks}

    # ------------------------------------------------------------------
    # Create paid enrollment + schedule
    # ------------------------------------------------------------------
    def create_enrollment_paid(self, email, course_name, duration_weeks=None,
                               country_code="IN", level="intermediate"):
        """
        Creates a pending_payment enrollment + (for EMI countries) the
        installment schedule. Reuses any existing pending_payment row so
        an abandoned checkout does not lock the student out.
        """
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT enrollment_id, status FROM charvak_enrollments
                WHERE email = %s AND course_name = %s AND user_level = %s
                  AND status IN ('active', 'pending_payment')
                ORDER BY started_at DESC LIMIT 1
            """, (email, course_name, level))
            existing = cur.fetchone()
            if existing:
                cur.close(); conn.close()
                return {"status": "exists",
                        "enrollment_id": existing[0],
                        "existing_status": existing[1]}

            # Resolve level-specific price and duration first.
            price = self.resolve_price(course_name, country_code, level)
            if price.get("status") != "success":
                cur.close(); conn.close()
                return price

            # Level-specific duration (overrides base course duration).
            level_weeks = int(price.get("duration_weeks") or duration_weeks or 8)

            enrollment_id = f"ENROLL-{secrets.token_hex(4).upper()}"

            cur.execute("""
                INSERT INTO charvak_enrollments
                    (enrollment_id, email, course_name, duration_weeks, user_level,
                     curriculum, total_weeks, status)
                VALUES (%s, %s, %s, %s, %s, NULL, %s, 'pending_payment')
            """, (enrollment_id, email, course_name, level_weeks, level, level_weeks))

            schedule = None
            if country_code.upper() in EMI_COUNTRIES:
                sched = self.compute_emi_schedule(price["amount_inr"], level_weeks)
                # sanity: every block must be within the course
                for _b in sched["blocks"]:
                    if _b["to"] > level_weeks or _b["from"] < 1:
                        logger.warning(f"EMI block out of range: {_b}, duration={level_weeks}")
                schedule = sched
                for b in sched["blocks"]:
                    inst_id = f"INST-{secrets.token_hex(4).upper()}"
                    due = _ist_today() + timedelta(weeks=b["due_week"] - 1)
                    cur.execute("""
                        INSERT INTO charvak_course_installments
                            (installment_id, enrollment_id, email,
                             installment_num, total_installments,
                             amount_inr, unlocks_from_week, unlocks_to_week,
                             due_week, due_date, status)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending')
                    """, (inst_id, enrollment_id, email,
                          b["num"], sched["num_installments"],
                          b["amount_inr"], b["from"], b["to"],
                          b["due_week"], due))

            conn.commit()
            cur.close(); conn.close()
            return {
                "status": "success",
                "enrollment_id": enrollment_id,
                "country_code": country_code.upper(),
                "level": level,
                "currency": price["currency"],
                "amount_local": price["amount_local"],
                "amount_inr": price["amount_inr"],
                "razorpay_paise": price["razorpay_paise"],
                "duration_weeks": level_weeks,
                "payment_type": "emi_installment" if schedule else "full",
                "schedule": schedule,
            }
        except Exception as e:
            logger.error(f"create_enrollment_paid failed: {e}")
            return {"status": "error", "message": str(e)}
    def record_payment(self, enrollment_id, email, course_name, country_code,
                       currency, amount_local, amount_inr, payment_type,
                       gateway, installment_num=None,
                       razorpay_payment_id=None, razorpay_order_id=None,
                       paypal_order_id=None):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            if razorpay_payment_id:
                cur.execute("""
                    SELECT payment_id FROM charvak_course_payments
                    WHERE razorpay_payment_id = %s AND status = 'captured'
                """, (razorpay_payment_id,))
                if cur.fetchone():
                    cur.close(); conn.close()
                    return {"status": "success", "already_recorded": True}

            pid = f"CPAY-{secrets.token_hex(5).upper()}"
            try:
                cur.execute("""
                    INSERT INTO charvak_course_payments
                        (payment_id, enrollment_id, email, course_name, country_code,
                         currency, amount_local, amount_inr, payment_type,
                         installment_num, razorpay_payment_id, razorpay_order_id,
                         paypal_order_id, gateway, status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'captured')
                """, (pid, enrollment_id, email, course_name, country_code,
                      currency, amount_local, amount_inr, payment_type,
                      installment_num, razorpay_payment_id, razorpay_order_id,
                      paypal_order_id, gateway))
            except Exception as ins_err:
                # Race: webhook + callback tried to insert same razorpay id
                conn.rollback()
                if razorpay_payment_id and "unique" in str(ins_err).lower():
                    cur.close(); conn.close()
                    return {"status": "success", "already_recorded": True}
                raise

            unlocked = None
            if payment_type == "emi_installment" and installment_num:
                cur.execute("""
                    UPDATE charvak_course_installments
                    SET status='paid', paid_at=CURRENT_TIMESTAMP, payment_id=%s
                    WHERE enrollment_id=%s AND installment_num=%s
                    RETURNING unlocks_from_week, unlocks_to_week
                """, (pid, enrollment_id, installment_num))
                row = cur.fetchone()
                if row:
                    unlocked = {"from": row[0], "to": row[1]}

            cur.execute("""
                UPDATE charvak_enrollments SET status='active'
                WHERE enrollment_id=%s
            """, (enrollment_id,))

            conn.commit()
            cur.close(); conn.close()
            return {"status": "success", "payment_id": pid,
                    "already_recorded": False, "unlocked": unlocked}
        except Exception as e:
            logger.error(f"record_payment failed: {e}")
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # Access check (allowed OR full unlock offer)
    # ------------------------------------------------------------------
    def check_access(self, enrollment_id, week_num):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute("""
                SELECT status, total_weeks FROM charvak_enrollments
                WHERE enrollment_id=%s
            """, (enrollment_id,))
            e = cur.fetchone()
            if not e:
                cur.close(); conn.close()
                return {"status": "error", "message": "Enrollment not found"}
            enroll_status, total_weeks = e[0], e[1] or 0

            cur.execute("""
                SELECT installment_num, total_installments, amount_inr,
                       unlocks_from_week, unlocks_to_week, due_date, status
                FROM charvak_course_installments
                WHERE enrollment_id=%s
                  AND unlocks_from_week <= %s AND unlocks_to_week >= %s
                ORDER BY installment_num LIMIT 1
            """, (enrollment_id, week_num, week_num))
            inst = cur.fetchone()

            if not inst:
                # No installment governs this week: full-payment or free course.
                cur.close(); conn.close()
                allowed = enroll_status in ("active", "completed")
                return {
                    "status": "success",
                    "allowed": allowed,
                    "week_num": week_num,
                    "enrollment_status": enroll_status,
                    "resume_week": week_num,
                }

            num, total, amt, ufrom, uto, due, st = inst

            # Compute resume week: first unlocked+unpaid week <= total
            cur.execute("""
                SELECT MIN(unlocks_from_week) FROM charvak_course_installments
                WHERE enrollment_id=%s AND status='pending'
            """, (enrollment_id,))
            resume_row = cur.fetchone()
            resume_week = resume_row[0] if resume_row and resume_row[0] else 1

            cur.close(); conn.close()

            if st == "paid":
                return {
                    "status": "success",
                    "allowed": True,
                    "week_num": week_num,
                    "enrollment_status": enroll_status,
                    "resume_week": resume_week,
                }

            days_until = (due - _ist_today()).days if due else None
            return {
                "status": "success",
                "allowed": False,
                "week_num": week_num,
                "reason": "installment_due",
                "installment": {"num": num, "of": total},
                "amount_inr": int(amt),
                "unlocks_weeks": f"{ufrom}-{uto}",
                "due_date": due.isoformat() if due else None,
                "days_until_due": days_until,
                "progress": {"block": num, "of": total},
                "resume_week": resume_week,
                "total_weeks": total_weeks,
                "pay_url": f"/my-course/{enrollment_id}",
                "message": (
                    f"Weeks {ufrom}-{uto} unlock after Installment "
                    f"{num} of {total} (INR {int(amt)})."
                ),
            }
        except Exception as e:
            logger.error(f"check_access failed: {e}")
            return {"status": "error", "message": str(e)}

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------
    def get_installments(self, enrollment_id):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT installment_num, total_installments, amount_inr,
                       unlocks_from_week, unlocks_to_week, due_week,
                       due_date, status, paid_at
                FROM charvak_course_installments
                WHERE enrollment_id=%s ORDER BY installment_num
            """, (enrollment_id,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            out = []
            for r in rows:
                out.append({
                    "installment_num": r[0],
                    "total_installments": r[1],
                    "amount_inr": int(r[2]),
                    "unlocks_from_week": r[3],
                    "unlocks_to_week": r[4],
                    "due_week": r[5],
                    "due_date": r[6].isoformat() if r[6] else None,
                    "status": r[7],
                    "paid_at": r[8].isoformat() if r[8] else None,
                })
            return {"status": "success", "installments": out, "count": len(out)}
        except Exception as e:
            logger.error(f"get_installments failed: {e}")
            return {"status": "error", "installments": [], "count": 0}

    def get_due_installments(self, days_ahead=3):
        """For the reminder script: installments due within N days or overdue."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT installment_id, enrollment_id, email, installment_num,
                       total_installments, amount_inr, unlocks_from_week,
                       unlocks_to_week, due_date, status
                FROM charvak_course_installments
                WHERE status IN ('pending','overdue')
                  AND due_date <= (CURRENT_DATE + %s)
                ORDER BY due_date
            """, (days_ahead,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            out = []
            for r in rows:
                out.append({
                    "installment_id": r[0],
                    "enrollment_id": r[1],
                    "email": r[2],
                    "installment_num": r[3],
                    "total_installments": r[4],
                    "amount_inr": int(r[5]),
                    "unlocks_from_week": r[6],
                    "unlocks_to_week": r[7],
                    "due_date": r[8].isoformat() if r[8] else None,
                    "status": r[9],
                })
            return {"status": "success", "installments": out, "count": len(out)}
        except Exception as e:
            logger.error(f"get_due_installments failed: {e}")
            return {"status": "error", "installments": [], "count": 0}



    # ------------------------------------------------------------------
    # Level listing (for the frontend selector)
    # ------------------------------------------------------------------
    def get_course_levels(self, course_name):
        """Return all 3 levels for a course with their India prices."""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT level, price_inr, duration_weeks, description
                FROM charvak_course_levels
                WHERE course_name = %s AND status = 'active'
                ORDER BY CASE level
                    WHEN 'beginner' THEN 1
                    WHEN 'intermediate' THEN 2
                    ELSE 3 END
            """, (course_name,))
            rows = cur.fetchall()
            cur.close(); conn.close()
            if not rows:
                # Fallback: synthesize 3 levels from catalog price
                cur2 = db.get_connection().cursor()
                return {"status": "error", "message": "No levels found for course"}
            levels = []
            for r in rows:
                levels.append({
                    "level": r[0],
                    "price_inr": int(r[1]),
                    "duration_weeks": int(r[2]),
                    "description": r[3] or "",
                })
            return {"status": "success", "course_name": course_name, "levels": levels}
        except Exception as e:
            logger.error(f"get_course_levels failed: {e}")
            return {"status": "error", "message": str(e)}

ai_course_payments = AICoursePayments()
