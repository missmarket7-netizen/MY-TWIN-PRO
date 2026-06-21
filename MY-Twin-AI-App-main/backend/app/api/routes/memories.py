"""
Memories Routes v2.0 – متكاملة مع TCMA
=========================================
تستدعي جميع طبقات الذاكرة الجديدة.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.api.dependencies.auth import get_current_user_id

router = APIRouter(prefix="/api/memories", tags=["memories"])

@router.get("/")
async def get_memories(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    memory_type: Optional[str] = None,
):
    """يجلب الذكريات من الأرشيف الخام"""
    try:
        from app.infrastructure.database.supabase_client import get_db
        from app.memory.archive.raw_archive import get_conversation_archive
        
        db = get_db()
        memories = await get_conversation_archive(user_id, limit, offset)
        return {
            "memories": memories,
            "total": len(memories),
            "limit": limit,
            "offset": offset,
            "source": "raw_archive"
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/emotional")
async def get_emotional_memories(
    user_id: str = Depends(get_current_user_id),
    days: int = Query(30, ge=1, le=365),
):
    """يجلب الذكريات العاطفية وتحليل الأنماط"""
    try:
        from app.memory.emotional.emotional_memory import get_emotional_patterns
        
        patterns = await get_emotional_patterns(user_id, days)
        return {"source": "emotional_memory", "patterns": patterns}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/reflections")
async def get_reflections(
    user_id: str = Depends(get_current_user_id),
    min_confidence: float = Query(0.6, ge=0, le=1),
):
    """يجلب الاستنتاجات المتراكمة عن المستخدم"""
    try:
        from app.memory.reflection.reflection_engine import get_user_insights
        
        insights = await get_user_insights(user_id, min_confidence)
        return {"source": "reflection_engine", "insights": insights}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/graph")
async def get_graph_memories(
    user_id: str = Depends(get_current_user_id),
    memory_id: Optional[str] = Query(None),
    depth: int = Query(2, ge=1, le=5),
):
    """يجلب الذكريات المرتبطة من الرسم البياني"""
    try:
        from app.memory.graph.memory_graph import get_connected_memories
        
        if not memory_id:
            return {"error": "يجب تحديد memory_id"}
        
        edges = await get_connected_memories(user_id, memory_id, depth)
        return {"source": "memory_graph", "edges": edges, "depth": depth}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/context")
async def get_context(
    query: str = Query(..., min_length=1),
    user_id: str = Depends(get_current_user_id),
):
    """يجلب السياق الكامل من جميع طبقات الذاكرة"""
    try:
        from app.memory.retrieval.memory_retriever import retrieve_full_context
        
        context = await retrieve_full_context(user_id, query)
        return {"source": "all_tcma_layers", "context": context}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/identity")
async def get_identity_endpoint(
    user_id: str = Depends(get_current_user_id),
):
    """يجلب أحدث نموذج هوية للمستخدم"""
    try:
        from app.memory.identity.identity_model import get_identity
        
        identity = await get_identity(user_id)
        return {"source": "identity_model", "identity": identity}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/people")
async def get_people_network(
    user_id: str = Depends(get_current_user_id),
    min_importance: int = Query(20, ge=0, le=100),
):
    """يجلب شبكة الأشخاص المهمين في حياة المستخدم"""
    try:
        from app.memory.relationship.person_node import get_person_network
        
        network = await get_person_network(user_id, min_importance)
        return {"source": "person_node", "people": network}
    except Exception as e:
        raise HTTPException(500, str(e))
