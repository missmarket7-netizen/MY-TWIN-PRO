"""
Relationship API - حالة العلاقة والتعلق
=========================================
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

router = APIRouter(prefix="/api/relationship", tags=["relationship"])

@router.get("/state")
async def get_relationship_state(user_id: str = Query(...)) -> Dict[str, Any]:
    try:
        from app.memory.relationship.relationship_memory import get_relationship_context_for_response
        context = await get_relationship_context_for_response(user_id, "")
        return {"status": "success", "data": context}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/attachment")
async def get_attachment_style(user_id: str = Query(...)) -> Dict[str, Any]:
    try:
        from app.memory.relationship.attachment_model import detect_attachment_style
        style = await detect_attachment_style(user_id)
        return {"status": "success", "data": style}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
