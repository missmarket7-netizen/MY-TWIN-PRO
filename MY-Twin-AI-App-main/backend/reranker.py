"""
MyTwin – Memory Reranker v1.5 (Ready for Integration)
- يعيد ترتيب الذكريات المسترجعة باستخدام LLM
- يحسن دقة الذكريات قبل إرسالها للسياق
- جاهز للربط في memory_retriever.py
"""
import logging, re
from typing import List, Dict, Any

logger = logging.getLogger("reranker")

class MemoryReranker:
    async def rerank(self, query: str, memories: List[Dict[str, Any]], multi_client) -> List[Dict[str, Any]]:
        if not memories or len(memories) <= 1:
            return memories

        mem_text = "\n".join(f"{i+1}. {m.get('content','')[:100]}" for i, m in enumerate(memories))
        prompt = f"""أعد ترتيب الذكريات التالية حسب صلتها بالاستعلام. أعد فقط أرقام الذكريات مرتبة (مثال: 3,1,2,5,4).

الاستعلام: {query}

الذكريات:
{mem_text}

الترتيب:"""

        try:
            reply = await multi_client.get_best_reply(prompt)
            if reply:
                numbers = [int(n) for n in re.findall(r'\d+', reply) if 1 <= int(n) <= len(memories)]
                if numbers:
                    reranked = [memories[n-1] for n in numbers if n-1 < len(memories)]
                    mentioned = set(n-1 for n in numbers if n-1 < len(memories))
                    for i, mem in enumerate(memories):
                        if i not in mentioned:
                            reranked.append(mem)
                    return reranked
        except Exception as e:
            logger.warning(f"Reranking failed: {e}")

        return memories


# نسخة عالمية
memory_reranker = MemoryReranker()
print("✅ Memory Reranker v1.5 initialized")
