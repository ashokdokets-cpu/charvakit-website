"""
Charvak IP-Based Location Detection
Auto-detects user's country for correct pricing
"""
import logging
import json
import os
import socket
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger("charvakit.ip_detection")

class IPLocationDetector:
    def __init__(self):
        self.location_cache = {}
        self.ip_ranges = self._initialize_ip_ranges()
        logger.info("IP Location Detector ready")
    
    def _initialize_ip_ranges(self):
        """Initialize IP ranges for major countries."""
        return {
            "IN": {
                "country": "India",
                "currency": "INR",
                "symbol": "₹",
                "ip_prefixes": ["103", "106", "110", "115", "116", "117", "120", "122", "123", "124", "125", "136", "139", "144", "150", "152", "157", "159", "160", "162", "163", "164", "165", "166", "167", "168", "169", "171", "175", "180", "182", "183", "192", "202", "203", "210", "212", "219", "220", "223"],
                "multiplier": 0.20
            },
            "US": {
                "country": "United States",
                "currency": "USD",
                "symbol": "$",
                "ip_prefixes": ["3", "4", "8", "9", "13", "15", "16", "18", "20", "23", "24", "32", "34", "35", "40", "44", "45", "47", "50", "52", "54", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76", "98", "99", "100", "104", "107", "108", "128", "129", "130", "131", "132", "134", "135", "136", "137", "138", "139", "140", "142", "143", "144", "146", "147", "148", "149", "152", "155", "156", "157", "158", "159", "160", "161", "162", "164", "165", "166", "167", "168", "169", "170", "171", "172", "173", "174", "184", "192", "198", "199", "204", "205", "206", "207", "208", "209", "216"],
                "multiplier": 1.0
            },
            "GB": {
                "country": "United Kingdom",
                "currency": "GBP",
                "symbol": "£",
                "ip_prefixes": ["2", "5", "25", "31", "51", "62", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "109", "145", "146", "147", "148", "149", "151", "176", "185", "188", "193", "194", "195", "212", "213", "217"],
                "multiplier": 1.05
            },
            "AU": {
                "country": "Australia",
                "currency": "AUD",
                "symbol": "A$",
                "ip_prefixes": ["1", "14", "27", "39", "49", "58", "59", "60", "61", "101", "103", "110", "111", "113", "114", "115", "116", "118", "119", "120", "121", "122", "123", "124", "125", "131", "132", "137", "138", "139", "144", "147", "149", "150", "153", "155", "157", "158", "159", "161", "163", "165", "167", "168", "175", "180", "182", "202", "203", "210", "211", "218", "219", "220", "222", "223"],
                "multiplier": 0.90
            }
        }
    
    def detect_country_from_ip(self, ip_address):
        """Detect country from IP address."""
        if not ip_address:
            return {"status": "error", "message": "No IP provided"}
        
        # Check cache first
        if ip_address in self.location_cache:
            return self.location_cache[ip_address]
        
        # Extract first octet
        try:
            first_octet = ip_address.split(".")[0]
        except:
            first_octet = "0"
        
        # Find matching country
        detected_country = "US"  # Default
        
        for country_code, data in self.ip_ranges.items():
            if first_octet in data["ip_prefixes"]:
                detected_country = country_code
                break
        
        result = {
            "status": "success",
            "ip": ip_address,
            "country_code": detected_country,
            "country": self.ip_ranges[detected_country]["country"],
            "currency": self.ip_ranges[detected_country]["currency"],
            "symbol": self.ip_ranges[detected_country]["symbol"],
            "multiplier": self.ip_ranges[detected_country]["multiplier"],
            "detected_at": datetime.now().isoformat()
        }
        
        # Cache result
        self.location_cache[ip_address] = result
        
        return result
    
    def detect_from_request(self, request):
        """Detect location from FastAPI request."""
        # Get IP from various headers
        ip_address = None
        
        # Check X-Forwarded-For (proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip_address = forwarded.split(",")[0].strip()
        
        # Check X-Real-IP
        if not ip_address:
            ip_address = request.headers.get("X-Real-IP")
        
        # Get from client
        if not ip_address and request.client:
            ip_address = request.client.host
        
        if not ip_address:
            ip_address = "127.0.0.1"
        
        return self.detect_country_from_ip(ip_address)
    
    def get_localized_response(self, request, base_price_usd):
        """Get complete localized pricing based on detected location."""
        location = self.detect_from_request(request)
        
        if location["status"] != "success":
            return location
        
        country_code = location["country_code"]
        multiplier = location["multiplier"]
        localized_price = base_price_usd * multiplier
        
        return {
            "status": "success",
            "detected_country": country_code,
            "country_name": location["country"],
            "currency": location["currency"],
            "symbol": location["symbol"],
            "base_price_usd": base_price_usd,
            "localized_price": round(localized_price, 2),
            "display_price": f"{location['symbol']}{round(localized_price, 2)}",
            "multiplier": multiplier
        }
    
    def get_client_ip_auto(self):
        """Auto-detect client IP using external service."""
        try:
            import requests
            # Use ipify to get public IP
            response = requests.get("https://api.ipify.org?format=json", timeout=3)
            ip_address = response.json().get("ip", "127.0.0.1")
            return self.detect_country_from_ip(ip_address)
        except:
            # Fallback to localhost
            return self.detect_country_from_ip("127.0.0.1")

ip_detector = IPLocationDetector()
