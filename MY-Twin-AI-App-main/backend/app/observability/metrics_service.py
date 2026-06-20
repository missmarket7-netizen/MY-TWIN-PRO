"""Metrics Service – tracks KPIs for SaaS at scale."""
import time, logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from collections import defaultdict

logger = logging.getLogger("metrics_service")

class MetricsService:
    def __init__(self):
        self._metrics = defaultdict(int)
        self._latencies = []
        self._errors = []
        self._start_time = datetime.now(timezone.utc)
    
    def record_request(self, path: str, status_code: int, latency_ms: float, user_tier: str = "free"):
        self._metrics[f"requests:{path}"] += 1
        self._metrics[f"requests:{status_code}"] += 1
        self._metrics[f"tier:{user_tier}"] += 1
        self._latencies.append(latency_ms)
        if status_code >= 500:
            self._errors.append({"path": path, "status": status_code, "time": datetime.now(timezone.utc).isoformat()})
    
    def get_snapshot(self) -> Dict[str, Any]:
        latencies = self._latencies[-1000:] if self._latencies else [0]
        avg_latency = sum(latencies) / len(latencies)
        sorted_lat = sorted(latencies)
        p95 = sorted_lat[int(len(sorted_lat) * 0.95)] if len(sorted_lat) > 20 else max(sorted_lat)
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
        
        return {
            "uptime_seconds": uptime,
            "total_requests": self._metrics.get("requests:/api/chat", 0),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95, 2),
            "error_count": len(self._errors),
            "by_tier": {k: v for k, v in self._metrics.items() if k.startswith("tier:")},
        }

metrics = MetricsService()
