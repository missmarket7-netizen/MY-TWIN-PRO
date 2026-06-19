"""Consciousness Service – reflection, awareness, goals (AR + EN)."""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger("consciousness_service")

_user_states: Dict[str, Dict[str, Any]] = {}

def _default_state() -> Dict[str, Any]:
    return {
        "internal_state": {
            "mood": "neutral", "energy": 0.7, "curiosity": 0.5,
            "last_thought_ar": "", "last_thought_en": "",
            "interaction_count": 0, "reflection_log": [],
        },
        "user_profile": {},
        "active_objectives": [],
    }

def _get_state(user_id: str) -> Dict[str, Any]:
    if user_id not in _user_states:
        _user_states[user_id] = _default_state()
    return _user_states[user_id]

async def load(user_id: str) -> Dict[str, Any]:
    return _get_state(user_id)

async def reflect(user_id: str, summary: str, twin_name: str = "MyTwin", lang: str = "ar") -> Optional[Dict]:
    if not summary.strip(): return None
    state = _get_state(user_id)
    reflection = {
        "summary": summary[:200],
        "lang": lang,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    log = state["internal_state"].setdefault("reflection_log", [])
    log.append(reflection)
    if len(log) > 10:
        state["internal_state"]["reflection_log"] = log[-10:]
    if lang == "en":
        state["internal_state"]["last_thought_en"] = summary[:200]
    else:
        state["internal_state"]["last_thought_ar"] = summary[:200]
    state["internal_state"]["interaction_count"] += 1
    logger.info(f"✅ Reflection: {user_id} ({lang})")
    return reflection

async def add_objective(user_id: str, title: str) -> None:
    state = _get_state(user_id)
    objectives = state.setdefault("active_objectives", [])
    objectives.append({
        "title": title, "progress": 0,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    if len(objectives) > 5:
        state["active_objectives"] = objectives[-5:]

async def get_objectives(user_id: str) -> List[Dict]:
    return _get_state(user_id).get("active_objectives", [])

async def update_profile(user_id: str, data: Dict) -> None:
    state = _get_state(user_id)
    profile = state.get("user_profile", {})
    for key in ["relationship_dims","journey_phase","journey_day","attachment_style","bond_level"]:
        if key in data and data[key] is not None:
            profile[key] = data[key]
    profile["last_updated"] = datetime.now(timezone.utc).isoformat()
    state["user_profile"] = profile

async def get_profile(user_id: str) -> Dict:
    return _get_state(user_id).get("user_profile", {})

async def get_state_summary(user_id: str) -> Dict[str, Any]:
    state = _get_state(user_id)
    return {
        "mood": state["internal_state"]["mood"],
        "energy": state["internal_state"]["energy"],
        "curiosity": state["internal_state"]["curiosity"],
        "active_objectives": [o["title"] for o in state.get("active_objectives", [])],
        "last_thought_ar": state["internal_state"]["last_thought_ar"],
        "last_thought_en": state["internal_state"]["last_thought_en"],
    }
