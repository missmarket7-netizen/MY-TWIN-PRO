"""
Domain Models for Chat v3.0 – متوافقة مع Twin Orchestrator v17
==================================================================
تعكس جميع السياقات الجديدة: التوصيات، الميزات الموجهة، التتبع.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class ChatRequest:
    message: str
    user_id: str
    twin_name: str = "توأمك"
    bond_level: float = 0.0
    relationship_dims: Dict[str, float] = field(default_factory=dict)
    history: List[Dict[str, str]] = field(default_factory=list)
    calm_mode: bool = False
    lang: str = "ar"
    twin_gender: str = "female"
    voice_enabled: bool = False


@dataclass
class ChatResponse:
    reply: str
    streaming: bool = False
    new_bond: Optional[float] = None
    emotion: Optional[Dict[str, Any]] = None
    provider: str = "gemini"
    latency_ms: float = 0.0
    journey_phase: Optional[str] = None
    journey_day: Optional[int] = None
    attachment_style: Optional[str] = None
    relationship_dims: Optional[Dict[str, float]] = None
    energy: Optional[int] = None
    
    # جديدة: توافق مع Twin Orchestrator v17
    intent: Optional[str] = None
    tool_results: Optional[List[Dict[str, Any]]] = None
    memory_context: Optional[str] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    feature_routed: Optional[str] = None  # الميزة التي تم توجيه الطلب إليها
    temporal_context: Optional[Dict[str, str]] = None
    proactive_additions: Optional[List[str]] = None
    self_awareness: Optional[str] = None
    trace_id: Optional[str] = None
