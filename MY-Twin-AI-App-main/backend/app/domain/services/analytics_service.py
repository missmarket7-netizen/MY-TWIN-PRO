"""Analytics Service – Advanced metrics, trends, and insights."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("analytics_service")

async def get_user_growth(days: int = 30) -> Dict[str, Any]:
    """Track user growth over time."""
    db = get_db()
    try:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        r = db.table("profiles").select("created_at").gte("created_at", cutoff).execute()
        if not r.data:
            return {"growth": [], "total": 0}
        
        # Group by date
        by_date = {}
        for user in r.data:
            date = user["created_at"][:10] if user.get("created_at") else None
            if date:
                by_date[date] = by_date.get(date, 0) + 1
        
        growth = [{"date": d, "count": c} for d, c in sorted(by_date.items())]
        return {"growth": growth, "total": sum(c for _, c in growth)}
    except Exception as e:
        logger.error(f"Failed to get user growth: {e}")
        return {"growth": [], "total": 0}

async def get_engagement_metrics(user_id: str) -> Dict[str, Any]:
    """Get engagement metrics for a user."""
    db = get_db()
    try:
        # Messages count
        msg_r = db.table("chat_sessions").select("messages").eq("user_id", user_id).execute()
        total_messages = sum(len(row.get("messages", [])) for row in (msg_r.data or []))

        # Active days
        active_r = db.table("profiles").select("last_active").eq("id", user_id).single().execute()
        
        # Mood trends
        mood_r = db.table("emotional_timeline").select("primary_emotion").eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
        moods = [row["primary_emotion"] for row in (mood_r.data or [])]
        
        # Bond progress
        bond_r = db.table("twin_states").select("bond_level").eq("user_id", user_id).single().execute()
        bond = bond_r.data.get("bond_level", 0) if bond_r.data else 0

        return {
            "total_messages": total_messages,
            "bond_level": bond,
            "recent_moods": moods[:10],
            "dominant_mood": max(set(moods), key=moods.count) if moods else "neutral",
        }
    except Exception as e:
        logger.error(f"Failed to get engagement: {e}")
        return {}

async def get_conversation_quality(user_id: str) -> Dict[str, Any]:
    """Analyze conversation quality metrics."""
    db = get_db()
    try:
        # Feedback analysis
        fb_r = db.table("message_feedback").select("rating").eq("user_id", user_id).execute()
        if fb_r.data:
            likes = sum(1 for r in fb_r.data if r.get("rating") == "like")
            dislikes = sum(1 for r in fb_r.data if r.get("rating") == "dislike")
            total = len(fb_r.data)
            quality_score = (likes / total * 100) if total > 0 else 0
        else:
            quality_score = 0

        # Average response length
        sessions = db.table("chat_sessions").select("messages").eq("user_id", user_id).execute()
        total_chars = 0
        msg_count = 0
        for session in (sessions.data or []):
            for msg in session.get("messages", []):
                if msg.get("role") == "twin":
                    total_chars += len(msg.get("content", ""))
                    msg_count += 1

        avg_response_length = total_chars / msg_count if msg_count > 0 else 0

        return {
            "quality_score": round(quality_score, 2),
            "avg_response_length": round(avg_response_length, 2),
            "total_feedback": len(fb_r.data) if fb_r and fb_r.data else 0,
        }
    except Exception as e:
        logger.error(f"Failed to get quality: {e}")
        return {}
