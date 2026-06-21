"""
Cost Dashboard v2.0 – لوحة تحكم التكاليف (متكاملة)
=============================================================
- تتبع التكاليف لكل مستخدم، ميزة، وباقة
- تكامل مع Observability و Metrics
- دعم النموذج الداخلي (تكلفة صفرية)
- تحليلات يومية/أسبوعية/شهرية
"""
import logging
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("cost_dashboard")

# تكاليف تقديرية لكل 1000 رمز (Token)
PROVIDER_COST_PER_1K = {
    "gemini": 0.0005,
    "groq": 0.0003,
    "openrouter": 0.0008,
    "internal_mytwin": 0.0,  # تكلفة صفرية للنموذج الداخلي
}

async def get_cost_per_user(user_id: str) -> Dict[str, Any]:
    """تقرير تكلفة مستخدم واحد"""
    db = get_db()
    try:
        r = db.table("ai_metrics").select("tokens_used,provider,task_type").eq("user_id", user_id).order("created_at", desc=True).limit(100).execute()
        if not r.data:
            return {"total_tokens": 0, "estimated_cost": 0.0}

        total_cost = 0.0
        total_tokens = 0
        providers = {}
        tasks = {}

        for row in r.data:
            tokens = row.get("tokens_used", 0)
            provider = row.get("provider", "unknown")
            task = row.get("task_type", "general")
            cost = tokens * PROVIDER_COST_PER_1K.get(provider, 0.0003) / 1000

            total_tokens += tokens
            total_cost += cost
            providers[provider] = providers.get(provider, 0) + tokens
            tasks[task] = tasks.get(task, 0) + tokens

        return {
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 6),
            "by_provider": providers,
            "by_task": tasks,
            "requests_count": len(r.data),
        }
    except Exception as e:
        logger.error(f"فشل جلب تكلفة المستخدم: {e}")
        return {"total_tokens": 0, "estimated_cost_usd": 0.0}

async def get_cost_summary(days: int = 7) -> Dict[str, Any]:
    """ملخص التكاليف لآخر أيام"""
    db = get_db()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        r = db.table("ai_metrics").select("tokens_used,provider,user_id,created_at").gte("created_at", cutoff).order("created_at", desc=True).limit(5000).execute()
        if not r.data:
            return {"total_tokens": 0, "estimated_cost_usd": 0.0}

        total_cost = 0.0
        total_tokens = 0
        providers = {}
        users = {}
        daily_cost = {}

        for row in r.data:
            tokens = row.get("tokens_used", 0)
            provider = row.get("provider", "unknown")
            user_id = row.get("user_id", "unknown")
            date_str = row.get("created_at", "")[:10] if row.get("created_at") else "unknown"

            cost = tokens * PROVIDER_COST_PER_1K.get(provider, 0.0003) / 1000
            total_tokens += tokens
            total_cost += cost

            providers[provider] = providers.get(provider, 0) + tokens
            users[user_id] = users.get(user_id, 0) + tokens
            daily_cost[date_str] = round(daily_cost.get(date_str, 0.0) + cost, 6)

        return {
            "period_days": days,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(total_cost, 6),
            "daily_breakdown": daily_cost,
            "top_providers": dict(sorted(providers.items(), key=lambda x: x[1], reverse=True)[:5]),
            "top_users": dict(sorted(users.items(), key=lambda x: x[1], reverse=True)[:10]),
        }
    except Exception as e:
        logger.error(f"فشل ملخص التكاليف: {e}")
        return {"total_tokens": 0, "estimated_cost_usd": 0.0}

async def get_savings_from_internal_model() -> Dict[str, Any]:
    """حساب التوفير من استخدام النموذج الداخلي"""
    db = get_db()
    try:
        r = db.table("ai_metrics").select("tokens_used,provider").eq("provider", "internal_mytwin").execute()
        internal_tokens = sum(row.get("tokens_used", 0) for row in (r.data or []))
        savings = internal_tokens * 0.0005 / 1000  # مقارنة بـ Gemini
        return {
            "internal_tokens_used": internal_tokens,
            "estimated_savings_usd": round(savings, 6),
            "compared_to": "gemini ($0.0005/1K tokens)"
        }
    except:
        return {"internal_tokens_used": 0, "estimated_savings_usd": 0.0}

logger.info("✅ Cost Dashboard v2.0 initialized")
