"""
P.A.S.S. – Personal Assistant & Smart Scheduler
==================================================
إدارة المهام، التقويم، الإيميلات، والتذكيرات.
يتكامل مع TCMA لتذكر التزامات المستخدم وتفضيلاته.
"""
from .pass_orchestrator import PASSOrchestrator, pass_assistant

__all__ = ["PASSOrchestrator", "pass_assistant"]
