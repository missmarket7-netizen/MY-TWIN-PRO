"""
Sales Psychology Engine v2.0 – محرك مبيعات حقيقي
=====================================================
يخصص استراتيجيات البيع حسب شخصية المستخدم ومرحلة المشروع.
"""
import logging
from typing import Dict, Any, List

logger = logging.getLogger("sales_psychology")

# صيغ البيع النفسية
SALES_FORMULAS = {
    "AIDA": ["جذب الانتباه", "إثارة الاهتمام", "خلق الرغبة", "دعوة للشراء"],
    "PAS": ["تحديد المشكلة", "تضخيم المشكلة", "تقديم الحل"],
    "FOMO": ["خلق شعور بالخوف من التفويت", "عرض محدود", "إثبات اجتماعي"],
    "BAB": ["قبل المنتج", "بعد المنتج", "الجسر بينهما"]
}

class SalesPsychologyEngine:
    def __init__(self):
        pass

    def create_marketing_plan(self, idea: str, profile, budget: float, language: str = "ar") -> Dict[str, Any]:
        risk = profile.get("risk_tolerance", "medium") if isinstance(profile, dict) else getattr(profile, "risk_tolerance", "medium")
        
        # اختيار الصيغة المناسبة حسب الشخصية
        if risk == "high":
            recommended_formula = "AIDA"
        elif risk == "low":
            recommended_formula = "PAS"
        else:
            recommended_formula = "FOMO"

        plan = {
            "product": idea,
            "budget": budget,
            "recommended_formula": recommended_formula,
            "formula_steps": SALES_FORMULAS.get(recommended_formula, SALES_FORMULAS["AIDA"]),
            "channels": {
                "digital": ["فيسبوك", "انستغرام", "تيك توك"] if budget > 500 else ["فيسبوك"],
                "traditional": ["منشورات", "شراكات محلية"] if budget > 1000 else []
            },
            "daily_budget_allocation": f"{budget * 0.7:.0f} للتسويق الرقمي، {budget * 0.3:.0f} للتقليدي"
        }
        return plan

sales = SalesPsychologyEngine()
