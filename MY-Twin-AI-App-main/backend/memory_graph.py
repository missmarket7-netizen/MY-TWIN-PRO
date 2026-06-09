"""
MyTwin – Unified Memory System v4.0
يدمج: Memory Engine + Personal Knowledge Graph + Memory Graph
- تصنيف ذكي للذكريات (core, emotional, preference, relationship)
- تخزين في Supabase مع استرجاع سياقي
- دمج المعرفة الشخصية من الكيانات
- متكامل مع multi_ai بدلاً من groq_helper
"""
import os, logging, json, asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from supabase import create_client, Client

logger = logging.getLogger("memory_graph")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
db: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# ========== أنواع الذكريات ==========
MEMORY_TYPES = {
    "core": "معلومة أساسية عن المستخدم (اسم، مهنة، عمر، مكان إقامة)",
    "emotional": "لحظة عاطفية قوية (فرح، حزن، خوف، حب)",
    "preference": "شيء يحبه أو يكرهه المستخدم (طعام، موسيقى، هوايات)",
    "relationship": "معلومة عن علاقة المستخدم مع شخص آخر (أم، أب، صديق)",
}

# ========== عميل AI ==========
def _get_multi_client():
    try:
        from multi_ai import MultiAIClient
        return MultiAIClient()
    except:
        return None

# ========== تصنيف الذكريات ==========
async def classify_memory(text: str) -> str:
    """استخدم multi_ai لتصنيف نوع الذاكرة"""
    client = _get_multi_client()
    if not client:
        return "core"
    try:
        prompt = f"""صنف هذه الذكرى إلى واحدة من: {', '.join(MEMORY_TYPES.keys())}
        أجب بنوع واحد فقط (core, emotional, preference, relationship).
        الذكرى: "{text}"
        النوع:"""
        result = await client.get_best_reply(prompt, task="deep_reasoning")
        if result:
            resp_text = result.strip().lower()
            if resp_text in MEMORY_TYPES:
                return resp_text
    except Exception as e:
        logger.warning(f"Memory classification failed: {e}")
    return "core"

# ========== تخزين الذكريات ==========
async def store_mem(uid: str, content: str, importance: float = 0.5, emotion: str = "neutral"):
    """تخزين ذكرى مع تصنيفها التلقائي"""
    if not db:
        return
    try:
        mem_type = await classify_memory(content)
        db.table("memories").insert({
            "user_id": uid,
            "content": content,
            "importance": importance,
            "emotion": emotion,
            "memory_type": mem_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        logger.info(f"✅ Memory stored [{mem_type}]: {content[:50]}...")
    except Exception as e:
        logger.error(f"Memory store error: {e}")

# ========== استرجاع الذكريات ==========
async def retrieve_memories(uid: str, query: str = "", days: int = 30, lim: int = 5, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
    if not db:
        return []
    try:
        req = db.table("memories").select("*").eq("user_id", uid).order("created_at", desc=True).limit(lim)
        if memory_type:
            req = req.eq("memory_type", memory_type)
        res = req.execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Memory retrieval error: {e}")
        return []

# ========== سياق الذاكرة للـ Prompt ==========
async def get_memory_context(uid: str) -> str:
    """بناء سياق نصي من جميع أنواع الذكريات والمعرفة الشخصية"""
    if not db:
        return ""
    try:
        core = await retrieve_memories(uid, memory_type="core", lim=3)
        emotional = await retrieve_memories(uid, memory_type="emotional", lim=2)
        preferences = await retrieve_memories(uid, memory_type="preference", lim=3)
        relationships = await retrieve_memories(uid, memory_type="relationship", lim=2)

        context = ""
        if core:
            context += "معلومات أساسية عن المستخدم: " + " | ".join([m["content"] for m in core]) + "\n"
        if emotional:
            context += "لحظات عاطفية مهمة: " + " | ".join([m["content"] for m in emotional]) + "\n"
        if preferences:
            context += "تفضيلات المستخدم: " + " | ".join([m["content"] for m in preferences]) + "\n"
        if relationships:
            context += "علاقات مهمة: " + " | ".join([m["content"] for m in relationships]) + "\n"

        # دمج المعرفة الشخصية من الكيانات
        knowledge = await get_knowledge_context(uid)
        if knowledge:
            context += "معرفة شخصية: " + knowledge + "\n"

        return context
    except Exception as e:
        logger.error(f"Memory context error: {e}")
        return ""

# ========== كيانات المعرفة ==========
async def extract_entities(user_id: str, message: str, lang: str = "ar"):
    """يستخرج الكيانات من رسالة المستخدم ويخزنها في جدول knowledge_entities"""
    if not db or not message.strip():
        return

    client = _get_multi_client()
    if not client:
        return

    prompt = f"""استخرج الكيانات التالية من هذه الرسالة وأعد ONLY JSON:
{{
  "people": ["اسم شخص وعلاقته"],
  "preferences": ["شيء يحبه أو يكرهه"],
  "goals": ["هدف أو طموح"],
  "habits": ["عادة أو روتين"],
  "facts": ["معلومة عامة عن المستخدم"]
}}
الرسالة: "{message}"
JSON:"""

    try:
        result = await client.get_best_reply(prompt, task="deep_reasoning")
        if result:
            raw = result.strip()
            if raw.startswith("```json"): raw = raw.split("```json")[1].split("```")[0].strip()
            elif raw.startswith("```"): raw = raw.split("```")[1].split("```")[0].strip()
            entities = json.loads(raw)

            for entity_type, items in entities.items():
                for item in items:
                    db.table("knowledge_entities").insert({
                        "user_id": user_id,
                        "entity_type": entity_type,
                        "entity_name": str(item),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                    }).execute()

            logger.info(f"✅ Extracted {sum(len(v) for v in entities.values())} entities for {user_id}")
    except Exception as e:
        logger.warning(f"Entity extraction failed: {e}")

async def get_knowledge_context(user_id: str) -> str:
    """استرجاع ملخص المعرفة الشخصية للمستخدم"""
    if not db:
        return ""
    try:
        res = db.table("knowledge_entities").select("entity_type, entity_name").eq("user_id", user_id).limit(10).execute()
        if not res.data:
            return ""

        grouped: Dict[str, List[str]] = {}
        for row in res.data:
            t = row["entity_type"]
            if t not in grouped:
                grouped[t] = []
            grouped[t].append(row["entity_name"])

        parts = []
        for t, items in grouped.items():
            parts.append(f"{t}: {', '.join(items)}")
        return " | ".join(parts)
    except Exception as e:
        logger.warning(f"Knowledge context failed: {e}")
        return ""

# ========== حفظ الكيانات والعلاقات ==========
async def save_entity(user_id: str, entity_type: str, entity_name: str, attributes: Optional[Dict] = None) -> bool:
    if not db:
        return False
    try:
        db.table("knowledge_entities").insert({
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_name": entity_name,
            "attributes": attributes or {},
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return True
    except Exception as e:
        logger.error(f"save_entity failed: {e}")
        return False

async def save_relation(user_id: str, entity1_id: int, relation_type: str, entity2_id: int, strength: float = 0.5) -> bool:
    if not db:
        return False
    try:
        db.table("entity_relations").insert({
            "user_id": user_id,
            "entity1_id": entity1_id,
            "relation_type": relation_type,
            "entity2_id": entity2_id,
            "strength": strength,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
        return True
    except Exception as e:
        logger.error(f"save_relation failed: {e}")
        return False

# ========== تلخيص المحادثات ==========
async def check_and_summarize(uid: str, chat_history: List[Dict[str, str]], twin_name: str):
    if len(chat_history) < 20:
        return
    client = _get_multi_client()
    if not client:
        return
    try:
        conversation = "\n".join([f"{'المستخدم' if m['role']=='user' else twin_name}: {m['content']}" for m in chat_history[-20:]])
        prompt = f"لخص هذه المحادثة في جملتين بالعربية، مع التركيز على أهم المواضيع والمشاعر:\n{conversation}"
        summary = await client.get_best_reply(prompt, task="deep_reasoning")
        if summary:
            await store_mem(uid, summary.strip(), importance=0.7, emotion="neutral")
            logger.info(f"✅ Chat summarized for user {uid}")
    except Exception as e:
        logger.error(f"Summarization error: {e}")

# ========== للتوافق مع الكود القديم ==========
class DeepMemorySystem:
    def retrieve(self, uid: str, query: str, days: int = 30, lim: int = 5, emotion_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        if not db:
            return []
        try:
            req = db.table("memories").select("*").eq("user_id", uid).order("created_at", desc=True).limit(lim)
            if emotion_filter:
                req = req.eq("emotion", emotion_filter)
            res = req.execute()
            return res.data or []
        except:
            return []

print("✅ Unified Memory System v4.0 جاهز")
