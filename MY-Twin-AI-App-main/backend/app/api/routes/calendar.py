"""Google Calendar Routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import httpx
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api/calendar", tags=["calendar"])

class CalendarEvent(BaseModel):
    id: str
    title: str
    start: str
    end: Optional[str] = None
    description: Optional[str] = None

@router.get("/google")
async def get_google_calendar(user_id: str = Depends(get_current_user_id)):
    """جلب أحداث Google Calendar للمستخدم."""
    db = get_db()
    try:
        profile = db.table("profiles").select("calendar_token").eq("id", user_id).single().execute()
        if not profile.data or not profile.data.get("calendar_token"):
            return {"events": [], "connected": False}
        
        token = profile.data["calendar_token"]
        now = datetime.now(timezone.utc).isoformat()
        end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={"Authorization": f"Bearer {token}"},
                params={"timeMin": now, "timeMax": end, "maxResults": 10, "singleEvents": True, "orderBy": "startTime"},
            )
            if resp.status_code == 200:
                events = resp.json().get("items", [])
                return {
                    "events": [
                        {
                            "id": e.get("id"),
                            "title": e.get("summary", ""),
                            "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")),
                            "end": e.get("end", {}).get("dateTime", ""),
                            "description": e.get("description", ""),
                        }
                        for e in events
                    ],
                    "connected": True,
                }
        return {"events": [], "connected": False}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/all")
async def get_all_events(user_id: str = Depends(get_current_user_id)):
    """جلب كل الأحداث (مهام + Google Calendar)."""
    db = get_db()
    events = []
    
    # جلب المهام المحلية
    try:
        tasks = db.table("tasks").select("*").eq("user_id", user_id).not_.is_("due_date", "null").order("due_date", asc=True).execute()
        for t in (tasks.data or []):
            events.append({
                "id": t["id"],
                "title": t["title"],
                "start": t["due_date"],
                "type": "task",
                "status": t.get("status", "pending"),
                "priority": t.get("priority", 3),
            })
    except:
        pass
    
    # جلب أحداث Google (إن وجدت)
    try:
        profile = db.table("profiles").select("calendar_token").eq("id", user_id).single().execute()
        if profile.data and profile.data.get("calendar_token"):
            token = profile.data["calendar_token"]
            now = datetime.now(timezone.utc).isoformat()
            end = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"timeMin": now, "timeMax": end, "maxResults": 10, "singleEvents": True, "orderBy": "startTime"},
                )
                if resp.status_code == 200:
                    for e in resp.json().get("items", []):
                        events.append({
                            "id": e.get("id"),
                            "title": e.get("summary", ""),
                            "start": e.get("start", {}).get("dateTime", e.get("start", {}).get("date", "")),
                            "type": "google_calendar",
                            "status": "confirmed",
                            "priority": 3,
                        })
    except:
        pass
    
    events.sort(key=lambda x: x.get("start", ""))
    return {"events": events}
