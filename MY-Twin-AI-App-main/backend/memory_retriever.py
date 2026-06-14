"""
MyTwin – Memory Retriever v4.0 (Agent-Ready + Persistent Embeddings)
- hard_memories (core type) always included
- query_embedding None? → fallback keyword retrieval
- type_priority as independent weight (not multiplier)
- MMR uses _embedding stored during scoring
- Agent-ready: retrieve_for_agent() for loop integration
- Persistent embeddings: stores embedding in DB after calculation
"""
import os, logging, asyncio, math
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("memory_retriever")

try:
    import google.generativeai as genai
    GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        EMBEDDING_MODEL = "models/text-embedding-004"
    else:
        EMBEDDING_MODEL = None
except ImportError:
    genai = None
    EMBEDDING_MODEL = None

WEIGHTS = {
    "semantic": 0.30,
    "importance": 0.25,
    "recency": 0.20,
    "emotional": 0.15,
    "type_priority": 0.10,
}

MEMORY_TYPE_PRIORITY = {
    "goal": 1.0, "relationship": 0.9, "preference": 0.8,
    "core": 1.0, "fact": 0.7, "daily": 0.5,
}

HIGH_EMOTIONAL_WEIGHT_WORDS = [
    "وفاة", "مات", "موت", "زواج", "زوجتي", "زوجي", "ابني", "ابنتي",
    "مرض", "سرطان", "حادث", "فقدت", "فقدان", "طلاق", "انفصال",
    "وظيفة جديدة", "ترقية", "فصل", "طرد", "حمل", "ولادة",
    "حب حياتي", "خيانة", "نجاح كبير", "فشل", "إنجاز",
    "death", "died", "marriage", "wedding", "son", "daughter",
    "cancer", "accident", "lost", "divorce", "separation",
    "new job", "promotion", "fired", "pregnant", "birth",
    "love of my life", "betrayal", "big success", "failure", "achievement"
]

class MemoryRetriever:
    def __init__(self):
        self.embedding_cache: Dict[str, List[float]] = {}

    async def _get_embedding(self, text: str, task_type: str = "retrieval_document") -> Optional[List[float]]:
        if not EMBEDDING_MODEL or not text:
            return None
        cache_key = f"{task_type}:{text[:200]}"
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model=EMBEDDING_MODEL,
                    content=text[:1000],
                    task_type=task_type
                )
            )
            embedding = result.get("embedding", [])
            if embedding:
                self.embedding_cache[cache_key] = embedding
                if len(self.embedding_cache) > 500:
                    self.embedding_cache.clear()
                return embedding
        except Exception as e:
            logger.warning(f"Embedding failed: {e}")
        return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _importance_score(self, memory: Dict[str, Any]) -> float:
        return float(memory.get("importance", 0.5) or 0.5)

    def _recency_score(self, memory: Dict[str, Any]) -> float:
        created_at = memory.get("created_at")
        if not created_at:
            return 0.5
        try:
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            days_ago = (datetime.now(timezone.utc) - created_at).days
            return math.exp(-days_ago / 30)
        except:
            return 0.5

    def _emotional_weight(self, memory: Dict[str, Any]) -> float:
        content = memory.get("content", "")
        keyword_score = sum(1 for word in HIGH_EMOTIONAL_WEIGHT_WORDS if word in content.lower()) * 0.15
        keyword_score = min(keyword_score, 1.0)
        stored_intensity = float(memory.get("emotion_intensity", 0) or 0)
        return max(keyword_score, stored_intensity)

    def _keyword_match_score(self, query: str, content: str) -> float:
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        if not query_words:
            return 0.0
        overlap = query_words.intersection(content_words)
        return len(overlap) / len(query_words)

    async def _store_embedding_in_db(self, memory_id: str, embedding: List[float]):
        """تخزين الـ embedding في Supabase للاستخدام المستقبلي."""
        try:
            from supabase import create_client
            url = os.getenv("SUPABASE_URL", ""); key = os.getenv("SUPABASE_SERVICE_KEY", "")
            if url and key and memory_id:
                db = create_client(url, key)
                db.table("memories").update({"embedding": embedding}).eq("id", memory_id).execute()
        except Exception as e:
            logger.warning(f"Failed to store embedding in DB: {e}")

    async def score_memory(
        self, memory: Dict[str, Any], query_embedding: Optional[List[float]], query_text: str = ""
    ) -> Dict[str, float]:
        content = memory.get("content", "")
        if not content:
            return {"final": 0.0}

        memory_embedding = memory.get("embedding")
        if not memory_embedding and query_embedding:
            memory_embedding = await self._get_embedding(content, "retrieval_document")
            # تخزين الـ embedding في DB إن أمكن
            if memory_embedding and memory.get("id"):
                await self._store_embedding_in_db(memory["id"], memory_embedding)

        if query_embedding and memory_embedding:
            sim = self._cosine_similarity(memory_embedding, query_embedding)
        else:
            sim = self._keyword_match_score(query_text, content) * 0.6

        imp = self._importance_score(memory)
        rec = self._recency_score(memory)
        emo = self._emotional_weight(memory)
        type_priority = MEMORY_TYPE_PRIORITY.get(memory.get("memory_type", "daily"), 0.5)

        final = (
            sim * WEIGHTS["semantic"] +
            imp * WEIGHTS["importance"] +
            rec * WEIGHTS["recency"] +
            emo * WEIGHTS["emotional"] +
            type_priority * WEIGHTS["type_priority"]
        )

        return {
            "semantic": round(sim, 4),
            "importance": round(imp, 4),
            "recency": round(rec, 4),
            "emotional": round(emo, 4),
            "type_priority": round(type_priority, 2),
            "final": round(min(final, 1.0), 4),
        }

    def _mmr(self, candidates: List[tuple], lambda_param: float = 0.7) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        selected = [candidates[0][1]]
        candidates = candidates[1:]

        while candidates and len(selected) < 5:
            mmr_scores = []
            for final_score, memory in candidates:
                mem_emb = memory.get("_embedding", memory.get("embedding", []))
                max_sim = 0
                for s in selected:
                    s_emb = s.get("_embedding", s.get("embedding", []))
                    sim = self._cosine_similarity(mem_emb, s_emb)
                    max_sim = max(max_sim, sim)
                mmr = lambda_param * final_score - (1 - lambda_param) * max_sim
                mmr_scores.append((mmr, memory))

            if not mmr_scores:
                break
            mmr_scores.sort(key=lambda x: x[0], reverse=True)
            selected.append(mmr_scores[0][1])
            candidates = [(fs, m) for fs, m in candidates if m != mmr_scores[0][1]]

        return selected

    async def retrieve_relevant(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
        min_score: float = 0.1,
        use_mmr: bool = True
    ) -> List[Dict[str, Any]]:
        try:
            from memory_graph import retrieve_memories
            
            hard_memories = await retrieve_memories(uid=user_id, query="", days=365, lim=20, memory_type="core")
            all_memories = await retrieve_memories(uid=user_id, query="", days=180, lim=100)
            
            hard_ids = {m.get("id") for m in hard_memories}
            all_memories = [m for m in all_memories if m.get("id") not in hard_ids]

            if not all_memories and not hard_memories:
                return []

            query_embedding = await self._get_embedding(query, "retrieval_query")

            scored = []
            all_candidates = hard_memories + all_memories
            
            for memory in all_candidates:
                scores = await self.score_memory(memory, query_embedding, query_text=query)
                if scores["final"] >= min_score:
                    memory["_embedding"] = memory.get("embedding") or await self._get_embedding(memory.get("content", ""), "retrieval_document")
                    scored.append((scores["final"], {**memory, "scores": scores}))

            scored.sort(key=lambda x: x[0], reverse=True)

            if use_mmr and len(scored) > 1:
                return self._mmr(scored, lambda_param=0.7)[:top_k]

        # ✅ Reranker: إعادة ترتيب الذكريات
        try:
            from reranker import MemoryReranker
            reranker = MemoryReranker()
            if twin_brain_instance and hasattr(twin_brain_instance, "multi"):
                reranked = await reranker.rerank(query, [mem for score, mem in scored[:top_k]], twin_brain_instance.multi)
                if reranked:
                    return reranked[:top_k]
        except:
            pass
            return [mem for score, mem in scored[:top_k]]

        except Exception as e:
            logger.error(f"Memory retrieval failed: {e}")
            return []

    async def retrieve_for_agent(self, plan: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        استرجاع مخصص لـ Agent Loop: يستخدم goal و needs_memory من الخطة.
        """
        if not plan.get("needs_memory"):
            return {"memories": [], "count": 0}
        
        query = plan.get("goal", "")
        if not query:
            return {"memories": [], "count": 0}
        
        return await self.retrieve_and_summarize(query, user_id, top_k=3)

    async def retrieve_and_summarize(self, query: str, user_id: str, top_k: int = 5) -> Dict[str, Any]:
        memories = await self.retrieve_relevant(query, user_id, top_k)
        return {"memories": memories, "count": len(memories)}


memory_retriever = MemoryRetriever()
print("✅ Memory Retriever v4.0 (Agent-Ready + Persistent Embeddings)")
