"""Feature Routes – with tier verification."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
from app.domain.services.tier_service import get_tier_config, get_feature_limit
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api/features", tags=["features"])

class StudyBody(BaseModel):
    topic: str = Field(..., min_length=3, max_length=2000)
    level: str = Field("intermediate")
    type: str = Field("explain")
    lang: str = Field("ar")

class ContentBody(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500)
    platform: str = Field("instagram")
    tone: str = Field("professional")
    lang: str = Field("ar")

class BusinessBody(BaseModel):
    text: str = Field(..., min_length=10, max_length=5000)
    analysis_type: str = Field("general")
    lang: str = Field("ar")

class CodeBody(BaseModel):
    task: str = Field(..., min_length=5, max_length=2000)
    language: str = Field("python")
    action: str = Field("write")
    lang: str = Field("ar")

class ImageBody(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)

async def get_user_tier(user_id: str) -> str:
    db = get_db()
    try:
        r = db.table("profiles").select("tier").eq("id", user_id).single().execute()
        return r.data.get("tier", "free") if r.data else "free"
    except:
        return "free"

async def check_feature_access(user_id: str, feature: str) -> str:
    tier = await get_user_tier(user_id)
    limit = get_feature_limit(tier, feature)
    if limit <= 0:
        raise HTTPException(403, "Feature not available on your plan")
    return tier

@router.post("/study")
async def study_mode(body: StudyBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "study")
    prompt = f"""أنت معلم خبير. مستوى الطالب: {body.level}. المهمة: {body.type} حول: {body.topic}. اللغة: {body.lang}."""
    try:
        reply, _ = await provider_router.route(prompt, task="coaching", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/content")
async def content_creation(body: ContentBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "content")
    guides = {"instagram": "منشور مع هاشتاغات", "twitter": "تغريدة 280 حرف", "linkedin": "منشور احترافي", "youtube": "وصف فيديو", "tiktok": "نص قصير"}
    prompt = f"""كاتب محتوى. المنصة: {body.platform}. النبرة: {body.tone}. {guides.get(body.platform, '')} الموضوع: {body.topic}. اللغة: {body.lang}."""
    try:
        reply, _ = await provider_router.route(prompt, task="general", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/business")
async def business_analysis(body: BusinessBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "business")
    guides = {"general": "حلل وأعطِ رؤى", "financial": "حلل الجوانب المالية", "marketing": "حلل التسويق", "strategy": "حلل الاستراتيجية"}
    prompt = f"""محلل أعمال. {guides.get(body.analysis_type, '')} النص: {body.text}. اللغة: {body.lang}."""
    try:
        reply, _ = await provider_router.route(prompt, task="deep_reasoning", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/code")
async def code_lab(body: CodeBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "code")
    guides = {"write": f"اكتب كود {body.language} مع تعليقات", "review": f"راجع كود {body.language} وحسّن", "explain": f"اشرح كود {body.language}", "debug": f"أصلح أخطاء كود {body.language}"}
    prompt = f"""{guides.get(body.action, '')}. المهمة: {body.task}. اللغة: {body.lang}."""
    try:
        reply, _ = await provider_router.route(prompt, task="coding", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI unavailable")

@router.post("/dream")

async def analyze_dream(body: dict, user_id: str = Depends(get_current_user_id)):

    """تفسير الأحلام"""

    tier = await check_feature_access(user_id, "dreams")

    if not body.get("dream"):

        raise HTTPException(400, "Dream text is required")

    prompt = f"""أنت محلل أحلام خبير. فسر الحلم التالي وأعد ONLY JSON:

{{

  "interpretation": "تفسير الحلم (3-4 جمل)",

  "symbols": ["رمز1", "رمز2", "رمز3"],

  "emotions": ["مشاعر1", "مشاعر2", "مشاعر3"],

  "reflection_question": "سؤال تأملي واحد"

}}

الحلم: {body["dream"]}

اللغة: {body.get("lang", "ar")}"""

    try:

        import json, re

        reply, _ = await provider_router.route(prompt, task="deep_reasoning", tier=tier)

        # استخراج JSON من الرد

        match = re.search(r"{[^}]+}", reply)

        if match:

            return json.loads(match.group())

        return {"interpretation": reply}

    except AIUnavailable:

        raise HTTPException(503, "AI unavailable")
@router.post("/smart-home")

async def smart_home_control(body: dict, user_id: str = Depends(get_current_user_id)):

    """التحكم في المنزل الذكي"""

    tier = await check_feature_access(user_id, "smart_home")

    command = body.get("command", "")

    entity_id = body.get("entity_id", "")

    if not command:

        raise HTTPException(400, "Command is required")

    try:

        from app.features.smart_home import process_voice_command

        result = await process_voice_command(command, user_id, tier)

        return {"result": result}

    except Exception as e:

        raise HTTPException(500, str(e))
@router.post("/coach/weekly")

async def weekly_life_plan(body: dict, user_id: str = Depends(get_current_user_id)):

    """خطة أسبوعية من مدرب الحياة"""

    tier = await check_feature_access(user_id, "coaching")

    domain = body.get("domain", "psychological")

    domain_labels = {"psychological": "نفسي", "social": "اجتماعي", "professional": "عملي", "personal": "شخصي"}

    prompt = f"""أنت مدرب حياة محترف. ضع خطة أسبوعية كاملة (7 أيام) للمستخدم في المجال: {domain_labels.get(domain, domain)}.

لكل يوم: مهمة واحدة، تمرين واحد، وتأمل واحد.

اللغة: {body.get("lang", "ar")}"""

    try:

        reply, _ = await provider_router.route(prompt, task="coaching", tier=tier)

        return {"plan": reply}

    except AIUnavailable:

        raise HTTPException(503, "AI unavailable")
@router.post("/coach")

async def life_coach(body: dict, user_id: str = Depends(get_current_user_id)):

    tier = await check_feature_access(user_id, "coaching")

    prompt = f"أنت مدرب حياة محترف. المجال: {body.get("domain")}. الموضوع: {body.get("topic")}. اللغة: {body.get("lang", "ar")}."

    try:

        reply, _ = await provider_router.route(prompt, task="coaching", tier=tier)

        return {"reply": reply}

    except AIUnavailable:

        raise HTTPException(503, "AI unavailable")
@router.get("/images")

async def get_user_images(user_id: str = Depends(get_current_user_id)):

    """معرض صور المستخدم"""

    db = get_db()

    try:

        r = db.table("generated_images").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()

        return r.data or []

    except Exception as e:

        raise HTTPException(500, str(e))
@router.post("/image")

async def generate_and_store_image(body: ImageBody, user_id: str = Depends(get_current_user_id)):

    tier = await check_feature_access(user_id, "image")

    try:

        from google import genai; import os, base64

        key = os.getenv("GEMINI_API_KEY", "")

        if not key: raise HTTPException(503, "Image API not configured")

        client = genai.Client(api_key=key)

        response = client.models.generate_content(model="gemini-2.0-flash-exp-image-generation", contents=body.prompt)

        if response.parts and hasattr(response.parts[0], "inline_data"):

            image_data = response.parts[0].inline_data.data

            db = get_db()

            db.table("generated_images").insert({

                "user_id": user_id,

                "prompt": body.prompt,

                "image_base64": image_data,

                "created_at": "now()",

            }).execute()

            return {"image_base64": image_data}

        desc = client.models.generate_content(model="gemini-2.5-flash", contents=f"وصف بصري لـ: {body.prompt}")

        return {"description": desc.text}

    except Exception as e:

        raise HTTPException(500, str(e))
@router.post("/image")
async def generate_image(body: ImageBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "image")
    try:
        from google import genai; import os
        key = os.getenv("GEMINI_API_KEY", "")
        if not key: raise HTTPException(503, "Image API not configured")
        client = genai.Client(api_key=key)
        response = client.models.generate_content(model="gemini-2.0-flash-exp-image-generation", contents=body.prompt)
        if response.parts and hasattr(response.parts[0], 'inline_data'):
            return {"image_base64": response.parts[0].inline_data.data}
        desc = client.models.generate_content(model="gemini-2.5-flash", contents=f"وصف بصري لـ: {body.prompt}")
        return {"description": desc.text}
    except Exception as e:
        raise HTTPException(500, str(e))
