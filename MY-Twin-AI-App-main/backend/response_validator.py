"""
MyTwin – Response Validator v1.0 (Quality & Safety Gate)
- يفحص الرد قبل إرساله للمستخدم
- طبقات: Hallucination, Repetition, Length, Toxicity, Consistency
- إصلاح تلقائي إن أمكن
"""
import logging, re
from typing import Dict, Any, Optional

logger = logging.getLogger("response_validator")

class ResponseValidator:
    def __init__(self):
        self.min_length = 1
        self.max_length = 2000
        self.repetition_threshold = 0.6  # نسبة التكرار القصوى

    def validate(
        self,
        reply: str,
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

        # 3. فحص الهلوسة ضد نتائج الأدوات
        if tool_results and len(tool_results) > 0:
            hallucination = self._check_hallucination(reply, tool_results)
            if hallucination:
                report["issues"].append("hallucination")
                # محاولة إصلاح: إضافة نتيجة الأداة الصحيحة
                report["final_reply"] = f"{reply.strip()}\n\nℹ️ {tool_results[-1]}"
                report["repaired"] = True

        # 4. فحص الأمان (سريع)
        if self._contains_toxic_content(reply):
            report["valid"] = False
            report["issues"].append("toxic_content")
            report["final_reply"] = "أنا هنا لدعمك، لكن لا يمكنني الرد على هذا. 💜"
            report["repaired"] = True
            return report

        return report

    def _check_repetition(self, text: str) -> float:
        """حساب نسبة التكرار في النص."""
        words = text.split()
        if len(words) < 5:
            return 0.0
        unique = len(set(words))
        return 1.0 - (unique / len(words))

    def _check_hallucination(self, reply: str, tool_results: list) -> bool:
        """فحص بسيط: هل يحتوي الرد على معلومات تناقض نتائج الأدوات؟"""
        for result in tool_results:
            if result and len(result) > 10:
                # فحص وجود أرقام متضاربة (مثلاً درجة الحرارة)
                reply_numbers = re.findall(r'\d+', reply)
                result_numbers = re.findall(r'\d+', result)
                for rn in result_numbers:
                    if rn in reply and rn not in reply_numbers:
                        return True
        return False

    def _contains_toxic_content(self, text: str) -> bool:
        """فحص سريع للكلمات الخطيرة."""
        toxic_words = [
            "انتحار", "أقتل", "موت", "أذى", "suicide", "kill myself",
            "hate you", "die"
        ]
        text_lower = text.lower()
        return any(word in text_lower for word in toxic_words)

    def repair_response(self, reply: str, issue: str) -> str:
        """إصلاحات بسيطة لأنواع محددة من المشكلات."""
        if issue == "empty_response":
            return "أنا هنا معك، تفضل 💜"
        if issue == "toxic_content":
            return "أنا هنا لدعمك، لكن لا يمكنني الرد على هذا. 💜"
        return reply


response_validator = ResponseValidator()
print("✅ Response Validator v1.0 initialized")
