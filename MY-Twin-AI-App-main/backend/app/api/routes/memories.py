"""Memories Routes – with semantic search and context."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db
from app.memory.memory_retriever import retrieve_and_summarize
from app.memory.memory_service import get_memory_context

router = APIRouter(prefix="/api", tags=["memories"])

@router.get("/memories")
async def get_memories(
    user_id: str = Depends(get_current_user_id),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    memory_type: Optional[str] = None,
):
    db = get_db()
    try:
        query = db.table("memories").select("*").eq("user_id", user_id).order("created_at", desc=True)
        if memory_type:
            query = query.eq("memory_type", memory_type)
        query = query.range(offset, offset + limit - 1)
        r = query.execute()
        return {"memories": r.data or [], "total": len(r.data or []), "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/memories/context")
async def get_relevant_context(
    query: str = Query(..., min_length=1),
    user_id: str = Depends(get_current_user_id),
):
    """Get memory context relevant to a query."""
    context = await get_memory_context(user_id, query)
    return {"context": context}
