"""
Charvak Integrated Location-Aware Pricing
Works with: AI Credits, Internships, Training, Assessments
"""
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger("charvakit.integrated_pricing")

class IntegratedPricingEngine:
    def __init__(self):
        self.location_data = self._initialize_locations()
        self.currency_rates = self._initialize_currency_rates()
        logger.info("Integrated Pricing Engine ready")
    
    def _initialize_locations(self):
        """Initialize location multipliers."""
        return {
            "US": 1.0, "CA": 0.95, "MX": 0.55,
            "GB": 1.05, "DE": 0.95, "FR": 0.90, "NL": 0.92,
            "SE": 0.95, "PL": 0.50,
            "IN": 0.20, "CN": 0.55, "JP": 0.85, "KR": 0.75,
            "SG": 0.85, "MY": 0.45, "TH": 0.35, "VN": 0.25,
            "ID": 0.30, "PH": 0.30, "BD": 0.20, "PK": 0.18,
            "LK": 0.22, "NP": 0.20,
            "AE": 0.75, "SA": 0.70, "QA": 0.75, "IL": 0.85,
            "AU": 0.90, "NZ": 0.85,
            "ZA": 0.40, "NG": 0.25, "KE": 0.25, "EG": 0.22,
            "BR": 0.45, "AR": 0.30, "CL": 0.40, "CO": 0.30, "PE": 0.35
        }
    
    def _initialize_currency_rates(self):
        """Initialize currency symbols and exchange rates (approximate)."""
        return {
            "USD": {"symbol": "$", "rate": 1.0},
            "INR": {"symbol": "₹", "rate": 83.0},
            "EUR": {"symbol": "€", "rate": 0.92},
            "GBP": {"symbol": "£", "rate": 0.79},
            "CAD": {"symbol": "C$", "rate": 1.36},
            "AUD": {"symbol": "A$", "rate": 1.52},
            "SGD": {"symbol": "S$", "rate": 1.34},
            "AED": {"symbol": "د.إ", "rate": 3.67},
            "BRL": {"symbol": "R$", "rate": 5.05},
            "NGN": {"symbol": "₦", "rate": 1550.0}
        }
    
    def get_localized_price(self, base_price_usd, country_code):
        """Get localized price for any product/service."""
        multiplier = self.location_data.get(country_code, 1.0)
        localized_usd = base_price_usd * multiplier
        
        # Get currency
        currency_map = {
            "US": "USD", "CA": "CAD", "MX": "MXN",
            "GB": "GBP", "DE": "EUR", "FR": "EUR", "NL": "EUR",
            "IN": "INR", "CN": "CNY", "JP": "JPY", "KR": "KRW",
            "SG": "SGD", "AE": "AED", "AU": "AUD",
            "BR": "BRL", "NG": "NGN"
        }
        
        currency = currency_map.get(country_code, "USD")
        rate = self.currency_rates.get(currency, {"rate": 1.0})["rate"]
        symbol = self.currency_rates.get(currency, {"symbol": "$"})["symbol"]
        
        localized_amount = localized_usd * rate
        
        return {
            "status": "success",
            "base_price_usd": base_price_usd,
            "country_code": country_code,
            "multiplier": multiplier,
            "localized_usd": round(localized_usd, 2),
            "currency": currency,
            "symbol": symbol,
            "localized_amount": round(localized_amount, 2),
            "display_price": f"{symbol}{round(localized_amount, 2)}"
        }
    
    def get_ai_credit_pricing(self, country_code):
        """Get AI credit pricing for location."""
        # Existing AI credit plans (from ai_credit_engine.py)
        plans = [
            {"name": "Free", "credits": 50, "price_usd": 0},
            {"name": "Starter", "credits": 500, "price_usd": 99},
            {"name": "Professional", "credits": 2000, "price_usd": 299},
            {"name": "Business", "credits": 10000, "price_usd": 999},
            {"name": "Enterprise", "credits": 50000, "price_usd": 4999}
        ]
        
        localized_plans = []
        for plan in plans:
            price = self.get_localized_price(plan["price_usd"], country_code)
            localized_plans.append({
                **plan,
                **price
            })
        
        return {"status": "success", "country": country_code, "plans": localized_plans}
    
    def get_internship_pricing(self, country_code):
        """Get internship pricing for location."""
        # From ai_internship_engine.py
        internships = [
            {"name": "Web Development", "price_usd": 2999},
            {"name": "Data Science", "price_usd": 2499},
            {"name": "AI/ML", "price_usd": 2799},
            {"name": "Cybersecurity", "price_usd": 2499},
            {"name": "Cloud Computing", "price_usd": 2999},
            {"name": "Mobile Development", "price_usd": 2799}
        ]
        
        localized = []
        for internship in internships:
            price = self.get_localized_price(internship["price_usd"], country_code)
            localized.append({**internship, **price})
        
        return {"status": "success", "country": country_code, "internships": localized}
    
    def get_training_pricing(self, country_code, course_type="standard"):
        """Get training course pricing for location."""
        type_multipliers = {
            "basic": 0.7,
            "standard": 1.0,
            "premium": 1.5,
            "enterprise": 2.0
        }
        
        # Base course prices
        courses = [
            {"name": "Python Programming", "base_price": 99},
            {"name": "Full Stack Development", "base_price": 199},
            {"name": "Data Science Bootcamp", "base_price": 299},
            {"name": "AI/ML Specialization", "base_price": 399},
            {"name": "DevOps Engineering", "base_price": 249},
            {"name": "Cloud Architecture", "base_price": 349}
        ]
        
        type_multiplier = type_multipliers.get(course_type, 1.0)
        
        localized = []
        for course in courses:
            final_base = course["base_price"] * type_multiplier
            price = self.get_localized_price(final_base, country_code)
            localized.append({**course, **price, "course_type": course_type})
        
        return {"status": "success", "country": country_code, "courses": localized}
    
    def get_assessment_pricing(self, country_code):
        """Get assessment pricing for location."""
        assessments = [
            {"name": "Versant English", "price_usd": 49},
            {"name": "Technical MCQ", "price_usd": 29},
            {"name": "Company Mock Drive", "price_usd": 79},
            {"name": "Skill Gap Analysis", "price_usd": 39},
            {"name": "Premium Assessment Bundle", "price_usd": 149}
        ]
        
        localized = []
        for assessment in assessments:
            price = self.get_localized_price(assessment["price_usd"], country_code)
            localized.append({**assessment, **price})
        
        return {"status": "success", "country": country_code, "assessments": localized}
    
    def get_complete_pricing(self, country_code):
        """Get all pricing for a location."""
        return {
            "status": "success",
            "country_code": country_code,
            "ai_credits": self.get_ai_credit_pricing(country_code)["plans"],
            "internships": self.get_internship_pricing(country_code)["internships"],
            "training": self.get_training_pricing(country_code)["courses"],
            "assessments": self.get_assessment_pricing(country_code)["assessments"]
        }

integrated_pricing = IntegratedPricingEngine()
