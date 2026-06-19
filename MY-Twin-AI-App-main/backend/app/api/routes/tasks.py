"""Task & Calendar Routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api", tags=["tasks"])

class CreateTaskBody(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    due_date: Optional[str] = None
    priority: int = Field(1, ge=1, le=5)
    category: str = Field("general")

class UpdateTaskBody(BaseModel):
    title: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    category: Optional[str] = None

@router.get("/tasks")
async def get_tasks(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("tasks").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/tasks")
async def create_task(body: CreateTaskBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        task = {
            "user_id": user_id,
            "title": body.title,
            "due_date": body.due_date,
            "priority": body.priority,
            "category": body.category,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        r = db.table("tasks").insert(task).execute()
        return r.data[0] if r.data else {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put("/tasks/{task_id}")
async def update_task(task_id: str, body: UpdateTaskBody, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    update_data = {}
    if body.title is not None:
        update_data["title"] = body.title
    if body.due_date is not None:
        update_data["due_date"] = body.due_date
    if body.priority is not None:
        update_data["priority"] = body.priority
    if body.status is not None:
        update_data["status"] = body.status
    if body.category is not None:
        update_data["category"] = body.category
    if update_data:
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        try:
            db.table("tasks").update(update_data).eq("id", task_id).eq("user_id", user_id).execute()
        except Exception as e:
            raise HTTPException(500, str(e))
    return {"status": "ok"}

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        db.table("tasks").delete().eq("id", task_id).eq("user_id", user_id).execute()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/calendar")
async def get_calendar_events(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("tasks").select("*").eq("user_id", user_id).not_.is_("due_date", "null").order("due_date", asc=True).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/tasks/today")
async def get_today_tasks(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    today = datetime.now(timezone.utc).date().isoformat()
    try:
        r = db.table("tasks").select("*").eq("user_id", user_id).eq("due_date", today).order("priority", desc=True).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/tasks/upcoming")
async def get_upcoming_tasks(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    today = datetime.now(timezone.utc).date().isoformat()
    end = (datetime.now(timezone.utc) + timedelta(days=7)).date().isoformat()
    try:
        r = db.table("tasks").select("*").eq("user_id", user_id).gte("due_date", today).lte("due_date", end).order("due_date", asc=True).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))
