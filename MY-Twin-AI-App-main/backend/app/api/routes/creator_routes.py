from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
router = APIRouter(prefix="/api/creator", tags=["creator"])

class OutlineRequest(BaseModel):
    user_id: str; title: str; type: str = "novel"; genre: str = ""
    language: str = "ar"; theory: str = ""; format_type: str = ""

class WriteRequest(BaseModel):
    user_id: str; part: str = "الفصل 1"; instructions: str = ""

class PolyglotRequest(BaseModel):
    text: str; source_lang: str = "ar"; target_lang: str = "en"; style: str = "bullet"

class BookRequest(BaseModel):
    user_id: str; title: str; chapters_count: int = 10; genre: str = ""
    language: str = "ar"; target_language: str = ""

class AdCopyRequest(BaseModel):
    user_id: str; product_name: str; product_features: str
    target_audience: str = ""; platform: str = "instagram"
    formula: str = "AIDA"; language: str = "ar"

@router.post("/outline")
async def outline(req: OutlineRequest):
    try:
        from app.features.creator.creator_orchestrator import creator
        return await creator.generate_outline(req.user_id, req.title, req.type, req.genre, req.language, req.theory, req.format_type)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/write")
async def write(req: WriteRequest):
    try:
        from app.features.creator.creator_orchestrator import creator
        return await creator.write_content(req.user_id, req.part, req.instructions)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/write-book")
async def write_book(req: BookRequest):
    try:
        from app.features.creator.creator_orchestrator import creator
        return await creator.write_full_book(req.user_id, req.title, req.chapters_count, req.genre, req.language, req.target_language)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/ad-copy")
async def ad_copy(req: AdCopyRequest):
    try:
        from app.features.creator.creator_orchestrator import creator
        return await creator.write_ad_copy(req.user_id, req.product_name, req.product_features, req.target_audience, req.platform, req.formula, req.language)
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/translate")
async def translate(req: PolyglotRequest):
    try:
        from app.features.creator.creator_orchestrator import creator
        return {"translation": await creator.polyglot.translate(req.text, req.source_lang, req.target_lang)}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/summarize")
async def summarize(req: PolyglotRequest):
    try:
        from app.features.creator.creator_orchestrator import creator
        return {"summary": await creator.polyglot.summarize(req.text, req.style, req.source_lang)}
    except Exception as e: raise HTTPException(500, str(e))
