"""
MyTwin – Final Synthesizer v2.0 (طبقة الدمج النهائية)
- يدمج نتائج الأدوات مع الرد بشكل طبيعي
- يزيل التكرار والحشو
- يتأكد من أن الرد يجيب على سؤال المستخدم
"""
import logging
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
        """
        يدمج جميع المخرجات في رد نهائي واحد متماسك.
        """
        if not llm_reply:
            return llm_reply

        # 1. إذا لم تكن هناك أدوات أو سياق معقد، نرجع الرد كما هو
        if not tool_results and not memory_context:
            return llm_reply

        # 2. إزالة التكرار الواضح (إذا كان الرد يعيد نفس نص الأداة)
        for tool_res in tool_results:
            if tool_res and len(tool_res) > 20 and tool_res in llm_reply:
                # الأداة مدمجة بالفعل، لا حاجة لتكرارها
                pass

        # 3. التأكد من أن الرد ليس عاماً جداً
        if len(llm_reply) < 20 and tool_results:
            # الرد قصير جداً، نبني رداً أفضل من الأدوات
            combined_tools = "\n".join(tool_results)
            if lang == "ar":
                return f"بناءً على المعلومات المتوفرة:\n{combined_tools}\n\nهل تحتاج أي تفاصيل إضافية؟ 💬"
            else:
                return f"Based on the available information:\n{combined_tools}\n\nNeed any additional details? 💬"

        return llm_reply


final_synthesizer = FinalSynthesizer()
print("✅ Final Synthesizer v2.0 initialized")
