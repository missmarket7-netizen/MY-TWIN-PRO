"""Cost Dashboard – real-time cost tracking per user/feature/tier."""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("cost_dashboard")

async def get_cost_per_user(user_id: str) -> Dict[str, Any]:
    db = get_db()
    try:
        r = db.table("ai_metrics").select("tokens_used,provider").eq("user_id", user_id).order("created_at", desc=True).limit(100).execute()
        if not r.data:
            return {"total_tokens": 0, "estimated_cost": 0.0}
        
        total_tokens = sum(row.get("tokens_used", 0) for row in r.data)
        providers = {}
        for row in r.data:
            p = row.get("provider", "unknown")
            providers[p] = providers.get(p, 0) + row.get("tokens_used", 0)
        
        return {
            "total_tokens": total_tokens,
            "estimated_cost": round(total_tokens * 0.0001, 6),  # $0.0001 per token (free models)
            "by_provider": providers,
            "requests_count": len(r.data),
        }
    except Exception as e:
        logger.error(f"Failed to get cost per user: {e}")
        return {"total_tokens": 0, "estimated_cost": 0.0}

async def get_cost_summary() -> Dict[str, Any]:
    db = get_db()
    try:
        r = db.table("ai_metrics").select("tokens_used,provider,user_id").order("created_at", desc=True).limit(1000).execute()
        if not r.data:
            return {"total_tokens": 0, "estimated_cost": 0.0, "by_tier": {}}
        
        total_tokens = sum(row.get("tokens_used", 0) for row in r.data)
        return {"total_tokens": total_tokens, "estimated_cost": round(total_tokens * 0.0001, 6)}
    except:
        return {"total_tokens": 0, "estimated_cost": 0.0}
