from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
router = APIRouter(prefix="/api/code-lab", tags=["code-lab"])

class ProjectRequest(BaseModel): user_id: str; name: str; project_type: str = "fastapi"
class CodeRequest(BaseModel): user_id: str; prompt: str; lang: str = "Python"
class DebugRequest(BaseModel): user_id: str; error: str; lang: str = "Python"
class ReviewRequest(BaseModel): user_id: str; code: str; lang: str = "Python"
class FullStackRequest(BaseModel): user_id: str; idea: str
class UIRequest(BaseModel): user_id: str; component_type: str; description: str; business_name: str = ""

@router.post("/start")
async def start(req: ProjectRequest):
    from app.features.code_lab.sdlc_orchestrator import code_lab
    return await code_lab.start_project(req.user_id, req.name, req.project_type)

@router.post("/generate-code")
async def generate_code(req: CodeRequest):
    from app.features.code_lab.sdlc_orchestrator import code_lab
    return await code_lab.generate_code(req.user_id, req.prompt, req.lang)

@router.post("/debug")
async def debug(req: DebugRequest):
    from app.features.code_lab.sdlc_orchestrator import code_lab
    return await code_lab.debug(req.user_id, req.error, req.lang)

@router.post("/review")
async def review(req: ReviewRequest):
    from app.features.code_lab.sdlc_orchestrator import code_lab
    return await code_lab.review(req.user_id, req.code, req.lang)

@router.post("/full-project")
async def full_project(req: FullStackRequest):
    from app.features.code_lab.sdlc_orchestrator import code_lab
    return await code_lab.generate_full_project(req.user_id, req.idea)

@router.post("/generate-ui")
async def generate_ui(req: UIRequest):
    from app.features.code_lab.sdlc_orchestrator import code_lab
    return await code_lab.generate_ui(req.user_id, req.component_type, req.description, req.business_name)
