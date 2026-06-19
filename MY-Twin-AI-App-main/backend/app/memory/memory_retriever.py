"""Memory Retriever – smart retrieval with MMR re‑ranking."""
import logging, asyncio, math
from typing import List, Dict, Any, Optional
from app.repositories.memory_repository import search_similar, get_recent
from app.models.memory import Memory

logger = logging.getLogger("memory_retriever")

WEIGHTS = {"semantic": 0.30, "importance": 0.25, "recency": 0.20, "emotional": 0.15, "type_priority": 0.10}
TYPE_PRIORITY = {"goal": 1.0, "relationship": 0.9, "core": 1.0, "fact": 0.7, "daily": 0.5}
HIGH_EMOTION = ["وفاة","مات","زواج","حب","مرض","سرطان","death","marriage","cancer","love"]


def _cosine(vec1: List[float], vec2: List[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot = sum(a * b for a, b in zip(vec1, vec2))
    n1 = sum(a * a for a in vec1) ** 0.5
    n2 = sum(b * b for b in vec2) ** 0.5
    return dot / (n1 * n2) if n1 and n2 else 0.0


def _score(memory: Memory, query_embedding: Optional[List[float]] = None) -> float:
    sim = _cosine(memory.embedding or [], query_embedding or []) if query_embedding and memory.embedding else 0.0
    imp = memory.importance or 0.5
    emo = 0.8 if any(w in (memory.content or "").lower() for w in HIGH_EMOTION) else 0.0
    tp = TYPE_PRIORITY.get(memory.memory_type, 0.5)
    return sim * 0.30 + imp * 0.25 + emo * 0.15 + tp * 0.10


def _mmr(candidates: List[tuple], lambda_param: float = 0.7, top_k: int = 5) -> List[Memory]:
    if not candidates:
        return []
    selected = [candidates[0][1]]
    remaining = candidates[1:]
    while remaining and len(selected) < top_k:
        scores = []
        for _, mem in remaining:
            max_sim = max((_cosine(mem.embedding or [], s.embedding or []) for s in selected), default=0)
            mmr = lambda_param * mem.scores.get("final", 0.5) - (1 - lambda_param) * max_sim
            scores.append((mmr, mem))
        scores.sort(key=lambda x: x[0], reverse=True)
        selected.append(scores[0][1])
        remaining = [(s, m) for s, m in remaining if m != scores[0][1]]
    return selected


async def retrieve(query_embedding: List[float], user_id: str,
                   top_k: int = 5, min_score: float = 0.1) -> List[Memory]:
    """Main retrieval with MMR."""
    memories = await search_similar(query_embedding, user_id, top_k * 3)
    if not memories:
        memories = await get_recent(user_id, top_k * 3)
    scored = []
    for m in memories:
        s = _score(m, query_embedding)
        if s >= min_score:
            m.scores = {"final": s}
            scored.append((s, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return _mmr(scored, 0.7, top_k) if len(scored) > 1 else [m for _, m in scored[:top_k]]


async def retrieve_and_summarize(query_embedding: List[float], user_id: str,
                                 top_k: int = 5) -> Dict[str, Any]:
    memories = await retrieve(query_embedding, user_id, top_k)
    return {"memories": memories, "count": len(memories)}
