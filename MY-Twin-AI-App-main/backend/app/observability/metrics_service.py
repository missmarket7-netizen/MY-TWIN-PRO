"""
Metrics Service – numeric counters and histograms.
Tracks requests, latency, cost, provider distribution, intents.
Sends aggregated metrics to Sentry and cache for dashboard.
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("metrics_service")

# In‑memory store (migrate to Redis for multi‑worker)
_metrics: Dict[str, Any] = {
    "requests": 0,
    "errors": 0,
    "total_latency_ms": 0.0,
    "latency_samples": [],
    "providers": {},
    "intents": {},
    "cost_estimate": 0.0,
    "last_reset": datetime.now(timezone.utc).isoformat(),
}

MAX_LATENCY_SAMPLES = 200


def record_request(
    duration_ms: float,
    provider: str = "unknown",
    intent: str = "general",
    tokens_used: int = 0,
    error: bool = False,
):
    """Record a single request."""
    _metrics["requests"] += 1
    _metrics["total_latency_ms"] += duration_ms
    _metrics["latency_samples"].append(duration_ms)
    if len(_metrics["latency_samples"]) > MAX_LATENCY_SAMPLES:
        _metrics["latency_samples"] = _metrics["latency_samples"][-MAX_LATENCY_SAMPLES:]

    _metrics["providers"][provider] = _metrics["providers"].get(provider, 0) + 1
    _metrics["intents"][intent] = _metrics["intents"].get(intent, 0) + 1

    # Cost estimation (free providers → 0)
    from app.domain.services.cost_service import estimate_cost
    _metrics["cost_estimate"] += estimate_cost(provider, tokens_used)

    if error:
        _metrics["errors"] += 1

    # Send to Sentry as breadcrumb for current transaction
    try:
        import sentry_sdk
        sentry_sdk.add_breadcrumb(
            category="metrics",
            message=f"Request: {duration_ms:.0f}ms via {provider} intent={intent}",
            level="info",
        )
    except Exception:
        pass


def get_snapshot() -> Dict[str, Any]:
    """Return current metrics snapshot."""
    samples = _metrics["latency_samples"]
    avg = sum(samples) / len(samples) if samples else 0.0
    return {
        "requests": _metrics["requests"],
        "errors": _metrics["errors"],
        "avg_latency_ms": round(avg, 2),
        "p95_latency_ms": round(_percentile(samples, 0.95), 2) if samples else 0.0,
        "p99_latency_ms": round(_percentile(samples, 0.99), 2) if samples else 0.0,
        "providers": dict(_metrics["providers"]),
        "intents": dict(_metrics["intents"]),
        "cost_estimate": round(_metrics["cost_estimate"], 6),
        "last_reset": _metrics["last_reset"],
    }


def reset():
    """Reset all metrics (e.g., daily)."""
    _metrics["requests"] = 0
    _metrics["errors"] = 0
    _metrics["total_latency_ms"] = 0.0
    _metrics["latency_samples"].clear()
    _metrics["providers"].clear()
    _metrics["intents"].clear()
    _metrics["cost_estimate"] = 0.0
    _metrics["last_reset"] = datetime.now(timezone.utc).isoformat()


def _percentile(sorted_data: list, pct: float) -> float:
    if not sorted_data:
        return 0.0
    data = sorted(sorted_data)
    idx = int(len(data) * pct)
    return data[min(idx, len(data) - 1)]
