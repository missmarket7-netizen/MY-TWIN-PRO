from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
router = APIRouter(prefix="/api/pass", tags=["pass"])

class TaskRequest(BaseModel):
    user_id: str; title: str; due_date: str = ""; priority: str = "medium"
    category: str = "personal"; notes: str = ""

class EventRequest(BaseModel):
    user_id: str; title: str; event_date: str; event_time: str = ""
    event_type: str = "meeting"; location: str = ""

# مهام
@router.post("/task")
async def create_task(req: TaskRequest):
    from app.features.task_manager.pass_orchestrator import pass_assistant
    return await pass_assistant.create_task(req.user_id, req.title, req.due_date, req.priority, req.category, req.notes)

@router.get("/tasks")
async def list_tasks(user_id: str = Query(...), status: str = "all"):
    from app.features.task_manager.pass_orchestrator import pass_assistant
    return await pass_assistant.list_tasks(user_id, status)

@router.post("/task/complete")
async def complete_task(user_id: str = Query(...), task_id: str = Query(...)):
    from app.features.task_manager.pass_orchestrator import pass_assistant
    return await pass_assistant.complete_task(user_id, task_id)

# تقويم
@router.post("/calendar")
async def add_event(req: EventRequest):
    from app.features.task_manager.pass_orchestrator import pass_assistant
    return await pass_assistant.add_calendar_event(req.user_id, req.title, req.event_date, req.event_time, req.event_type, req.location)

@router.get("/calendar/upcoming")
async def upcoming_events(user_id: str = Query(...), days: int = 7):
    from app.features.task_manager.pass_orchestrator import pass_assistant
    return await pass_assistant.get_upcoming_events(user_id, days)

# خدمات خارجية
@router.get("/weather")
async def weather(city: str = "Cairo", lang: str = "ar"):
    from app.features.task_manager.external_services import get_weather
    return await get_weather(city, lang)

@router.get("/news")
async def news(country: str = "sa", lang: str = "ar"):
    from app.features.task_manager.external_services import get_news
    return await get_news(country, lang)

@router.get("/currency")
async def currency(base: str = "USD", symbols: str = "SAR,EGP,EUR"):
    from app.features.task_manager.external_services import get_currency
    return await get_currency(base, symbols)

@router.get("/search")
async def search(query: str = Query(...), lang: str = "ar"):
    from app.features.task_manager.external_services import search_web
    return await search_web(query, lang)

@router.get("/deep-search")
async def deep_search(query: str = Query(...), lang: str = "ar"):
    from app.features.task_manager.external_services import deep_search
    return await deep_search(query, lang)

# لوحة المعلومات الشاملة
@router.get("/dashboard")
async def dashboard(user_id: str = Query(...)):
    from app.features.task_manager.pass_orchestrator import pass_assistant
    return await pass_assistant.get_dashboard(user_id)

@router.get("/google-calendar")
async def google_calendar(user_id: str = Query(...)):
    from app.features.task_manager.pass_orchestrator import pass_assistant
    return await pass_assistant.get_google_calendar_events(user_id)
