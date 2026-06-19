"""Tier model – subscription tiers, limits, features."""
from pydantic import BaseModel, Field
from typing import List, Optional


class TierConfig(BaseModel):
    tier: str = Field(default="free")
    daily_messages: int = Field(default=15)
    daily_tokens: int = Field(default=500)
    bond_ceiling: int = Field(default=28)
    features: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=lambda: ["groq", "gemini"])
    voice_provider: str = Field(default="edge_tts")
    elevenlabs_enabled: bool = Field(default=False)
    long_memory_enabled: bool = Field(default=False)
    coaching_enabled: bool = Field(default=False)
    dreams_enabled: bool = Field(default=False)
    proactive_enabled: bool = Field(default=False)


TIER_CONFIGS: dict = {
    "free": TierConfig(tier="free", daily_messages=15, daily_tokens=500, bond_ceiling=28,
                       features=["chat","weather","search"], models=["groq","gemini"],
                       voice_provider="edge_tts"),
    "plus": TierConfig(tier="plus", daily_messages=50, daily_tokens=1500, bond_ceiling=70,
                       features=["chat","weather","search","spotify","news","proactive"],
                       models=["groq","gemini","openrouter"], voice_provider="edge_tts",
                       long_memory_enabled=True, proactive_enabled=True),
    "premium": TierConfig(tier="premium", daily_messages=150, daily_tokens=4000, bond_ceiling=90,
                          features=["chat","weather","search","spotify","news","calendar","coaching","dreams","proactive"],
                          models=["groq","gemini","openrouter"], voice_provider="elevenlabs",
                          elevenlabs_enabled=True, long_memory_enabled=True,
                          coaching_enabled=True, dreams_enabled=True, proactive_enabled=True),
    "pro": TierConfig(tier="pro", daily_messages=500, daily_tokens=7000, bond_ceiling=100,
                      features=["chat","weather","search","spotify","news","calendar","coaching","dreams","proactive","smart_home"],
                      models=["groq","gemini","openrouter"], voice_provider="elevenlabs",
                      elevenlabs_enabled=True, long_memory_enabled=True,
                      coaching_enabled=True, dreams_enabled=True, proactive_enabled=True),
    "yearly": TierConfig(tier="yearly", daily_messages=9999, daily_tokens=15000, bond_ceiling=100,
                         features=["all"], models=["groq","gemini","openrouter"],
                         voice_provider="elevenlabs", elevenlabs_enabled=True,
                         long_memory_enabled=True, coaching_enabled=True,
                         dreams_enabled=True, proactive_enabled=True),
}


def get_tier_config(tier: str) -> TierConfig:
    return TIER_CONFIGS.get(tier, TIER_CONFIGS["free"])
