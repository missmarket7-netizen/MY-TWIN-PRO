"""
MyTwin – Growth Tracker v2.0 (دعم Multi-LLM + تحليل عميق + كشف نقاط الضعف)
"""
import os, logging, json, asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from supabase import create_client, Client

logger = logging.getLogger("growth_tracker")

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

db: Optional[Client] = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

def _get_ai_client():
    """الحصول على عميل AI متعدد النماذج (MultiAIClient) من النظام"""
    try:
        from multi_ai import MultiAIClient
        return MultiAIClient()
    except Exception:
        # محاولة احتياطية: استخدام Gemini مباشرة
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
            return genai.GenerativeModel("gemini-2.5-flash")
        except Exception:
            return None

async def _call_llm(prompt: str, task: str = "deep_reasoning") -> Optional[str]:
    """استدعاء LLM عبر الطبقة المتعددة مع احتياط Gemini"""
    client = _get_ai_client()
    if not client:
        return None
    try:
        if hasattr(client, 'get_best_reply'):
            # MultiAIClient
            return await client.get_best_reply(prompt, task=task)
        elif hasattr(client, 'generate_content'):
            # Gemini مباشرة
            loop = asyncio.get_running_loop()
            resp = await loop.run_in_executor(None, lambda: client.generate_content(prompt))
            return resp.text if resp else None
    except Exception as e:
        logger.warning(f"LLM call failed: {e}")
    return None

def _parse_json(response: str) -> Dict[str, Any]:
    """استخراج JSON آمن من رد LLM"""
    if not response:
        return {}
    text = response.strip()
    # إزالة علامات Markdown المحتملة
    if text.startswith("```json"):
        text = text.split("```json")[1].split("```")[0].strip()
    elif text.startswith("```"):
        text = text.split("```")[1].split("```")[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # محاولة إيجاد أول كائن JSON
        import re
        match = re.search(r'\{[^}]+\}', text)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {}

async def track_growth(user_id: str, personality_data: Dict[str, Any], lang: str = "ar") -> Dict[str, Any]:
    """
    تحليل تطور شخصية المستخدم بمقارنة أحدث تحليل مع التحليلات السابقة.
    """
    if not db:
        return {"status": "unavailable"}

    try:
        res = db.table("personality_profiles").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(2).execute()
        if not res.data or len(res.data) < 2:
            return {"status": "not_enough_data", "message": "يحتاج تحليلين على الأقل للمقارنة."}

        current = res.data[0]
        previous = res.data[1]

        prompt = f"""قارن بين تحليلين لشخصية المستخدم وأعد ONLY JSON:
{{
  "changes": ["التغير الأول", "التغير الثاني"],
  "positive_growth": ["نقطة إيجابية"],
  "areas_to_improve": ["نقطة للتحسين"],
  "summary": "ملخص التطور في جملتين بالعامية"
}}

التحليل الحالي: {json.dumps(current.get('analyzed_traits', {}), ensure_ascii=False)}
التحليل السابق: {json.dumps(previous.get('analyzed_traits', {}), ensure_ascii=False)}
JSON:"""

        response = await _call_llm(prompt)
        if not response:
            return {"status": "error", "message": "فشل الاتصال بنموذج الذكاء الاصطناعي"}

        result = _parse_json(response)
        if result:
            db.table("growth_reports").insert({
                "user_id": user_id,
                "report": result,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()

        return result if result else {"status": "error", "message": "فشل تحليل التطور"}
    except Exception as e:
        logger.error(f"Growth tracking failed: {e}")
        return {"status": "error", "message": str(e)}


async def analyze_progress(
    user_id: str,
    recent_data: Dict[str, Any],
    lang: str = "ar"
) -> Dict[str, Any]:
    """
    تحليل التقدم الحالي للمستخدم بناءً على بيانات حديثة (مشاعر، أبعاد علاقة، مرحلة الرحلة...).
    يستخرج نقاط القوة والضعف ومجالات النمو.
    """
    if not db:
        return {"status": "unavailable"}

    # جلب سجل النمو السابق للمقارنة
    try:
        history = await get_growth_history(user_id, limit=3)
    except:
        history = []

    # بناء الـ Prompt مع البيانات المتاحة
    prompt_parts = []
    if recent_data.get("emotion"):
        prompt_parts.append(f"المشاعر الحالية: {json.dumps(recent_data['emotion'], ensure_ascii=False)}")
    if recent_data.get("relationship_dims"):
        prompt_parts.append(f"أبعاد العلاقة: {json.dumps(recent_data['relationship_dims'], ensure_ascii=False)}")
    if recent_data.get("journey_phase"):
        prompt_parts.append(f"مرحلة الرحلة: {recent_data['journey_phase']}")
    if recent_data.get("attachment_style"):
        prompt_parts.append(f"نمط التعلق: {recent_data['attachment_style']}")
    if recent_data.get("goals"):
        prompt_parts.append(f"الأهداف: {json.dumps(recent_data['goals'], ensure_ascii=False)}")
    if history:
        # تلخيص آخر تقرير نمو للمقارنة
        last_report = history[0].get("report", {})
        prompt_parts.append(f"آخر تقرير نمو: {json.dumps(last_report, ensure_ascii=False)}")

    data_context = "\n".join(prompt_parts)

    if lang == "ar":
        prompt = f"""حلل تطور المستخدم الحالي وأعد ONLY JSON:
{{
  "strengths": ["قوة 1", "قوة 2"],
  "weaknesses": ["ضعف 1", "ضعف 2"],
  "emotional_pattern": "نمط عاطفي متكرر",
  "growth_potential": "مجال للنمو المستقبلي",
  "recommendation": "نصيحة عملية واحدة للمستخدم"
}}

بيانات المستخدم الحالية:
{data_context}
JSON:"""
    else:
        prompt = f"""Analyze the user's current progress and return ONLY JSON:
{{
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "emotional_pattern": "recurring emotional pattern",
  "growth_potential": "area for future growth",
  "recommendation": "one practical tip"
}}

Current user data:
{data_context}
JSON:"""

    response = await _call_llm(prompt)
    if not response:
        return {"status": "error", "message": "فشل الاتصال بنموذج الذكاء الاصطناعي"}

    result = _parse_json(response)
    if result:
        # تخزين التحليل كتقرير نمو جديد
        try:
            db.table("growth_reports").insert({
                "user_id": user_id,
                "report": result,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }).execute()
        except Exception as e:
            logger.warning(f"Failed to store progress analysis: {e}")

    return result if result else {"status": "error", "message": "فشل تحليل التطور"}


async def get_growth_history(user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
    """استرجاع سجل تقارير النمو."""
    if not db:
        return []
    try:
        res = db.table("growth_reports").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except Exception as e:
        logger.error(f"Failed to get growth history: {e}")
        return []


async def get_weaknesses(user_id: str) -> List[str]:
    """استخراج نقاط الضعف من آخر تقارير النمو."""
    reports = await get_growth_history(user_id, limit=5)
    weaknesses = []
    for r in reports:
        report_data = r.get("report", {})
        if isinstance(report_data, dict):
            weaknesses.extend(report_data.get("weaknesses", []))
            weaknesses.extend(report_data.get("areas_to_improve", []))
    # إزالة التكرار
    return list(dict.fromkeys(weaknesses))
