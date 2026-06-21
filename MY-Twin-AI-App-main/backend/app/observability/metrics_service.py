"""
Metrics Service v2.0 – تتبع مؤشرات الأداء مع دعم الإنتاج
============================================================
- تجميع دوري للبيانات لتوفير الذاكرة
- تتبع الأخطاء والتنبيهات
- متوافق مع Alert Service
"""
import time, logging, asyncio
from typing import Dict, Any, List
from datetime import datetime, timezone, timedelta
from collections import defaultdict

logger = logging.getLogger("metrics_service")

class MetricsService:
    def __init__(self):
        self._metrics = defaultdict(int)
        self._latencies: List[float] = []
        self._errors: List[Dict[str, Any]] = []
        self._start_time = datetime.now(timezone.utc)
        self._hourly_snapshots: List[Dict] = []
        self._active_users: set = set()

    def record_request(self, path: str, status_code: int, latency_ms: float, user_id: Optional[str] = None, user_tier: str = "free"):
        """تسجيل طلب واحد"""
        self._metrics[f"requests:{path}"] += 1
        self._metrics[f"status:{status_code}"] += 1
        self._metrics[f"tier:{user_tier}"] += 1
        self._latencies.append(latency_ms)
        
        if user_id:
            self._active_users.add(user_id)
            
        if status_code >= 500:
            self._errors.append({
                "path": path,
                "status": status_code,
                "time": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id
            })
            # الاحتفاظ بآخر 100 خطأ فقط
            if len(self._errors) > 100:
                self._errors = self._errors[-100:]

    def record_error(self, error_message: str, source: str = "unknown"):
        """تسجيل خطأ عام"""
        self._errors.append({
            "path": source,
            "status": 500,
            "message": error_message,
            "time": datetime.now(timezone.utc).isoformat()
        })

    def get_snapshot(self) -> Dict[str, Any]:
        """توليد لقطة للمقاييس الحالية"""
        # حساب الإحصائيات من آخر 1000 طلب
        recent_latencies = self._latencies[-1000:] if self._latencies else [0]
        avg_latency = sum(recent_latencies) / len(recent_latencies)
        sorted_lat = sorted(recent_latencies)
        p95 = sorted_lat[int(len(sorted_lat) * 0.95)] if len(sorted_lat) > 20 else max(sorted_lat)
        uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()

        return {
            "uptime_seconds": uptime,
            "total_requests": sum(v for k, v in self._metrics.items() if k.startswith("requests:")),
            "active_users": len(self._active_users),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95, 2),
            "error_count": len([e for e in self._errors if e.get("time", "") > (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()]),
            "total_errors": len(self._errors),
            "by_tier": {k.replace("tier:", ""): v for k, v in self._metrics.items() if k.startswith("tier:")},
            "by_status": {k.replace("status:", ""): v for k, v in self._metrics.items() if k.startswith("status:")},
        }

    async def run_hourly_aggregation(self):
        """تجميع البيانات كل ساعة لمنع تضخم الذاكرة"""
        snapshot = self.get_snapshot()
        self._hourly_snapshots.append(snapshot)
        
        # الاحتفاظ بآخر 24 ساعة فقط
        if len(self._hourly_snapshots) > 24:
            self._hourly_snapshots = self._hourly_snapshots[-24:]
            
        # التحقق من التنبيهات
        if snapshot["p95_latency_ms"] > 3000 or snapshot["error_count"] > 10:
            try:
                from app.observability.alert_service import send_alert
                await send_alert(
                    f"مقاييس حرجة: P95={snapshot['p95_latency_ms']}ms, أخطاء={snapshot['error_count']}",
                    severity="critical"
                )
            except: pass

        # إعادة ضبط العدادات المؤقتة
        self._active_users.clear()
        self._metrics.clear()
        logger.info("✅ Hourly metrics aggregated")


# نسخة عالمية
metrics = MetricsService()
