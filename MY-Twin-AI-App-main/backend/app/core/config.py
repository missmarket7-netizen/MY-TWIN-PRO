"""
MyTwin – Centralized Configuration
===================================
جميع إعدادات البيئة في مكان واحد.
تُستخدم من قبل جميع طبقات التطبيق.
"""
import os
from typing import Optional

class Config:
    """إعدادات التطبيق المركزية"""
    
    # == Supabase ==
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # == Redis (اختياري) ==
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # == الذكاء الاصطناعي ==
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_API_KEY_2: str = os.getenv("GEMINI_API_KEY_2", "")
    GEMINI_API_KEY_3: str = os.getenv("GEMINI_API_KEY_3", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_API_KEY_2: str = os.getenv("GROQ_API_KEY_2", "")
    GROQ_API_KEY_3: str = os.getenv("GROQ_API_KEY_3", "")
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_API_KEY_2: str = os.getenv("OPENROUTER_API_KEY_2", "")
    OPENROUTER_API_KEY_3: str = os.getenv("OPENROUTER_API_KEY_3", "")
    
    # == أمان ==
    CRON_SECRET_KEY: str = os.getenv("CRON_SECRET_KEY", "")
    SYSTEM_API_KEY: str = os.getenv("SYSTEM_API_KEY", "")
    
    # == مراقبة ==
    SENTRY_DSN: str = os.getenv("SENTRY_DSN", "")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    
    # == تطبيق ==
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    PORT: int = int(os.getenv("PORT", "8000"))

# نسخة عامة للاستخدام
config = Config()
