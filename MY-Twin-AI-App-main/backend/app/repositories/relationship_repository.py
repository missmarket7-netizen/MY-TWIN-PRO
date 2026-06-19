"""Relationship Repository – bond state, stages, dimensions."""
import logging
from typing import Optional
from datetime import datetime, timezone
from app.infrastructure.database.supabase_client import get_db
from app.models.relationship import RelationshipState, RelationshipDims

logger = logging.getLogger(__name__)

async def get_state(user_id: str) -> RelationshipState:
    db = get_db()
    try:
        r = db.table("twin_states").select("*").eq("user_id", user_id).single().execute()
        if r.data:
            d = r.data
            return RelationshipState(
                user_id=user_id,
                bond_level=d.get("bond_level", 0.0),
                stage=d.get("stage", "stranger"),
                dims=RelationshipDims(**d.get("dims", {}) if d.get("dims") else {}),
                interaction_count=d.get("interaction_count", 0),
                relationship_health=d.get("relationship_health", 100.0),
                updated_at=d.get("updated_at", datetime.now(timezone.utc).isoformat()),
            )
    except Exception as e:
        logger.warning(f"get_state failed: {e}")
    return RelationshipState(user_id=user_id)


async def save_state(state: RelationshipState) -> None:
    db = get_db()
    try:
        db.table("twin_states").upsert({
            "user_id": state.user_id,
            "bond_level": state.bond_level,
            "stage": state.stage,
            "dims": state.dims.model_dump(),
            "interaction_count": state.interaction_count,
            "relationship_health": state.relationship_health,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }, on_conflict="user_id").execute()
    except Exception as e:
        logger.error(f"save_state failed: {e}")


async def log_interaction(user_id: str, message: str, emotion: str) -> None:
    db = get_db()
    try:
        db.table("interaction_log").insert({
            "user_id": user_id,
            "message": message[:200],
            "emotion": emotion,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }).execute()
    except:
        pass
