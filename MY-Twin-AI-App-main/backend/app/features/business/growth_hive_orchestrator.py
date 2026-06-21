"""
GrowthHiveOrchestrator - عقل الأعمال المتكامل
==============================================
ينسق بين طبقات البحث، التحليل، التسويق، المبيعات، والمتابعة.
يتكامل مع الذاكرة العاطفية وشبكة العلاقات لتخصيص النصائح.
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field

try:
    from app.infrastructure.ai.provider_router import provider_router
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

try:
    from app.memory.identity.identity_model import get_identity
    from app.memory.emotional.emotional_memory import get_emotional_state_for_response, store_emotional_memory
    from app.memory.relationship.person_node import process_message_for_persons, get_person_network
    from app.memory.relationship.relationship_memory import get_relationship_context_for_response
    from app.memory.reflection.reflection_engine import process_message_for_reflections
    from app.memory.graph.memory_graph import auto_create_edges_from_memory
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

try:
    from app.features.business.market_researcher import MarketResearcher
    from app.features.business.financial_analyzer import FinancialAnalyzer
    from app.features.business.business_canvas_generator import BusinessCanvasGenerator
    from app.features.business.sales_psychology import SalesPsychologyEngine
    from app.features.business.business_kpi_tracker import BusinessKPITracker
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False

logger = logging.getLogger("growth_hive")

# ============================================================
# هياكل البيانات
# ============================================================
@dataclass
class EntrepreneurProfile:
    """ملف رائد الأعمال المستخلص من الذاكرة"""
    identity_traits: List[str] = field(default_factory=list)
    risk_tolerance: str = "medium"          # low, medium, high
    social_network_strength: int = 0
    current_emotion: str = "neutral"
    preferred_domain: str = "general"       # tech, food, service, etc.
    business_experience: str = "beginner"   # beginner, intermediate, expert

@dataclass
class VentureProject:
    """حالة المشروع الحالي"""
    name: str
    stage: str = "ideation"                # ideation, planning, launching, growing, scaling
    industry: str = ""
    business_model: Dict = field(default_factory=dict)
    swot: Dict = field(default_factory=dict)
    financials: Dict = field(default_factory=dict)
    kpis: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class GrowthHiveOrchestrator:
    """المايسترو - يدير جميع خدمات الأعمال"""
    def __init__(self):
        self.active_projects: Dict[str, VentureProject] = {}
        if SERVICES_AVAILABLE:
            self.market = MarketResearcher()
            self.finance = FinancialAnalyzer()
            self.canvas = BusinessCanvasGenerator()
            self.sales = SalesPsychologyEngine()
            self.kpi = BusinessKPITracker()
        logger.info("🐝 GrowthHive Orchestrator initialized")

    async def build_entrepreneur_profile(self, user_id: str, language: str = "ar") -> EntrepreneurProfile:
        """يبني ملف رائد الأعمال من طبقات الذاكرة"""
        profile = EntrepreneurProfile()
        if not TCMA_AVAILABLE: return profile
        
        try:
            identity = await get_identity(user_id)
            if identity:
                traits = identity.get("traits", [])
                profile.identity_traits = traits
                # استنتاج تحمل المخاطر
                if any(t in ["مغامر", "bold", "شجاع"] for t in traits):
                    profile.risk_tolerance = "high"
                elif any(t in ["حذر", "cautious", "متردد"] for t in traits):
                    profile.risk_tolerance = "low"
                # استنتاج المجال المفضل
                if any(t in ["تقني", "مبرمج", "tech"] for t in traits):
                    profile.preferred_domain = "tech"
                elif any(t in ["اجتماعي", "social", "طباخ"] for t in traits):
                    profile.preferred_domain = "food"
            
            emotion = await get_emotional_state_for_response(user_id, "")
            if emotion:
                profile.current_emotion = emotion.get("current_emotion", "neutral")
            
            network = await get_person_network(user_id, min_importance=20)
            profile.social_network_strength = len(network) if network else 0
            
        except Exception as e:
            logger.error(f"فشل بناء ملف رائد الأعمال: {e}")
        return profile

    async def _generate_with_ai(self, prompt: str, language: str = "ar") -> str:
        """استدعاء الذكاء الاصطناعي لتوليد الرد"""
        if not AI_AVAILABLE:
            return ""
        try:
            return await provider_router.generate(prompt, language=language) or ""
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return ""

    async def _update_memory(self, user_id: str, message: str, context_type: str, emotion: str = "neutral"):
        """تحديث الذاكرة العاطفية والاستنتاجات"""
        if not TCMA_AVAILABLE: return
        try:
            await store_emotional_memory(
                user_id=user_id, expressed_text=message,
                detected_emotion={"primary": emotion, "intensity": 0.5, "valence": 0.0},
                trigger=context_type, cultural_context=f"أعمال: {context_type}"
            )
            await process_message_for_reflections(
                user_id=user_id, message=message, language="ar", detected_emotion=emotion
            )
        except Exception as e:
            logger.error(f"Memory update failed: {e}")

logger.info("✅ GrowthHive Orchestrator Part 1 loaded")

    # ============================================================
    # المرحلة 1: GUIDE & RESEARCH - توليد فكرة المشروع
    # ============================================================
    async def generate_business_idea(
        self, user_id: str, budget: float, interests: str = "",
        location: str = "", language: str = "ar"
    ) -> Dict[str, Any]:
        """يولد أفكار مشاريع بناءً على الميزانية والاهتمامات"""
        
        profile = await self.build_entrepreneur_profile(user_id, language)
        await self._update_memory(user_id, f"يبحث عن فكرة مشروع بميزانية {budget}", "business_idea", "curious")
        
        ideas = []
        if AI_AVAILABLE:
            prompt = f"""
أنت خبير تطوير أعمال. أنشئ 3 أفكار مشاريع لرائد أعمال في {location} بميزانية {budget}.
اهتماماته: {interests or profile.preferred_domain}.
شخصيته: {', '.join(profile.identity_traits) if profile.identity_traits else 'عامة'}.
قدم كل فكرة باختصار: الاسم، الوصف، التكلفة التقريبية، والميزة التنافسية.
اللغة: {language}.
"""
            response = await self._generate_with_ai(prompt, language)
            # تحليل الأفكار من النص (نسخة مبسطة)
            if response:
                ideas = [{"title": line.strip()} for line in response.split("\n") if line.strip()][:3]
        
        return {
            "budget": budget,
            "profile_risk": profile.risk_tolerance,
            "ideas": ideas,
            "recommendation": f"نظراً لشخصيتك {profile.risk_tolerance} المخاطر، ركز على الأفكار ذات رأس المال المنخفض."
        }

    # ============================================================
    # المرحلة 2: OPTIMIZE - تحليل السوق ودراسة الجدوى
    # ============================================================
    async def analyze_market_opportunity(
        self, user_id: str, idea: str, industry: str = "", language: str = "ar"
    ) -> Dict[str, Any]:
        """تحليل السوق والمنافسين للفكرة المختارة"""
        
        await self._update_memory(user_id, f"يحلل السوق لفكرة: {idea}", "market_research", "focused")
        
        # إنشاء مشروع جديد
        project = VentureProject(name=idea, industry=industry, stage="planning")
        self.active_projects[user_id] = project
        
        analysis = {}
        if SERVICES_AVAILABLE:
            analysis = await self.market.analyze(idea, industry, language)
        elif AI_AVAILABLE:
            prompt = f"حلل السوق والمنافسين لفكرة '{idea}' في صناعة '{industry}'. أذكر حجم السوق، أهم 3 منافسين، والفرصة المتاحة. اللغة: {language}."
            text = await self._generate_with_ai(prompt, language)
            analysis = {"raw_analysis": text}
        
        return {
            "idea": idea,
            "analysis": analysis,
            "next_step": "قم باختيار الفكرة لننتقل إلى دراسة الجدوى المالية."
        }

    # ============================================================
    # المرحلة 3: WIN - دراسة الجدوى المالية
    # ============================================================
    async def generate_feasibility_study(
        self, user_id: str, idea: str, budget: float, language: str = "ar"
    ) -> Dict[str, Any]:
        """دراسة جدوى مالية شاملة"""
        
        await self._update_memory(user_id, f"يعد دراسة جدوى لـ {idea}", "feasibility", "excited")
        
        study = {}
        if SERVICES_AVAILABLE:
            study = await self.finance.analyze_feasibility(idea, budget, language)
        elif AI_AVAILABLE:
            prompt = f"""
أعدد دراسة جدوى مبسطة لمشروع '{idea}' بميزانية {budget}.
تشمل: التكاليف الثابتة، التكاليف المتغيرة، الإيرادات المتوقعة، نقطة التعادل، وصافي الربح الشهري المتوقع.
اللغة: {language}. قدم الأرقام بشكل واضح.
"""
            text = await self._generate_with_ai(prompt, language)
            study = {"raw_feasibility": text}
        
        return {
            "idea": idea,
            "budget": budget,
            "feasibility": study,
            "next_step": "إذا كانت الأرقام مقبولة، يمكننا بناء نموذج العمل التجاري."
        }

    # ============================================================
    # المرحلة 4: نموذج العمل التجاري (Business Model Canvas)
    # ============================================================
    async def generate_business_canvas(
        self, user_id: str, idea: str, language: str = "ar"
    ) -> Dict[str, Any]:
        """توليد نموذج العمل التجاري (Business Model Canvas)"""
        
        await self._update_memory(user_id, f"يبني نموذج العمل لـ {idea}", "canvas", "analytical")
        
        canvas = {}
        if SERVICES_AVAILABLE:
            canvas = await self.canvas.generate(idea, language)
        elif AI_AVAILABLE:
            prompt = f"أنشئ نموذج العمل التجاري (Business Model Canvas) لمشروع '{idea}' باللغة {language}. غطِّ جميع العناصر التسعة."
            text = await self._generate_with_ai(prompt, language)
            canvas = {"raw_canvas": text}
        
        # تحديث المشروع النشط
        if user_id in self.active_projects:
            self.active_projects[user_id].business_model = canvas
        
        return {"idea": idea, "canvas": canvas, "next_step": "لننتقل إلى خطة التسويق والمبيعات."}

logger.info("✅ GrowthHive Orchestrator Part 2 loaded")

    # ============================================================
    # المرحلة 5: TRACK & WIN - خطة التسويق والمبيعات
    # ============================================================
    async def generate_marketing_plan(
        self, user_id: str, idea: str, budget: float = 0, language: str = "ar"
    ) -> Dict[str, Any]:
        """خطة تسويق ومبيعات مخصصة"""
        
        profile = await self.build_entrepreneur_profile(user_id, language)
        await self._update_memory(user_id, f"يخطط لتسويق {idea}", "marketing", "motivated")
        
        plan = {}
        if SERVICES_AVAILABLE:
            plan = await self.sales.create_marketing_plan(idea, profile, budget, language)
        elif AI_AVAILABLE:
            prompt = f"""
أنشئ خطة تسويقية لمشروع '{idea}' لرائد أعمال شخصيته {profile.risk_tolerance} المخاطر.
الميزانية التسويقية: {budget}.
شبكة علاقاته: {profile.social_network_strength} شخص.
قدم استراتيجيات رقمية وتقليدية مناسبة للميزانية. اللغة: {language}.
"""
            text = await self._generate_with_ai(prompt, language)
            plan = {"raw_plan": text}
        
        return {"idea": idea, "plan": plan}

    async def sales_roleplay(
        self, user_id: str, scenario: str, language: str = "ar"
    ) -> Dict[str, Any]:
        """محاكاة عملية بيع مع عميل افتراضي"""
        
        await self._update_memory(user_id, f"يتدرب على البيع: {scenario}", "sales_training", "anxious")
        
        script = ""
        if AI_AVAILABLE:
            prompt = f"أنت عميل صعب المراس. أنشئ حواراً تدريبياً لرائد الأعمال حول '{scenario}'. ابدأ كعميل. اللغة: {language}."
            script = await self._generate_with_ai(prompt, language)
        
        return {"scenario": scenario, "script": script}

    # ============================================================
    # المرحلة 6: HUMANIZE - الدعم النفسي والتذكير بالإنجازات
    # ============================================================
    async def entrepreneurial_support(self, user_id: str, language: str = "ar") -> Dict[str, Any]:
        """دعم نفسي مخصص لرائد الأعمال"""
        
        profile = await self.build_entrepreneur_profile(user_id, language)
        emotion = profile.current_emotion
        
        support_message = ""
        if AI_AVAILABLE:
            prompt = f"""
رائد أعمال يشعر بـ {emotion}. شخصيته: {', '.join(profile.identity_traits) if profile.identity_traits else 'طموح'}.
قدم رسالة دعم وتحفيز قصيرة. تذكر أن ريادة الأعمال رحلة صعبة. اللغة: {language}.
"""
            support_message = await self._generate_with_ai(prompt, language)
        
        await self._update_memory(user_id, "تلقى دعماً نفسياً", "support", emotion)
        
        return {"emotion": emotion, "message": support_message or "أنت تقوم بعمل رائع. استمر!"}

    # ============================================================
    # المرحلة 7: INTEGRATED VENTURE ENGINE - تقرير المشروع المتكامل
    # ============================================================
    async def venture_report(self, user_id: str, language: str = "ar") -> Dict[str, Any]:
        """تقرير متكامل عن حالة المشروع"""
        
        project = self.active_projects.get(user_id)
        if not project:
            return {"error": "لا يوجد مشروع نشط"}
        
        report = {
            "project_name": project.name,
            "stage": project.stage,
            "business_model_complete": bool(project.business_model),
            "financials_complete": bool(project.financials),
            "kpis": project.kpis,
        }
        
        # دمج مع الرسم البياني للذاكرة (أحداث متعلقة بالمشروع)
        if TCMA_AVAILABLE:
            try:
                from app.memory.graph.memory_graph import get_memory_cluster
                # افتراضي - سيتم التوسع لاحقاً
                report["memory_cluster"] = {"nodes": 0, "edges": 0}
            except:
                pass
        
        return report

# نسخة عالمية
growth_hive = GrowthHiveOrchestrator()
logger.info("🐝 GrowthHive Orchestrator fully initialized")
