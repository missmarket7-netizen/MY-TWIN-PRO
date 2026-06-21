"""Goal model v2.0 – متوافق مع P.A.S.S. و TCMA"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class Goal(BaseModel):
    id: Optional[str] = None  # يُملأ من قاعدة البيانات
    user_id: str
    title: str = Field(..., min_length=1, max_length=200)
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    priority: int = Field(default=1, ge=1, le=5)
    status: str = Field(default="active")  # active | completed | abandoned | paused
    category: str = Field(default="general")  # health, work, study, personal, finance
    due_date: Optional[str] = None  # تاريخ الاستحقاق
    reminder_enabled: bool = Field(default=False)
    reflection: Optional[str] = None  # تأملات المستخدم حول الهدف
    emotional_impact: Optional[str] = None  # من TCMA: إيجابي/سلبي/محايد
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
