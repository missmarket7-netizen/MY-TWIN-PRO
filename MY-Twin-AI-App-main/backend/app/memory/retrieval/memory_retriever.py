"""
Perfect Memory Retrieval - Multi-source retrieval engine (Rebuilt)
===================================================================
يجمع السياق من جميع طبقات TCMA الستة + PersonNode + Memory Graph.
يستخدم الرسم البياني للذاكرة لاسترجاع ذكريات مترابطة.
"""

import logging
from typing import Dict, Any, Optional, List
from app.memory.archive.raw_archive import get_conversation_archive
from app.memory.emotional.emotional_memory import get_emotional_patterns
from app.memory.relationship.relationship_memory import get_relationship_insights
from app.memory.relationship.person_node import get_person_network
from app.memory.identity.identity_model import get_identity
from app.memory.reflection.reflection_engine import get_user_insights
from app.memory.graph.memory_graph import get_connected_memories

logger = logging.getLogger("memory_retriever")

# ============================================================
# الجزء 1: استدعاء كل طبقات الذاكرة
# ============================================================
async def retrieve_context(
    user_id: str,
    query: str,
    top_k: int = 10,
    recent_memory_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    استرجاع سياق متعدد المصادر للمحادثة.
    يجمع: عواطف، علاقات، أشخاص، هوية، استنتاجات، أرشيف، ورسم بياني.
    """
    
    # 1. الأنماط العاطفية
    emotional_patterns = await get_emotional_patterns(user_id, days=30)
    
    # 2. تحليل العلاقة
    relationship = await get_relationship_insights(user_id)
    
    # 3. شبكة الأشخاص المهمين
    person_network = await get_person_network(user_id, min_importance=20)
    
    # 4. نموذج الهوية
    identity = await get_identity(user_id)
    
    # 5. الاستنتاجات المتراكمة
    insights = await get_user_insights(user_id, min_confidence=0.6)
    
    # 6. المحادثات الأخيرة
    recent = await get_conversation_archive(user_id, limit=5)
    
    # 7. رسم الذاكرة البياني (إذا توفرت IDs حديثة)
    graph_context = {}
    if recent_memory_ids:
        graph_edges = []
        for mem_id in recent_memory_ids[-5:]:
            edges = await get_connected_memories(user_id, mem_id, depth=1)
            graph_edges.extend(edges)
        graph_context = {
            "active_edges": len(graph_edges),
            "connected_memories": len(set(e["source_id"] for e in graph_edges) | set(e["target_id"] for e in graph_edges)),
        }
    
    # 8. تركيب السياق النهائي
    context_parts = []
    
    # الهوية أولاً
    if identity and identity.get("traits"):
        context_parts.append(f"هوية المستخدم: {identity.get('self_view', '')} | صفاته: {', '.join(identity.get('traits', []))}")
    if identity and identity.get("family_role"):
        context_parts.append(f"دوره العائلي: {identity.get('family_role')}")
    if identity and identity.get("cultural_conflicts"):
        context_parts.append(f"صراعاته: {'; '.join(identity.get('cultural_conflicts', []))}")
    
    # العلاقة
    if relationship:
        context_parts.append(f"علاقته بالتوأم: ثقة {relationship.get('trust_level', 0)}% | توجه {relationship.get('trend', 'مستقر')}")
    
    # الشبكة الاجتماعية
    if person_network:
        important = [p["name"] for p in person_network[:5]]
        context_parts.append(f"شبكته الاجتماعية: {', '.join(important)}")
    
    # الأنماط العاطفية
    if emotional_patterns.get("patterns"):
        context_parts.append(f"أنماطه العاطفية: {'; '.join(emotional_patterns['patterns'])}")
    context_parts.append(f"عاطفته المسيطرة: {emotional_patterns.get('dominant_emotion', 'محايد')}")
    
    # الاستنتاجات
    if insights.get("insights"):
        top_insights = [i["text"] for i in insights["insights"][:5]]
        context_parts.append(f"استنتاجات عنه: {'; '.join(top_insights)}")
    
    # الأرشيف الحديث
    if recent:
        context_parts.append("<RECENT>")
        for msg in recent[:3]:
            role = "المستخدم" if msg.get("role") == "user" else "التوأم"
            context_parts.append(f"- [{role}]: {msg.get('content', '')[:100]}")
        context_parts.append("</RECENT>")
    
    # الرسم البياني
    if graph_context:
        context_parts.append(f"شبكة الذكريات: {graph_context['connected_memories']} عقدة | {graph_context['active_edges']} رابط")
    
    return {
        "context": "\n".join(context_parts),
        "emotional_dominant": emotional_patterns.get("dominant_emotion", "neutral"),
        "relationship_trend": relationship.get("trend", "stable"),
        "identity_traits": identity.get("traits", []),
        "important_people": [p["name"] for p in person_network[:5]] if person_network else [],
        "insights_count": len(insights.get("insights", [])),
        "recent_messages": len(recent),
        "graph_active": bool(graph_context),
    }

logger.info("✅ Memory Retriever Part 1 loaded")

# ============================================================
# الجزء 2: دوال مساعدة للمنسق
# ============================================================
async def retrieve_emotional_context(user_id: str) -> Dict[str, Any]:
    """سياق عاطفي سريع للمنسق."""
    patterns = await get_emotional_patterns(user_id, days=7)
    return {
        "dominant_emotion": patterns.get("dominant_emotion", "neutral"),
        "patterns": patterns.get("patterns", []),
        "recommendation": patterns.get("recommendation", ""),
    }

async def retrieve_social_context(user_id: str) -> Dict[str, Any]:
    """سياق اجتماعي سريع للمنسق."""
    network = await get_person_network(user_id, min_importance=20)
    relationship = await get_relationship_insights(user_id)
    return {
        "important_people": [p["name"] for p in network[:5]],
        "family_focus": any(p.get("relationship_type") == "family" for p in network),
        "trust_level": relationship.get("trust_level", 50),
        "trend": relationship.get("trend", "stable"),
    }

async def retrieve_identity_context(user_id: str) -> Dict[str, Any]:
    """سياق هوية سريع للمنسق."""
    identity = await get_identity(user_id)
    insights = await get_user_insights(user_id, min_confidence=0.7)
    return {
        "self_view": identity.get("self_view", "غير معروف"),
        "traits": identity.get("traits", []),
        "conflicts": identity.get("cultural_conflicts", []),
        "core_values": identity.get("core_values", []),
        "top_insights": [i["text"] for i in insights.get("insights", [])[:3]],
    }

async def retrieve_full_context(
    user_id: str,
    query: str,
    recent_memory_ids: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    الدالة الشاملة. تستدعي كل السياقات وتدمجها.
    هذه هي الدالة التي يستخدمها المنسق مباشرة.
    """
    context = await retrieve_context(user_id, query, recent_memory_ids=recent_memory_ids)
    emotional = await retrieve_emotional_context(user_id)
    social = await retrieve_social_context(user_id)
    identity_ctx = await retrieve_identity_context(user_id)
    
    return {
        "context_text": context["context"],
        "emotional": emotional,
        "social": social,
        "identity": identity_ctx,
        "meta": {
            "recent_messages": context["recent_messages"],
            "insights_count": context["insights_count"],
            "graph_active": context["graph_active"],
        },
    }

logger.info("✅ Memory Retriever Engine initialized (full)")
