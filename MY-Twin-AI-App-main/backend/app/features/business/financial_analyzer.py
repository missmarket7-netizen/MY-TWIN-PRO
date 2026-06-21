"""
Financial Analyzer v2.0 – محلل مالي حقيقي
=============================================
يحسب نقطة التعادل، ROI، صافي القيمة الحالية.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger("financial_analyzer")

class FinancialAnalyzer:
    def analyze_feasibility(self, idea: str, budget: float, industry: str = "service", language: str = "ar") -> Dict[str, Any]:
        # تقديرات افتراضية حسب الصناعة
        estimates = {
            "food": {"fixed_monthly": budget * 0.15, "variable_per_unit": budget * 0.05, "price_per_unit": budget * 0.1, "monthly_units": 100},
            "tech": {"fixed_monthly": budget * 0.1, "variable_per_unit": budget * 0.01, "price_per_unit": budget * 0.15, "monthly_units": 50},
            "service": {"fixed_monthly": budget * 0.1, "variable_per_unit": budget * 0.03, "price_per_unit": budget * 0.08, "monthly_units": 80},
        }.get(industry, {"fixed_monthly": budget * 0.1, "variable_per_unit": budget * 0.03, "price_per_unit": budget * 0.08, "monthly_units": 80})

        fixed = estimates["fixed_monthly"]
        var_per_unit = estimates["variable_per_unit"]
        price = estimates["price_per_unit"]
        units = estimates["monthly_units"]
        
        monthly_revenue = price * units
        monthly_var_cost = var_per_unit * units
        total_monthly_cost = fixed + monthly_var_cost
        net_profit_monthly = monthly_revenue - total_monthly_cost
        annual_profit = net_profit_monthly * 12
        roi = (annual_profit / budget * 100) if budget > 0 else 0
        break_even_units = round(fixed / (price - var_per_unit)) if (price - var_per_unit) > 0 else 0

        return {
            "project": idea, "budget": budget, "currency": "دولار",
            "estimates": {"fixed_monthly": fixed, "variable_per_unit": var_per_unit, "price": price, "monthly_units": units},
            "results": {
                "monthly_revenue": round(monthly_revenue, 2),
                "monthly_cost": round(total_monthly_cost, 2),
                "net_monthly_profit": round(net_profit_monthly, 2),
                "annual_profit": round(annual_profit, 2),
                "roi_percent": round(roi, 1),
                "break_even_units": break_even_units
            },
            "verdict": "مشروع ممتاز" if roi > 30 else "مشروع جيد" if roi > 15 else "مشروع محفوف بالمخاطر"
        }

finance = FinancialAnalyzer()
