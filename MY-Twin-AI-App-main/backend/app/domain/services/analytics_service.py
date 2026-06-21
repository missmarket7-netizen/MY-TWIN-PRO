"""
Analytics Service v2.0 – تحليلات متقدمة (متكاملة مع TCMA)
=============================================================
- تحليل نمو المستخدمين
- مقاييس التفاعل (من TCMA)
- جودة المحادثة (من TCMA)
- تكامل مع Observability
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("analytics_service")

async def get_user_growth(days: int = 30) -> Dict[str, Any]:
    """تتبع نمو المستخدمين"""
    db = get_db()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        r = db.table("profiles").select("created_at").gte("created_at", cutoff).execute()
        if not r.data:
            return {"growth": [], "total": 0}
        
        by_date = {}
        for user in r.data:
            date = user["created_at"][:10] if user.get("created_at") else None
            if date:
                by_date[date] = by_date.get(date, 0) + 1
        
        growth = [{"date": d, "count": c} for d, c in sorted(by_date.items())]
        return {"growth": growth, "total": sum(c for _, c in growth)}
    except Exception as e:
        logger.error(f"فشل تحليل نمو المستخدمين: {e}")
        return {"growth": [], "total": 0}

async def get_engagement_metrics(user_id: str) -> Dict[str, Any]:
    """مقاييس التفاعل من TCMA"""
    metrics = {
        "total_messages": 0,
        "bond_level": 0,
        "dominant_mood": "neutral",
        "recent_moods": [],
        "active_days": 0,
    }
    
    try:
        # 1. عدد الرسائل من الأرشيف
        from app.memory.archive.raw_archive import get_conversation_archive
        archive = await get_conversation_archive(user_id, limit=1000)
        metrics["total_messages"] = len(archive)
        
        # 2. مستوى الرابطة من ذاكرة العلاقات
        try:
            from app.memory.relationship.relationship_memory import get_relationship_insights
            rel = await get_relationship_insights(user_id)
            metrics["bond_level"] = rel.get("trust_level", 0)
        except: pass
        
        # 3. المشاعر المسيطرة من الذاكرة العاطفية
        try:
            from app.memory.emotional.emotional_memory import get_emotional_patterns
            patterns = await get_emotional_patterns(user_id, days=30)
            metrics["dominant_mood"] = patterns.get("dominant_emotion", "neutral")
            # استخراج المشاعر الأخيرة
            distribution = patterns.get("emotion_distribution", {})
            metrics["recent_moods"] = [
                {"emotion": k, "percentage": v}
                for k, v in sorted(distribution.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
        except: pass
        
        # 4. أيام النشاط
        dates = set()
        for msg in archive:
            if msg.get("created_at"):
                dates.add(msg["created_at"][:10])
        metrics["active_days"] = len(dates)
        
    except Exception as e:
        logger.error(f"فشل تحليل التفاعل: {e}")
    
    return metrics

async def get_conversation_quality(user_id: str) -> Dict[str, Any]:
    """تحليل جودة المحادثة من TCMA"""
    quality = {"quality_score": 0, "avg_response_length": 0, "total_reflections": 0}
    
    try:
        # 1. عدد الاستنتاجات (Reflections) كمؤشر على عمق المحادثة
        from app.memory.reflection.reflection_engine import get_user_insights
        insights = await get_user_insights(user_id, min_confidence=0.5)
        quality["total_reflections"] = len(insights.get("insights", []))
        
        # 2. متوسط طول الردود من الأرشيف
        from app.memory.archive.raw_archive import get_conversation_archive
        archive = await get_conversation_archive(user_id, limit=100)
        twin_msgs = [m for m in archive if m.get("role") == "twin"]
        if twin_msgs:
            total_chars = sum(len(m.get("content", "")) for m in twin_msgs)
            quality["avg_response_length"] = round(total_chars / len(twin_msgs), 2)
        
        # 3. درجة الجودة (من الثقة في العلاقة)
        try:
            from app.memory.relationship.relationship_memory import get_relationship_insights
            rel = await get_relationship_insights(user_id)
            quality["quality_score"] = rel.get("trust_level", 0)
        except: pass
        
    except Exception as e:
        logger.error(f"فشل تحليل الجودة: {e}")
    
    return quality

logger.info("✅ Analytics Service v2.0 initialized (TCMA Integrated)")
