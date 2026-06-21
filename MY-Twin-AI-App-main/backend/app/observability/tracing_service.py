"""
Tracing Service v2.0 – تتبع الطلبات الشامل
=============================================
- عزل سياقي آمن للطلبات المتزامنة (contextvars)
- تكامل كامل مع Metrics Service و Sentry
- تسجيل تلقائي لخطوات الأوركسترا
"""
import time, logging, uuid
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from contextvars import ContextVar

logger = logging.getLogger("tracing_service")

# عزل سياقي آمن لكل طلب
_current_trace_var: ContextVar[Optional['Trace']] = ContextVar('current_trace', default=None)

try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False

class Span:
    """خطوة واحدة في مسار الطلب"""
    def __init__(self, name: str):
        self.name = name
        self.start_time: float = 0.0
        self.duration_ms: float = 0.0
        self.metadata: Dict[str, Any] = {}
        self.children: List['Span'] = []

    def start(self) -> 'Span':
        self.start_time = time.time()
        return self

    def stop(self):
        self.duration_ms = (time.time() - self.start_time) * 1000
        return self

    def add_child(self, child: 'Span'):
        self.children.append(child)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "metadata": self.metadata,
            "children": [c.to_dict() for c in self.children] if self.children else []
        }

class Trace:
    """مسار طلب كامل"""
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())[:8]
        self.spans: List[Span] = []
        self.start_time = time.time()

    def start_span(self, name: str) -> Span:
        span = Span(name)
        span.start()
        self.spans.append(span)
        return span

    def finish(self) -> Dict[str, Any]:
        """إنهاء التتبع وتسجيل النتائج"""
        total_duration = (time.time() - self.start_time) * 1000
        
        # إنهاء جميع الـ spans المفتوحة
        for span in self.spans:
            if span.duration_ms == 0:
                span.stop()

        summary = {
            "correlation_id": self.correlation_id,
            "total_duration_ms": round(total_duration, 2),
            "spans": [s.to_dict() for s in self.spans],
            "span_count": len(self.spans)
        }

        # تسجيل المقاييس
        try:
            from app.observability.metrics_service import metrics
            metrics.record_request("trace", 200, total_duration)
        except Exception:
            pass

        # إرسال إلى Sentry
        if SENTRY_AVAILABLE:
            try:
                for span in self.spans:
                    sentry_sdk.add_breadcrumb(
                        category="trace",
                        message=span.name,
                        data={"duration_ms": span.duration_ms}
                    )
            except Exception:
                pass

        logger.info(f"Trace {self.correlation_id}: {summary['span_count']} spans, {total_duration:.1f}ms")
        return summary

def start_trace() -> Trace:
    """بدء تتبع طلب جديد"""
    trace = Trace()
    _current_trace_var.set(trace)
    try:
        from app.observability.logging_service import set_correlation_id
        set_correlation_id(trace.correlation_id)
    except:
        pass
    return trace

def get_current_trace() -> Optional[Trace]:
    """الحصول على التتبع الحالي (آمن سياقياً)"""
    return _current_trace_var.get()

def get_correlation_id() -> str:
    """الحصول على معرف التتبع الحالي"""
    trace = get_current_trace()
    return trace.correlation_id if trace else "-"

def finish_trace() -> Optional[Dict[str, Any]]:
    """إنهاء التتبع الحالي"""
    trace = get_current_trace()
    if trace:
        result = trace.finish()
        _current_trace_var.set(None)
        return result
    return None

@contextmanager
def span(name: str, metadata: Optional[Dict[str, Any]] = None):
    """مدير سياق لتتبع كتلة من الكود"""
    trace = get_current_trace()
    span_obj = trace.start_span(name) if trace else None
    try:
        yield span_obj
    finally:
        if span_obj:
            span_obj.stop()
            if metadata:
                span_obj.metadata.update(metadata)
            logger.debug(f"  ⏱  {name}: {span_obj.duration_ms:.1f}ms")

async def async_span(name: str, coro, metadata: Optional[Dict[str, Any]] = None):
    """تتبع عملية غير متزامنة"""
    trace = get_current_trace()
    span_obj = trace.start_span(name) if trace else None
    try:
        result = await coro
        return result
    finally:
        if span_obj:
            span_obj.stop()
            if metadata:
                span_obj.metadata.update(metadata)

logger.info("✅ Tracing Service v2.0 initialized")
