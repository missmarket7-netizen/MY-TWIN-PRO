"""Tier Service – Unified tier configuration and limits."""
from typing import Dict, Any

TIER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "free": {
        "name": "Free",
        "price": 0,
        "daily_messages": 10,
        "daily_features": {
            "study": 1, "content": 1, "business": 0, "code": 0, "image": 1,
        },
        "ads_required": True,
        "memory_days": 3,
        "models": ["groq"],
        "voice": "edge_tts",
        "coaching": False,
        "dreams": False,
    },
    "plus": {
        "name": "Plus",
        "price": 5.99,
        "daily_messages": 30,
        "daily_features": {
            "study": 5, "content": 5, "business": 2, "code": 2, "image": 3,
        },
        "ads_required": False,
        "memory_days": 30,
        "models": ["groq", "gemini"],
        "voice": "edge_tts",
        "coaching": False,
        "dreams": False,
    },
    "premium": {
        "name": "Premium",
        "price": 14.99,
        "daily_messages": 100,
        "daily_features": {
            "study": 20, "content": 20, "business": 10, "code": 10, "image": 10,
        },
        "ads_required": False,
        "memory_days": 90,
        "models": ["gemini", "groq", "openrouter"],
        "voice": "elevenlabs",
        "coaching": True,
        "dreams": True,
    },
    "pro": {
        "name": "Pro",
        "price": 110,
        "billing_period": "6_months",
        "daily_messages": 500,
        "daily_features": {
            "study": 100, "content": 100, "business": 50, "code": 50, "image": 30,
        },
        "ads_required": False,
        "memory_days": 365,
        "models": ["gemini", "groq", "openrouter"],
        "voice": "elevenlabs",
        "coaching": True,
        "dreams": True,
    },
    "yearly": {
        "name": "Yearly",
        "price": 199,
        "billing_period": "yearly",
        "daily_messages": 9999,
        "daily_features": {
            "study": 999, "content": 999, "business": 999, "code": 999, "image": 999,
        },
        "ads_required": False,
        "memory_days": 999,
        "models": ["gemini", "groq", "openrouter"],
        "voice": "elevenlabs",
        "coaching": True,
        "dreams": True,
    },
}

def get_tier_config(tier: str) -> Dict[str, Any]:
    return TIER_CONFIGS.get(tier, TIER_CONFIGS["free"])

def get_feature_limit(tier: str, feature: str) -> int:
    config = get_tier_config(tier)
    return config.get("daily_features", {}).get(feature, 0)

def can_use_feature(tier: str, feature: str) -> bool:
    limit = get_feature_limit(tier, feature)
    return limit > 0

def is_ads_required(tier: str) -> bool:
    config = get_tier_config(tier)
    return config.get("ads_required", False)
