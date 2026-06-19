"""Feature Routes – Study, Content, Business, Code, Image, Dream, Coach, Smart Home."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.ai.provider_router import provider_router, AIUnavailable
from app.domain.services.tier_service import get_tier_config, get_feature_limit
from app.infrastructure.database.supabase_client import get_db

router = APIRouter(prefix="/api/features", tags=["features"])

# ========== نماذج البيانات ==========

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

class CoachBody(BaseModel):
    topic: str = Field(..., min_length=3, max_length=1000)
    domain: str = Field("personal")
    lang: str = Field("ar")

class DreamBody(BaseModel):
    dream: str = Field(..., min_length=10, max_length=3000)
    lang: str = Field("ar")

class ImageBody(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=500)

class SmartHomeBody(BaseModel):
    command: str = Field(..., min_length=2, max_length=500)
    entity_id: Optional[str] = None

class WeeklyPlanBody(BaseModel):
    domain: str = Field("personal")
    lang: str = Field("ar")

# ========== دوال مساعدة ==========

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
        raise HTTPException(403, f"Feature '{feature}' not available on your plan")
    return tier

# ========== نقاط النهاية ==========

@router.post("/study")
async def study_mode(body: StudyBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "study")
    if body.type == "explain":
        prompt = "اشرح الموضوع التالي بطريقة مبسطة مع أمثلة."
    elif body.type == "summarize":
        prompt = "لخص الموضوع التالي بأسلوب واضح ومختصر."
    elif body.type == "solve":
        prompt = "حل المسألة التالية خطوة بخطوة."
    else:
        prompt = "ضع خطة دراسية منظمة للموضوع التالي."
    full_prompt = f"{prompt}\nالموضوع: {body.topic}\nالمستوى: {body.level}\nاللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(full_prompt, task="coaching", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI service unavailable")

@router.post("/content")
async def content_creation(body: ContentBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "content")
    guides = {
        "instagram": "اكتب منشوراً جذاباً مع هاشتاغات مناسبة.",
        "twitter": "اكتب تغريدة مختصرة وقوية في 280 حرفاً.",
        "linkedin": "اكتب منشوراً احترافياً بأسلوب عمل.",
        "youtube": "اكتب وصف فيديو مشوق مع كلمات مفتاحية.",
        "tiktok": "اكتب نصاً قصيراً وسريعاً لجذب الانتباه.",
    }
    guide = guides.get(body.platform, "")
    full_prompt = f"أنت كاتب محتوى محترف. المنصة: {body.platform}. النبرة: {body.tone}. {guide}\nالموضوع: {body.topic}\nاللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(full_prompt, task="general", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI service unavailable")

@router.post("/business")
async def business_analysis(body: BusinessBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "business")
    guides = {
        "general": "حلل النص التالي وأعطِ رؤى عملية.",
        "financial": "حلل الجوانب المالية والأرقام في النص.",
        "marketing": "حلل استراتيجية التسويق في النص.",
        "strategy": "حلل الاستراتيجية العامة وقدم توصيات.",
    }
    guide = guides.get(body.analysis_type, "")
    full_prompt = f"أنت محلل أعمال خبير. {guide}\nالنص: {body.text}\nاللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(full_prompt, task="deep_reasoning", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI service unavailable")

@router.post("/code")
async def code_lab(body: CodeBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "code")
    if body.action == "write":
        prompt = "اكتب كود {} كاملاً ونظيفاً للمهمة التالية. أضف تعليقات توضيحية.".format(body.language)
    elif body.action == "review":
        prompt = "راجع الكود التالي بلغة {} واقترح تحسينات.".format(body.language)
    elif body.action == "explain":
        prompt = "اشرح الكود التالي بلغة {} خطوة بخطوة.".format(body.language)
    else:
        prompt = "اكتشف الأخطاء في الكود التالي بلغة {} وأصلحها.".format(body.language)
    full_prompt = f"{prompt}\nالمهمة: {body.task}\nاللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(full_prompt, task="coding", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI service unavailable")

@router.post("/coach")
async def life_coach(body: CoachBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "coach")
    domain_labels = {
        "psychological": "نفسي",
        "social": "اجتماعي", 
        "professional": "عملي",
        "personal": "شخصي"
    }
    domain_name = domain_labels.get(body.domain, body.domain)
    full_prompt = f"أنت مدرب حياة محترف. المجال: {domain_name}. الموضوع: {body.topic}. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(full_prompt, task="coaching", tier=tier)
        return {"reply": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI service unavailable")

@router.post("/coach/weekly")
async def weekly_life_plan(body: WeeklyPlanBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "coach")
    domain_labels = {
        "psychological": "نفسي",
        "social": "اجتماعي",
        "professional": "عملي",
        "personal": "شخصي"
    }
    domain_name = domain_labels.get(body.domain, body.domain)
    full_prompt = f"أنت مدرب حياة محترف. ضع خطة أسبوعية كاملة (7 أيام) للمستخدم في المجال: {domain_name}. لكل يوم: مهمة واحدة، تمرين واحد، وتأمل واحد. اللغة: {body.lang}"
    try:
        reply, _ = await provider_router.route(full_prompt, task="coaching", tier=tier)
        return {"plan": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI service unavailable")

@router.post("/dream")
async def analyze_dream(body: DreamBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "dreams")
    full_prompt = f"أنت محلل أحلام خبير. فسر الحلم التالي وأعد ONLY JSON: {{\"interpretation\": \"تفسير الحلم (3-4 جمل)\", \"symbols\": [\"رمز1\", \"رمز2\", \"رمز3\"], \"emotions\": [\"مشاعر1\", \"مشاعر2\", \"مشاعر3\"], \"reflection_question\": \"سؤال تأملي واحد\"}}\nالحلم: {body.dream}\nاللغة: {body.lang}"
    try:
        import json, re
        reply, _ = await provider_router.route(full_prompt, task="deep_reasoning", tier=tier)
        match = re.search(r"\{[^}]+\}", reply)
        if match:
            return json.loads(match.group())
        return {"interpretation": reply}
    except AIUnavailable:
        raise HTTPException(503, "AI service unavailable")

@router.post("/image")
async def generate_image(body: ImageBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "image")
    try:
        from google import genai
        import os
        key = os.getenv("GEMINI_API_KEY", "")
        if not key:
            raise HTTPException(503, "Image API not configured")
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=body.prompt,
        )
        if response.parts and hasattr(response.parts[0], 'inline_data'):
            return {"image_base64": response.parts[0].inline_data.data}
        desc_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"وصف بصري لـ: {body.prompt}",
        )
        return {"description": desc_response.text}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/smart-home")
async def smart_home_control(body: SmartHomeBody, user_id: str = Depends(get_current_user_id)):
    tier = await check_feature_access(user_id, "smart_home")
    try:
        from app.features.smart_home import process_voice_command
        result = await process_voice_command(body.command, user_id, tier)
        return {"result": result}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/images")
async def get_user_images(user_id: str = Depends(get_current_user_id)):
    db = get_db()
    try:
        r = db.table("generated_images").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
        return r.data or []
    except Exception as e:
        raise HTTPException(500, str(e))
