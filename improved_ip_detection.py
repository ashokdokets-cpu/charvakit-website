"""
Charvak Improved IP Detection
Better detection for real-world IPs
"""
import logging
import os
import socket
from datetime import datetime

logger = logging.getLogger("charvakit.improved_ip")

class ImprovedIPDetector:
    def __init__(self):
        self.cache = {}
        logger.info("Improved IP Detector ready")
    
    def detect_country(self, ip_address):
        """Detect country with better accuracy."""
        if ip_address in self.cache:
            return self.cache[ip_address]
        
        country = "US"  # Default
        
        # Skip localhost
        if ip_address in ["127.0.0.1", "localhost", "::1"]:
            country = "IN"  # Default to India for localhost (your location)
        else:
            first_octet = ip_address.split(".")[0]
            
            # Indian IP ranges (more comprehensive)
            indian_ranges = [
                "1", "14", "27", "39", "42", "45", "47", "49", "59", "60",
                "61", "101", "103", "106", "110", "115", "116", "117", "120",
                "122", "123", "124", "125", "136", "139", "144", "150", "152",
                "157", "159", "160", "162", "163", "164", "165", "166", "167",
                "168", "169", "171", "175", "180", "182", "183", "192", "202",
                "203", "210", "212", "219", "220", "223"
            ]
            
            if first_octet in indian_ranges:
                country = "IN"
            else:
                # Check other countries
                us_ranges = ["3", "4", "8", "9", "13", "15", "16", "18", "20", "23", "24", "32", "34", "35", "40", "44", "45", "47", "50", "52", "54", "63", "64", "65", "66", "67", "68", "69", "70", "71", "72", "73", "74", "75", "76"]
                uk_ranges = ["2", "5", "25", "31", "51", "62", "77", "78", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95"]
                au_ranges = ["101", "110", "111", "113", "114", "115", "116", "118", "119", "120", "121", "122", "123", "124", "125", "131", "132", "137", "138", "139", "144", "147", "149", "150", "153", "155", "157", "158", "159", "161", "163", "165", "167", "168", "175", "180", "182", "202", "203", "210", "211", "218", "219", "220", "222", "223"]
                
                if first_octet in us_ranges:
                    country = "US"
                elif first_octet in uk_ranges:
                    country = "GB"
                elif first_octet in au_ranges:
                    country = "AU"
        
        country_data = {
            "IN": {"country": "India", "currency": "INR", "symbol": "₹", "multiplier": 0.20},
            "US": {"country": "United States", "currency": "USD", "symbol": "$", "multiplier": 1.0},
            "GB": {"country": "United Kingdom", "currency": "GBP", "symbol": "£", "multiplier": 1.05},
            "AU": {"country": "Australia", "currency": "AUD", "symbol": "A$", "multiplier": 0.90}
        }
        
        data = country_data.get(country, country_data["US"])
        
        result = {
            "status": "success",
            "ip": ip_address,
            "country_code": country,
            **data,
            "detected_at": datetime.now().isoformat()
        }
        
        self.cache[ip_address] = result
        return result
    
    def detect_from_request(self, request):
        """Detect from FastAPI request."""
        ip_address = None
        
        # Check headers first (for proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip_address = forwarded.split(",")[0].strip()
        
        if not ip_address:
            ip_address = request.headers.get("X-Real-IP")
        
        if not ip_address and request.client:
            ip_address = request.client.host
        
        if not ip_address or ip_address in ["127.0.0.1", "localhost", "::1"]:
            # Default to India for localhost (developer location)
            ip_address = "127.0.0.1"
        
        return self.detect_country(ip_address)

improved_ip_detector = ImprovedIPDetector()
