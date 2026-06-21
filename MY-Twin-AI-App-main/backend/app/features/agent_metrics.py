"""
Agent Metrics v2.0 – متوافق مع Unified Tool Registry & TCMA
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

try:
    from app.memory.emotional.emotional_memory import store_emotional_memory
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("agent_metrics")

class AgentMetrics:
    async def log_tool_execution(
        self,
        user_id: str,
        tool_name: str,
        success: bool,
        latency_ms: float = 0,
        input_query: str = "",
        output_summary: str = "",
        error_message: str = ""
    ):
        if not DB_AVAILABLE: return
        db = get_db()
        try:
            db.table("agent_metrics").insert({
                "user_id": user_id,
                "tool_name": tool_name,
                "success": success,
                "latency_ms": latency_ms,
                "input_query": input_query[:200],
                "output_summary": output_summary[:200],
                "error_message": error_message[:200],
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()

            # تكامل اختياري مع TCMA: تسجيل مشاعر عند فشل متكرر
            if not success and TCMA_AVAILABLE:
                # يمكن توسيعه لاحقاً لتحليل عدد مرات الفشل
                pass
        except Exception as e:
            logger.warning(f"Metric log failed: {e}")

    async def get_tool_stats(self, user_id: str) -> Dict[str, Any]:
        if not DB_AVAILABLE: return {}
        db = get_db()
        try:
            res = db.table("agent_metrics").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(100).execute()
            if not res.data: return {"total": 0, "tools": {}}
            
            stats = {"total": len(res.data), "tools": {}}
            for row in res.data:
                tool = row["tool_name"]
                if tool not in stats["tools"]:
                    stats["tools"][tool] = {"count": 0, "success": 0}
                stats["tools"][tool]["count"] += 1
                if row["success"]:
                    stats["tools"][tool]["success"] += 1
            return stats
        except Exception as e:
            logger.warning(f"Stats failed: {e}")
            return {}

agent_metrics = AgentMetrics()
