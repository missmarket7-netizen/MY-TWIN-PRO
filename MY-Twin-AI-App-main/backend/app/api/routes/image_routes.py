from fastapi import APIRouter, HTTPException, Query
router = APIRouter(prefix="/api/image-lab", tags=["image-lab"])

@router.post("/generate")
async def generate_image(
    user_id: str = Query(...),
    prompt: str = Query(...),
    style: str = "realistic",
    size: str = "1024x1024",
    provider: str = "stable_diffusion"
):
    try:
        from app.features.image_lab.image_orchestrator import image_lab
        return await image_lab.generate(user_id, prompt, style, size, provider)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/enhance-prompt")
async def enhance_prompt(user_id: str = Query(...), prompt: str = Query(...)):
    try:
        from app.features.image_lab.image_orchestrator import image_lab
        return {"enhanced": await image_lab.enhance_prompt(user_id, prompt)}
    except Exception as e:
        raise HTTPException(500, str(e))
