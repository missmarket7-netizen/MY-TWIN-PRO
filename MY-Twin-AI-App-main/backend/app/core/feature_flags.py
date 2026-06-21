"""
Feature Flags v2.0 – جميع ميزات MyTwin الجديدة
==================================================
- أعلام لجميع الميزات المطورة
- تكامل مع نظام الباقات (Tier)
- تخزين في الكاش للسرعة
"""
import os, logging
from typing import Dict, Any, Optional

logger = logging.getLogger("feature_flags")

try:
    from app.infrastructure.cache.cache_service import get, set as cache_set
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

# جميع الميزات المتاحة في MyTwin
FEATURE_FLAGS: Dict[str, bool] = {
    # الأساسية
    "chat": True,
    "voice": True,
    "ads": True,
    # TCMA (الذاكرة)
    "long_memory": True,
    "emotional_memory": True,
    "reflection_engine": True,
    "identity_model": True,
    "memory_graph": True,
    "person_node": True,
    # الميزات الرئيسية
    "study": True,           # ATHENA
    "business": True,        # GROWTH-HIVE
    "creator": True,         # C.R.E.A.T.O.R.
    "code_lab": True,        # C.O.D.E. Lab
    "life_coach": True,      # L.I.F.E. C.O.A.C.H.
    "dreams": True,          # Dream Analysis
    "smart_home": True,      # S.M.A.R.T. Home
    "task_manager": True,    # P.A.S.S.
    # المحركات المتقدمة
    "proactive": True,
    "temporal_context": True,
    "meta_reflection": True,
    "shadow_mode": True,
    "cross_feature": True,
    # الخدمات
    "search": True,
    "deep_search": True,
    "translate": True,
    "summarize": True,
    "weather": True,
    "news": True,
    "currency": True,
    # التوصيات
    "recommendations": True,
    "weekly_report": True,
}

def is_feature_enabled(feature: str) -> bool:
    """التحقق من تفعيل ميزة (من الكاش أو القاموس)"""
    if CACHE_AVAILABLE:
        cached = get(f"feature:{feature}")
        if cached is not None:
            return cached == "true"
    return FEATURE_FLAGS.get(feature, False)

def set_feature_flag(feature: str, enabled: bool) -> None:
    """تحديث علم ميزة (في القاموس والكاش)"""
    FEATURE_FLAGS[feature] = enabled
    if CACHE_AVAILABLE:
        cache_set(f"feature:{feature}", str(enabled).lower(), 3600)

def get_all_flags() -> Dict[str, bool]:
    """جلب جميع الأعلام الحالية"""
    return {f: is_feature_enabled(f) for f in FEATURE_FLAGS}

def is_tier_allowed(tier: str, feature: str) -> bool:
    """التحقق من أن الباقة تسمح بهذه الميزة"""
    from app.models.tier import get_tier_config
    config = get_tier_config(tier)
    
    # الميزات الخاصة
    feature_tier_map = {
        "study": config.study_enabled,
        "business": config.business_enabled,
        "creator": config.creator_enabled,
        "code_lab": config.code_lab_enabled,
        "life_coach": config.coaching_enabled,
        "dreams": config.dreams_enabled,
        "smart_home": config.smart_home_enabled,
        "proactive": config.proactive_enabled,
        "long_memory": config.long_memory_enabled,
        "deep_search": config.deep_search_enabled,
        "translate": config.translate_enabled,
        "summarize": config.summarize_enabled,
        "shadow_mode": config.shadow_mode_enabled,
    }
    
    if feature in feature_tier_map:
        return feature_tier_map[feature]
    
    # الميزات العامة متاحة للجميع
    return True

async def get_available_features(user_id: str, tier: str = "free") -> Dict[str, bool]:
    """جلب الميزات المتاحة لمستخدم محدد (حسب الباقة والأعلام)"""
    available = {}
    for feature in FEATURE_FLAGS:
        flag_enabled = is_feature_enabled(feature)
        tier_allowed = is_tier_allowed(tier, feature)
        available[feature] = flag_enabled and tier_allowed
    
    return available

logger.info("✅ Feature Flags v2.0 initialized")
