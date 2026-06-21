""" Business KPI Tracker - تتبع مؤشرات الأداء الرئيسية """
import logging
logger = logging.getLogger("kpi_tracker")

class BusinessKPITracker:
    async def get_default_kpis(self, industry: str) -> list:
        kpis = {
            "food": ["عدد الطلبات اليومية", "متوسط قيمة الطلب", "تكلفة المكونات"],
            "tech": ["المستخدمون النشطون", "معدل التحويل", "الإيراد الشهري المتكرر (MRR)"],
            "service": ["عدد العملاء الجدد", "معدل رضا العملاء", "الإيرادات الشهرية"],
        }
        return kpis.get(industry, kpis["service"])
