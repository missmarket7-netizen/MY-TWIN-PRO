"""Profile model – user profile, tier, energy, settings."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class VoiceConfig(BaseModel):
    provider: str = Field(default="edge_tts")
    voice_id: str = Field(default="ar-EG-SalmaNeural")
    language: str = Field(default="ar")
    pitch: float = Field(default=1.0, ge=0.5, le=2.0)
    rate: float = Field(default=1.0, ge=0.5, le=2.0)
    gender: str = Field(default="female")
    personality: str = Field(default="friend")
    emotion: str = Field(default="neutral")


class TierConfig(BaseModel):
    tier: str = Field(default="free")
    daily_messages_limit: int = Field(default=15)
    daily_tokens_limit: int = Field(default=500)
    features: List[str] = Field(default_factory=list)


class UserProfile(BaseModel):
    user_id: str
    full_name: Optional[str] = None
    twin_name: str = Field(default="توأمك")
    twin_gender: str = Field(default="female")
    twin_style: str = Field(default="supportive")
    lang: str = Field(default="ar")
    tier: str = Field(default="free")
    signup_date: Optional[str] = None
    last_active: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    daily_messages_used: int = Field(default=0)
    daily_tokens_used: int = Field(default=0)
    twin_energy: int = Field(default=100, ge=0, le=100)
    voice_config: VoiceConfig = Field(default_factory=VoiceConfig)
    tier_config: TierConfig = Field(default_factory=TierConfig)
