"""
Study Knowledge Graph - الرسم المعرفي مع الثبات في Supabase
=============================================================
يبني شبكة علاقات بين المفاهيم. يخزن تقدم الطالب في قاعدة البيانات.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("study_knowledge_graph")

# ============================================================
# الرسم المعرفي (في الذاكرة للمفاهيم العامة، وفي DB لتقدم الطالب)
# ============================================================
class StudyKnowledgeGraph:
    def __init__(self):
        self.graph: Dict[str, Dict] = {}
        self._init_default_concepts()
    
    def _init_default_concepts(self):
        """تهيئة المفاهيم الافتراضية"""
        default_concepts = [
            ("numbers", "الأعداد", "رياضيات", [], "easy", "child"),
            ("addition", "الجمع", "رياضيات", ["numbers"], "easy", "child"),
            ("subtraction", "الطرح", "رياضيات", ["numbers"], "easy", "child"),
            ("multiplication", "الضرب", "رياضيات", ["addition"], "medium", "child"),
            ("division", "القسمة", "رياضيات", ["multiplication"], "medium", "child"),
            ("fractions", "الكسور", "رياضيات", ["division"], "medium", "teen"),
            ("algebra", "الجبر", "رياضيات", ["fractions"], "hard", "teen"),
            ("geometry", "الهندسة", "رياضيات", ["algebra"], "hard", "teen"),
            ("calculus", "التفاضل والتكامل", "رياضيات", ["algebra", "geometry"], "hard", "young_adult"),
        ]
        for c in default_concepts:
            self.add_concept(*c)
    
    def add_concept(self, concept_id: str, name: str, subject: str, prerequisites: List[str] = None, difficulty: str = "medium", age_range: str = "teen"):
        self.graph[concept_id] = {
            "id": concept_id, "name": name, "subject": subject,
            "prerequisites": prerequisites or [], "dependents": [],
            "difficulty": difficulty, "age_range": age_range,
        }
        for prereq_id in (prerequisites or []):
            if prereq_id in self.graph:
                if concept_id not in self.graph[prereq_id]["dependents"]:
                    self.graph[prereq_id]["dependents"].append(concept_id)
    
    def get_learning_path(self, target_concept_id: str) -> List[str]:
        if target_concept_id not in self.graph:
            return [target_concept_id]
        path, visited = [], set()
        def dfs(cid):
            if cid in visited: return
            visited.add(cid)
            for prereq in self.graph.get(cid, {}).get("prerequisites", []):
                dfs(prereq)
            path.append(cid)
        dfs(target_concept_id)
        return path

    # ============================================================
    # إدارة تقدم الطالب (في Supabase)
    # ============================================================
    async def update_user_knowledge(
        self, user_id: str, concept_id: str, quality: int,
        concept_name: str = None, emotional_state: str = "neutral"
    ) -> Dict[str, Any]:
        db = get_db()
        try:
            # جلب البيانات الحالية إن وجدت
            current = db.table("user_knowledge_state").select("*").eq("user_id", user_id).eq("concept_id", concept_id).execute()
            
            # حساب معاملات SM-2 الجديدة
            from app.features.study.spaced_repetition_sm2 import scheduler
            if current.data:
                c = current.data[0]
                new_state = scheduler.calculate_next_review(
                    concept=concept_id, quality=quality,
                    current_ease=c.get("ease_factor", 2.5),
                    current_interval=c.get("interval_days", 0),
                    repetition_count=c.get("repetition_count", 0),
                    emotional_state=emotional_state,
                )
                db.table("user_knowledge_state").update({
                    "mastery_level": min(quality / 5.0, 1.0),
                    "ease_factor": new_state["ease_factor"],
                    "interval_days": new_state["interval_days"],
                    "repetition_count": new_state["repetition_count"],
                    "last_reviewed": datetime.now(timezone.utc).isoformat(),
                    "next_review_date": new_state["next_review_date"],
                    "emotional_state": emotional_state,
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }).eq("id", c["id"]).execute()
            else:
                new_state = scheduler.calculate_next_review(
                    concept=concept_id, quality=quality,
                    emotional_state=emotional_state,
                )
                db.table("user_knowledge_state").insert({
                    "user_id": user_id, "concept_id": concept_id,
                    "concept_name": concept_name or concept_id,
                    "mastery_level": min(quality / 5.0, 1.0),
                    "ease_factor": new_state["ease_factor"],
                    "interval_days": new_state["interval_days"],
                    "repetition_count": new_state["repetition_count"],
                    "last_reviewed": datetime.now(timezone.utc).isoformat(),
                    "next_review_date": new_state["next_review_date"],
                    "emotional_state": emotional_state,
                }).execute()
            
            # تسجيل المراجعة
            db.table("study_reviews").insert({
                "user_id": user_id, "concept_id": concept_id, "quality": quality,
                "ease_factor": new_state["ease_factor"],
                "interval_days": new_state["interval_days"],
                "repetition_count": new_state["repetition_count"],
                "emotional_state": emotional_state,
            }).execute()
            
            return new_state
        except Exception as e:
            logger.error(f"فشل تحديث معرفة المستخدم: {e}")
            return {}

    async def get_user_knowledge(self, user_id: str, concept_id: str) -> Optional[Dict]:
        db = get_db()
        try:
            res = db.table("user_knowledge_state").select("*").eq("user_id", user_id).eq("concept_id", concept_id).execute()
            return res.data[0] if res.data else None
        except: return None

knowledge_graph = StudyKnowledgeGraph()
logger.info("✅ Study Knowledge Graph initialized with DB persistence")
