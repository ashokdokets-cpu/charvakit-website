"""
Charvak Advanced Security Middleware
API key authentication + IP blacklisting
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict

logger = logging.getLogger("charvakit.security")

API_KEY = os.getenv("CHARVAK_API_KEY", "charvak-secure-key-2026")

# IP Blacklist (add abusive IPs here)
BLACKLISTED_IPS = set()

# Rate tracking for suspicious activity
suspicious_ips = {}


class SecurityManager:
    """Advanced security manager."""
    
    def __init__(self):
        self.api_key = API_KEY
        self.blacklisted_ips = BLACKLISTED_IPS
        self.login_attempts = {}
        logger.info("Security Manager ready")
    
    def validate_api_key(self, provided_key: str) -> bool:
        """Validate API key."""
        if not provided_key:
            return False
        return provided_key == self.api_key
    
    def check_ip_blacklist(self, ip: str) -> bool:
        """Check if IP is blacklisted."""
        return ip in self.blacklisted_ips
    
    def blacklist_ip(self, ip: str, reason: str = "suspicious_activity"):
        """Add IP to blacklist."""
        self.blacklisted_ips.add(ip)
        logger.warning(f"IP blacklisted: {ip} - {reason}")
    
    def track_login_attempt(self, ip: str, success: bool):
        """Track login attempts for brute force detection."""
        if ip not in self.login_attempts:
            self.login_attempts[ip] = {"count": 0, "last_attempt": datetime.now()}
        
        attempts = self.login_attempts[ip]
        
        if not success:
            attempts["count"] += 1
            attempts["last_attempt"] = datetime.now()
            
            # Blacklist after 10 failed attempts
            if attempts["count"] >= 10:
                self.blacklist_ip(ip, "10 failed login attempts")
                return True
        else:
            attempts["count"] = 0
        
        return False
    
    def get_security_stats(self) -> Dict:
        """Get security statistics."""
        return {
            "status": "success",
            "blacklisted_ips": len(self.blacklisted_ips),
            "tracked_ips": len(self.login_attempts),
            "api_key_protected": True
        }


security_manager = SecurityManager()