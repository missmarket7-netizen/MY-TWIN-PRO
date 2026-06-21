"""
Prompt Builder v2.0 – محرك بناء البرومبت الديناميكي المتكيف
================================================================
يبني System Prompt حي من حالة المستخدم في TCMA.
يتكيف مع العمر، اللغة، والثقافة ليكون: حكيماً، مرحاً، أو من جيل Z.
"""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("prompt_builder")

# تحميل القوالب من الملفات
def _load_template(filename: str) -> str:
    try:
        import os
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

SYSTEM_TEMPLATE = _load_template("system_v2.txt")
RELATIONSHIP_TEMPLATE = _load_template("relationship_v2.txt")
JOURNEY_TEMPLATE = _load_template("journey_v2.txt")

class PromptBuilder:
    async def build(
        self,
        user_id: str,
        message: str,
        lang: str = "ar",
        twin_name: str = "توأمك",
    ) -> str:
        """بناء System Prompt متكامل من الذاكرة الحية"""
        
        # 1. تحديد نمط الشخصية المناسب
        persona = await self._detect_persona(user_id, message, lang)

        # 2. بناء أجزاء البرومبت
        parts = [SYSTEM_TEMPLATE, persona.get("instructions", "")]

        # 3. ملء قالب العلاقة
        relationship_prompt = await self._build_relationship_prompt(user_id)
        if relationship_prompt:
            parts.append(relationship_prompt)

        # 4. ملء قالب الرحلة
        journey_prompt = await self._build_journey_prompt(user_id)
        if journey_prompt:
            parts.append(journey_prompt)

        # 5. إضافة سياق الزمان والمكان
        temporal_context = self._build_temporal_context()
        if temporal_context:
            parts.append(temporal_context)

        return "\n\n".join(parts)

    async def _detect_persona(self, user_id: str, message: str, lang: str) -> Dict[str, str]:
        """
        يحدد شخصية التوأم المناسبة بناءً على أسلوب المستخدم.
        يدعم: sage (حكيم)، genz (مرح/شبابي)، default (متوازن).
        """
        msg_lower = message.lower()
        
        # كشف أسلوب Gen Z / المرح
        genz_keywords = ["😂", "🔥", "مضحك", "ههه", "funny", "lol", "chill", "vibe", "cool"]
        genz_arabic = ["والله", "ياعم", "جداً", "يلا", "حبيبي", "روق"]
        
        is_genz = any(kw in msg_lower for kw in genz_keywords + genz_arabic)
        
        # كشف أسلوب الحكمة / العمق
        sage_keywords = ["معنى", "هدف", "حياة", "مستقبل", "قرار", "wisdom", "purpose", "deep", "philosophy"]
        sage_arabic = ["الحكمة", "تأمل", "تفكر", "نصيحة"]
        
        is_sage = any(kw in msg_lower for kw in sage_keywords + sage_arabic)

        if is_genz:
            return {
                "style": "genz",
                "instructions": "[شخصيتك الآن: مرح، شبابي، Gen Z]\n- استخدم الإيموجي والتعبيرات العصرية.\n- تحدث كصديق مقرب من جيله.\n- استخدم كلمات مثل 'فايبز'، 'أجواء'، 'يلا'.\n- كن خفيف الظل ومباشر."
            }
        elif is_sage:
            return {
                "style": "sage",
                "instructions": "[شخصيتك الآن: حكيم، عميق، متأمل]\n- تحدث بلغة فلسفية هادئة.\n- اطرح أسئلة عميقة.\n- استخدم الاقتباسات والأمثال.\n- كن ملاذاً للتفكر."
            }
        else:
            return {
                "style": "default",
                "instructions": "[شخصيتك الآن: متوازن، ذكي، داعم]\n- توازن بين المرح والعمق.\n- تكيف مع مزاج المستخدم.\n- كن الصديق الذي يحتاجه."
            }

    async def _build_relationship_prompt(self, user_id: str) -> str:
        try:
            from app.memory.relationship.relationship_memory import get_relationship_insights
            from app.memory.relationship.person_node import get_person_network
            from app.memory.relationship.attachment_model import detect_attachment_style
            from app.memory.reflection.reflection_engine import get_user_insights

            rel = await get_relationship_insights(user_id)
            people = await get_person_network(user_id, min_importance=30)
            attachment = await detect_attachment_style(user_id)
            insights = await get_user_insights(user_id, min_confidence=0.6)

            return RELATIONSHIP_TEMPLATE.format(
                stage=rel.get("trend", "مستقرة"),
                trust=rel.get("trust_level", 50),
                openness=rel.get("openness_level", 50),
                attachment_style=attachment.get("style", "غير معروف"),
                important_people=", ".join([p["name"] for p in people[:5]]) if people else "لا يوجد",
                latest_insight=insights.get("insights", [{}])[0].get("text", "لا يوجد") if insights.get("insights") else "لا يوجد"
            )
        except Exception as e:
            logger.warning(f"Relationship prompt failed: {e}")
            return ""

    async def _build_journey_prompt(self, user_id: str) -> str:
        try:
            from app.twin_state.journey_service import get_current_phase, get_behavior, get_daily_message

            phase = await get_current_phase(user_id)
            behavior = await get_behavior(phase)
            daily = await get_daily_message(phase)

            return JOURNEY_TEMPLATE.format(
                phase=phase,
                behaviors=str(behavior),
                daily_message=daily
            )
        except Exception as e:
            logger.warning(f"Journey prompt failed: {e}")
            return ""

    def _build_temporal_context(self) -> str:
        try:
            from app.features.temporal_context import temporal_engine
            ctx = temporal_engine.get_current_context("")
            return f"[سياق زمني]\n- الوقت: {ctx.get('time_of_day', '')}\n- اليوم: {ctx.get('day_type', '')}\n- الموسم: {ctx.get('season', '')}"
        except:
            return ""


# نسخة عالمية
prompt_builder = PromptBuilder()
logger.info("✅ Prompt Builder v2.0 with Gen Z & Sage initialized")
