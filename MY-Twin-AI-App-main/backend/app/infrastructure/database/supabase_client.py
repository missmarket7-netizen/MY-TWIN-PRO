"""
MyTwin – Supabase Client (Singleton)
=====================================
عميل Supabase الوحيد في المشروع كله.
يستخدم SERVICE_KEY (خاص، لا يُكشف أبداً).
"""
import logging
from app.core.config import config

logger = logging.getLogger(__name__)

_db: Client = None


def get_db() -> Client:
    """
    جلب عميل Supabase (نمط Singleton).
    يُنشأ مرة واحدة ويعاد استخدامه.
    """
    global _db
    
    if _db is None:
        if not config.SUPABASE_URL or not config.SUPABASE_SERVICE_KEY:
            raise RuntimeError("❌ SUPABASE_URL و SUPABASE_SERVICE_KEY مطلوبان")
        
        _db = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
        logger.info("✅ Supabase client initialized")
    
    return _db
