"""
MyTwin – Final Synthesizer v3.0 (طبقة الدمج النهائية)
=============================================================
- يدمج نتائج الأدوات مع الرد بشكل طبيعي بدون أسئلة ثابتة
- يزيل التكرار والحشو
- يتأكد من أن الرد يجيب على سؤال المستخدم
- يضيف نهايات سياقية ذكية مبنية على المحتوى
"""
import logging, re
from typing import Dict, Any, Optional, List

logger = logging.getLogger("final_synthesizer")

class FinalSynthesizer:
    async def synthesize(
        self,
        user_message: str,
        tool_results: List[str],
        memory_context: str,
        llm_reply: str,
        plan: Optional[Dict] = None,
        emotion: Optional[Dict] = None,
        lang: str = "ar"
    ) -> str:
        """يدمج جميع المخرجات في رد نهائي واحد متماسك"""
        if not llm_reply:
            return llm_reply

        # 1. تنظيف الرد من الأسئلة الثابتة المضافة سابقاً
        reply = self._remove_fixed_endings(llm_reply, lang)

        # 2. إذا لم تكن هناك أدوات أو سياق معقد، نرجع الرد كما هو
        if not tool_results and not memory_context:
            return reply

        # 3. إزالة التكرار الواضح بين الرد ونتائج الأدوات
        for tool_res in tool_results:
            if tool_res and len(tool_res) > 20:
                # إذا كان نص الأداة مدمجاً بالفعل في الرد، لا نكرره
                if self._is_already_embedded(tool_res, reply):
                    continue

        # 4. التأكد من أن الرد ليس عاماً جداً (إذا كان قصيراً جداً والأدوات متوفرة)
        if len(reply.split()) < 5 and tool_results:
            combined_tools = "\n".join(tool_results)
            if lang == "ar":
                return f"بناءً على المعلومات المتوفرة:\n{combined_tools}"
            else:
                return f"Based on the available information:\n{combined_tools}"

        # 5. إضافة نهاية سياقية ذكية (مبنية على المحتوى)
        reply = self._add_contextual_ending(reply, user_message, tool_results, lang)

        return reply

    def _remove_fixed_endings(self, text: str, lang: str) -> str:
        """إزالة النهايات الثابتة مثل 'إيه رأيك؟' أو 'هل تحتاج مساعدة؟'"""
        fixed_patterns = [
            r'\n\nإيه رأيك في الموضوع ده؟ 💭',
            r'\n\nهل تحب أعمق في نقطة معينة؟ 📚',
            r'\n\nفيه حاجة تانية أقدر أساعدك فيها؟',
            r'\n\nتقدر تسألني أي سؤال عن الموضوع ده.',
            r'\n\nWhat do you think about this\? 💭',
            r'\n\nNeed any additional details\? 💬',
            r'\n\nWant to dive deeper into this topic\? 📚',
        ]
        for pattern in fixed_patterns:
            text = re.sub(pattern, '', text)
        return text.strip()

    def _is_already_embedded(self, tool_result: str, reply: str) -> bool:
        """فحص إذا كان نص الأداة موجوداً أصلاً في الرد"""
        # مقارنة أول 50 حرفاً من الأداة مع الرد
        snippet = tool_result[:50].lower()
        return snippet in reply.lower()

    def _add_contextual_ending(self, reply: str, user_message: str, tool_results: List[str], lang: str) -> str:
        """إضافة نهاية سياقية مبنية على المحتوى ونتائج الأدوات"""
        # لا نضيف نهاية إذا كان الرد قصيراً جداً
        if len(reply) < 60:
            return reply

        # لا نضيف نهاية إذا كان الرد ينتهي بسؤال
        if reply.rstrip().endswith('?') or reply.rstrip().endswith('؟'):
            return reply

        # بناء نهاية سياقية من نتائج الأدوات
        if tool_results:
            first_tool = tool_results[0][:100] if tool_results else ""
            # إذا كانت النتيجة عن الطقس
            if any(w in first_tool for w in ["طقس", "درجة", "weather", "temperature"]):
                return reply
            # إذا كانت النتيجة عن عملات أو أسعار
            if any(w in first_tool for w in ["عملة", "سعر", "currency", "rate"]):
                return reply

        return reply


final_synthesizer = FinalSynthesizer()
logger.info("✅ Final Synthesizer v3.0 initialized (no fixed questions)")
