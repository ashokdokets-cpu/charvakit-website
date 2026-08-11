"""
Charvak Escrow Engine (Dokets VouchAI)
Handles secure payment escrow for B2B transactions
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

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
        self.transactions = []
        logger.info(f"✅ Escrow Engine: {'LIVE' if self.mode == 'live' else 'TEST'} mode | Fee: {PLATFORM_FEE_PERCENT}%")
    
    # ============================================================
    # CREATE ESCROW TRANSACTION
    # ============================================================
    
    def create_escrow(self, data: Dict) -> Dict:
        """
        Create a new escrow transaction.
        
        data = {
            "client_name": str,
            "client_email": str,
            "vendor_name": str,
            "vendor_email": str,
            "amount": float,
            "currency": str,
            "description": str,
            "milestones": List[Dict],
            "duration_days": int
        }
        """
        escrow_id = f"ESC-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        amount = float(data.get("amount", 0))
        platform_fee = round(amount * PLATFORM_FEE_PERCENT / 100, 2)
        
        transaction = {
            "escrow_id": escrow_id,
            "client_name": data.get("client_name"),
            "client_email": data.get("client_email"),
            "vendor_name": data.get("vendor_name"),
            "vendor_email": data.get("vendor_email"),
            "amount": amount,
            "currency": data.get("currency", "INR"),
            "platform_fee": platform_fee,
            "vendor_payout": round(amount - platform_fee, 2),
            "description": data.get("description", ""),
            "milestones": data.get("milestones", []),
            "status": EscrowStatus.AWAITING_DEPOSIT,
            "payment_method": "Dokets VouchAI Escrow",
            "created_at": datetime.now().isoformat(),
            "funded_at": None,
            "delivered_at": None,
            "released_at": None,
            "duration_days": data.get("duration_days", 30),
            "expires_at": (datetime.now() + timedelta(days=data.get("duration_days", 30))).isoformat(),
            "timeline": [
                {
                    "status": EscrowStatus.AWAITING_DEPOSIT,
                    "timestamp": datetime.now().isoformat(),
                    "note": "Escrow created — awaiting client deposit"
                }
            ]
        }
        
        self.transactions.append(transaction)
        logger.info(f"Escrow created: {escrow_id} | {data.get('client_name')} → {data.get('vendor_name')} | {amount} {data.get('currency', 'INR')}")
        
        return {
            "status": "success",
            "escrow_id": escrow_id,
            "amount": amount,
            "platform_fee": platform_fee,
            "vendor_receives": transaction["vendor_payout"],
            "message": "Escrow created. Client must deposit funds to activate.",
            "payment_link": f"/invoice?service=Escrow+Deposit&client={data.get('client_name')}&amount={int(amount)}",
            "expires_at": transaction["expires_at"]
        }
    
    # ============================================================
    # DEPOSIT FUNDS
    # ============================================================
    
    def deposit_funds(self, escrow_id: str, payment_details: Dict) -> Dict:
        """Client deposits funds into escrow."""
        for t in self.transactions:
            if t["escrow_id"] == escrow_id:
                if t["status"] != EscrowStatus.AWAITING_DEPOSIT:
                    return {"status": "error", "message": f"Cannot deposit. Current status: {t['status']}"}
                
                t["status"] = EscrowStatus.FUNDS_HELD
                t["funded_at"] = datetime.now().isoformat()
                t["payment_details"] = payment_details
                t["timeline"].append({
                    "status": EscrowStatus.FUNDS_HELD,
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Funds deposited: {t['amount']} {t['currency']} | Fee: {t['platform_fee']} {t['currency']}"
                })
                
                logger.info(f"Escrow funded: {escrow_id} | {t['amount']} {t['currency']}")
                
                return {
                    "status": "success",
                    "escrow_id": escrow_id,
                    "amount_held": t["amount"],
                    "message": "Funds secured in escrow. Vendor can begin work.",
                    "next_step": "Vendor delivers work → Client reviews → Funds released"
                }
        
        return {"status": "error", "message": "Escrow ID not found"}
    
    # ============================================================
    # DELIVER WORK
    # ============================================================
    
    def deliver_work(self, escrow_id: str, delivery_data: Dict) -> Dict:
        """Vendor marks work as delivered."""
        for t in self.transactions:
            if t["escrow_id"] == escrow_id:
                if t["status"] not in [EscrowStatus.FUNDS_HELD, EscrowStatus.WORK_IN_PROGRESS]:
                    return {"status": "error", "message": f"Cannot deliver. Current status: {t['status']}"}
                
                t["status"] = EscrowStatus.WORK_DELIVERED
                t["delivered_at"] = datetime.now().isoformat()
                t["delivery_data"] = delivery_data
                t["timeline"].append({
                    "status": EscrowStatus.WORK_DELIVERED,
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Work delivered by {t['vendor_name']}"
                })
                
                logger.info(f"Work delivered for escrow: {escrow_id}")
                
                return {
                    "status": "success",
                    "escrow_id": escrow_id,
                    "message": "Work delivered. Awaiting client review.",
                    "review_deadline": (datetime.now() + timedelta(days=7)).isoformat(),
                    "auto_release": f"Funds will auto-release in 7 days if no dispute is raised"
                }
        
        return {"status": "error", "message": "Escrow ID not found"}
    
    # ============================================================
    # RELEASE / APPROVE
    # ============================================================
    
    def release_funds(self, escrow_id: str) -> Dict:
        """Client approves work → funds released to vendor."""
        for t in self.transactions:
            if t["escrow_id"] == escrow_id:
                if t["status"] != EscrowStatus.WORK_DELIVERED:
                    return {"status": "error", "message": f"Cannot release. Current status: {t['status']}"}
                
                t["status"] = EscrowStatus.RELEASED
                t["released_at"] = datetime.now().isoformat()
                t["timeline"].append({
                    "status": EscrowStatus.RELEASED,
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Funds released to {t['vendor_name']}: {t['vendor_payout']} {t['currency']}"
                })
                
                logger.info(f"✅ Funds released: {escrow_id} | Vendor receives {t['vendor_payout']} {t['currency']}")
                
                return {
                    "status": "success",
                    "escrow_id": escrow_id,
                    "amount_released": t["vendor_payout"],
                    "platform_fee": t["platform_fee"],
                    "message": f"Funds released to {t['vendor_name']}. Transaction complete."
                }
        
        return {"status": "error", "message": "Escrow ID not found"}
    
    # ============================================================
    # DISPUTE
    # ============================================================
    
    def raise_dispute(self, escrow_id: str, dispute_data: Dict) -> Dict:
        """
        Raise a dispute on an escrow transaction.
        
        dispute_data = {
            "raised_by": "client" or "vendor",
            "reason": str,
            "details": str
        }
        """
        for t in self.transactions:
            if t["escrow_id"] == escrow_id:
                t["status"] = EscrowStatus.DISPUTED
                t["dispute"] = {
                    "raised_by": dispute_data.get("raised_by"),
                    "reason": dispute_data.get("reason"),
                    "details": dispute_data.get("details"),
                    "raised_at": datetime.now().isoformat(),
                    "status": "open"
                }
                t["timeline"].append({
                    "status": EscrowStatus.DISPUTED,
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Dispute raised by {dispute_data.get('raised_by')}: {dispute_data.get('reason')}"
                })
                
                logger.warning(f"⚠️ Dispute raised: {escrow_id} by {dispute_data.get('raised_by')}")
                
                return {
                    "status": "success",
                    "escrow_id": escrow_id,
                    "message": "Dispute registered. Our team will review within 48 hours.",
                    "resolution_process": [
                        "AI-powered dispute analysis",
                        "Mediation by Charvak team if needed",
                        "Evidence review from both parties",
                        "Final decision within 7 business days"
                    ]
                }
        
        return {"status": "error", "message": "Escrow ID not found"}
    
    def resolve_dispute(self, escrow_id: str, resolution: Dict) -> Dict:
        """
        Admin resolves a dispute.
        
        resolution = {
            "decision": "release_to_vendor" or "refund_to_client" or "split",
            "vendor_amount": float,
            "client_refund": float,
            "notes": str
        }
        """
        for t in self.transactions:
            if t["escrow_id"] == escrow_id and t["status"] == EscrowStatus.DISPUTED:
                t["dispute"]["status"] = "resolved"
                t["dispute"]["resolution"] = resolution
                t["dispute"]["resolved_at"] = datetime.now().isoformat()
                
                decision = resolution.get("decision")
                if decision == "release_to_vendor":
                    t["status"] = EscrowStatus.RELEASED
                    t["released_at"] = datetime.now().isoformat()
                elif decision == "refund_to_client":
                    t["status"] = EscrowStatus.REFUNDED
                else:
                    t["status"] = EscrowStatus.RELEASED
                
                t["timeline"].append({
                    "status": t["status"],
                    "timestamp": datetime.now().isoformat(),
                    "note": f"Dispute resolved: {resolution.get('notes', decision)}"
                })
                
                logger.info(f"Dispute resolved: {escrow_id} → {decision}")
                
                return {
                    "status": "success",
                    "escrow_id": escrow_id,
                    "resolution": decision,
                    "message": "Dispute resolved"
                }
        
        return {"status": "error", "message": "Escrow ID not found or not in dispute"}
    
    # ============================================================
    # QUERY
    # ============================================================
    
    def get_escrow(self, escrow_id: str) -> Dict:
        """Get escrow transaction details."""
        for t in self.transactions:
            if t["escrow_id"] == escrow_id:
                return {"status": "success", "transaction": t}
        return {"status": "error", "message": "Escrow ID not found"}
    
    def get_user_escrows(self, email: str) -> Dict:
        """Get all escrows for a user (client or vendor)."""
        user_escrows = [
            t for t in self.transactions 
            if t.get("client_email") == email or t.get("vendor_email") == email
        ]
        return {
            "status": "success",
            "escrows": user_escrows,
            "count": len(user_escrows),
            "active": len([t for t in user_escrows if t["status"] not in [EscrowStatus.RELEASED, EscrowStatus.REFUNDED, EscrowStatus.CANCELLED]]),
            "completed": len([t for t in user_escrows if t["status"] == EscrowStatus.RELEASED])
        }
    
    def get_stats(self) -> Dict:
        """Get escrow system statistics."""
        total = len(self.transactions)
        active = len([t for t in self.transactions if t["status"] not in [EscrowStatus.RELEASED, EscrowStatus.REFUNDED, EscrowStatus.CANCELLED]])
        total_held = sum(t["amount"] for t in self.transactions if t["status"] in [EscrowStatus.FUNDS_HELD, EscrowStatus.WORK_IN_PROGRESS, EscrowStatus.WORK_DELIVERED])
        total_fees = sum(t["platform_fee"] for t in self.transactions if t["status"] == EscrowStatus.RELEASED)
        disputed = len([t for t in self.transactions if t["status"] == EscrowStatus.DISPUTED])
        
        return {
            "status": "success",
            "stats": {
                "total_transactions": total,
                "active_escrows": active,
                "funds_held": round(total_held, 2),
                "platform_fees_earned": round(total_fees, 2),
                "disputed": disputed,
                "fee_percentage": PLATFORM_FEE_PERCENT
            }
        }


# ============================================================
# SINGLETON
# ============================================================
escrow_engine = EscrowEngine()