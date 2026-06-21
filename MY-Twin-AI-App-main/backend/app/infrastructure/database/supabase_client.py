"""
Singleton Supabase Client v2.0 – مدير اتصال قوي
================================================
- اتصال واحد (Singleton) لتجنب تعدد الاتصالات
- إعادة محاولة تلقائية عند الفشل (Retry)
- فحص صحة الاتصال (Health Check)
- دعم الإعدادات من config.py
"""
import os, logging, time
from typing import Optional, Dict, Any
from supabase import create_client, Client

logger = logging.getLogger("supabase_client")

# الإعدادات
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
MAX_RETRIES = 3
RETRY_DELAY = 1.0  # ثانية

_db: Optional[Client] = None

def get_db() -> Client:
    """
    جلب عميل Supabase (Singleton).
    يعيد المحاولة تلقائياً إذا فشل الاتصال.
    """
    global _db
    if _db is not None:
        return _db

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise RuntimeError("❌ SUPABASE_URL و SUPABASE_SERVICE_KEY مطلوبان في متغيرات البيئة")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            _db = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            # اختبار الاتصال
            _db.table("profiles").select("id", count="exact").limit(1).execute()
            logger.info(f"✅ Supabase client initialized (attempt {attempt})")
            return _db
        except Exception as e:
            logger.warning(f"⚠️ فشل الاتصال بـ Supabase (محاولة {attempt}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise RuntimeError(f"❌ فشل الاتصال بـ Supabase بعد {MAX_RETRIES} محاولات")

    raise RuntimeError("❌ تعذر الاتصال بـ Supabase")

def reset_db():
    """إعادة تعيين الاتصال (للاستخدام في الاختبارات أو إعادة التحميل)"""
    global _db
    if _db:
        _db = None
        logger.info("🔄 تم إعادة تعيين اتصال Supabase")

async def check_db_health() -> Dict[str, Any]:
    """فحص صحة الاتصال بقاعدة البيانات"""
    try:
        db = get_db()
        start = time.time()
        db.table("profiles").select("id", count="exact").limit(1).execute()
        latency = (time.time() - start) * 1000
        return {
            "status": "healthy",
            "latency_ms": round(latency, 2),
            "url": SUPABASE_URL[:30] + "..."
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)[:200]
        }

# دوال مساعدة للتوافق مع الكود القديم
async def get_profile(user_id: str) -> Dict[str, Any]:
    """جلب الملف الشخصي للمستخدم (متوافقة مع الاستدعاءات القديمة)"""
    db = get_db()
    try:
        result = db.table("profiles").select("*").eq("id", user_id).execute()
        return result.data[0] if result.data else {}
    except Exception as e:
        logger.error(f"فشل جلب الملف الشخصي: {e}")
        return {}

logger.info("✅ Supabase Client v2.0 initialized")
