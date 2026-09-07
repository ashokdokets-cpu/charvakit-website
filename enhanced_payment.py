"""
Charvak Enhanced Payment System
Integrates with existing payment_engine
Adds: Subscriptions, Discounts, IP Detection
"""
import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.enhanced_payment")

class EnhancedPaymentSystem:
    def __init__(self):
        self.subscriptions = {}
        self.discount_codes = self._initialize_discount_codes()
        self.transactions = {}
        self.subscription_plans = self._initialize_subscription_plans()
        logger.info("Enhanced Payment System ready")
    
    def _initialize_discount_codes(self):
        """Initialize discount code system with expiry."""
        return {
            "STUDENT25": {
                "type": "student",
                "discount_percent": 25,
                "valid_until": "2026-12-31",
                "max_uses": 1000,
                "used_count": 0,
                "status": "active",
                "description": "25% off for verified students"
            },
            "STUDENT50": {
                "type": "student",
                "discount_percent": 50,
                "valid_until": "2026-12-31",
                "max_uses": 500,
                "used_count": 0,
                "status": "active",
                "description": "50% off for verified students"
            },
            "LAUNCH20": {
                "type": "promotional",
                "discount_percent": 20,
                "valid_until": "2026-09-30",
                "max_uses": 100,
                "used_count": 0,
                "status": "active",
                "description": "Launch offer - 20% off"
            },
            "FLASH50": {
                "type": "promotional",
                "discount_percent": 50,
                "valid_until": "2026-09-15",
                "max_uses": 50,
                "used_count": 0,
                "status": "active",
                "description": "Flash sale - 50% off"
            },
            "EARLYBIRD30": {
                "type": "promotional",
                "discount_percent": 30,
                "valid_until": "2026-10-01",
                "max_uses": 200,
                "used_count": 0,
                "status": "active",
                "description": "Early bird - 30% off"
            },
            "BULK10": {
                "type": "bulk",
                "discount_percent": 10,
                "min_quantity": 5,
                "valid_until": "2026-12-31",
                "max_uses": 500,
                "used_count": 0,
                "status": "active",
                "description": "10% off for 5+ seats"
            },
            "BULK20": {
                "type": "bulk",
                "discount_percent": 20,
                "min_quantity": 10,
                "valid_until": "2026-12-31",
                "max_uses": 300,
                "used_count": 0,
                "status": "active",
                "description": "20% off for 10+ seats"
            },
            "BULK30": {
                "type": "bulk",
                "discount_percent": 30,
                "min_quantity": 20,
                "valid_until": "2026-12-31",
                "max_uses": 200,
                "used_count": 0,
                "status": "active",
                "description": "30% off for 20+ seats"
            },
            "FESTIVE15": {
                "type": "seasonal",
                "discount_percent": 15,
                "valid_until": "2026-11-15",
                "max_uses": 500,
                "used_count": 0,
                "status": "active",
                "description": "Festive season - 15% off"
            },
            "NEWYEAR25": {
                "type": "seasonal",
                "discount_percent": 25,
                "valid_until": "2027-01-15",
                "max_uses": 300,
                "used_count": 0,
                "status": "active",
                "description": "New Year - 25% off"
            }
        }
    
    def _initialize_subscription_plans(self):
        """Initialize subscription plans."""
        return [
            {
                "id": "free",
                "name": "Free",
                "price_usd": 0,
                "duration_months": 0,
                "features": [
                    "Basic assessments",
                    "5 AI credits/month",
                    "Community support"
                ]
            },
            {
                "id": "starter",
                "name": "Starter",
                "price_usd": 29,
                "duration_months": 1,
                "features": [
                    "All assessments",
                    "50 AI credits/month",
                    "Email support",
                    "1 certificate/month"
                ]
            },
            {
                "id": "professional",
                "name": "Professional",
                "price_usd": 79,
                "duration_months": 1,
                "features": [
                    "Unlimited assessments",
                    "200 AI credits/month",
                    "Priority support",
                    "5 certificates/month",
                    "Company mock drives"
                ]
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price_usd": 299,
                "duration_months": 1,
                "features": [
                    "Everything in Professional",
                    "Unlimited AI credits",
                    "Dedicated support",
                    "Team management",
                    "Custom assessments"
                ]
            },
            {
                "id": "annual_starter",
                "name": "Annual Starter",
                "price_usd": 290,
                "duration_months": 12,
                "features": [
                    "Everything in Starter",
                    "2 months free",
                    "Annual discount"
                ]
            },
            {
                "id": "annual_professional",
                "name": "Annual Professional",
                "price_usd": 790,
                "duration_months": 12,
                "features": [
                    "Everything in Professional",
                    "2 months free",
                    "Annual discount"
                ]
            }
        ]
    
    def get_subscription_plans(self, country_code="US"):
        """Get subscription plans with localized pricing."""
        from integrated_pricing import integrated_pricing
        
        localized_plans = []
        for plan in self.subscription_plans:
            price = integrated_pricing.get_localized_price(plan["price_usd"], country_code)
            localized_plans.append({
                **plan,
                "localized_price": price["localized_amount"],
                "currency": price["currency"],
                "symbol": price["symbol"],
                "display_price": price["display_price"]
            })
        
        return {"status": "success", "country": country_code, "plans": localized_plans}
    
    def validate_discount_code(self, code, user_type=None, quantity=1):
        """Validate discount code with all checks."""
        code = code.upper().strip() if code else ""
        
        if code not in self.discount_codes:
            return {"status": "error", "message": "Invalid discount code"}
        
        discount = self.discount_codes[code]
        
        # Check if active
        if discount["status"] != "active":
            return {"status": "error", "message": f"Code {discount['status']}"}
        
        # Check expiry
        try:
            valid_until = datetime.strptime(discount["valid_until"], "%Y-%m-%d")
            if datetime.now() > valid_until:
                discount["status"] = "expired"
                return {"status": "error", "message": "Discount code has expired"}
        except:
            pass
        
        # Check usage
        if discount["used_count"] >= discount["max_uses"]:
            return {"status": "error", "message": "Discount code usage limit reached"}
        
        # Check bulk requirement
        if discount["type"] == "bulk" and quantity < discount.get("min_quantity", 1):
            return {
                "status": "error", 
                "message": f"Minimum {discount.get('min_quantity')} seats required for this code"
            }
        
        # Check student verification
        if discount["type"] == "student" and user_type != "student":
            return {
                "status": "error", 
                "message": "Student verification required. Please use your student email."
            }
        
        return {
            "status": "success",
            "code": code,
            "discount_percent": discount["discount_percent"],
            "type": discount["type"],
            "description": discount.get("description", ""),
            "valid_until": discount["valid_until"]
        }
    
    def apply_discount(self, base_price, discount_code, user_type=None, quantity=1):
        """Apply discount to price."""
        validation = self.validate_discount_code(discount_code, user_type, quantity)
        
        if validation["status"] != "success":
            return validation
        
        discount_percent = validation["discount_percent"]
        discount_amount = base_price * (discount_percent / 100)
        final_price = base_price - discount_amount
        
        # Increment usage
        self.discount_codes[discount_code]["used_count"] += 1
        
        return {
            "status": "success",
            "base_price": base_price,
            "discount_code": discount_code,
            "discount_percent": discount_percent,
            "discount_amount": round(discount_amount, 2),
            "final_price": round(final_price, 2),
            "savings": round(discount_amount, 2)
        }
    
    def subscribe_user(self, email, plan_id, country_code="US", discount_code=None, user_type=None):
        """Subscribe user to plan with discount."""
        plans = self.get_subscription_plans(country_code)["plans"]
        plan = next((p for p in plans if p["id"] == plan_id), None)
        
        if not plan:
            return {"status": "error", "message": "Plan not found"}
        
        base_price = plan["price_usd"]
        final_price = base_price
        discount_info = None
        
        if discount_code:
            discount_result = self.apply_discount(base_price, discount_code, user_type)
            if discount_result["status"] == "success":
                final_price = discount_result["final_price"]
                discount_info = discount_result
            else:
                return discount_result
        
        subscription_id = f"SUB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        duration_days = plan["duration_months"] * 30 if plan["duration_months"] > 0 else 0
        expires_at = (datetime.now() + timedelta(days=duration_days)).isoformat() if duration_days > 0 else None
        
        self.transactions[subscription_id] = {
            "subscription_id": subscription_id,
            "email": email,
            "plan_id": plan_id,
            "plan_name": plan["name"],
            "country": country_code,
            "base_price": base_price,
            "final_price": final_price,
            "discount": discount_info,
            "started_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "status": "active"
        }
        
        return {
            "status": "success",
            "subscription": self.transactions[subscription_id]
        }
    
    def detect_location_from_ip(self, ip_address):
        """Detect location from IP (production: use geolocation)."""
        # In production, use:
        # - ipapi.co, ipinfo.io, MaxMind GeoIP
        # For now, simple mapping
        ip_country_map = {
            "8.8.8.8": "US",
            "8.8.4.4": "US",
            "1.1.1.1": "AU",
            "103.0.0.0": "IN"
        }
        
        country_code = ip_country_map.get(ip_address, "US")
        
        from integrated_pricing import integrated_pricing
        price_info = integrated_pricing.get_localized_price(100, country_code)
        
        return {
            "status": "success",
            "ip": ip_address,
            "country_code": country_code,
            "currency": price_info["currency"],
            "symbol": price_info["symbol"],
            "multiplier": price_info["multiplier"]
        }
    
    def get_discount_codes(self, type_filter=None):
        """Get all discount codes."""
        codes = []
        for code, data in self.discount_codes.items():
            if type_filter and data["type"] != type_filter:
                continue
            codes.append({
                "code": code,
                **data
            })
        
        return {"status": "success", "total": len(codes), "codes": codes}
    
    def create_custom_discount(self, code, discount_percent, valid_days, max_uses, discount_type="promotional", description=""):
        """Create custom discount code with expiry."""
        code = code.upper().strip()
        valid_until = (datetime.now() + timedelta(days=valid_days)).strftime("%Y-%m-%d")
        
        self.discount_codes[code] = {
            "type": discount_type,
            "discount_percent": discount_percent,
            "valid_until": valid_until,
            "max_uses": max_uses,
            "used_count": 0,
            "status": "active",
            "description": description
        }
        
        return {"status": "success", "code": code, "discount": self.discount_codes[code]}
    

    def get_auto_localized_pricing(self, request, base_price):
        """Auto-detect location and return localized pricing."""
        from ip_detection import ip_detector
        location = ip_detector.detect_from_request(request)
        
        if location["status"] != "success":
            return location
        
        country_code = location["country_code"]
        multiplier = location["multiplier"]
        
        from integrated_pricing import integrated_pricing
        price_info = integrated_pricing.get_localized_price(base_price, country_code)
        
        return {
            "status": "success",
            "detected_country": country_code,
            "country_name": location["country"],
            "currency": price_info["currency"],
            "symbol": price_info["symbol"],
            "base_price_usd": base_price,
            "localized_price": price_info["localized_amount"],
            "display_price": price_info["display_price"]
        }
    
    def check_expired_discounts(self):
        """Check and update expired discounts."""
        expired = []
        today = datetime.now()
        
        for code, data in self.discount_codes.items():
            try:
                valid_until = datetime.strptime(data["valid_until"], "%Y-%m-%d")
                if today > valid_until and data["status"] == "active":
                    data["status"] = "expired"
                    expired.append(code)
            except:
                pass
        
        return {"status": "success", "expired_codes": expired}

enhanced_payment = EnhancedPaymentSystem()
