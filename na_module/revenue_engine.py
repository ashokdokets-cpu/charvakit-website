"""
Charvak North America - Revenue Engine
Automated billing, subscription management, and revenue tracking
"""
import secrets
from typing import Dict, List
from datetime import datetime, timedelta
from enum import Enum

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
    """Automated revenue tracking and billing"""
    
    PRICING = {
        "placement_fee_pct": 0.02,  # 2% of contract value
        "saas_starter": 50,  # $50/month
        "saas_growth": 100,  # $100/month
        "saas_pro": 250,  # $250/month
        "enterprise_monthly": 2000,  # Starting at $2,000/month
        "resume_processing": 0.75,  # $0.75 per resume
        "premium_matching": 25,  # $25 per premium match
    }
    
    def __init__(self):
        self.subscriptions = {}
        self.transactions = []
        self.revenue_by_stream = {stream.value: 0 for stream in RevenueStream}
        self.monthly_revenue = {}
    
    # ============ SUBSCRIPTION MANAGEMENT ============
    
    def create_subscription(self, firm_id: str, tier: SubscriptionTier) -> Dict:
        """Create or upgrade a consulting firm's subscription"""
        subscription = {
            "subscription_id": f"SUB-{secrets.token_hex(4).upper()}",
            "firm_id": firm_id,
            "tier": tier.value,
            "bench_limit": self._get_bench_limit(tier),
            "features": self._get_features(tier),
            "monthly_fee": self._get_monthly_fee(tier),
            "status": "active",
            "start_date": datetime.now().isoformat(),
            "next_billing": (datetime.now() + timedelta(days=30)).isoformat(),
            "payment_method": "Dokets VouchAI Escrow",
            "auto_renew": True
        }
        
        self.subscriptions[firm_id] = subscription
        self._track_revenue(RevenueStream.SAAS_SUBSCRIPTION, subscription["monthly_fee"])
        
        return subscription
    
    def _get_bench_limit(self, tier: SubscriptionTier) -> int:
        limits = {
            SubscriptionTier.FREE: 5,
            SubscriptionTier.STARTER: 10,
            SubscriptionTier.GROWTH: 25,
            SubscriptionTier.PRO: 100,
            SubscriptionTier.ENTERPRISE: 999999
        }
        return limits.get(tier, 5)
    
    def _get_monthly_fee(self, tier: SubscriptionTier) -> float:
        fees = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.STARTER: self.PRICING["saas_starter"],
            SubscriptionTier.GROWTH: self.PRICING["saas_growth"],
            SubscriptionTier.PRO: self.PRICING["saas_pro"],
            SubscriptionTier.ENTERPRISE: self.PRICING["enterprise_monthly"]
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
    
    def track_placement(self, firm_id: str, candidate_id: str, 
                        contract_value: float, rate: float) -> Dict:
        """Track a successful placement and calculate fee"""
        fee = round(contract_value * self.PRICING["placement_fee_pct"], 2)
        
        transaction = {
            "transaction_id": f"TXN-{secrets.token_hex(4).upper()}",
            "type": RevenueStream.PLACEMENT_FEE.value,
            "firm_id": firm_id,
            "candidate_id": candidate_id,
            "contract_value": contract_value,
            "rate": rate,
            "fee": fee,
            "fee_pct": self.PRICING["placement_fee_pct"],
            "status": "pending_payment",
            "created_at": datetime.now().isoformat(),
            "payment_method": "Dokets VouchAI Escrow"
        }
        
        self.transactions.append(transaction)
        self._track_revenue(RevenueStream.PLACEMENT_FEE, fee)
        
        return transaction
    
    def track_resume_processing(self, firm_id: str, resume_count: int) -> Dict:
        """Track bulk resume processing charges"""
        total_fee = round(resume_count * self.PRICING["resume_processing"], 2)
        
        transaction = {
            "transaction_id": f"TXN-{secrets.token_hex(4).upper()}",
            "type": RevenueStream.RESUME_PROCESSING.value,
            "firm_id": firm_id,
            "resume_count": resume_count,
            "rate_per_resume": self.PRICING["resume_processing"],
            "total_fee": total_fee,
            "created_at": datetime.now().isoformat()
        }
        
        self.transactions.append(transaction)
        self._track_revenue(RevenueStream.RESUME_PROCESSING, total_fee)
        
        return transaction
    
    def track_premium_match(self, firm_id: str, match_count: int = 1) -> Dict:
        """Track premium matching requests"""
        total_fee = match_count * self.PRICING["premium_matching"]
        
        transaction = {
            "transaction_id": f"TXN-{secrets.token_hex(4).upper()}",
            "type": RevenueStream.PREMIUM_MATCHING.value,
            "firm_id": firm_id,
            "match_count": match_count,
            "total_fee": total_fee,
            "created_at": datetime.now().isoformat()
        }
        
        self.transactions.append(transaction)
        self._track_revenue(RevenueStream.PREMIUM_MATCHING, total_fee)
        
        return transaction
    
    # ============ REVENUE ANALYTICS ============
    
    def _track_revenue(self, stream: RevenueStream, amount: float):
        """Internal revenue tracking"""
        self.revenue_by_stream[stream.value] += amount
        
        month_key = datetime.now().strftime("%Y-%m")
        if month_key not in self.monthly_revenue:
            self.monthly_revenue[month_key] = {s.value: 0 for s in RevenueStream}
        self.monthly_revenue[month_key][stream.value] += amount
    
    def get_total_revenue(self) -> Dict:
        """Get total revenue across all streams"""
        return {
            "total_revenue": sum(self.revenue_by_stream.values()),
            "by_stream": self.revenue_by_stream,
            "total_transactions": len(self.transactions),
            "active_subscriptions": len([s for s in self.subscriptions.values() if s["status"] == "active"]),
            "monthly_recurring_revenue": sum(
                s["monthly_fee"] for s in self.subscriptions.values() if s["status"] == "active"
            )
        }
    
    def get_monthly_revenue(self, month: str = None) -> Dict:
        """Get revenue for a specific month"""
        if not month:
            month = datetime.now().strftime("%Y-%m")
        return self.monthly_revenue.get(month, {})
    
    def get_firm_revenue(self, firm_id: str) -> Dict:
        """Get revenue from a specific firm"""
        firm_txns = [t for t in self.transactions if t.get("firm_id") == firm_id]
        subscription = self.subscriptions.get(firm_id, {})
        
        return {
            "firm_id": firm_id,
            "subscription": subscription,
            "total_transactions": len(firm_txns),
            "total_revenue": sum(t.get("fee", t.get("total_fee", 0)) for t in firm_txns),
            "subscription_revenue": subscription.get("monthly_fee", 0),
            "transactions": firm_txns[-10:]  # Last 10 transactions
        }

# Initialize revenue engine
revenue_engine = RevenueEngine()

# Seed some sample data
revenue_engine.create_subscription("FIRM-001", SubscriptionTier.GROWTH)
revenue_engine.create_subscription("FIRM-002", SubscriptionTier.STARTER)
revenue_engine.track_placement("FIRM-001", "CAND-001", 160000, 80)  # $160K contract, $80/hr
revenue_engine.track_placement("FIRM-002", "CAND-002", 140000, 70)
revenue_engine.track_resume_processing("FIRM-001", 50)
revenue_engine.track_premium_match("FIRM-001", 3)

print(f"✅ Revenue Engine initialized")
print(f"   Total Revenue: ${revenue_engine.get_total_revenue()['total_revenue']:,.2f}")
print(f"   Active Subscriptions: {revenue_engine.get_total_revenue()['active_subscriptions']}")
print(f"   MRR: ${revenue_engine.get_total_revenue()['monthly_recurring_revenue']:,.2f}")