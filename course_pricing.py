"""
Charvak Global Course Pricing
Location-based competitive pricing for 25 courses
"""
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger("charvakit.course_pricing")

class CoursePricing:
    def __init__(self):
        self.base_prices = self._initialize_base_prices()
        self.location_multipliers = self._initialize_location_multipliers()
        logger.info("Course Pricing ready")
    
    def _initialize_base_prices(self):
        """Base prices in USD - competitive with Coursera, Udemy, edX."""
        return {
            "Full Stack Web Development": {"price": 1999, "duration": "12 Weeks", "hours": 120},
            "Data Science & ML": {"price": 2999, "duration": "16 Weeks", "hours": 160},
            "Python Programming": {"price": 499, "duration": "6 Weeks", "hours": 60},
            "AWS Cloud Computing": {"price": 1499, "duration": "10 Weeks", "hours": 100},
            "DevOps Engineering": {"price": 1999, "duration": "12 Weeks", "hours": 120},
            "Cybersecurity": {"price": 2499, "duration": "14 Weeks", "hours": 140},
            "Java Development": {"price": 999, "duration": "10 Weeks", "hours": 100},
            "React & Frontend": {"price": 899, "duration": "8 Weeks", "hours": 80},
            "SQL & Database": {"price": 399, "duration": "4 Weeks", "hours": 40},
            "Docker & Kubernetes": {"price": 899, "duration": "6 Weeks", "hours": 60},
            "AI & Deep Learning": {"price": 3499, "duration": "16 Weeks", "hours": 160},
            "Mobile App Development": {"price": 1499, "duration": "12 Weeks", "hours": 120},
            "Blockchain Development": {"price": 2499, "duration": "12 Weeks", "hours": 120},
            "Data Analytics": {"price": 999, "duration": "8 Weeks", "hours": 80},
            "UI/UX Design": {"price": 699, "duration": "6 Weeks", "hours": 60},
            "Cloud Architecture": {"price": 2999, "duration": "14 Weeks", "hours": 140},
            "Node.js Backend": {"price": 899, "duration": "8 Weeks", "hours": 80},
            "Python for Data Science": {"price": 1299, "duration": "10 Weeks", "hours": 100},
            "Machine Learning Ops": {"price": 2499, "duration": "12 Weeks", "hours": 120},
            "Spring Boot": {"price": 899, "duration": "8 Weeks", "hours": 80},
            "Angular Development": {"price": 699, "duration": "6 Weeks", "hours": 60},
            "Ethical Hacking": {"price": 2999, "duration": "12 Weeks", "hours": 120},
            "Big Data": {"price": 2499, "duration": "12 Weeks", "hours": 120},
            "Software Testing": {"price": 399, "duration": "4 Weeks", "hours": 40},
            "Git & DevOps Tools": {"price": 199, "duration": "2 Weeks", "hours": 20}
        }
    
    def _initialize_location_multipliers(self):
        """Competitive multipliers for different regions."""
        return {
            "IN": {"multiplier": 0.15, "currency": "INR", "symbol": "₹", "rate": 83},
            "US": {"multiplier": 1.0, "currency": "USD", "symbol": "$", "rate": 1},
            "GB": {"multiplier": 0.8, "currency": "GBP", "symbol": "£", "rate": 0.79},
            "EU": {"multiplier": 0.75, "currency": "EUR", "symbol": "€", "rate": 0.92},
            "AE": {"multiplier": 0.6, "currency": "AED", "symbol": "د.إ", "rate": 3.67},
            "SG": {"multiplier": 0.65, "currency": "SGD", "symbol": "S$", "rate": 1.34},
            "AU": {"multiplier": 0.7, "currency": "AUD", "symbol": "A$", "rate": 1.52},
            "BR": {"multiplier": 0.35, "currency": "BRL", "symbol": "R$", "rate": 5.05},
            "NG": {"multiplier": 0.2, "currency": "NGN", "symbol": "₦", "rate": 1550}
        }
    
    def get_course_price(self, course_name, country_code="US"):
        """Get location-based price for a course."""
        course = self.base_prices.get(course_name)
        if not course:
            return {"status": "error", "message": "Course not found"}
        
        location = self.location_multipliers.get(country_code, self.location_multipliers["US"])
        
        base_price = course["price"]
        localized_usd = base_price * location["multiplier"]
        localized_amount = localized_usd * location["rate"]
        
        # EMI (12 months)
        emi = localized_amount / 12
        
        return {
            "status": "success",
            "course": course_name,
            "duration": course["duration"],
            "hours": course["hours"],
            "country": country_code,
            "currency": location["currency"],
            "symbol": location["symbol"],
            "base_price_usd": base_price,
            "localized_price": round(localized_amount, 2),
            "emi_12_months": round(emi, 2),
            "display_price": f"{location['symbol']}{round(localized_amount, 2)}",
            "display_emi": f"{location['symbol']}{round(emi, 2)}/mo"
        }
    
    def get_all_course_prices(self, country_code="US"):
        """Get all 25 courses with location pricing."""
        courses = []
        for course_name in self.base_prices:
            price_info = self.get_course_price(course_name, country_code)
            courses.append(price_info)
        
        return {"status": "success", "country": country_code, "courses": courses}

course_pricing = CoursePricing()
