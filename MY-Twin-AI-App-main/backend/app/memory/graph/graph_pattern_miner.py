"""
Graph Pattern Miner – Layer 11 Extension
==========================================
يقرأ الرسم البياني للذاكرة ويستخرج أنماطاً مخفية.
مثلاً: "عندما يتحدث عن المال، يغضب. لكن عندما يذكر أمه، يهدأ."
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from collections import Counter
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("graph_pattern_miner")

# ============================================================
# تنقيب الأنماط من الرسم البياني
# ============================================================
async def mine_patterns(
    user_id: str,
    days: int = 30,
    min_pattern_strength: int = 3,
) -> Dict[str, Any]:
    """
    يستخرج أنماطاً متكررة من الرسم البياني للذاكرة.
    """
    db = get_db()
    
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        # 1. جلب كل الحواف في الفترة
        edges = (
            db.table("memory_graph_edges")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", cutoff)
            .execute()
        )
        
        if not edges.data or len(edges.data) < 3:
            return {
                "patterns_found": 0,
                "patterns": [],
                "summary": "لا توجد بيانات كافية لاستخراج الأنماط",
            }

        edge_list = edges.data
        
        # 2. تصنيف الحواف حسب النوع
        edge_by_type = {}
        for edge in edge_list:
            rtype = edge.get("relation_type", "unknown")
            if rtype not in edge_by_type:
                edge_by_type[rtype] = []
            edge_by_type[rtype].append(edge)
        
        patterns = []
        
        # 3. نمط: عاطفة → شخص → عاطفة أخرى
        # "كلما ذكر فلان، تحولت عاطفته من X إلى Y"
        involves_person_edges = edge_by_type.get("involves_person", [])
        triggered_by_edges = edge_by_type.get("triggered_by", [])
        
        # تبسيط: ابحث عن أشخاص مرتبطين بعواطف متكررة
        person_emotion_map = {}
        for edge in involves_person_edges:
            source = edge.get("source_id")
            target = edge.get("target_id")
            metadata = edge.get("metadata", {})
            emotion = metadata.get("emotion", "")
            if emotion and target:
                if target not in person_emotion_map:
                    person_emotion_map[target] = []
                person_emotion_map[target].append(emotion)
        
        for person_id, emotions in person_emotion_map.items():
            if len(emotions) >= min_pattern_strength:
                most_common = Counter(emotions).most_common(1)[0]
                # جلب اسم الشخص
                person_info = db.table("person_nodes").select("name").eq("id", person_id).single().execute()
                person_name = person_info.data.get("name", person_id) if person_info.data else person_id
                
                patterns.append({
                    "type": "person_emotion_link",
                    "description": f"عند ذكر {person_name}، غالباً يشعر بـ {most_common[0]}",
                    "strength": most_common[1],
                    "person_id": person_id,
                    "emotion": most_common[0],
                })
        
        # 4. نمط: تكرار نفس المحفز
        trigger_map = {}
        for edge in triggered_by_edges:
            source = edge.get("source_id")
            if source not in trigger_map:
                trigger_map[source] = 0
            trigger_map[source] += 1
        
        frequent_triggers = [
            {"source_id": k, "count": v}
            for k, v in trigger_map.items()
            if v >= min_pattern_strength
        ]
        
        if frequent_triggers:
            # جلب تفاصيل المحفزات
            for trigger in frequent_triggers[:3]:
                memory = db.table("emotional_memory").select("trigger,expressed_text").eq("id", trigger["source_id"]).single().execute()
                if memory.data:
                    patterns.append({
                        "type": "recurring_trigger",
                        "description": f"محفز متكرر: {memory.data.get('trigger', 'غير معروف')}",
                        "strength": trigger["count"],
                        "example": memory.data.get("expressed_text", "")[:100],
                    })

        # 5. نمط: تحول عاطفي
        # "بعد الغضب من المال، يهدأ عندما يتحدث عن أمه"
        # (نسخة مبسطة)
        if "involves_person" in edge_by_type and "triggered_by" in edge_by_type:
            for person_edge in involves_person_edges[:5]:
                person_id = person_edge.get("target_id")
                person_emotion = person_edge.get("metadata", {}).get("emotion", "")
                
                if person_emotion in ["joy", "sadness"]:  # عواطف إيجابية بعد الصعبة
                    patterns.append({
                        "type": "emotional_shift",
                        "description": f"شخص {person_id} يرتبط بتحول عاطفي نحو {person_emotion}",
                        "strength": 1,
                    })
        
        # 6. تلخيص
        summary = f"تم اكتشاف {len(patterns)} نمط من الرسم البياني"
        if patterns:
            pattern_descriptions = [p["description"] for p in patterns[:3]]
            summary += f": {'; '.join(pattern_descriptions)}"
        
        return {
            "patterns_found": len(patterns),
            "patterns": patterns[:10],
            "summary": summary,
            "analyzed_edges": len(edge_list),
        }
        
    except Exception as e:
        logger.error(f"فشل تنقيب الأنماط: {e}")
        return {"patterns_found": 0, "patterns": [], "summary": "خطأ في التحليل"}


# ============================================================
# ضغط الرسم البياني (إزالة الحواف الضعيفة)
# ============================================================
async def compress_graph(
    user_id: str,
    min_weight: float = 0.3,
    max_age_days: int = 90,
) -> Dict[str, Any]:
    """
    يضغط الرسم البياني بحذف الحواف الضعيفة والقديمة.
    """
    db = get_db()
    
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).isoformat()
        
        # حذف الحواف الضعيفة والقديمة
        result = (
            db.table("memory_graph_edges")
            .delete()
            .eq("user_id", user_id)
            .lt("weight", min_weight)
            .lt("created_at", cutoff)
            .execute()
        )
        
        deleted = len(result.data) if result.data else 0
        
        logger.info(f"🗜️ ضغط الرسم: حذف {deleted} حافة ضعيفة/قديمة")
        
        return {
            "deleted_edges": deleted,
            "min_weight_threshold": min_weight,
            "max_age_days": max_age_days,
        }
        
    except Exception as e:
        logger.error(f"فشل ضغط الرسم: {e}")
        return {"deleted_edges": 0}


logger.info("✅ Graph Pattern Miner initialized")
