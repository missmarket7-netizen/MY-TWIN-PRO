"""
S.M.A.R.T. Home System – نظام المنزل الذكي المتكامل
=======================================================
يدعم: Home Assistant، WLED، ESPHome، MQTT
يتكامل مع TCMA للوعي بالسياق والروتين اليومي.
"""
from .smart_home_orchestrator import SmartHomeOrchestrator, smart_home

__all__ = ["SmartHomeOrchestrator", "smart_home"]
