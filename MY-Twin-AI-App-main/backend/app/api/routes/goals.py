"""
Goals Routes v3.0 – متكاملة مع TCMA و P.A.S.S.
====================================================
- أهداف ذكية مع تكامل الذاكرة العاطفية
- إحصائيات وتحليلات
- ربط مع نظام إدارة المهام (P.A.S.S.)
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("goals_routes")
router = APIRouter(prefix="/api/goals", tags=["goals"])

class AddGoalBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field("general")
    priority: int = Field(1, ge=1, le=5)
    deadline: Optional[str] = None

class UpdateGoalBody(BaseModel):
    title: Optional[str] = None
    progress: Optional[float] = None
    status: Optional[str] = None
    priority: Optional[int] = None

@router.get("/")
async def get_goals(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("goals").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/")
async def add_goal(body: AddGoalBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        goal_data = {
            "user_id": user_id, "title": body.title, "status": "active",
            "progress": 0, "category": body.category, "priority": body.priority,
            "deadline": body.deadline,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        r = db.table("goals").insert(goal_data).execute()
        
        # تسجيل في TCMA
        try:
            from app.memory.emotional.emotional_memory import store_emotional_memory
            await store_emotional_memory(
                user_id=user_id,
                expressed_text=f"هدف جديد: {body.title}",
                detected_emotion={"primary": "motivated", "intensity": 0.8, "valence": 0.7},
                trigger="goal_created"
            )
        except: pass
        
        # إرسال حدث
        try:
            from app.events.event_bus import emit
            await emit({
                "type": "goal_created",
                "user_id": user_id,
                "title": body.title,
            })
        except: pass
        
        return r.data[0] if r.data else {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put("/{goal_id}")
async def update_goal(goal_id: str, body: UpdateGoalBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    update_data = {}
    if body.title is not None: update_data["title"] = body.title
    if body.progress is not None: update_data["progress"] = body.progress
    if body.status is not None: update_data["status"] = body.status
    if body.priority is not None: update_data["priority"] = body.priority
    
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        db.table("goals").update(update_data).eq("id", goal_id).eq("user_id", user_id).execute()
        
        # إذا اكتمل الهدف
        if body.status == "completed":
            try:
                from app.memory.emotional.emotional_memory import store_emotional_memory
                from app.events.event_bus import emit
                
                goal = db.table("goals").select("title").eq("id", goal_id).single().execute()
                title = goal.data.get("title", "هدف") if goal.data else "هدف"
                
                await store_emotional_memory(
                    user_id=user_id,
                    expressed_text=f"أكملت هدف: {title}",
                    detected_emotion={"primary": "joy", "intensity": 0.9, "valence": 0.8},
                    trigger="goal_completed"
                )
                await emit({
                    "type": "goal_completed",
                    "user_id": user_id,
                    "goal_id": goal_id,
                    "title": title,
                })
            except: pass
    
    return {"status": "ok"}

@router.delete("/{goal_id}")
async def delete_goal(goal_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        db.table("goals").delete().eq("id", goal_id).eq("user_id", user_id).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/stats")
async def get_goal_stats(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("goals").select("status,progress,priority").eq("user_id", user_id).execute()
        if not r.data:
            return {"active": 0, "completed": 0, "avg_progress": 0}
        
        active = sum(1 for g in r.data if g.get("status") == "active")
        completed = sum(1 for g in r.data if g.get("status") == "completed")
        avg_progress = sum(g.get("progress", 0) for g in r.data) / len(r.data) if r.data else 0
        
        return {"active": active, "completed": completed, "avg_progress": round(avg_progress, 2)}
    except:
        return {"active": 0, "completed": 0, "avg_progress": 0}

logger.info("✅ Goals Routes v3.0 initialized")
