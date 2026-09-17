"""
Charvak North America - Revenue Engine
Automated billing, subscription management, and revenue tracking
(DB-backed - Session G/3)
"""
import json
import logging
import os
import secrets
from typing import Dict, List
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger("charvakit.na.revenue")


class SubscriptionTier(Enum):
    FREE = "Free (5 bench candidates)"
    STARTER = "Starter ($50/mo - 10 candidates)"
    GROWTH = "Growth ($100/mo - 25 candidates)"
    PRO = "Pro ($250/mo - 100 candidates)"
    ENTERPRISE = "Enterprise (Custom)"


class RevenueStream(Enum):
    PLACEMENT_FEE = "Placement Success Fee"
    SAAS_SUBSCRIPTION = "SaaS Subscription"
    ENTERPRISE_TIER = "Enterprise Tier"
    RESUME_PROCESSING = "Resume Processing"
    PREMIUM_MATCHING = "Premium Matching"


class RevenueEngine:
    """Automated revenue tracking and billing (DB-backed)"""

    PRICING = {
        "placement_fee_pct": 0.02,
        "saas_starter": 50,
        "saas_growth": 100,
        "saas_pro": 250,
        "enterprise_monthly": 2000,
        "resume_processing": 0.75,
        "premium_matching": 25,
    }

    def __init__(self):
        self._ensure_tables()
        logger.info("Revenue Engine ready (DB-backed)")

    def _ensure_tables(self):
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_revenue_subscriptions (
                    firm_id         TEXT PRIMARY KEY,
                    subscription_id TEXT,
                    tier            TEXT,
                    bench_limit     INTEGER DEFAULT 0,
                    features        JSONB DEFAULT '[]'::jsonb,
                    monthly_fee     NUMERIC(12,2) DEFAULT 0,
                    status          TEXT DEFAULT 'active',
                    start_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    next_billing    TIMESTAMP,
                    payment_method  TEXT,
                    auto_renew      BOOLEAN DEFAULT TRUE
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_rev_subs_status ON charvak_na_revenue_subscriptions(status)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_rev_subs_tier   ON charvak_na_revenue_subscriptions(tier)''')
            cur.execute('''
                CREATE TABLE IF NOT EXISTS charvak_na_revenue_transactions (
                    transaction_id  TEXT PRIMARY KEY,
                    firm_id         TEXT NOT NULL,
                    stream          TEXT NOT NULL,
                    amount          NUMERIC(12,2) DEFAULT 0,
                    details         JSONB DEFAULT '{}'::jsonb,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_rev_txn_firm   ON charvak_na_revenue_transactions(firm_id)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_rev_txn_stream ON charvak_na_revenue_transactions(stream)''')
            cur.execute('''CREATE INDEX IF NOT EXISTS idx_na_rev_txn_time   ON charvak_na_revenue_transactions(created_at)''')
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"revenue_engine tables init failed: {e}")

    # ============ SUBSCRIPTION MANAGEMENT ============

    def create_subscription(self, firm_id: str, tier: SubscriptionTier) -> Dict:
        """Create or upgrade a consulting firm's subscription"""
        subscription_id = f"SUB-{secrets.token_hex(4).upper()}"
        now = datetime.now()
        next_billing = now + timedelta(days=30)

        subscription = {
            "subscription_id": subscription_id,
            "firm_id": firm_id,
            "tier": tier.value,
            "bench_limit": self._get_bench_limit(tier),
            "features": self._get_features(tier),
            "monthly_fee": self._get_monthly_fee(tier),
            "status": "active",
            "start_date": now.isoformat(),
            "next_billing": next_billing.isoformat(),
            "payment_method": "Dokets VouchAI Escrow",
            "auto_renew": True,
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO charvak_na_revenue_subscriptions (
                    firm_id, subscription_id, tier, bench_limit, features,
                    monthly_fee, status, start_date, next_billing, payment_method, auto_renew
                ) VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (firm_id) DO UPDATE SET
                    subscription_id = EXCLUDED.subscription_id,
                    tier = EXCLUDED.tier,
                    bench_limit = EXCLUDED.bench_limit,
                    features = EXCLUDED.features,
                    monthly_fee = EXCLUDED.monthly_fee,
                    status = EXCLUDED.status,
                    start_date = EXCLUDED.start_date,
                    next_billing = EXCLUDED.next_billing,
                    payment_method = EXCLUDED.payment_method,
                    auto_renew = EXCLUDED.auto_renew
            ''', (
                firm_id, subscription_id, subscription["tier"], subscription["bench_limit"],
                json.dumps(subscription["features"]), subscription["monthly_fee"],
                subscription["status"], subscription["start_date"], subscription["next_billing"],
                subscription["payment_method"], subscription["auto_renew"],
            ))

            self._insert_transaction(
                cur, RevenueStream.SAAS_SUBSCRIPTION.value, firm_id,
                subscription["monthly_fee"], subscription,
            )
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"create_subscription failed: {e}")

        return subscription

    def _get_bench_limit(self, tier: SubscriptionTier) -> int:
        limits = {
            SubscriptionTier.FREE: 5,
            SubscriptionTier.STARTER: 10,
            SubscriptionTier.GROWTH: 25,
            SubscriptionTier.PRO: 100,
            SubscriptionTier.ENTERPRISE: 999999,
        }
        return limits.get(tier, 5)

    def _get_monthly_fee(self, tier: SubscriptionTier) -> float:
        fees = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.STARTER: self.PRICING["saas_starter"],
            SubscriptionTier.GROWTH: self.PRICING["saas_growth"],
            SubscriptionTier.PRO: self.PRICING["saas_pro"],
            SubscriptionTier.ENTERPRISE: self.PRICING["enterprise_monthly"],
        }
        return fees.get(tier, 0)

    def _get_features(self, tier: SubscriptionTier) -> List[str]:
        base_features = ["AI Matching", "Work Auth Verification", "Basic Tracking"]
        if tier in [SubscriptionTier.GROWTH, SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]:
            base_features.extend(["Priority Matching", "Advanced Analytics", "API Access"])
        if tier in [SubscriptionTier.PRO, SubscriptionTier.ENTERPRISE]:
            base_features.extend(["Dedicated Account Manager", "Custom Integrations", "Bulk Resume Processing"])
        if tier == SubscriptionTier.ENTERPRISE:
            base_features.extend(["White Label Option", "SLA Guarantee", "24/7 Support"])
        return base_features

    # ============ TRANSACTION TRACKING ============

    def _insert_transaction(self, cur, stream: str, firm_id: str, amount: float, details: Dict):
        """Helper: insert a transaction row (assumes open cursor)."""
        txn_id = details.get("transaction_id") or f"TXN-{secrets.token_hex(4).upper()}"
        cur.execute('''
            INSERT INTO charvak_na_revenue_transactions
                (transaction_id, firm_id, stream, amount, details)
            VALUES (%s, %s, %s, %s, %s::jsonb)
        ''', (txn_id, firm_id, stream, amount, json.dumps(details)))

    def track_placement(self, firm_id: str, candidate_id: str,
                        contract_value: float, rate: float) -> Dict:
        """Track a successful placement and calculate fee"""
        fee = round(contract_value * self.PRICING["placement_fee_pct"], 2)
        txn_id = f"TXN-{secrets.token_hex(4).upper()}"

        transaction = {
            "transaction_id": txn_id,
            "type": RevenueStream.PLACEMENT_FEE.value,
            "firm_id": firm_id,
            "candidate_id": candidate_id,
            "contract_value": contract_value,
            "rate": rate,
            "fee": fee,
            "fee_pct": self.PRICING["placement_fee_pct"],
            "status": "pending_payment",
            "created_at": datetime.now().isoformat(),
            "payment_method": "Dokets VouchAI Escrow",
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            self._insert_transaction(cur, RevenueStream.PLACEMENT_FEE.value, firm_id, fee, transaction)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"track_placement failed: {e}")

        return transaction

    def track_resume_processing(self, firm_id: str, resume_count: int) -> Dict:
        """Track bulk resume processing charges"""
        total_fee = round(resume_count * self.PRICING["resume_processing"], 2)
        txn_id = f"TXN-{secrets.token_hex(4).upper()}"

        transaction = {
            "transaction_id": txn_id,
            "type": RevenueStream.RESUME_PROCESSING.value,
            "firm_id": firm_id,
            "resume_count": resume_count,
            "rate_per_resume": self.PRICING["resume_processing"],
            "total_fee": total_fee,
            "created_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            self._insert_transaction(cur, RevenueStream.RESUME_PROCESSING.value, firm_id, total_fee, transaction)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"track_resume_processing failed: {e}")

        return transaction

    def track_premium_match(self, firm_id: str, match_count: int = 1) -> Dict:
        """Track premium matching requests"""
        total_fee = match_count * self.PRICING["premium_matching"]
        txn_id = f"TXN-{secrets.token_hex(4).upper()}"

        transaction = {
            "transaction_id": txn_id,
            "type": RevenueStream.PREMIUM_MATCHING.value,
            "firm_id": firm_id,
            "match_count": match_count,
            "total_fee": total_fee,
            "created_at": datetime.now().isoformat(),
        }

        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            self._insert_transaction(cur, RevenueStream.PREMIUM_MATCHING.value, firm_id, total_fee, transaction)
            conn.commit()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"track_premium_match failed: {e}")

        return transaction

    # ============ REVENUE ANALYTICS ============

    def get_total_revenue(self) -> Dict:
        """Get total revenue across all streams"""
        empty_streams = {s.value: 0 for s in RevenueStream}
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('SELECT COALESCE(SUM(amount), 0) FROM charvak_na_revenue_transactions')
            total_revenue = float(cur.fetchone()[0] or 0)

            cur.execute('''
                SELECT stream, COALESCE(SUM(amount), 0)
                FROM charvak_na_revenue_transactions
                GROUP BY stream
            ''')
            for stream, amt in cur.fetchall():
                empty_streams[stream] = float(amt or 0)

            cur.execute('SELECT COUNT(*) FROM charvak_na_revenue_transactions')
            total_transactions = int(cur.fetchone()[0] or 0)

            cur.execute("SELECT COUNT(*) FROM charvak_na_revenue_subscriptions WHERE status = 'active'")
            active_subscriptions = int(cur.fetchone()[0] or 0)

            cur.execute('''
                SELECT COALESCE(SUM(monthly_fee), 0)
                FROM charvak_na_revenue_subscriptions WHERE status = 'active'
            ''')
            mrr = float(cur.fetchone()[0] or 0)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_total_revenue failed: {e}")
            return {
                "total_revenue": 0,
                "by_stream": empty_streams,
                "total_transactions": 0,
                "active_subscriptions": 0,
                "monthly_recurring_revenue": 0,
            }

        return {
            "total_revenue": total_revenue,
            "by_stream": empty_streams,
            "total_transactions": total_transactions,
            "active_subscriptions": active_subscriptions,
            "monthly_recurring_revenue": mrr,
        }

    def get_monthly_revenue(self, month: str = None) -> Dict:
        """Get revenue for a specific month"""
        if not month:
            month = datetime.now().strftime("%Y-%m")
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()
            cur.execute('''
                SELECT stream, COALESCE(SUM(amount), 0)
                FROM charvak_na_revenue_transactions
                WHERE TO_CHAR(created_at, 'YYYY-MM') = %s
                GROUP BY stream
            ''', (month,))
            rows = cur.fetchall()
            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_monthly_revenue failed: {e}")
            return {}

        return {stream: float(amt or 0) for stream, amt in rows}

    def get_firm_revenue(self, firm_id: str) -> Dict:
        """Get revenue from a specific firm"""
        try:
            from database import db
            conn = db.get_connection()
            cur = conn.cursor()

            cur.execute('''
                SELECT firm_id, subscription_id, tier, bench_limit, features,
                       monthly_fee, status, start_date, next_billing, payment_method, auto_renew
                FROM charvak_na_revenue_subscriptions WHERE firm_id = %s
            ''', (firm_id,))
            sub_row = cur.fetchone()
            subscription = {}
            if sub_row:
                subscription = {
                    "subscription_id": sub_row[1],
                    "firm_id": sub_row[0],
                    "tier": sub_row[2],
                    "bench_limit": sub_row[3],
                    "features": sub_row[4] if isinstance(sub_row[4], list) else (json.loads(sub_row[4]) if sub_row[4] else []),
                    "monthly_fee": float(sub_row[5]) if sub_row[5] is not None else 0,
                    "status": sub_row[6],
                    "start_date": sub_row[7].isoformat() if hasattr(sub_row[7], "isoformat") else str(sub_row[7]),
                    "next_billing": sub_row[8].isoformat() if sub_row[8] and hasattr(sub_row[8], "isoformat") else None,
                    "payment_method": sub_row[9],
                    "auto_renew": bool(sub_row[10]),
                }

            cur.execute('SELECT COUNT(*) FROM charvak_na_revenue_transactions WHERE firm_id = %s', (firm_id,))
            total_transactions = int(cur.fetchone()[0] or 0)

            cur.execute('SELECT COALESCE(SUM(amount), 0) FROM charvak_na_revenue_transactions WHERE firm_id = %s', (firm_id,))
            total_revenue = float(cur.fetchone()[0] or 0)

            cur.execute('''
                SELECT details FROM charvak_na_revenue_transactions
                WHERE firm_id = %s
                ORDER BY created_at DESC
                LIMIT 10
            ''', (firm_id,))
            txns = []
            for r in cur.fetchall():
                d = r[0] if isinstance(r[0], dict) else (json.loads(r[0]) if r[0] else {})
                txns.append(d)

            cur.close(); conn.close()
        except Exception as e:
            logger.error(f"get_firm_revenue failed: {e}")
            return {
                "firm_id": firm_id,
                "subscription": {},
                "total_transactions": 0,
                "total_revenue": 0,
                "subscription_revenue": 0,
                "transactions": [],
            }

        return {
            "firm_id": firm_id,
            "subscription": subscription,
            "total_transactions": total_transactions,
            "total_revenue": total_revenue,
            "subscription_revenue": subscription.get("monthly_fee", 0),
            "transactions": txns[-10:],
        }


# Initialize revenue engine
revenue_engine = RevenueEngine()

# ============================================================
# DEMO REVENUE - loaded only when CHARVAK_LOAD_DEMO_REVENUE=1
# ============================================================
if os.getenv("CHARVAK_LOAD_DEMO_REVENUE", "0") == "1":
    revenue_engine.create_subscription("FIRM-001", SubscriptionTier.GROWTH)
    revenue_engine.create_subscription("FIRM-002", SubscriptionTier.STARTER)
    revenue_engine.track_placement("FIRM-001", "CAND-001", 160000, 80)
    revenue_engine.track_placement("FIRM-002", "CAND-002", 140000, 70)
    revenue_engine.track_resume_processing("FIRM-001", 50)
    revenue_engine.track_premium_match("FIRM-001", 3)
    logger.info("Revenue Engine: loaded demo data (CHARVAK_LOAD_DEMO_REVENUE=1)")