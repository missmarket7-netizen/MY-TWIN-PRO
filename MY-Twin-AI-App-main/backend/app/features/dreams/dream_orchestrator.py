"""
Dream Orchestrator – عقل تفسير الأحلام المتكامل
"""
import logging, json
from typing import Dict, Any, List
from datetime import datetime, timezone

from app.features.dreams.symbol_library import search_symbol
from app.features.dreams.dream_memory_bridge import dream_bridge

logger = logging.getLogger("dream_orchestrator")

class DreamOrchestrator:
    def __init__(self):
        self.dreams_history: Dict[str, List[Dict]] = {}

    async def interpret(self, user_id: str, dream_text: str, lang: str = "ar", preferred_school: str = "all") -> Dict[str, Any]:
        if not dream_text or not dream_text.strip():
            return {"interpretation": "", "symbols": [], "emotions": [], "reflection_question": ""}

        symbols = search_symbol(dream_text)
        analysis = await self._analyze(dream_text, symbols, lang, preferred_school)
        
        # تخزين في TCMA
        await dream_bridge.store_dream(user_id, dream_text, analysis, lang)

        # حفظ للتاريخ
        if user_id not in self.dreams_history:
            self.dreams_history[user_id] = []
        self.dreams_history[user_id].append({
            "date": datetime.now(timezone.utc).isoformat(),
            "text": dream_text[:200], "symbols": [s["symbol"] for s in symbols], "emotions": analysis.get("emotions", [])
        })

        return analysis

    async def _analyze(self, dream: str, symbols: List[Dict], lang: str, school: str) -> Dict[str, Any]:
        # محاولة استخدام Gemini
        if GEMINI_API_KEY:
            return await self._ai_analyze(dream, symbols, lang, school)
        return self._local_analyze(dream, symbols, lang)

    async def _ai_analyze(self, dream: str, symbols: List[Dict], lang: str, school: str) -> Dict[str, Any]:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            prompt = f"""
            حلل هذا الحلم كمحلل أحلام خبير.
            الحلم: "{dream}"
            الرموز: {json.dumps([s['symbol'] for s in symbols], ensure_ascii=False)}
            أعد ONLY JSON: {{"interpretation": "...", "symbols_analysis": [...], "emotions": [...], "reflection_question": "...", "psychological_insight": "..."}}
            اللغة: {lang}.
            """
            response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            raw = response.text.strip()
            if raw.startswith("```json"): raw = raw.split("```json")[1].split("```")[0].strip()
            elif raw.startswith("```"): raw = raw.split("```")[1].split("```")[0].strip()
            return json.loads(raw)
        except Exception as e:
            logger.error(f"AI failed: {e}")
            return self._local_analyze(dream, symbols, lang)

    def _local_analyze(self, dream: str, symbols: List[Dict], lang: str) -> Dict[str, Any]:
        return {
            "interpretation": "حلمك يعكس مشاعرك الداخلية." if lang == "ar" else "Your dream reflects your inner feelings.",
            "symbols_analysis": [f"{s['symbol']}: {', '.join(s['theories'].values())[:100]}" for s in symbols[:5]],
            "emotions": ["فضول"],
            "reflection_question": "ما هو أول شيء فكرت فيه عند استيقاظك؟" if lang == "ar" else "What was the first thing you thought when you woke up?",
            "psychological_insight": "الأحلام هي رسائل من اللاوعي." if lang == "ar" else "Dreams are messages from the unconscious."
        }

    async def weekly_report(self, user_id: str, lang: str = "ar") -> Dict[str, Any]:
        dreams = self.dreams_history.get(user_id, [])
        if not dreams:
            return {"total": 0, "message": "لا أحلام هذا الأسبوع" if lang == "ar" else "No dreams this week"}

        all_symbols = [s for d in dreams for s in d.get("symbols", [])]
        all_emotions = [e for d in dreams for e in d.get("emotions", [])]
        return {
            "total": len(dreams),
            "recurring_symbols": list(set(all_symbols))[:10],
            "dominant_emotions": list(set(all_emotions)),
        }

dream_orchestrator = DreamOrchestrator()
logger.info("✅ Dream Orchestrator ready")
