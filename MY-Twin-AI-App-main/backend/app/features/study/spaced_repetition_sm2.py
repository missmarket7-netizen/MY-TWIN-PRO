"""
Spaced Repetition SM-2 - خوارزمية التكرار المتباعد المعدَّلة
==============================================================
تطبيق خوارزمية SM-2 مع تعديلات عاطفية.
تأخذ في الاعتبار: صعوبة المفهوم، تقييم الطالب، حالته النفسية.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("spaced_repetition_sm2")

# ============================================================
# خوارزمية SM-2 المعدَّلة
# ============================================================
class SpacedRepetitionScheduler:
    """يدير جدولة المراجعة للمفاهيم"""
    
    def __init__(self):
        # معاملات SM-2 الأساسية
        self.default_ease = 2.5
        self.min_ease = 1.3
        self.ease_bonus = 0.15
        self.ease_penalty = 0.20
        
        # فترات المراجعة (بالأيام)
        self.intervals = [1, 3, 7, 14, 30, 60, 120, 240]
    
    def calculate_next_review(
        self,
        concept: str,
        quality: int,  # 0-5 (تقييم الطالب لصعوبة التذكر)
        current_ease: float = None,
        current_interval: int = 0,
        repetition_count: int = 0,
        emotional_state: str = "neutral",
    ) -> Dict[str, Any]:
        """
        يحسب موعد المراجعة القادم.
        
        quality: 0 (نسيت تماماً) إلى 5 (تذكرت بسهولة)
        """
        
        if current_ease is None:
            current_ease = self.default_ease
        
        # تطبيق خوارزمية SM-2
        if quality >= 3:  # استدعاء ناجح
            if repetition_count == 0:
                interval = 1
            elif repetition_count == 1:
                interval = 3
            else:
                interval = round(current_interval * current_ease)
            
            repetition_count += 1
            # زيادة ease عند النجاح
            ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:  # استدعاء فاشل
            interval = 1
            repetition_count = 0
            # خفض ease عند الفشل
            ease = current_ease - self.ease_penalty
        
        # تأكيد الحد الأدنى للـ ease
        ease = max(ease, self.min_ease)
        
        # التعديل العاطفي
        emotional_modifier = self._emotional_modifier(emotional_state)
        interval = round(interval * emotional_modifier)
        interval = max(interval, 1)  # لا تقل عن يوم واحد
        
        next_review_date = datetime.now(timezone.utc) + timedelta(days=interval)
        
        return {
            "concept": concept,
            "quality": quality,
            "ease_factor": round(ease, 2),
            "interval_days": interval,
            "repetition_count": repetition_count,
            "next_review_date": next_review_date.isoformat(),
            "emotional_state": emotional_state,
        }
    
    def _emotional_modifier(self, emotion: str) -> float:
        """تعديل فترة المراجعة حسب الحالة النفسية"""
        modifiers = {
            "joy": 1.1,          # إذا كان سعيداً، أبعد المراجعة قليلاً
            "confident": 1.2,    # واثق = يراجع أبعد
            "neutral": 1.0,
            "frustration": 0.8,  # محبط = يراجع أقرب
            "anxiety": 0.7,      # قلق = يراجع أقرب بكثير
            "sadness": 0.8,
            "fear": 0.6,
        }
        return modifiers.get(emotion, 1.0)
    
    def get_due_reviews(
        self,
        user_id: str,
        all_concepts: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        يسترجع المفاهيم المستحقة للمراجعة الآن.
        """
        now = datetime.now(timezone.utc)
        due = []
        
        for concept in all_concepts:
            next_review = concept.get("next_review_date")
            if next_review:
                next_date = datetime.fromisoformat(next_review)
                if next_date <= now:
                    due.append(concept)
        
        return due
    
    def get_optimal_review_schedule(
        self,
        concepts: List[Dict[str, Any]],
        days_ahead: int = 30,
    ) -> Dict[str, List[Dict]]:
        """
        يبني جدول مراجعة مثالي للأيام القادمة.
        """
        schedule = {}
        today = datetime.now(timezone.utc)
        
        for day_offset in range(days_ahead):
            date = (today + timedelta(days=day_offset)).strftime("%Y-%m-%d")
            schedule[date] = []
            
            for concept in concepts:
                next_review = concept.get("next_review_date", "")
                if next_review.startswith(date):
                    schedule[date].append({
                        "concept": concept["concept"],
                        "ease": concept.get("ease_factor", self.default_ease),
                        "repetition": concept.get("repetition_count", 0),
                    })
        
        return schedule


scheduler = SpacedRepetitionScheduler()
logger.info("✅ Spaced Repetition SM-2 initialized")
