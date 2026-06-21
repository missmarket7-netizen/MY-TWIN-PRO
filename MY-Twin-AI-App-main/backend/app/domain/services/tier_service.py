"""
Tier Service v2.0 – متكامل مع جميع ميزات MyTwin الجديدة
=============================================================
- 5 باقات (Free, Plus, Premium, Pro, Yearly)
- حدود لكل ميزة على حدة
- تكامل مع Feature Flags و Limits Service
"""
from typing import Dict, Any

TIER_CONFIGS: Dict[str, Dict[str, Any]] = {
    "free": {
        "name": "Free", "price": 0, "daily_messages": 15,
        "daily_features": {
            "chat": 15, "study": 3, "content": 2, "business": 1,
            "code_lab": 1, "life_coach": 1, "dreams": 1, "smart_home": 3,
            "search": 5, "translate": 3, "summarize": 3, "weather": 10,
            "news": 5, "currency": 5, "voice": 3,
        },
        "ads_required": True, "memory_days": 3,
        "models": ["groq", "gemini"], "voice": "edge_tts",
        "coaching": False, "dreams": False, "study": True,
    },
    "plus": {
        "name": "Plus", "price": 5.99, "daily_messages": 50,
        "daily_features": {
            "chat": 50, "study": 15, "content": 10, "business": 5,
            "code_lab": 5, "life_coach": 3, "dreams": 3, "smart_home": 10,
            "search": 20, "translate": 15, "summarize": 15, "weather": 30,
            "news": 20, "currency": 20, "voice": 10,
        },
        "ads_required": False, "memory_days": 30,
        "models": ["groq", "gemini", "openrouter"], "voice": "edge_tts",
        "coaching": True, "dreams": True, "study": True,
    },
    "premium": {
        "name": "Premium", "price": 14.99, "daily_messages": 150,
        "daily_features": {
            "chat": 150, "study": 50, "content": 40, "business": 30,
            "code_lab": 30, "life_coach": 20, "dreams": 20, "smart_home": 50,
            "search": 100, "translate": 50, "summarize": 50, "weather": 100,
            "news": 100, "currency": 100, "voice": 50,
        },
        "ads_required": False, "memory_days": 90,
        "models": ["gemini", "openrouter", "groq"], "voice": "elevenlabs",
        "coaching": True, "dreams": True, "study": True,
    },
    "pro": {
        "name": "Pro", "price": 110, "billing_period": "6_months", "daily_messages": 500,
        "daily_features": {
            "chat": 500, "study": 200, "content": 150, "business": 100,
            "code_lab": 100, "life_coach": 50, "dreams": 50, "smart_home": 200,
            "search": 500, "translate": 200, "summarize": 200, "weather": 500,
            "news": 500, "currency": 500, "voice": 200,
        },
        "ads_required": False, "memory_days": 365,
        "models": ["gemini", "openrouter", "groq"], "voice": "elevenlabs",
        "coaching": True, "dreams": True, "study": True,
    },
    "yearly": {
        "name": "Yearly", "price": 199, "billing_period": "yearly", "daily_messages": 9999,
        "daily_features": {
            "chat": 9999, "study": 9999, "content": 9999, "business": 9999,
            "code_lab": 9999, "life_coach": 9999, "dreams": 9999, "smart_home": 9999,
            "search": 9999, "translate": 9999, "summarize": 9999, "weather": 9999,
            "news": 9999, "currency": 9999, "voice": 9999,
        },
        "ads_required": False, "memory_days": 999,
        "models": ["gemini", "openrouter", "groq"], "voice": "elevenlabs",
        "coaching": True, "dreams": True, "study": True,
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

def get_daily_messages(tier: str) -> int:
    config = get_tier_config(tier)
    return config.get("daily_messages", 15)
