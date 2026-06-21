"""
MyTwin – Response Validator v2.0 (Quality & Safety Gate)
=============================================================
- يفحص الرد قبل إرساله للمستخدم
- طبقات: Hallucination, Repetition, Length, Toxicity, Consistency, Emotional Fit
- إصلاح تلقائي إن أمكن
- يتكامل مع TCMA للتحقق من التناسق العاطفي
"""
import logging, re
from typing import Dict, Any, Optional

logger = logging.getLogger("response_validator")

class ResponseValidator:
    def __init__(self):
        self.min_length = 2
        self.max_length = 2000
        self.repetition_threshold = 0.6

    async def validate(
        self,
        reply: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tool_results: Optional[list] = None,
        emotion: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        فحص الرد وإرجاع تقرير بالصلاحية.
        """
        report = {
            "valid": True,
            "issues": [],
            "repaired": False,
            "final_reply": reply,
            "warnings": [],
        }

        if not reply or not reply.strip():
            report["valid"] = False
            report["issues"].append("empty_response")
            report["final_reply"] = "أنا هنا معك، تفضل 💜"
            report["repaired"] = True
            return report

        # 1. فحص الطول
        if len(reply) < self.min_length:
            report["warnings"].append("short_response")
        if len(reply) > self.max_length:
            report["final_reply"] = reply[: self.max_length - 3] + "..."
            report["repaired"] = True
            report["warnings"].append("trimmed_long_response")

        # 2. فحص التكرار
        repetition_score = self._check_repetition(reply)
        if repetition_score > self.repetition_threshold:
            report["warnings"].append(f"high_repetition ({repetition_score:.2f})")

        # 3. فحص التناسق العاطفي (جديد - TCMA)
        if user_id and emotion:
            emotional_fit = await self._check_emotional_fit(user_id, reply, emotion)
            if not emotional_fit:
                report["warnings"].append("emotional_mismatch")

        # 4. فحص الهلوسة ضد نتائج الأدوات
        if tool_results and len(tool_results) > 0:
            hallucination = self._check_hallucination(reply, tool_results)
            if hallucination:
                report["issues"].append("hallucination")
                report["final_reply"] = f"{reply.strip()}\n\nℹ️ {tool_results[-1]}"
                report["repaired"] = True

        # 5. فحص الأمان (سريع)
        if self._contains_toxic_content(reply):
            report["valid"] = False
            report["issues"].append("toxic_content")
            report["final_reply"] = "أنا هنا لدعمك، لكن لا يمكنني الرد على هذا. 💜"
            report["repaired"] = True
            return report

        return report

    async def _check_emotional_fit(self, user_id: str, reply: str, emotion: Dict[str, Any]) -> bool:
        """
        فحص ما إذا كان الرد مناسباً للحالة العاطفية للمستخدم.
        """
        try:
            from app.memory.emotional.emotional_memory import get_emotional_state_for_response
            user_emotion = await get_emotional_state_for_response(user_id, reply)
            
            if user_emotion and user_emotion.get("current_emotion") == "sadness":
                # لا يجب أن يكون الرد مرحاً جداً إذا كان المستخدم حزيناً
                happy_words = ["ههه", "😂", "رائع", "مضحك", "lol", "amazing", "funny"]
                if any(w in reply for w in happy_words):
                    return False
        except Exception as e:
            logger.warning(f"Emotional fit check failed: {e}")
        return True

    def _check_repetition(self, text: str) -> float:
        words = text.split()
        if len(words) < 5:
            return 0.0
        unique = len(set(words))
        return 1.0 - (unique / len(words))

    def _check_hallucination(self, reply: str, tool_results: list) -> bool:
        for result in tool_results:
            if result and len(result) > 10:
                reply_numbers = re.findall(r'\d+', reply)
                result_numbers = re.findall(r'\d+', result)
                for rn in result_numbers:
                    if rn in reply and rn not in reply_numbers:
                        return True
        return False

    def _contains_toxic_content(self, text: str) -> bool:
        toxic_words = [
            "انتحار", "أقتل", "موت", "أذى", "suicide", "kill myself",
            "hate you", "die"
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in toxic_words)


response_validator = ResponseValidator()
logger.info("✅ Response Validator v2.0 initialized with TCMA emotional fit")
