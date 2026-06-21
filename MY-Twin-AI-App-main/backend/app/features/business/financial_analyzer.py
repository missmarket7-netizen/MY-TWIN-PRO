"""
Financial Analyzer - المحلل المالي الشامل
===========================================
يحسب التكاليف، الإيرادات، نقطة التعادل، والعائد على الاستثمار.
يدعم العملات المختلفة والمصطلحات المالية العربية والإنجليزية.
"""
import logging
from typing import Dict, Any, Optional

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

logger = logging.getLogger("financial_analyzer")

# مصطلحات مالية بالعربية والإنجليزية
FINANCIAL_TERMS = {
    "break_even": {"ar": "نقطة التعادل", "en": "Break-Even Point"},
    "roi": {"ar": "العائد على الاستثمار", "en": "Return on Investment (ROI)"},
    "profit_margin": {"ar": "هامش الربح", "en": "Profit Margin"},
    "fixed_cost": {"ar": "تكاليف ثابتة", "en": "Fixed Costs"},
    "variable_cost": {"ar": "تكاليف متغيرة", "en": "Variable Costs"},
}

class FinancialAnalyzer:
    def __init__(self):
        pass

    async def analyze_feasibility(
        self,
        idea: str,
        budget: float,
        language: str = "ar",
        industry: str = "",
        currency: str = "جنيه"
    ) -> Dict[str, Any]:
        """دراسة جدوى مالية شاملة مع حسابات دقيقة"""
        
        # 1. تحليل ذكي لتقدير التكاليف والإيرادات
        ai_estimates = {}
        if AI_AVAILABLE:
            prompt = self._build_ai_prompt(idea, budget, language, currency)
            try:
                raw = await provider_router.generate(prompt, language=language)
                ai_estimates["ai_analysis"] = raw
            except Exception as e:
                logger.error(f"AI financial analysis failed: {e}")
        
        # 2. حسابات مالية فعلية
        # تقدير افتراضي للصناعات المختلفة (يمكن تخصيصه)
        estimates = self._industry_estimates(industry, budget)
        
        # حساب نقطة التعادل
        break_even_units = 0
        if estimates.get("price_per_unit") and estimates.get("variable_cost_per_unit"):
            cm = estimates["price_per_unit"] - estimates["variable_cost_per_unit"]
            if cm > 0:
                break_even_units = estimates["fixed_costs"] / cm
        
        # حساب صافي الربح الشهري
        monthly_revenue = estimates.get("monthly_revenue", 0)
        monthly_costs = estimates.get("fixed_costs", 0) + estimates.get("variable_costs_total", 0)
        net_profit = monthly_revenue - monthly_costs
        
        # حساب العائد على الاستثمار (ROI)
        investment = max(budget, estimates.get("initial_investment", budget))
        annual_profit = net_profit * 12
        roi = (annual_profit / investment * 100) if investment > 0 else 0
        
        return {
            "project": idea,
            "currency": currency,
            "budget": budget,
            "estimates": {
                "initial_investment": investment,
                "monthly_fixed_costs": estimates.get("fixed_costs", 0),
                "monthly_variable_costs": estimates.get("variable_costs_total", 0),
                "price_per_unit": estimates.get("price_per_unit", 0),
                "monthly_revenue_estimate": monthly_revenue,
            },
            "analysis": {
                "break_even_units": round(break_even_units),
                "break_even_label": self._term("break_even", language),
                "net_monthly_profit": round(net_profit, 2),
                "net_annual_profit": round(annual_profit, 2),
                "roi_percent": round(roi, 1),
                "roi_label": self._term("roi", language),
                "profit_margin_percent": round((net_profit / monthly_revenue * 100) if monthly_revenue else 0, 1),
                "profit_margin_label": self._term("profit_margin", language),
            },
            "verdict": self._verdict(roi, net_profit, language),
            **ai_estimates
        }

    def _build_ai_prompt(self, idea, budget, language, currency):
        if language == "ar":
            return f"""
أنت محلل مالي خبير. أعدد دراسة جدوى مبسطة لمشروع '{idea}' بميزانية {budget} {currency}.
قدم تقديرات: التكاليف الثابتة، التكاليف المتغيرة، الإيرادات المتوقعة، نقطة التعادل، وصافي الربح.
أجب بالأرقام والتحليل المالي الواضح.
"""
        return f"""
You are an expert financial analyst. Create a feasibility study for '{idea}' with budget {budget} {currency}.
Provide: fixed costs, variable costs, expected revenue, break-even point, and net profit.
"""

    def _industry_estimates(self, industry: str, budget: float) -> Dict[str, float]:
        """تقديرات افتراضية حسب الصناعة"""
        if industry == "food":
            return {
                "fixed_costs": budget * 0.2,
                "variable_costs_total": budget * 0.4,
                "variable_cost_per_unit": budget * 0.05,
                "price_per_unit": budget * 0.1,
                "monthly_revenue": budget * 0.8,
                "initial_investment": budget,
            }
        elif industry == "tech":
            return {
                "fixed_costs": budget * 0.1,
                "variable_costs_total": budget * 0.1,
                "variable_cost_per_unit": budget * 0.001,
                "price_per_unit": budget * 0.05,
                "monthly_revenue": budget * 0.5,
                "initial_investment": budget * 1.2,
            }
        else:  # service
            return {
                "fixed_costs": budget * 0.15,
                "variable_costs_total": budget * 0.3,
                "variable_cost_per_unit": budget * 0.02,
                "price_per_unit": budget * 0.06,
                "monthly_revenue": budget * 0.6,
                "initial_investment": budget,
            }

    def _term(self, key: str, language: str) -> str:
        """يجلب المصطلح المالي باللغة المناسبة"""
        return FINANCIAL_TERMS.get(key, {}).get(language, key)

    def _verdict(self, roi: float, net_profit: float, language: str) -> str:
        if roi > 50:
            return "مشروع ممتاز، موصى به بشدة" if language == "ar" else "Excellent project, highly recommended"
        elif roi > 20:
            return "مشروع جيد، جدير بالاستثمار" if language == "ar" else "Good project, worth investing"
        else:
            return "مشروع محفوف بالمخاطر، يحتاج إعادة تقييم" if language == "ar" else "Risky project, needs re-evaluation"
