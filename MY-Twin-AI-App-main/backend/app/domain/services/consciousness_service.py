"""Consciousness Service – reflection, episodic memory, user profile."""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("consciousness_service")

_user_states: Dict[str, Dict[str, Any]] = {}

def _default_state() -> Dict[str, Any]:
    return {
        "internal_state": {"mood":"neutral","energy":0.7,"curiosity":0.5,"last_thought":"","interaction_count":0,"reflection_log":[]},
        "identity": {"traits":["متفهم","صبور","ذكي","دافئ"],"evolution_stage":0,"description":"رفيق ذكي أتعلم من تفاعلاتنا."},
        "user_profile": {},
        "active_objectives": [],
    }

async def load_state(user_id: str) -> Dict[str, Any]:
    if user_id not in _user_states:
        _user_states[user_id] = _default_state()
    return _user_states[user_id]

async def save_state(user_id: str) -> None:
    pass

async def reflect(user_id: str, conversation_summary: str, twin_name: str = "MyTwin") -> Optional[Dict]:
    if not conversation_summary.strip():
        return None
    state = await load_state(user_id)
    reflection = {
        "timestamp": __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),
        "summary": conversation_summary[:200],
    }
    log = state["internal_state"].setdefault("reflection_log", [])
    log.append(reflection)
    if len(log) > 10:
        state["internal_state"]["reflection_log"] = log[-10:]
    await save_state(user_id)
    logger.info(f"✅ Reflection: {user_id}")
    return reflection

async def update_user_profile(user_id: str, data: Dict) -> None:
    state = await load_state(user_id)
    profile = state.get("user_profile", {})
    for key in ["relationship_dims","journey_phase","journey_day","attachment_style","bond_level"]:
        if key in data and data[key] is not None:
            profile[key] = data[key]
    profile["last_updated"] = __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
    state["user_profile"] = profile
    await save_state(user_id)
