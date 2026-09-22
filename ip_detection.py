"""
Charvak IP-Based Location Detection
Auto-detects user's country for correct pricing.

Two-layer strategy (W2a):
  1. Cloudflare CF-IPCountry header (instant, auto-updated weekly by CF)
  2. Self-hosted GeoLite2 City MMDB (fallback, lazy refresh after 7 days)
  3. Default country (India) as last resort

Invalid CF values rejected: XX (unknown), T1 (Tor exit node).
"""
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger("charvakit.ip_detection")

try:
    import geoip2.database
    import geoip2.errors
    _GEOIP_AVAILABLE = True
except ImportError:
    _GEOIP_AVAILABLE = False
    logger.warning("geoip2 not installed - country detection falls back to header/default")

GEOLITE2_DB_PATH = Path("data/GeoLite2-City.mmdb")
GEOLITE2_MAX_AGE_DAYS = 7
DEFAULT_COUNTRY = "IN"

# CF-IPCountry values that are NOT usable country codes
_CF_INVALID = {"XX", "T1", ""}


class IPLocationDetector:
    """Country detection: CF header > GeoLite2 > default."""

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
        self._refresh_in_progress = False
        self._refresh_lock = threading.Lock()
        self._load_geolite()
        self._check_staleness_async()
        logger.info("IP Location Detector ready (GeoLite2: %s, CF header: enabled)",
                    "ENABLED" if self._geolite_reader else "DISABLED")

    # ---------- GeoLite2 loading & refresh ----------
    def _load_geolite(self):
        """Open GeoLite2 MMDB if present."""
        if not _GEOIP_AVAILABLE:
            return
        if not GEOLITE2_DB_PATH.exists():
            logger.warning("GeoLite2 DB not found at %s", GEOLITE2_DB_PATH)
            return
        try:
            old = self._geolite_reader
            self._geolite_reader = geoip2.database.Reader(str(GEOLITE2_DB_PATH))
            if old:
                try:
                    old.close()
                except Exception:
                    pass
            logger.info("GeoLite2 loaded: %s", GEOLITE2_DB_PATH)
        except Exception as e:
            logger.error("GeoLite2 load failed: %s", e)
            self._geolite_reader = None

    def _db_age_days(self) -> Optional[float]:
        if not GEOLITE2_DB_PATH.exists():
            return None
        age_seconds = time.time() - GEOLITE2_DB_PATH.stat().st_mtime
        return age_seconds / 86400.0

    def _check_staleness_async(self):
        """If DB is stale or missing, kick off a background refresh."""
        age = self._db_age_days()
        if age is None:
            logger.info("GeoLite2 missing - scheduling background download")
            self._spawn_refresh()
        elif age > GEOLITE2_MAX_AGE_DAYS:
            logger.info("GeoLite2 is %.1f days old - scheduling background refresh", age)
            self._spawn_refresh()

    def _spawn_refresh(self):
        """Start the background refresh thread (idempotent)."""
        with self._refresh_lock:
            if self._refresh_in_progress:
                return
            self._refresh_in_progress = True
        t = threading.Thread(target=self._background_refresh, daemon=True)
        t.start()

    def _background_refresh(self):
        """Download + hot-swap the DB without blocking requests."""
        try:
            logger.info("GeoLite2 background refresh starting...")
            import scripts.update_geoip as updater  # noqa
        except Exception:
            # Fallback: run the download logic inline
            try:
                self._download_and_swap()
            except Exception as e:
                logger.error("GeoLite2 refresh failed: %s", e)
        finally:
            with self._refresh_lock:
                self._refresh_in_progress = False

    def _download_and_swap(self):
        """Download, decompress, hot-swap the MMDB."""
        import gzip
        import urllib.request
        import shutil as _shutil

        url = "https://cdn.jsdelivr.net/npm/geolite2-city/GeoLite2-City.mmdb.gz"
        tmp_gz = GEOLITE2_DB_PATH.with_suffix(".mmdb.gz.tmp")
        tmp_out = GEOLITE2_DB_PATH.with_suffix(".mmdb.new")

        GEOLITE2_DB_PATH.parent.mkdir(exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Charvak-Refresh/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(tmp_gz, "wb") as f:
            _shutil.copyfileobj(resp, f, length=1024 * 1024)

        with gzip.open(tmp_gz, "rb") as f_in, open(tmp_out, "wb") as f_out:
            _shutil.copyfileobj(f_in, f_out, length=1024 * 1024)

        if GEOLITE2_DB_PATH.exists():
            GEOLITE2_DB_PATH.unlink()
        tmp_out.rename(GEOLITE2_DB_PATH)
        try:
            tmp_gz.unlink()
        except Exception:
            pass

        # Hot-swap reader
        self._load_geolite()
        logger.info("GeoLite2 hot-swapped successfully")

    # ---------- Layer 1: Cloudflare header ----------
    def _from_cf_header(self, request) -> Optional[str]:
        """Return ISO country code from CF-IPCountry header, or None."""
        try:
            raw = request.headers.get("cf-ipcountry") or ""
            code = raw.strip().upper()
            if not code or code in _CF_INVALID:
                return None
            # Must be 2 letters
            if len(code) != 2 or not code.isalpha():
                return None
            return code
        except Exception:
            return None

    # ---------- Layer 2: GeoLite2 ----------
    def _geolite_lookup(self, ip_address: str) -> Optional[str]:
        if not self._geolite_reader or not ip_address:
            return None
        try:
            r = self._geolite_reader.city(ip_address)
            code = (r.country.iso_code or "").upper()
            if code and code not in _CF_INVALID and len(code) == 2:
                return code
        except geoip2.errors.AddressNotFoundError:
            logger.debug("IP not in GeoLite2: %s", ip_address)
        except Exception as e:
            logger.warning("GeoLite2 lookup failed for %s: %s", ip_address, e)
        return None

    # ---------- Public API ----------
    def _build_result(self, ip: str, code: str, source: str) -> Dict:
        meta = self._COUNTRY_META.get(code)
        if not meta:
            meta = {"country": code, "currency": "USD", "symbol": "$", "multiplier": 1.0}
        return {
            "status": "success",
            "ip": ip,
            "country_code": code,
            "country": meta["country"],
            "currency": meta["currency"],
            "symbol": meta["symbol"],
            "multiplier": meta["multiplier"],
            "source": source,
            "detected_at": datetime.now().isoformat(),
        }

    def detect_country_from_ip(self, ip_address: str, cf_country: Optional[str] = None) -> Dict:
        """Detect via: CF header > GeoLite2 > default. Cached per ip+cf key."""
        cache_key = f"{ip_address}|{cf_country or ''}"
        if cache_key in self.location_cache:
            return self.location_cache[cache_key]

        code: Optional[str] = None
        source = "default"

        # Layer 1: CF header (already validated by caller or _from_cf_header)
        if cf_country:
            c = cf_country.strip().upper()
            if c and c not in _CF_INVALID and len(c) == 2 and c.isalpha():
                code = c
                source = "cf_header"

        # Layer 2: GeoLite2
        if not code and ip_address:
            code = self._geolite_lookup(ip_address)
            if code:
                source = "geolite2"

        # Layer 3: default
        if not code:
            code = DEFAULT_COUNTRY
            source = "default"

        result = self._build_result(ip_address or "", code, source)
        self.location_cache[cache_key] = result
        return result

    def detect_from_request(self, request) -> Dict:
        """Extract signals from a FastAPI request and detect country."""
        # CF header first
        cf_country = self._from_cf_header(request)

        # IP fallback chain
        ip_address = None
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            ip_address = forwarded.split(",")[0].strip()
        if not ip_address:
            ip_address = request.headers.get("x-real-ip")
        if not ip_address and getattr(request, "client", None):
            ip_address = request.client.host
        if not ip_address:
            ip_address = "127.0.0.1"

        return self.detect_country_from_ip(ip_address, cf_country=cf_country)

    def get_localized_response(self, request, base_price_usd: float) -> Dict:
        location = self.detect_from_request(request)
        if location.get("status") != "success":
            return location
        multiplier = location["multiplier"]
        return {
            "status": "success",
            "detected_country": location["country_code"],
            "country_name": location["country"],
            "currency": location["currency"],
            "symbol": location["symbol"],
            "multiplier": multiplier,
            "base_price_usd": base_price_usd,
            "localized_price": round(base_price_usd * multiplier, 2),
            "source": location.get("source", "unknown"),
        }

    def get_client_ip_auto(self):
        """Placeholder for compatibility."""
        return None


ip_detector = IPLocationDetector()