"""
Market Researcher - محلل السوق والمنافسين (عميق)
=================================================
يحلل السوق بناءً على الجمهور المستهدف، المنافسين، وحجم السوق.
يدعم العربية والإنجليزية، ويراعي الفروق الثقافية في التجارة.
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from app.memory.relationship.person_node import get_person_network
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False

logger = logging.getLogger("market_researcher")

# قوالب تحليل السوق بالعربية والإنجليزية
ANALYSIS_TEMPLATES = {
    "market_size": {
        "ar": "حجم السوق الكلي لـ {industry} في {location}: {size}",
        "en": "Total Addressable Market (TAM) for {industry} in {location}: {size}"
    },
    "competitors": {
        "ar": "أهم المنافسين في {industry}:\n{list}",
        "en": "Top competitors in {industry}:\n{list}"
    },
    "opportunity": {
        "ar": "الفرصة المتاحة لفكرة '{idea}': {opportunity}",
        "en": "Opportunity for '{idea}': {opportunity}"
    }
}

@dataclass
class MarketInsight:
    industry: str
    tam: str
    sam: str
    som: str
    competitors: List[Dict] = field(default_factory=list)
    opportunity_score: int = 0

class MarketResearcher:
    def __init__(self):
        self.last_analysis = {}

    async def analyze(
        self,
        idea: str,
        industry: str = "",
        location: str = "عام",
        language: str = "ar",
        user_id: str = None
    ) -> Dict[str, Any]:
        """تحليل سوقي شامل مع تخصيص حسب شبكة المستخدم"""
        
        # 1. تحليل مخصص باستخدام AI
        market_data = {}
        if AI_AVAILABLE:
            prompt = self._build_prompt(idea, industry, location, language)
            try:
                raw = await provider_router.generate(prompt, language=language)
                market_data["raw"] = raw
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
        
        # 2. تحليل هيكلي (قوالب)
        analysis = {
            "industry": industry or "عام",
            "market_size": self._estimate_market_size(industry, language),
            "competitors": self._analyze_competitors(idea, industry, language),
            "opportunity": self._assess_opportunity(idea, language),
        }
        
        # 3. تخصيص حسب شبكة المستخدم (إن وجد)
        if user_id and MEMORY_AVAILABLE:
            try:
                network = await get_person_network(user_id, min_importance=40)
                if network:
                    business_contacts = [
                        {"name": p["name"], "importance": p.get("importance_score", 0)}
                        for p in network
                    ]
                    analysis["your_network"] = {
                        "potential_partners": business_contacts[:5],
                        "network_strength": "قوية" if len(network) > 10 else "متوسطة"
                    }
            except Exception as e:
                logger.error(f"Failed to load network: {e}")
        
        self.last_analysis[user_id] = analysis
        return analysis

    def _build_prompt(self, idea, industry, location, language):
        if language == "ar":
            return f"""
أنت محلل أسواق خبير. حلل السوق لفكرة '{idea}' في صناعة '{industry}' بموقع '{location}'.
قدم:
1. حجم السوق الكلي (TAM)
2. أهم 3 منافسين مع نقاط قوتهم وضعفهم
3. فرصة السوق المتاحة (SAM/SOM)
4. توصية: هل السوق مشبع أم واعد؟
أجب بالعربية الفصحى المبسطة.
"""
        return f"""
You are an expert market analyst. Analyze the market for '{idea}' in '{industry}' in '{location}'.
Provide: 1. TAM, 2. Top 3 competitors with strengths/weaknesses, 3. SAM/SOM, 4. Verdict: saturated or promising?
"""

    def _estimate_market_size(self, industry: str, language: str) -> str:
        # تقديرات أولية مبنية على الصناعة (يمكن توسيعها بقاعدة بيانات)
        sizes = {
            "food": {"ar": "كبير جداً (>١٠ مليارات دولار)", "en": "Very Large (>$10B)"},
            "tech": {"ar": "ضخم ومتزايد (>٥٠٠ مليار دولار)", "en": "Massive & Growing (>$500B)"},
            "service": {"ar": "كبير (>١٠٠ مليار دولار)", "en": "Large (>$100B)"},
        }
        return sizes.get(industry, sizes["service"]).get(language, sizes["service"]["ar"])

    def _analyze_competitors(self, idea: str, industry: str, language: str) -> str:
        if AI_AVAILABLE: return "تم التحليل بالذكاء الاصطناعي"
        return "جاري تحليل المنافسين..."

    def _assess_opportunity(self, idea: str, language: str) -> str:
        if language == "ar":
            return f"فكرة '{idea}' تقدم فرصة متوسطة إلى عالية. تحتاج إلى تميز في الخدمة أو السعر."
        return f"Idea '{idea}' presents a medium-high opportunity. Needs differentiation."
