"""
CreatorOrchestrator v2.0 - عقل الكتابة الإبداعية والرقمية المتكامل
=====================================================================
يدعم: الرواية، القصة، البحث، الكتاب، الفيديو، التدوين، التسويق.
يتكامل مع نظريات (رحلة البطل، البناء الدرامي) وعلم النفس (النماذج البدئية).
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
    from app.memory.relationship.person_node import get_person_network
    TCMA_AVAILABLE = True
except ImportError:
    TCMA_AVAILABLE = False

logger = logging.getLogger("creator_orchestrator")

# ============================================================
# محرك النظريات الأدبية (WriterTheoryEngine)
# ============================================================
class WriterTheoryEngine:
    """يضخ نظريات أدبية وفلسفية في عملية الكتابة"""
    
    THEORIES = {
        "heros_journey": {
            "ar": ["العالم العادي", "الدعوة إلى المغامرة", "رفض الدعوة", "لقاء المرشد", "تجاوز العتبة", "الاختبارات", "الاقتراب من الكهف", "المحنة", "المكافأة", "طريق العودة", "البعث", "العودة بالإكسير"],
            "en": ["Ordinary World", "Call to Adventure", "Refusal", "Mentor", "Crossing Threshold", "Tests", "Approach", "Ordeal", "Reward", "Road Back", "Resurrection", "Return with Elixir"]
        },
        "three_act": {
            "ar": ["التهيئة", "المواجهة", "الحل"],
            "en": ["Setup", "Confrontation", "Resolution"]
        },
        "archetypes": {
            "ar": {"البطل": "يسعى للخير", "الظل": "الجانب المظلم", "المخادع": "يخلق الفوضى"},
            "en": {"Hero": "Seeks good", "Shadow": "Dark side", "Trickster": "Creates chaos"}
        }
    }

    def apply_theory(self, outline: str, theory: str, lang: str) -> str:
        """يطبق نظرية على الهيكل"""
        stages = self.THEORIES.get(theory, {}).get(lang, [])
        if not stages: return outline
        return f"هيكل القصة مبني على '{theory}':\n" + "\n".join(f"{i+1}. {s}" for i, s in enumerate(stages))

# ============================================================
# محول المحتوى الرقمي (DigitalContentAdapter)
# ============================================================
class DigitalContentAdapter:
    """يكيّف الكتابة للمنصات الرقمية المختلفة"""
    
    FORMATS = {
        "youtube_script": {
            "ar": "أسلوب حواري، مقدمة قوية (Hook)، محتوى قيم، دعوة للإعجاب والاشتراك.",
            "en": "Conversational style, Strong Hook, Value, Call to Action."
        },
        "instagram_post": {
            "ar": "مختصر، بصري، هاشتاقات، Emojis، سؤال تفاعلي.",
            "en": "Short, Visual, Hashtags, Emojis, Engaging Question."
        },
        "product_description": {
            "ar": "ميزات، فوائد، كلمات مفتاحية، دعوة للشراء.",
            "en": "Features, Benefits, Keywords, Call to Purchase."
        },
        "research_paper": {
            "ar": "لغة أكاديمية، مقدمة، منهجية، نتائج، مناقشة، مراجع.",
            "en": "Academic tone, Abstract, Methodology, Results, Discussion, References."
        }
    }

    def adapt_prompt(self, base_prompt: str, format_type: str, lang: str) -> str:
        """يضيف تعليمات التنسيق للذكاء الاصطناعي"""
        rules = self.FORMATS.get(format_type, {}).get(lang, "")
        return f"التنسيق المطلوب: {rules}\n\n---\n{base_prompt}"

# ============================================================
# خدمة الترجمة والتلخيص (Polyglot)
# ============================================================
class PolyglotService:
    """الترجمة والتلخيص الفوري"""
    
    async def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        if not AI_AVAILABLE: return "خدمة الترجمة غير متاحة"
        prompt = f"ترجم النص التالي من {source_lang} إلى {target_lang} مع الحفاظ على الروح الأدبية:\n{text}"
        return await provider_router.generate(prompt, language=target_lang)

    async def summarize(self, text: str, style: str = "bullet", lang: str = "ar") -> str:
        if not AI_AVAILABLE: return "خدمة التلخيص غير متاحة"
        prompt = f"لخص النص التالي بأسلوب '{style}' باللغة {lang}:\n{text}"
        return await provider_router.generate(prompt, language=lang)

# ============================================================
# المايسترو (CreatorOrchestrator v2.0)
# ============================================================
@dataclass
class ContentProject:
    title: str
    type: str
    genre: str = ""
    audience: str = "general"
    language: str = "ar"
    theory: str = ""
    outline: str = ""

class CreatorOrchestrator:
    def __init__(self):
        self.active_projects: Dict[str, ContentProject] = {}
        self.theories = WriterTheoryEngine()
        self.adapter = DigitalContentAdapter()
        self.polyglot = PolyglotService()

    async def get_user_writing_profile(self, user_id: str) -> Dict[str, Any]:
        if not TCMA_AVAILABLE: return {}
        try:
            identity = await get_identity(user_id)
            traits = identity.get("traits", []) if identity else []
            style = "أدبي" if any(t in traits for t in ["فني", "شاعر", "كاتب"]) else "عملي"
            people = await get_person_network(user_id, min_importance=50)
            return {"traits": traits, "preferred_style": style, "important_people": people}
        except: return {}

    async def generate_outline(self, user_id: str, title: str, type: str, genre: str = "", language: str = "ar", theory: str = "", format_type: str = "") -> Dict[str, Any]:
        profile = await self.get_user_writing_profile(user_id)
        
        # 1. بناء الهيكل الأساسي
        prompt = f"""أنشئ هيكلاً تفصيلياً ل{type} بعنوان "{title}" (نوع: {genre}، جمهور: {profile.get('audience', 'عام')}).
        قدم مقدمة، 5-10 فصول/أقسام، وخاتمة. اللغة: {language}."""
        
        # 2. تطبيق النظرية الأدبية (إن وجدت)
        if theory:
            prompt += f"\n\nاستخدم النظرية الأدبية التالية: {self.theories.apply_theory('', theory, language)}"
            
        # 3. التكييف الرقمي (إن وجد)
        if format_type:
            prompt = self.adapter.adapt_prompt(prompt, format_type, language)
            
        raw_outline = ""
        if AI_AVAILABLE:
            raw_outline = await provider_router.generate(prompt, language=language)
            
        self.active_projects[user_id] = ContentProject(title=title, type=type, genre=genre, language=language, theory=theory, outline=raw_outline)
        return {"title": title, "type": type, "outline": raw_outline}

    async def write_content(self, user_id: str, part: str, instructions: str = "") -> Dict[str, Any]:
        project = self.active_projects.get(user_id)
        if not project: return {"error": "لا يوجد مشروع نشط"}
        profile = await self.get_user_writing_profile(user_id)
        
        prompt = f"اكتب {part} من {project.type} '{project.title}'.\nالهيكل: {project.outline}\nالتعليمات: {instructions}\nاللغة: {project.language}"
        if AI_AVAILABLE:
            return {"content": await provider_router.generate(prompt, language=project.language)}
        return {"content": "خدمة الكتابة غير متاحة"}

# نسخة عالمية
creator = CreatorOrchestrator()
logger.info("✍️ Creator v2.0 initialized with Theories & Digital Adapter")

    # ============================================================
    # مدير الكتاب الكامل (Full Book Manager)
    # ============================================================
    async def write_full_book(
        self, user_id: str, title: str, chapters_count: int = 10,
        genre: str = "", language: str = "ar", target_language: str = ""
    ) -> Dict[str, Any]:
        """يكتب كتاباً كاملاً (مقدمة + فصول + خاتمة) ويترجمه اختيارياً"""
        
        # 1. توليد الهيكل
        outline = await self.generate_outline(user_id, title, "book", genre, language)
        
        # 2. كتابة كل الفصول
        full_book = []
        for i in range(1, chapters_count + 1):
            chapter = await self.write_content(user_id, f"الفصل {i}", "اكتب بتوسع")
            full_book.append({"chapter": i, "content": chapter.get("content", "")})
        
        # 3. ترجمة الكتاب كاملاً إن طُلب
        translated_book = []
        if target_language and target_language != language:
            for ch in full_book:
                translated = await self.polyglot.translate(ch["content"], language, target_language)
                translated_book.append({"chapter": ch["chapter"], "content": translated})
        
        return {
            "title": title,
            "chapters": chapters_count,
            "original": full_book,
            "translated": translated_book if translated_book else None,
            "target_language": target_language or "لا يوجد"
        }

    # ============================================================
    # محرك كتابة الإعلانات (Copywriting Engine)
    # ============================================================
    async def write_ad_copy(
        self, user_id: str, product_name: str, product_features: str,
        target_audience: str = "", platform: str = "instagram",
        formula: str = "AIDA", language: str = "ar"
    ) -> Dict[str, Any]:
        """
        يكتب كابشن/إعلان لمنتج باستخدام صيغ البيع النفسية.
        الصيغ المدعومة: AIDA, PAS, FOMO, BAB
        """
        formulas = {
            "AIDA": "Attention (جذب انتباه), Interest (إثارة اهتمام), Desire (خلق رغبة), Action (دعوة للشراء)",
            "PAS": "Problem (تحديد مشكلة), Agitate (تضخيم المشكلة), Solution (تقديم المنتج كحل)",
            "FOMO": "خلق شعور بالخوف من التفويت (Limited offer, Scarcity)",
            "BAB": "Before (قبل المنتج), After (بعد المنتج), Bridge (المنتج كجسر للتحول)"
        }
        
        formula_desc = formulas.get(formula, formulas["AIDA"])
        
        prompt = f"""أنت خبير تسويق ومبيعات. اكتب إعلاناً لمنتج '{product_name}' (الميزات: {product_features}).
        الجمهور المستهدف: {target_audience}.
        المنصة: {platform}.
        استخدم صيغة البيع: {formula} ({formula_desc}).
        اللغة: {language}.
        اجعل الإعلان مقنعاً وعاطفياً ويحث على الشراء فوراً."""
        
        ad_copy = ""
        if AI_AVAILABLE:
            ad_copy = await provider_router.generate(prompt, language=language)
        
        return {"product": product_name, "formula": formula, "copy": ad_copy}

    # ============================================================
    # محرك كتابة الإعلانات (Copywriting Engine)
    # ============================================================
    async def write_ad_copy(
        self, user_id: str, product_name: str, product_features: str,
        target_audience: str = "", platform: str = "instagram",
        formula: str = "AIDA", language: str = "ar"
    ) -> Dict[str, Any]:
        """
        يكتب كابشن/إعلان لمنتج باستخدام صيغ البيع النفسية.
        الصيغ المدعومة: AIDA, PAS, FOMO, BAB
        """
        formulas = {
            "AIDA": "Attention (جذب انتباه), Interest (إثارة اهتمام), Desire (خلق رغبة), Action (دعوة للشراء)",
            "PAS": "Problem (تحديد مشكلة), Agitate (تضخيم المشكلة), Solution (تقديم المنتج كحل)",
            "FOMO": "خلق شعور بالخوف من التفويت (Limited offer, Scarcity)",
            "BAB": "Before (قبل المنتج), After (بعد المنتج), Bridge (المنتج كجسر للتحول)"
        }
        
        formula_desc = formulas.get(formula, formulas["AIDA"])
        
        prompt = f"""أنت خبير تسويق ومبيعات. اكتب إعلاناً لمنتج '{product_name}' (الميزات: {product_features}).
        الجمهور المستهدف: {target_audience}.
        المنصة: {platform}.
        استخدم صيغة البيع: {formula} ({formula_desc}).
        اللغة: {language}.
        اجعل الإعلان مقنعاً وعاطفياً ويحث على الشراء فوراً."""
        
        ad_copy = ""
        if AI_AVAILABLE:
            ad_copy = await provider_router.generate(prompt, language=language)
        
        return {"product": product_name, "formula": formula, "copy": ad_copy}

    # ============================================================
    # تكامل مع شبكة الأشخاص (PersonNode)
    # ============================================================
    async def write_story_with_real_people(
        self, user_id: str, title: str, genre: str = "", language: str = "ar"
    ) -> Dict[str, Any]:
        """توليد قصة شخصياتها من شبكة معارف المستخدم الحقيقية"""
        profile = await self.get_user_writing_profile(user_id)
        people = profile.get("important_people", [])
        
        if not people:
            return {"error": "لا توجد شبكة معارف كافية. تحدث مع توأمك أكثر!"}
        
        # استخدام أهم 3 أشخاص كشخصيات رئيسية
        characters = [p["name"] for p in people[:3]]
        
        prompt = f"""اكتب قصة قصيرة بعنوان '{title}' (نوع: {genre}).
        استخدم هذه الشخصيات الحقيقية كأبطال للقصة: {', '.join(characters)}.
        اجعل القصة مؤثرة وشخصية. اللغة: {language}."""
        
        story = await provider_router.generate(prompt, language=language) if AI_AVAILABLE else ""
        return {"title": title, "characters": characters, "story": story}

creator = CreatorOrchestrator()

    # ============================================================
    # تفعيل التخصيص التلقائي (v2.1)
    # ============================================================
    async def write_content_auto(self, user_id: str, part: str, instructions: str = "") -> Dict[str, Any]:
        project = self.active_projects.get(user_id)
        if not project: return {"error": "لا يوجد مشروع نشط"}
        profile = await self.get_user_writing_profile(user_id)
        people = profile.get("important_people", [])
        
        # تخصيص تلقائي: أضف شخصيات من حياة المستخدم
        auto_instructions = instructions
        if people and "قصة" in project.type:
            auto_instructions += f"\nاستخدم هذه الشخصيات الحقيقية: {', '.join(p['name'] for p in people[:3])}"
        
        return await self.write_content(user_id, part, auto_instructions)

creator = CreatorOrchestrator()
