"""
Charvak IP-Based Location Detection
Auto-detects user's country for correct pricing.
W1d: GeoLite2 primary, default-country fallback.
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("charvakit.ip_detection")

# W1d - GeoLite2 integration (auto-updated via scripts/update_geoip.py)
try:
    import geoip2.database
    import geoip2.errors
    _GEOIP_AVAILABLE = True
except ImportError:
    _GEOIP_AVAILABLE = False
    logger.warning("geoip2 not installed - country detection falls back to default")

GEOLITE2_DB_PATH = Path("data/GeoLite2-City.mmdb")
DEFAULT_COUNTRY = "US"


class IPLocationDetector:
    """Detect country from IP using GeoLite2 (self-hosted MMDB)."""

    # ISO country code -> metadata (currency / symbol / multiplier)
    _COUNTRY_META = {
        "IN": {"country": "India",                "currency": "INR", "symbol": "Rs",  "multiplier": 0.20},
        "US": {"country": "United States",        "currency": "USD", "symbol": "$",   "multiplier": 1.0},
        "GB": {"country": "United Kingdom",       "currency": "GBP", "symbol": "GBP", "multiplier": 1.05},
        "AU": {"country": "Australia",            "currency": "AUD", "symbol": "A$",  "multiplier": 0.90},
        "AE": {"country": "United Arab Emirates", "currency": "AED", "symbol": "AED", "multiplier": 0.95},
        "SG": {"country": "Singapore",            "currency": "SGD", "symbol": "S$",  "multiplier": 0.85},
        "CA": {"country": "Canada",               "currency": "CAD", "symbol": "C$",  "multiplier": 0.95},
        "DE": {"country": "Germany",              "currency": "EUR", "symbol": "EUR", "multiplier": 0.95},
        "FR": {"country": "France",               "currency": "EUR", "symbol": "EUR", "multiplier": 0.95},
        "JP": {"country": "Japan",                "currency": "JPY", "symbol": "JPY", "multiplier": 1.0},
    }

    def __init__(self):
        self.location_cache: Dict[str, Dict] = {}
        self._geolite_reader = None
        self._load_geolite()
        logger.info("IP Location Detector ready (GeoLite2: %s)",
                    "ENABLED" if self._geolite_reader else "DISABLED")

    def _load_geolite(self):
        """Open GeoLite2 database if present."""
        if not _GEOIP_AVAILABLE:
            return
        if not GEOLITE2_DB_PATH.exists():
            logger.warning("GeoLite2 DB not found at %s", GEOLITE2_DB_PATH)
            return
        try:
            self._geolite_reader = geoip2.database.Reader(str(GEOLITE2_DB_PATH))
            logger.info("GeoLite2 loaded: %s", GEOLITE2_DB_PATH)
        except Exception as e:
            logger.error("GeoLite2 load failed: %s", e)
            self._geolite_reader = None

    def _geolite_lookup(self, ip_address: str) -> Optional[str]:
        """Return ISO country code or None."""
        if not self._geolite_reader:
            return None
        try:
            r = self._geolite_reader.city(ip_address)
            code = r.country.iso_code
            if code:
                return code
        except geoip2.errors.AddressNotFoundError:
            logger.debug("IP not in GeoLite2: %s", ip_address)
        except Exception as e:
            logger.warning("GeoLite2 lookup failed for %s: %s", ip_address, e)
        return None

    def detect_country_from_ip(self, ip_address: str) -> Dict:
        """Detect country from IP. Cached per IP."""
        if not ip_address:
            return {"status": "error", "message": "No IP provided"}

        if ip_address in self.location_cache:
            return self.location_cache[ip_address]

        code = self._geolite_lookup(ip_address)
        source = "geolite2"

        if not code:
            code = DEFAULT_COUNTRY
            source = "default"

        if code in self._COUNTRY_META:
            meta = self._COUNTRY_META[code]
        else:
            # Unknown ISO code - return minimal info
            meta = {"country": code, "currency": "USD", "symbol": "$", "multiplier": 1.0}

        result = {
            "status": "success",
            "ip": ip_address,
            "country_code": code,
            "country": meta["country"],
            "currency": meta["currency"],
            "symbol": meta["symbol"],
            "multiplier": meta["multiplier"],
            "source": source,
            "detected_at": datetime.now().isoformat(),
        }
        self.location_cache[ip_address] = result
        return result

    def detect_from_request(self, request) -> Dict:
        """Extract IP from FastAPI request and detect country."""
        ip_address = None

        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip_address = forwarded.split(",")[0].strip()

        if not ip_address:
            ip_address = request.headers.get("X-Real-IP")

        if not ip_address and request.client:
            ip_address = request.client.host

        if not ip_address:
            ip_address = "127.0.0.1"

        return self.detect_country_from_ip(ip_address)

    def get_localized_response(self, request, base_price_usd: float) -> Dict:
        """Get localized pricing based on detected location."""
        location = self.detect_from_request(request)

        if location.get("status") != "success":
            return location

        country_code = location["country_code"]
        multiplier = location["multiplier"]
        localized_price = round(base_price_usd * multiplier, 2)

        return {
            "status": "success",
            "detected_country": country_code,
            "country_name": location["country"],
            "currency": location["currency"],
            "symbol": location["symbol"],
            "multiplier": multiplier,
            "base_price_usd": base_price_usd,
            "localized_price": localized_price,
            "source": location.get("source", "unknown"),
        }

    def get_client_ip_auto(self):
        """Placeholder for compatibility."""
        return None


ip_detector = IPLocationDetector()