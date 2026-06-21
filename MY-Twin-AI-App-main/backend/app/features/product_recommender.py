"""
MyTwin – Product Recommender v3.0 (متوافق مع TCMA والهيكل الجديد)
محرك توصية المنتجات (إعلانات سياقية) داخل المحادثة.
يكتشف نية الشراء، يجلب أفضل منتج حسب الباقة، ويسجل مرات الظهور والنقرات.
يتكامل مع TCMA لتسجيل مشاعر الشراء.
"""
import os, logging, hashlib
from datetime import datetime, timezone
from typing import Optional, Dict

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.infrastructure.cache.cache_service import get as cache_get, set as cache_set
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import store_emotional_memory
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger(__name__)

INTENT_KEYWORDS = {
    "health": ["رياضة", "جيم", "صحة", "مكمل", "نادي", "جري", "دايت", "gym", "health", "fitness", "diet", "protein", "vitamin"],
    "productivity": ["عمل", "إنتاجية", "مكتب", "تنظيم", "وقت", "work", "productivity", "time management", "planner", "tool"],
    "learning": ["تعلم", "دورة", "كتاب", "قراءة", "كورس", "تعليم", "course", "book", "learn", "udemy", "skillshare"],
    "entertainment": ["فيلم", "لعبة", "موسيقى", "ترفيه", "نتفلكس", "game", "movie", "music", "netflix", "spotify"],
    "lifestyle": ["عناية", "بشرة", "شعر", "موضة", "ملابس", "skin", "hair", "fashion", "clothes", "perfume"],
}

RECO_FREQUENCY = {
    "free": 3,
    "plus": 5,
    "premium": 10,
    "pro": 0,
    "yearly": 0,
}

class ProductRecommender:
    def __init__(self):
        self.interaction_counter: Dict[str, int] = {}

    async def detect_purchase_intent(self, message: str, user_id: Optional[str] = None) -> Optional[str]:
        if not message or len(message.strip()) < 10:
            return None

        text_hash = hashlib.md5(message.encode()).hexdigest()
        cache_key = f"intent:{text_hash}"
        if CACHE_AVAILABLE:
            cached = cache_get(cache_key)
            if cached is not None:
                return cached if cached != "none" else None

        msg_lower = message.lower()
        for category, keywords in INTENT_KEYWORDS.items():
            if any(kw in msg_lower for kw in keywords):
                if CACHE_AVAILABLE:
                    cache_set(cache_key, category, 3600)
                return category

        if AI_AVAILABLE:
            try:
                prompt = f"""
                Analyze this message and extract product category if user shows purchase intent.
                Categories: health, productivity, learning, entertainment, lifestyle, none.
                Return ONLY one word.
                Message: "{message}"
                """
                result = await provider_router.generate(prompt, language="en")
                if result:
                    result = result.strip().lower()
                    for cat in ["health", "productivity", "learning", "entertainment", "lifestyle"]:
                        if cat in result:
                            if CACHE_AVAILABLE:
                                cache_set(cache_key, cat, 3600)
                            return cat
            except Exception as e:
                logger.warning(f"Intent detection via AI failed: {e}")

        if CACHE_AVAILABLE:
            cache_set(cache_key, "none", 3600)
        return None

    def should_recommend(self, user_id: str, tier: str) -> bool:
        freq = RECO_FREQUENCY.get(tier, 999)
        if freq == 0:
            return False
        if not CACHE_AVAILABLE:
            return True  # بدون كاش، نسمح بالتوصية
        key = f"rec_counter:{user_id}"
        count = cache_get(key) or 0
        count += 1
        cache_set(key, count, 86400)
        if count % freq == 0:
            return True
        return False

    async def get_best_product(self, category: str, tier: str = "free") -> Optional[Dict]:
        if not DB_AVAILABLE:
            return None
        db = get_db()
        try:
            result = (
                db.table("products")
                .select("*")
                .eq("category", category)
                .eq("active", True)
                .order("priority", desc=True)
                .limit(1)
                .execute()
            )
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error fetching product: {e}")
            return None

    def format_suggestion(self, product: Dict, lang: str = "ar") -> str:
        name = product.get("name", "منتج")
        desc = product.get("description", "")
        link = product.get("affiliate_link", "#")
        price = product.get("price", "")
        rating = product.get("rating", "")
        stars = "⭐" * int(float(rating)) if rating else ""
        price_str = f"💰 {price}" if price else ""
        if lang == "ar":
            return f"\n\n💡 *اكتشاف قد يعجبك*\n**{name}** {stars}\n_{desc}_\n{price_str}\n🔗 [تسوق الآن]({link})"
        else:
            return f"\n\n💡 *You might like*\n**{name}** {stars}\n_{desc}_\n{price_str}\n🔗 [Shop now]({link})"

    def log_impression(self, user_id: str, product_id: str, message_id: str = "") -> bool:
        if not DB_AVAILABLE: return False
        db = get_db()
        try:
            db.table("product_impressions").insert({
                "user_id": user_id,
                "product_id": product_id,
                "message_id": message_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Impression log error: {e}")
            return False

    def log_click(self, user_id: str, product_id: str) -> bool:
        if not DB_AVAILABLE: return False
        db = get_db()
        try:
            db.table("product_clicks").insert({
                "user_id": user_id,
                "product_id": product_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
            return True
        except Exception as e:
            logger.error(f"Click log error: {e}")
            return False

    async def process_and_attach(self, user_id: str, message: str, reply: str,
                                 tier: str, lang: str = "ar") -> str:
        if "🆘" in reply or "safety_alert" in reply:
            return reply
        if not self.should_recommend(user_id, tier):
            return reply
        category = await self.detect_purchase_intent(message, user_id)
        if not category:
            return reply
        product = await self.get_best_product(category, tier)
        if not product:
            return reply
        suggestion = self.format_suggestion(product, lang)
        final_reply = reply + suggestion
        self.log_impression(user_id, product["id"], str(hashlib.md5(message.encode()).hexdigest())[:10])
        
        # تكامل مع TCMA: تسجيل مشاعر الشراء
        if TCMA_AVAILABLE:
            try:
                await store_emotional_memory(
                    user_id=user_id, expressed_text=f"توصية منتج: {product.get('name', '')}",
                    detected_emotion={"primary": "curious", "intensity": 0.5, "valence": 0.3},
                    trigger="product_recommendation", cultural_context=category
                )
            except Exception as e:
                logger.warning(f"TCMA product log failed: {e}")
        
        return final_reply

product_recommender = ProductRecommender()
