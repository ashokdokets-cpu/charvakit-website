"""
Charvak Global Configuration
Multi-currency, multi-language, multi-region support
"""
from typing import Dict, List, Optional

# --- Supported Languages ---
LANGUAGES = {
    "en": {"name": "English", "flag": "🇺🇸", "dir": "ltr"},
    "hi": {"name": "हिन्दी", "flag": "🇮🇳", "dir": "ltr"},
    "te": {"name": "తెలుగు", "flag": "🇮🇳", "dir": "ltr"},
    "es": {"name": "Español", "flag": "🇪🇸", "dir": "ltr"},
    "fr": {"name": "Français", "flag": "🇫🇷", "dir": "ltr"},
    "de": {"name": "Deutsch", "flag": "🇩🇪", "dir": "ltr"},
    "zh": {"name": "中文", "flag": "🇨🇳", "dir": "ltr"},
    "ja": {"name": "日本語", "flag": "🇯🇵", "dir": "ltr"},
    "ko": {"name": "한국어", "flag": "🇰🇷", "dir": "ltr"},
    "ar": {"name": "العربية", "flag": "🇦🇪", "dir": "rtl"},
    "pt": {"name": "Português", "flag": "🇧🇷", "dir": "ltr"},
    "ru": {"name": "Русский", "flag": "🇷🇺", "dir": "ltr"},
    "it": {"name": "Italiano", "flag": "🇮🇹", "dir": "ltr"},
    "nl": {"name": "Nederlands", "flag": "🇳🇱", "dir": "ltr"},
    "tr": {"name": "Türkçe", "flag": "🇹🇷", "dir": "ltr"},
    "vi": {"name": "Tiếng Việt", "flag": "🇻🇳", "dir": "ltr"},
    "th": {"name": "ไทย", "flag": "🇹🇭", "dir": "ltr"},
    "id": {"name": "Bahasa Indonesia", "flag": "🇮🇩", "dir": "ltr"},
    "ms": {"name": "Bahasa Melayu", "flag": "🇲🇾", "dir": "ltr"},
    "fil": {"name": "Filipino", "flag": "🇵🇭", "dir": "ltr"},
    "sw": {"name": "Kiswahili", "flag": "🇰🇪", "dir": "ltr"},
    "am": {"name": "አማርኛ", "flag": "🇪🇹", "dir": "ltr"},
    "ha": {"name": "Hausa", "flag": "🇳🇬", "dir": "ltr"},
    "yo": {"name": "Yorùbá", "flag": "🇳🇬", "dir": "ltr"},
    "ig": {"name": "Igbo", "flag": "🇳🇬", "dir": "ltr"},
    "zu": {"name": "isiZulu", "flag": "🇿🇦", "dir": "ltr"},
    "so": {"name": "Soomaali", "flag": "🇸🇴", "dir": "ltr"},
    "bn": {"name": "বাংলা", "flag": "🇧🇩", "dir": "ltr"},
    "mr": {"name": "मराठी", "flag": "🇮🇳", "dir": "ltr"},
    "ta": {"name": "தமிழ்", "flag": "🇮🇳", "dir": "ltr"},
    "gu": {"name": "ગુજરાતી", "flag": "🇮🇳", "dir": "ltr"},
    "kn": {"name": "ಕನ್ನಡ", "flag": "🇮🇳", "dir": "ltr"},
    "ml": {"name": "മലയാളം", "flag": "🇮🇳", "dir": "ltr"},
    "pa": {"name": "ਪੰਜਾਬੀ", "flag": "🇮🇳", "dir": "ltr"},
}

# --- Supported Currencies ---
CURRENCIES = {
    "INR": {"symbol": "₹", "name": "Indian Rupee", "rate": 1.0},
    "USD": {"symbol": "$", "name": "US Dollar", "rate": 0.012},
    "EUR": {"symbol": "€", "name": "Euro", "rate": 0.011},
    "GBP": {"symbol": "£", "name": "British Pound", "rate": 0.0095},
    "AED": {"symbol": "د.إ", "name": "UAE Dirham", "rate": 0.044},
    "SGD": {"symbol": "S$", "name": "Singapore Dollar", "rate": 0.016},
    "AUD": {"symbol": "A$", "name": "Australian Dollar", "rate": 0.018},
    "CAD": {"symbol": "C$", "name": "Canadian Dollar", "rate": 0.016},
    "JPY": {"symbol": "¥", "name": "Japanese Yen", "rate": 1.75},
    "CNY": {"symbol": "¥", "name": "Chinese Yuan", "rate": 0.087},
    "BRL": {"symbol": "R$", "name": "Brazilian Real", "rate": 0.059},
    "NGN": {"symbol": "₦", "name": "Nigerian Naira", "rate": 18.5},
    "ZAR": {"symbol": "R", "name": "South African Rand", "rate": 0.22},
}

# --- Country Pricing Tiers ---
PRICING_TIERS = {
    "tier_1": {  # India, Nigeria, Bangladesh, etc.
        "countries": ["IN", "NG", "BD", "KE", "ET", "GH", "TZ", "UG"],
        "multiplier": 1.0,
        "label": "Regional Pricing"
    },
    "tier_2": {  # Brazil, South Africa, Philippines, etc.
        "countries": ["BR", "ZA", "PH", "ID", "VN", "EG", "MA"],
        "multiplier": 1.5,
        "label": "Emerging Market"
    },
    "tier_3": {  # US, UK, EU, Canada, Australia, etc.
        "countries": ["US", "GB", "DE", "FR", "CA", "AU", "SG", "JP", "AE"],
        "multiplier": 3.0,
        "label": "Global Standard"
    }
}

# --- Region-Specific Features ---
REGIONS = {
    "Asia": {"timezone": "Asia/Kolkata", "popular_currencies": ["INR", "SGD", "AED", "JPY", "CNY"]},
    "Europe": {"timezone": "Europe/London", "popular_currencies": ["EUR", "GBP", "USD"]},
    "North America": {"timezone": "America/New_York", "popular_currencies": ["USD", "CAD"]},
    "South America": {"timezone": "America/Sao_Paulo", "popular_currencies": ["BRL", "USD"]},
    "Africa": {"timezone": "Africa/Lagos", "popular_currencies": ["NGN", "ZAR", "KES"]},
    "Middle East": {"timezone": "Asia/Dubai", "popular_currencies": ["AED", "USD"]},
    "Oceania": {"timezone": "Australia/Sydney", "popular_currencies": ["AUD", "USD"]},
}

# --- Service Pricing (in INR, adjusted by tier) ---
SERVICE_PRICING = {
    "voice_to_web_pro": 499,
    "resume_pro": 499,
    "job_post": 999,
    "mock_interview": 199,
    "auditbot_scan": 2999,
    "auditbot_monthly": 1999,
    "lock_breaker_monthly": 4999,
    "neural_wireframe": 999,
    "skill_twin_verified": 499,
    "globalize_growth": 1499,
    "globalize_enterprise": 4999,
    "micro_squads_starter": 49999,
    "micro_squads_growth": 99999,
    "agency_twin_pro": 999,
    "geo_compliance_contract": 999,
    "design_token_pro": 2499,
    "design_token_enterprise": 7999,
    "legacy_shift_migration": 19999,
    "agent_ready_setup": 4999,
    "silent_killer_monthly": 3499,
    "ai_slop_cleanup": 5999,
    "developer_entropy_monthly": 999,
    "reverse_staffing_hire": 14999,
    "reverse_staffing_monthly": 4999,
    "background_check_basic": 499,
    "background_check_complete": 3999,
}

def get_pricing(service: str, currency: str = "INR", country: str = "IN") -> Dict:
    """Get localized pricing for a service"""
    base_price = SERVICE_PRICING.get(service, 0)
    
    # Determine tier
    tier = "tier_1"
    for t, data in PRICING_TIERS.items():
        if country in data["countries"]:
            tier = t
            break
    
    multiplier = PRICING_TIERS[tier]["multiplier"]
    adjusted_price = base_price * multiplier
    
    # Convert currency
    currency_rate = CURRENCIES.get(currency, {"rate": 1.0})["rate"]
    converted_price = round(adjusted_price * currency_rate, 2)
    
    return {
        "amount": converted_price,
        "currency": currency,
        "symbol": CURRENCIES.get(currency, {}).get("symbol", "$"),
        "tier": tier,
        "label": PRICING_TIERS[tier]["label"],
        "original_inr": base_price
    }

def detect_user_region(ip_address: str = None, accept_language: str = None) -> Dict:
    """Detect user's region, language, and currency preferences"""
    # Default to India
    region = {"country": "IN", "language": "en", "currency": "INR", "timezone": "Asia/Kolkata"}
    
    if accept_language:
        lang = accept_language.split(",")[0].split("-")[0]
        if lang in LANGUAGES:
            region["language"] = lang
    
    # Map language to likely currency
    lang_currency_map = {
        "en": "USD", "hi": "INR", "te": "INR", "es": "EUR", "fr": "EUR",
        "de": "EUR", "ja": "JPY", "zh": "CNY", "ar": "AED", "pt": "BRL",
        "bn": "INR", "ta": "INR", "mr": "INR", "gu": "INR"
    }
    
    if region["language"] in lang_currency_map:
        region["currency"] = lang_currency_map[region["language"]]
    
    return region