from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
router = APIRouter(prefix="/api/smart-home", tags=["smart-home"])

class CommandRequest(BaseModel):
    user_id: str
    command: str
    lang: str = "ar"

@router.post("/command")
async def process_command(req: CommandRequest):
    try:
        from app.features.smart_home.smart_home_orchestrator import smart_home
        return await smart_home.process_command(req.user_id, req.command, req.lang)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status(user_id: str = Query(...)):
    try:
        from app.features.smart_home.smart_home_orchestrator import smart_home
        return await smart_home.get_status(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
