"""
Core – الخدمات الأساسية لـ MyTwin
=====================================
- config: الإعدادات المركزية
- security: المصادقة وفك JWT
- feature_flags: أعلام الميزات
- i18n: الترجمة والرسائل
- streaming: محرك SSE للتدفق
- redis_config: اتصال Redis
- unified_recommendation_engine: محرك التوصيات الشامل
- cross_feature_analyzer: محلل الروابط بين الميزات
"""
from .config import config, Config
from .security import (
    decode_access_token,
    extract_user_id,
    extract_tier,
    get_user_context,
    validate_token,
)
from .feature_flags import (
    is_feature_enabled,
    set_feature_flag,
    get_all_flags,
    is_tier_allowed,
    get_available_features,
)
from .i18n import msg
from .streaming import streaming, sse_generator
from .redis_config import get_redis, REDIS_AVAILABLE
from .unified_recommendation_engine import engine as recommendation_engine
from .cross_feature_analyzer import analyzer as cross_feature_analyzer

__all__ = [
    # Config
    "config", "Config",
    # Security
    "decode_access_token", "extract_user_id", "extract_tier",
    "get_user_context", "validate_token",
    # Feature Flags
    "is_feature_enabled", "set_feature_flag", "get_all_flags",
    "is_tier_allowed", "get_available_features",
    # i18n
    "msg",
    # Streaming
    "streaming", "sse_generator",
    # Redis
    "get_redis", "REDIS_AVAILABLE",
    # Recommendations
    "recommendation_engine",
    # Cross Feature
    "cross_feature_analyzer",
]
