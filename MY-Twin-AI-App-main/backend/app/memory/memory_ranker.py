"""Memory Ranker – semantic and emotional importance ranking."""
import logging
from typing import List, Optional
from app.models.memory import Memory

logger = logging.getLogger("memory_ranker")

HIGH_EMOTION_WORDS = [
    "وفاة","مات","موت","زواج","حب","مرض","سرطان","خيانة","نجاح","فشل",
    "death","marriage","cancer","love","betrayal","success","failure",
]


def rank(memories: List[Memory], query: str = "") -> List[Memory]:
    """
    Rank memories by combined importance:
    - Emotional weight (keyword presence)
    - Memory importance score
    - Query keyword overlap
    """
    query_words = set(query.lower().split()) if query else set()

    def _score(m: Memory) -> float:
        content = (m.content or "").lower()
        # Emotional weight
        emo = sum(1 for w in HIGH_EMOTION_WORDS if w.lower() in content) * 0.15
        emo = min(emo, 1.0)
        # Importance
        imp = m.importance or 0.5
        # Query overlap
        overlap = len(query_words & set(content.split())) / max(len(query_words), 1) if query_words else 0.0
        return emo * 0.3 + imp * 0.4 + overlap * 0.3

    ranked = sorted(memories, key=lambda m: _score(m), reverse=True)
    for i, m in enumerate(ranked):
        if m.scores is None:
            m.scores = {}
        m.scores["rank_score"] = _score(m)
        m.scores["rank"] = i + 1
    return ranked


def separate_by_priority(memories: List[Memory]) -> tuple:
    """Split memories into important and secondary."""
    important = [m for m in memories if (m.importance or 0) >= 0.7 or m.is_hard]
    secondary = [m for m in memories if m not in important]
    return important, secondary
