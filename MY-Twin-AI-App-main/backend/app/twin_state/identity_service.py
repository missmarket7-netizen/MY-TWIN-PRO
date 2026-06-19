"""Identity Service – Who am I? Core identity, traits, evolution."""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("identity_service")

DEFAULT_TRAITS = ["متفهم", "صبور", "ذكي", "دافئ"]
IDENTITY_TEMPLATES = {
    "ar": "أنا {twin_name}، رفيق ذكي أتعلم من تفاعلاتنا. {traits_desc}.",
    "en": "I am {twin_name}, an intelligent companion learning from our interactions. {traits_desc}.",
}

_user_identities: Dict[str, Dict[str, Any]] = {}


def _get_state(user_id: str) -> Dict[str, Any]:
    if user_id not in _user_identities:
        _user_identities[user_id] = {
            "traits": DEFAULT_TRAITS[:],
            "evolution_stage": 0,
            "description_ar": IDENTITY_TEMPLATES["ar"].format(
                twin_name="MyTwin", traits_desc="، ".join(DEFAULT_TRAITS)
            ),
            "description_en": IDENTITY_TEMPLATES["en"].format(
                twin_name="MyTwin", traits_desc=", ".join(DEFAULT_TRAITS)
            ),
        }
    return _user_identities[user_id]


async def get_identity(user_id: str, twin_name: str = "MyTwin", lang: str = "ar") -> Dict[str, Any]:
    state = _get_state(user_id)
    if twin_name != "MyTwin":
        state["description_ar"] = IDENTITY_TEMPLATES["ar"].format(
            twin_name=twin_name, traits_desc="، ".join(state["traits"])
        )
        state["description_en"] = IDENTITY_TEMPLATES["en"].format(
            twin_name=twin_name, traits_desc=", ".join(state["traits"])
        )
    return {
        "traits": state["traits"],
        "evolution_stage": state["evolution_stage"],
        "description": state.get(f"description_{lang}", state["description_ar"]),
    }


async def evolve(user_id: str, new_trait: str, reflection: str) -> None:
    state = _get_state(user_id)
    if new_trait and new_trait not in state["traits"] and len(state["traits"]) < 10:
        state["traits"].append(new_trait)
    state["evolution_stage"] += 1
    traits_str = "، ".join(state["traits"])
    state["description_ar"] = IDENTITY_TEMPLATES["ar"].format(twin_name="MyTwin", traits_desc=traits_str)
    state["description_en"] = IDENTITY_TEMPLATES["en"].format(twin_name="MyTwin", traits_desc=traits_str)
    logger.info(f"🎭 Identity evolved: stage {state['evolution_stage']}, traits: {state['traits']}")


async def get_traits(user_id: str) -> List[str]:
    return _get_state(user_id)["traits"]


async def get_evolution_stage(user_id: str) -> int:
    return _get_state(user_id)["evolution_stage"]
