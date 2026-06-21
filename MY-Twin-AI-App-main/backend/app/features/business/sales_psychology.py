"""
Sales Psychology Engine - محرك البيع النفسي
============================================
يخصص استراتيجيات البيع حسب شخصية رائد الأعمال.
يدعم الأسواق العربية والغربية.
"""
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

logger = logging.getLogger("sales_psychology")

# أنماط الشخصية واستراتيجيات البيع المناسبة
PERSONALITY_SALES_MAP = {
    "high_risk": {
        "ar": ["بيع استشاري", "عروض محدودة", "شراكة طويلة الأجل"],
        "en": ["Consultative selling", "Limited offers", "Long-term partnerships"]
    },
    "low_risk": {
        "ar": ["بيع تدريجي", "تجربة مجانية", "ضمان استرداد المال"],
        "en": ["Gradual selling", "Free trials", "Money-back guarantee"]
    },
    "social": {
        "ar": ["تسويق شفهي", "مجموعات فيسبوك", "تعاون مع مؤثرين"],
        "en": ["Word of mouth", "Facebook groups", "Influencer collaborations"]
    },
}

class SalesPsychologyEngine:
    def __init__(self):
        pass

    async def create_marketing_plan(
        self,
        idea: str,
        profile,
        budget: float,
        language: str = "ar"
    ) -> Dict[str, Any]:
        """خطة تسويق مخصصة للشخصية"""
        
        risk = profile.risk_tolerance if hasattr(profile, 'risk_tolerance') else "medium"
        traits = profile.identity_traits if hasattr(profile, 'identity_traits') else []
        
        # اختيار الاستراتيجيات المناسبة
        strategies = []
        if risk == "high":
            strategies = PERSONALITY_SALES_MAP["high_risk"]
        elif risk == "low":
            strategies = PERSONALITY_SALES_MAP["low_risk"]
        else:
            strategies = PERSONALITY_SALES_MAP["social"]
        
        # دمج مع الذكاء الاصطناعي
        plan = {
            "personality_based_strategies": strategies.get(language, strategies["ar"]),
            "budget_allocation": {
                "digital": f"{budget * 0.6:.0f}" if budget > 0 else "0",
                "traditional": f"{budget * 0.4:.0f}" if budget > 0 else "0",
            }
        }
        
        if AI_AVAILABLE:
            prompt = self._build_plan_prompt(idea, risk, traits, budget, language)
            try:
                plan["detailed_plan"] = await provider_router.generate(prompt, language=language)
            except Exception as e:
                logger.error(f"AI marketing plan failed: {e}")
        
        return plan

    def _build_plan_prompt(self, idea, risk, traits, budget, language):
        if language == "ar":
            return f"""
أنشئ خطة تسويقية مفصلة لرائد أعمال '{'، '.join(traits) if traits else 'عملي'}'
يميل إلى المخاطرة '{risk}'، لمشروع '{idea}' بميزانية {budget}.
قدم استراتيجيات رقمية (سوشيال ميديا، إعلانات) وتقليدية (منشورات، شراكات).
"""
        return f"""
Create a detailed marketing plan for an entrepreneur with traits '{traits}',
risk tolerance '{risk}', for project '{idea}' with budget {budget}.
Provide digital and traditional strategies.
"""
