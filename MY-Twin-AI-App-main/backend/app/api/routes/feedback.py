"""
Feedback Routes v3.0 – متكاملة مع TCMA و Event Bus
========================================================
- حفظ التقييم (إعجاب / عدم إعجاب)
- تسجيل التقييم في الذاكرة العاطفية
- إرسال حدث إلى Event Bus للتحليل
- جلب سجل التقييمات
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from app.api.dependencies.auth import get_current_user_id
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("feedback_routes")
router = APIRouter(prefix="/api/feedback", tags=["feedback"])

class FeedbackRequest(BaseModel):
    rating: str = Field(..., pattern="^(like|dislike)$")
    message_id: Optional[str] = None
    comment: Optional[str] = Field(None, max_length=500)
    conversation_id: Optional[str] = None

@router.post("/send")
async def submit_feedback(
    body: FeedbackRequest,
    user_id: str = Depends(get_current_user_id),
):
    """إرسال تقييم (إعجاب / عدم إعجاب)"""
    db = get_db()
    try:
        # 1. حفظ التقييم في قاعدة البيانات
        feedback_data = {
            "user_id": user_id,
            "rating": body.rating,
            "message_id": body.message_id,
            "comment": body.comment,
            "conversation_id": body.conversation_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        db.table("message_feedback").insert(feedback_data).execute()

        # 2. تسجيل في الذاكرة العاطفية (TCMA)
        try:
            from app.memory.emotional.emotional_memory import store_emotional_memory
            emotion = "joy" if body.rating == "like" else "sadness"
            await store_emotional_memory(
                user_id=user_id,
                expressed_text=f"تقييم: {body.rating}" + (f" - {body.comment}" if body.comment else ""),
                detected_emotion={"primary": emotion, "intensity": 0.6, "valence": 0.5 if body.rating == "like" else -0.3},
                trigger="user_feedback"
            )
        except Exception as e:
            logger.warning(f"TCMA feedback failed: {e}")

        # 3. إرسال حدث إلى Event Bus
        try:
            from app.events.event_bus import emit
            await emit({
                "type": "feedback_received",
                "user_id": user_id,
                "rating": body.rating,
                "comment": body.comment,
            })
        except: pass

        return {
            "status": "success",
            "rating": body.rating,
            "message": "شكراً لتقييمك! 💜" if body.rating == "like" else "شكراً لملاحظتك، سأتحسن 💜"
        }

    except Exception as e:
        logger.error(f"Feedback failed: {e}")
        raise HTTPException(500, "فشل حفظ التقييم")

@router.get("/history")
async def get_feedback_history(
    user_id: str = Depends(get_current_user_id),
    limit: int = 20,
):
    """جلب سجل التقييمات"""
    db = get_db()
    try:
        result = db.table("message_feedback").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        
        # إحصائيات سريعة
        feedbacks = result.data or []
        likes = sum(1 for f in feedbacks if f.get("rating") == "like")
        dislikes = sum(1 for f in feedbacks if f.get("rating") == "dislike")
        total = len(feedbacks)
        
        return {
            "feedbacks": feedbacks,
            "stats": {
                "total": total,
                "likes": likes,
                "dislikes": dislikes,
                "satisfaction_rate": f"{(likes / total * 100):.0f}%" if total > 0 else "0%"
            }
        }
    except Exception as e:
        raise HTTPException(500, str(e))

logger.info("✅ Feedback Routes v3.0 initialized")
