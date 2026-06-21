"""
Graph Routes - تحليل الرسم البياني للذاكرة
===========================================
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any

router = APIRouter(prefix="/api/graph", tags=["graph"])

@router.post("/mine-patterns")
async def mine_patterns(user_id: str = Query(...)) -> Dict[str, Any]:
    """استخراج أنماط من ذاكرة المستخدم"""
    try:
        from app.memory.graph.graph_pattern_miner import mine_patterns
        patterns = await mine_patterns(user_id)
        return {"status": "success", "patterns": patterns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compress")
async def compress(user_id: str = Query(...)) -> Dict[str, Any]:
    """ضغط الرسم البياني للذاكرة"""
    try:
        from app.memory.graph.graph_pattern_miner import compress_graph
        result = await compress_graph(user_id)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
