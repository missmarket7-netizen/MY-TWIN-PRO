"""
MyTwin – Centralized Configuration v2.0
========================================
جميع إعدادات البيئة في مكان واحد.
تشمل جميع الخدمات والميزات الجديدة.
"""
import os
from typing import Optional, List

class Config:
    """إعدادات التطبيق المركزية"""
    
    # == البيئة ==
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DEBUG: bool = ENVIRONMENT in ["development", "staging"]
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # == Supabase ==
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # == Redis ==
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_AVAILABLE: bool = False  # يُحدد عند الاتصال
    
    # == الذكاء الاصطناعي ==
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEY_2: str = os.getenv("GEMINI_API_KEY_2", "")
    GEMINI_API_KEY_3: str = os.getenv("GEMINI_API_KEY_3", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEY_2: str = os.getenv("GROQ_API_KEY_2", "")
    GROQ_API_KEY_3: str = os.getenv("GROQ_API_KEY_3", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    
    # == نموذج MyTwin الداخلي ==
    MYTWIN_MODEL_PATH: str = os.getenv("MYTWIN_MODEL_PATH", "./mytwin-llama3-lora")
    INTERNAL_MODEL_ENABLED: bool = os.getenv("INTERNAL_MODEL_ENABLED", "false").lower() == "true"
    
    # == المنزل الذكي ==
    HOME_ASSISTANT_URL: str = os.getenv("HOME_ASSISTANT_URL", "")
    HOME_ASSISTANT_TOKEN: str = os.getenv("HOME_ASSISTANT_TOKEN", "")
    WLED_BASE_URL: str = os.getenv("WLED_BASE_URL", "")
    ESPHOME_BASE_URL: str = os.getenv("ESPHOME_BASE_URL", "")
    
    # == الصوت ==
    VOICE_PROVIDER: str = os.getenv("VOICE_PROVIDER", "edge_tts")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # == الأمان ==
    CRON_SECRET_KEY: str = os.getenv("CRON_SECRET_KEY", "")
    SYSTEM_API_KEY: str = os.getenv("SYSTEM_API_KEY", "")
    
    # == مراقبة ==
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    
    # == إشعارات ==
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # == تطبيق ==
    ALLOWED_ORIGINS: List[str] = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
    EXPO_PUBLIC_API_URL: str = os.getenv("EXPO_PUBLIC_API_URL", "https://mytwin.app")
    
    # == حدود الاستخدام (افتراضية) ==
    DAILY_MESSAGES_LIMIT: int = int(os.getenv("DAILY_MESSAGES_LIMIT", "15"))
    DAILY_TOKENS_LIMIT: int = int(os.getenv("DAILY_TOKENS_LIMIT", "500"))
    
    # == ميزات مفعلة ==
    FEATURES_ENABLED: List[str] = os.getenv("FEATURES_ENABLED", "all").split(",")

# نسخة عامة للاستخدام
config = Config()
