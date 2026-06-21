"""
Agent Budget v2.0 – متكامل مع حدود الاشتراكات
"""
import logging
from typing import Dict, Optional

logger = logging.getLogger("agent_budget")

class AgentBudget:
    def __init__(self):
        self.default_limits = {
            "max_tool_calls": 5,
            "max_cost": 0.05,
            "max_time_ms": 20000,
        }
        self.tool_costs = {
            "emotional_state": 0.001, "user_identity": 0.001,
            "reflections": 0.001, "people_network": 0.001,
            "study": 0.005, "business": 0.005, "code": 0.008,
            "life_coach": 0.005, "dream": 0.003, "recommendation": 0.001,
        }

    def get_limits(self, tier: str = "free") -> Dict:
        limits = self.default_limits.copy()
        if tier in ["premium", "pro", "yearly"]:
            limits["max_tool_calls"] = 10
            limits["max_cost"] = 0.10
            limits["max_time_ms"] = 30000
        elif tier == "plus":
            limits["max_tool_calls"] = 7
            limits["max_cost"] = 0.07
            limits["max_time_ms"] = 25000
        return limits

    async def can_execute(
        self, tool_name: str, calls_made: int, cost_so_far: float,
        time_elapsed_ms: float, user_id: str, tier: str = "free"
    ) -> bool:
        # 1. التحقق من حدود الميزانية (التكلفة الحسابية)
        limits = self.get_limits(tier)
        if calls_made >= limits["max_tool_calls"]:
            logger.info(f"Budget: max calls reached for {user_id}")
            return False
        if cost_so_far + self.tool_costs.get(tool_name, 0.001) > limits["max_cost"]:
            logger.info(f"Budget: max cost reached for {user_id}")
            return False
        if time_elapsed_ms > limits["max_time_ms"]:
            logger.info(f"Budget: max time reached for {user_id}")
            return False

        # 2. التحقق من حدود الاشتراك (الحصة اليومية)
        try:
            from message_limits import check_feature_usage
            allowed, remaining = await check_feature_usage(user_id, tier, tool_name)
            if not allowed:
                logger.info(f"Subscription: limit reached for {tool_name} by {user_id}")
                return False
        except ImportError:
            pass  # الملف غير موجود، نتجاهل الحدود
        
        return True

    def get_tool_cost(self, tool_name: str) -> float:
        return self.tool_costs.get(tool_name, 0.001)

agent_budget = AgentBudget()
