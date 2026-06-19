"""Dynamic Prompt Builder v9.0 – loads templates from files."""
import logging, re, os
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "app", "prompts")

def _load_template(filename: str) -> str:
    path = os.path.join(PROMPT_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

class PromptBuilder:
    async def build(self, twin_name: str, user_name: str, relationship: Dict[str, Any],
                    emotion: Dict[str, Any], voice: Dict[str, Any], dialect: Dict[str, Any],
                    user_id: Optional[str] = None, journey_info: Optional[Dict] = None,
                    attachment_info: Optional[Dict] = None,
                    response_adjustments: Optional[Dict] = None,
                    message: str = "", memory_context: str = "",
                    reasoning_result: Optional[Dict] = None,
                    consciousness_context: Optional[Dict] = None,
                    history: Optional[List[Dict[str, str]]] = None,
                    task_type: str = "general", intent: str = "general", **kwargs) -> str:
        has_arabic = any("\u0600" <= c <= "\u06ff" for c in message)
        lang = "ar" if has_arabic else "en"

        # Load system prompt
        sys_template = _load_template("system_v1.txt")
        system = sys_template.format(
            twin_name=twin_name,
            user_name=user_name,
            bond_level=relationship.get("bond_level", 0),
            stage=relationship.get("label", ""),
        ) if sys_template else ""

        # Load relationship prompt
        rel_template = _load_template("relationship_v1.txt")
        relationship_block = ""
        if rel_template and relationship:
            relationship_block = rel_template.format(
                bond_level=relationship.get("bond_level", 0),
                stage=relationship.get("label", ""),
                trust=relationship.get("trust", 0),
                comfort=relationship.get("comfort", 0),
                openness=relationship.get("openness", 0),
                attachment=relationship.get("attachment", 0),
                romantic=relationship.get("romantic", 0),
                humor=relationship.get("humor", 0),
                stage_instruction=relationship.get("instruction", ""),
                attachment_style=attachment_info.get("style", "unknown") if attachment_info else "unknown",
                tone=response_adjustments.get("tone", "balanced") if response_adjustments else "balanced",
                warmth=response_adjustments.get("warmth", 0.6) if response_adjustments else 0.6,
            )

        # Load journey prompt
        journey_template = _load_template("journey_v1.txt")
        journey_block = ""
        if journey_template and journey_info:
            journey_block = journey_template.format(
                phase=journey_info.get("phase", "introduction"),
                progress=journey_info.get("progress", 0),
                warmth=journey_info.get("warmth", 0.5),
                curiosity=journey_info.get("curiosity", 0.5),
                humor=journey_info.get("humor", 0.5),
                depth=journey_info.get("depth", 0.5),
                recommendation=journey_info.get("recommendation", ""),
            )

        sections = [system, relationship_block, journey_block]

        if intent:
            sections.append(self._build_intent(intent, lang))
        sections.append(self._build_response_structure(lang))
        if memory_context:
            sections.append(f"<MEMORIES>\n{memory_context}\n</MEMORIES>")
        if consciousness_context:
            goals = consciousness_context.get("active_goals", [])
            thought = consciousness_context.get("last_thought", "")
            if goals or thought:
                sections.append(f"<CONSCIOUSNESS>\nGoals: {', '.join(goals)}\nLast Thought: {thought}\n</CONSCIOUSNESS>")
        if history:
            lines = [f"{'المستخدم' if h.get('role')=='user' else 'التوأم'}: {h.get('content','')[:150]}" for h in history[-4:]]
            sections.append("<RECENT_CHAT>\n" + "\n".join(lines) + "\n</RECENT_CHAT>")
        sections.append(f"<MESSAGE>\n{message}\n</MESSAGE>")
        sections.append("<FINAL>\nأجب الآن.\n</FINAL>")

        return "\n\n".join(s.strip() for s in sections if s and s.strip())

    def _build_intent(self, intent, lang):
        guides = {
            "coaching": {"ar":"أعطِ نصائح عملية.","en":"Give actionable advice."},
            "emotional": {"ar":"كن متعاطفاً.","en":"Be empathetic."},
            "decision": {"ar":"ساعد في رؤية الخيارات.","en":"Help see options."},
        }
        g = guides.get(intent, {}).get(lang, "")
        return f"<INTENT>\n{g}\n</INTENT>" if g else ""

    def _build_response_structure(self, lang):
        return "<STRUCTURE>\n1. إجابة مباشرة\n2. سياق (إن لزم)\n3. خطوة تالية\n</STRUCTURE>"

prompt_builder = PromptBuilder()
