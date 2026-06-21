"""
Observability – نظام المراقبة والملاحظة الشامل
=================================================
- alert_service: تنبيهات Slack, Telegram, Discord
- logging_service: سجلات منظمة مع تنسيق JSON و Sentry
- metrics_service: مقاييس SaaS مع تجميع دوري
- tracing_service: تتبع الطلبات مع عزل سياقي
- system_monitor: مراقبة النظام وتنبؤات وتنبيهات
"""
from .alert_service import send_alert, check_health_metrics, check_system_health
from .logging_service import setup_logging, set_correlation_id, get_logger, log_error
from .metrics_service import metrics, MetricsService
from .tracing_service import (
    start_trace, finish_trace, get_current_trace, get_correlation_id,
    span, async_span, Trace, Span
)
from .system_monitor import (
    tracker, AIMonitor, LatencyTracker, ErrorLogger,
    collect_system_metrics, check_alerts_and_notify, get_health_report,
    start_periodic_monitoring, record_metric
)

__all__ = [
    # Alert
    "send_alert", "check_health_metrics", "check_system_health",
    # Logging
    "setup_logging", "set_correlation_id", "get_logger", "log_error",
    # Metrics
    "metrics", "MetricsService",
    # Tracing
    "start_trace", "finish_trace", "get_current_trace", "get_correlation_id",
    "span", "async_span", "Trace", "Span",
    # System Monitor
    "tracker", "AIMonitor", "LatencyTracker", "ErrorLogger",
    "collect_system_metrics", "check_alerts_and_notify", "get_health_report",
    "start_periodic_monitoring", "record_metric",
]
