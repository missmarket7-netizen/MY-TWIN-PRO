"""Memory model – semantic memories with embeddings."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, timezone


class Memory(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str = Field(..., min_length=1, max_length=5000)
    embedding: Optional[List[float]] = None
    memory_type: str = Field(default="daily")  # core | goal | relationship | preference | fact | daily
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    emotion: Optional[str] = None
    emotion_intensity: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    scores: Optional[Dict[str, float]] = None
    is_hard: bool = Field(default=False)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
