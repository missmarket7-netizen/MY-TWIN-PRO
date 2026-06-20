"""Feature Flags – toggle features without redeployment."""
import os
from typing import Dict, Any
from app.infrastructure.cache.cache_service import get, set as cache_set

FEATURE_FLAGS: Dict[str, bool] = {
    "study": True,
    "code": True,
    "business": True,
    "coach": True,
    "content": True,
    "dreams": True,
    "image": True,
    "smart_home": True,
    "voice": True,
    "ads": True,
}

def is_feature_enabled(feature: str) -> bool:
    cached = get(f"feature:{feature}")
    if cached is not None:
        return cached == "true"
    return FEATURE_FLAGS.get(feature, False)

def set_feature_flag(feature: str, enabled: bool):
    FEATURE_FLAGS[feature] = enabled
    cache_set(f"feature:{feature}", str(enabled).lower(), 3600)

def get_all_flags() -> Dict[str, bool]:
    return {f: is_feature_enabled(f) for f in FEATURE_FLAGS}
