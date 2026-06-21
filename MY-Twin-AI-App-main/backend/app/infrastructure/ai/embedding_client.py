"""
Embedding Client v2.0 – توليد التضمينات (متعدد المزودين)
=============================================================
يدعم: Gemini، OpenAI، نموذج محلي (HuggingFace).
مع تخزين مؤقت (Cache) وتكامل مع Metrics.
"""
import os, logging, hashlib
from typing import List, Optional

logger = logging.getLogger("embedding_client")

# ============================================================
# الإعدادات
# ============================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini")  # gemini, openai, local
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "768"))

# تخزين مؤقت بسيط
_cache: dict = {}

# ============================================================
# مزود Gemini
# ============================================================
async def _gemini_embed(text: str) -> List[float]:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY غير متوفر")
    from google import genai
    client = genai.Client(api_key=GEMINI_API_KEY)
    result = await client.aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
    )
    if result.embeddings and len(result.embeddings) > 0:
        return list(result.embeddings[0].values)
    return []

# ============================================================
# مزود OpenAI
# ============================================================
async def _openai_embed(text: str) -> List[float]:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY غير متوفر")
    import openai
    client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    if response.data:
        return response.data[0].embedding
    return []

# ============================================================
# مزود محلي (HuggingFace)
# ============================================================
async def _local_embed(text: str) -> List[float]:
    """توليد التضمين محلياً باستخدام HuggingFace (إن وُجد)"""
    try:
        from sentence_transformers import SentenceTransformer
        import asyncio
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, model.encode, text)
        return embeddings.tolist()
    except ImportError:
        logger.error("sentence_transformers غير مثبتة – الرجاء تثبيتها للوضع المحلي")
        return []

# ============================================================
# دالة التوليد الموحدة
# ============================================================
async def generate_embedding(text: str) -> List[float]:
    """
    توليد تضمين للنص.
    يستخدم التخزين المؤقت لتجنب إعادة التوليد.
    """
    # 1. فحص التخزين المؤقت
    cache_key = hashlib.md5(text.encode()).hexdigest()
    if cache_key in _cache:
        return _cache[cache_key]

    # 2. محاولة التوليد حسب المزود
    try:
        if EMBEDDING_PROVIDER == "openai":
            vector = await _openai_embed(text)
        elif EMBEDDING_PROVIDER == "local":
            vector = await _local_embed(text)
        else:  # gemini
            vector = await _gemini_embed(text)

        if vector:
            # تخزين في الكاش
            if len(_cache) > 10000:
                _cache.clear()
            _cache[cache_key] = vector

            # تسجيل المقياس
            try:
                from app.observability.metrics_service import metrics
                metrics.record_request("embedding", 200, 0)
            except:
                pass

            return vector
    except Exception as e:
        logger.error(f"توليد التضمين فشل ({EMBEDDING_PROVIDER}): {e}")

    # 3. احتياطي: تضمين وهمي
    logger.warning("استخدام تضمين وهمي (Mock Embedding)")
    h = hashlib.md5(text.encode()).digest()
    return list(h.ljust(VECTOR_DIMENSION // 8, b'\x00'))[:VECTOR_DIMENSION]

async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """توليد تضمينات لمجموعة نصوص"""
    results = []
    for text in texts:
        emb = await generate_embedding(text)
        results.append(emb)
    return results

logger.info(f"✅ Embedding Client v2.0 initialized (provider: {EMBEDDING_PROVIDER})")
