"""Goal model – active objectives and progress."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class Goal(BaseModel):
    id: str = Field(default_factory=lambda: f"goal_{int(datetime.now(timezone.utc).timestamp())}")
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    priority: int = Field(default=1, ge=1, le=5)
    status: str = Field(default="active")  # active | completed | abandoned
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
