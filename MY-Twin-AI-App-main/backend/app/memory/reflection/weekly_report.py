"""
Weekly Reflection Report – Layer 8 Extension
=============================================
يولد تقريراً تأملياً أسبوعياً عن المستخدم.
هذا هو "وعي" التوأم: أن يراقب ويتأمل ويخبر المستخدم بما يراه.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("weekly_report")

# ============================================================
# توليد التقرير الأسبوعي
# ============================================================
async def generate_weekly_report(user_id: str) -> Dict[str, Any]:
    """
    يحلل آخر 7 أيام ويولد تقريراً تأملياً.
    """
    db = get_db()
    
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        
        # 1. جمع العواطف
        emotions = (
            db.table("emotional_memory")
            .select("real_emotion,trigger,created_at")
            .eq("user_id", user_id)
            .gte("created_at", cutoff)
            .order("created_at", desc=True)
            .execute()
        )
        
        # 2. جمع الاستنتاجات الجديدة
        reflections = (
            db.table("reflection_insights")
            .select("insight_text,insight_type,confidence")
            .eq("user_id", user_id)
            .gte("last_observed", cutoff)
            .order("confidence", desc=True)
            .execute()
        )
        
        # 3. جمع الأشخاص المذكورين
        persons = (
            db.table("person_nodes")
            .select("name,importance_score,emotional_associations")
            .eq("user_id", user_id)
            .order("importance_score", desc=True)
            .limit(5)
            .execute()
        )
        
        # 4. تحليل البيانات
        emotion_data = emotions.data or []
        reflection_data = reflections.data or []
        person_data = persons.data or []
        
        # العاطفة المسيطرة هذا الأسبوع
        emotion_counts = {}
        for e in emotion_data:
            em = e.get("real_emotion", "neutral")
            emotion_counts[em] = emotion_counts.get(em, 0) + 1
        dominant = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "محايد"
        
        # الاستنتاجات الجديدة
        new_insights = [r["insight_text"] for r in reflection_data[:3]]
        
        # أشخاص بارزون
        important_people = []
        for p in person_data:
            emo_assoc = p.get("emotional_associations", [])
            if emo_assoc:
                top_emo = max(emo_assoc, key=lambda x: x.get("count", 0))
                important_people.append(f"{p['name']} (غالباً {top_emo['emotion']})")
            else:
                important_people.append(p["name"])
        
        # 5. بناء التقرير
        report_parts = []
        report_parts.append(f"🗓️ تقرير الأسبوع | {datetime.now().strftime('%d/%m/%Y')}")
        report_parts.append("")
        report_parts.append(f"📊 العاطفة المسيطرة: {dominant}")
        report_parts.append(f"📈 عدد التفاعلات العاطفية: {len(emotion_data)}")
        
        if new_insights:
            report_parts.append("")
            report_parts.append("💡 ما لاحظته عنك هذا الأسبوع:")
            for ins in new_insights:
                report_parts.append(f"   • {ins}")
        
        if important_people:
            report_parts.append("")
            report_parts.append("👤 الأشخاص الأبرز:")
            for p in important_people:
                report_parts.append(f"   • {p}")
        
        if dominant in ["sadness", "fear"]:
            report_parts.append("")
            report_parts.append("💜 ملاحظة: لاحظت أن هذا الأسبوع كان صعباً. أنا هنا من أجلك.")
        elif dominant in ["joy"]:
            report_parts.append("")
            report_parts.append("🌟 هذا الأسبوع كان إيجابياً! استمر في هذا الزخم.")
        
        report_text = "\n".join(report_parts)
        
        return {
            "report_text": report_text,
            "dominant_emotion": dominant,
            "interaction_count": len(emotion_data),
            "new_insights": new_insights,
            "important_people": important_people,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        
    except Exception as e:
        logger.error(f"فشل توليد التقرير الأسبوعي: {e}")
        return {"report_text": "تعذر توليد التقرير", "dominant_emotion": "neutral"}


logger.info("✅ Weekly Report Engine initialized")
