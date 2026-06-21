"""
Routine Engine – محرك الروتين اليومي
=======================================
يتعلم روتين المستخدم ويقترح أتمتة ذكية.
مثال: "لاحظت أنك تطفئ الأنوار الساعة 11 مساءً كل يوم. هل أؤتمت هذا؟"
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("routine_engine")

class RoutineEngine:
    def __init__(self):
        self.action_log: Dict[str, List[Dict]] = {}

    def log_action(self, user_id: str, action: str, device: str, time: str = None):
        """يسجل إجراءً في السجل"""
        if user_id not in self.action_log:
            self.action_log[user_id] = []
        self.action_log[user_id].append({
            "action": action,
            "device": device,
            "time": time or datetime.now(timezone.utc).isoformat(),
        })

    def detect_patterns(self, user_id: str) -> List[Dict]:
        """يكتشف أنماطاً متكررة في تصرفات المستخدم"""
        actions = self.action_log.get(user_id, [])
        if len(actions) < 3:
            return []

        patterns = []
        # تبسيط: لو تكرر نفس الإجراء 3 مرات في نفس الساعة، نقترح أتمتة
        action_counts = {}
        for a in actions:
            hour = datetime.fromisoformat(a["time"]).hour
            key = f"{a['action']}_{a['device']}_{hour}"
            action_counts[key] = action_counts.get(key, 0) + 1

        for key, count in action_counts.items():
            if count >= 3:
                action, device, hour = key.split("_")
                patterns.append({
                    "action": action,
                    "device": device,
                    "hour": int(hour),
                    "count": count,
                    "suggestion": f"هل تريد أتمتة {action} لـ {device} كل يوم الساعة {hour}:00؟"
                })

        return patterns

routine_engine = RoutineEngine()
logger.info("✅ Routine Engine initialized")
