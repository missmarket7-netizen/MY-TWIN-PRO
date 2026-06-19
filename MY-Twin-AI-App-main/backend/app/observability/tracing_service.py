"""
Tracing Service – follows a request through the orchestrator steps.
Creates spans for each service call and logs duration.
Integrates with Sentry performance monitoring.
"""
import time
import logging
from typing import Optional
from contextlib import contextmanager
from app.observability.logging_service import set_correlation_id, get_logger
import uuid

logger = get_logger("tracing_service")

# Sentry integration (optional)
try:
    import sentry_sdk
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


class Span:
    """Represents a single step in the request pipeline."""
    def __init__(self, name: str, parent: Optional["Span"] = None):
        self.name = name
        self.parent = parent
        self.start_time: float = 0.0
        self.duration_ms: float = 0.0
        self.metadata: dict = {}

    def start(self):
        self.start_time = time.time()
        return self

    def stop(self):
        self.duration_ms = (time.time() - self.start_time) * 1000

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "duration_ms": round(self.duration_ms, 2),
            "metadata": self.metadata,
        }


class Trace:
    """Holds the full trace of a single request."""
    def __init__(self, correlation_id: Optional[str] = None):
        self.correlation_id = correlation_id or str(uuid.uuid4())[:8]
        self.spans: list = []
        self._root: Optional[Span] = None

    def start_span(self, name: str) -> Span:
        span = Span(name)
        span.start()
        self.spans.append(span)
        return span

    def finish(self):
        total = sum(s.duration_ms for s in self.spans)
        logger.info(
            f"Trace {self.correlation_id}: {len(self.spans)} spans, {total:.1f}ms total"
        )
        # Send to Sentry if available
        if SENTRY_AVAILABLE:
            try:
                with sentry_sdk.start_span(op="request", description=f"trace {self.correlation_id}") as root_span:
                    for s in self.spans:
                        root_span.set_data(s.name, s.to_dict())
            except Exception:
                pass


# Global trace storage for current request (use contextvars in production)
_current_trace: Optional[Trace] = None


def start_trace() -> Trace:
    global _current_trace
    trace = Trace()
    set_correlation_id(trace.correlation_id)
    _current_trace = trace
    return trace


def get_current_trace() -> Optional[Trace]:
    return _current_trace


def finish_trace():
    global _current_trace
    if _current_trace:
        _current_trace.finish()
        _current_trace = None


@contextmanager
def span(name: str):
    """Context manager for instrumenting a block of code."""
    trace = _current_trace
    span_obj = trace.start_span(name) if trace else None
    try:
        yield span_obj
    finally:
        if span_obj:
            span_obj.stop()
            logger.debug(f"  ⏱  {name}: {span_obj.duration_ms:.1f}ms")
