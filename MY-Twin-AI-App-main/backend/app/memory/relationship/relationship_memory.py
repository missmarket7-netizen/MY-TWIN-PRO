"""
Relationship Memory with Attachment Model
==========================================
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db
from app.memory.relationship.person_node import get_person_network, process_message_for_persons
from app.memory.relationship.attachment_model import detect_attachment_style

logger = logging.getLogger("relationship_memory")
TABLE_NAME = "relationship_memory"

async def store_relationship_snapshot(
    user_id: str, dimensions: Dict[str, float], stage: str,
    close_circle: Optional[List[Dict[str, Any]]] = None,
    sensitive_topics: Optional[List[str]] = None,
) -> str:
    db = get_db()
    try:
        payload = {
            "user_id": user_id, "trust": dimensions.get("trust", 0),
            "openness": dimensions.get("openness", 0),
            "attachment": dimensions.get("attachment", 0),
            "comfort": dimensions.get("comfort", 0),
            "relationship_stage": stage,
            "close_circle": close_circle or [],
            "sensitive_topics": sensitive_topics or [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        res = db.table(TABLE_NAME).insert(payload).execute()
        return res.data[0]["id"] if res.data else ""
    except Exception as e:
        logger.error(f"فشل تخزين اللقطة: {e}")
        return ""

async def get_relationship_insights(user_id: str) -> Dict[str, Any]:
    db = get_db()
    try:
        res = db.table(TABLE_NAME).select("*").eq("user_id", user_id).order("created_at", desc=True).limit(10).execute()
        if not res.data or len(res.data) < 2:
            return {"trend": "stable", "insight": "لا توجد بيانات كافية", "cultural_note": ""}
        first, last = res.data[0], res.data[-1]
        trust_change = first["trust"] - last["trust"]
        openness_change = first["openness"] - last["openness"]
        insights = []
        if trust_change > 10: insights.append("الثقة في نمو ملحوظ")
        if openness_change > 10: insights.append("المستخدم أصبح أكثر انفتاحاً")
        sensitive = first.get("sensitive_topics", [])
        if "المال / Money" in sensitive: insights.append("يحتاج حساسية عند الحديث عن المال")
        return {
            "trend": "improving" if trust_change > 0 else "declining",
            "trust_level": first["trust"], "openness_level": first["openness"],
            "insights": insights,
            "cultural_note": "العائلة قد تكون مفتاح الثقة" if "العائلة" in str(sensitive) else "",
        }
    except Exception as e:
        logger.error(f"فشل تحليل العلاقة: {e}")
        return {"trend": "stable", "insight": "خطأ في التحليل"}

async def analyze_social_context(
    user_id: str, current_message: str, detected_emotion: Optional[str] = None,
) -> Dict[str, Any]:
    mentioned = await process_message_for_persons(user_id, current_message, detected_emotion)
    network = await get_person_network(user_id, min_importance=20)
    family = [p for p in network if p.get("relationship_type") == "family"]
    top = sorted(network, key=lambda x: x.get("importance_score", 0), reverse=True)[:5]
    rec = ""
    if family: rec = f"العائلة مهمة: {', '.join(p['name'] for p in family[:3])}"
    if mentioned: rec += f" | ذُكر الآن: {', '.join(p['name'] for p in mentioned)}"
    return {
        "mentioned_in_message": mentioned,
        "top_people": top,
        "family_members": family,
        "network_size": len(network),
        "recommendation": rec or "لا يوجد سياق اجتماعي محدد",
    }

async def get_relationship_context_for_response(
    user_id: str, current_message: str, detected_emotion: Optional[str] = None,
) -> Dict[str, Any]:
    rel_insights = await get_relationship_insights(user_id)
    social = await analyze_social_context(user_id, current_message, detected_emotion)
    attachment = await detect_attachment_style(user_id)
    return {
        "relationship": {
            "trust": rel_insights.get("trust_level", 50),
            "openness": rel_insights.get("openness_level", 50),
            "trend": rel_insights.get("trend", "stable"),
            "insights": rel_insights.get("insights", []),
        },
        "social": {
            "mentioned_people": social["mentioned_in_message"],
            "important_people": [p["name"] for p in social["top_people"][:3]],
            "family_focus": len(social["family_members"]) > 2,
        },
        "attachment": attachment,
        "recommendation": rel_insights.get("cultural_note", "") + " | " + social.get("recommendation", ""),
    }

logger.info("✅ Relationship Memory with Attachment initialized")
