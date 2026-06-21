"""
Smart Home Orchestrator – عقل المنزل الذكي
=============================================
ينسق بين: وحدات التحكم، الروتين، جسر TCMA، والتوصيات.
"""
import logging, asyncio
from typing import Dict, Any, Optional

from app.features.smart_home.device_controllers import (
    ha_call_service, ha_get_state, wled_set_color, wled_turn_off, esphome_control, COLORS_RGB
)
from app.features.smart_home.routine_engine import routine_engine
from app.features.smart_home.smart_home_memory_bridge import smart_home_bridge

try:
    from app.core.unified_recommendation_engine import engine as rec_engine
    REC_AVAILABLE = True
except ImportError:
    REC_AVAILABLE = False

logger = logging.getLogger("smart_home_orchestrator")

VOICE_COMMANDS = {
    "شغل النور": ("light.turn_on", "light.living_room"),
    "اطفئ النور": ("light.turn_off", "light.living_room"),
    "شغل المكيف": ("climate.turn_on", "climate.living_room"),
    "اطفئ المكيف": ("climate.turn_off", "climate.living_room"),
    "غير لون النور إلى": ("set_color", None),
}

class SmartHomeOrchestrator:
    def __init__(self):
        pass

    async def process_command(
        self, user_id: str, command: str, lang: str = "ar"
    ) -> Dict[str, Any]:
        """يعالج أمراً من المستخدم وينفذه على الأجهزة"""
        
        # 1. تحليل الأمر
        executed = False
        response = ""
        
        for phrase, (service, entity) in VOICE_COMMANDS.items():
            if phrase in command:
                if phrase == "غير لون النور إلى":
                    color = command.split("إلى")[-1].strip()
                    if WLED_BASE_URL:
                        executed = await wled_set_color(color)
                        response = f"✨ تم تغيير الإضاءة إلى {color}" if executed else "❌ فشل تغيير اللون"
                    elif HA_URL:
                        executed = await ha_call_service("light.turn_on", entity or "light.living_room", {"color_name": color})
                        response = f"✨ تم تغيير الإضاءة" if executed else "❌ فشل"
                else:
                    if HA_URL:
                        executed = await ha_call_service(service, entity)
                    elif WLED_BASE_URL and "light" in service:
                        if "turn_on" in service:
                            executed = await wled_set_color("أبيض", 255)
                        else:
                            executed = await wled_turn_off()
                    elif ESPHOME_BASE_URL:
                        action = "turn_on" if "turn_on" in service else "turn_off" if "turn_off" in service else "toggle"
                        executed = await esphome_control(entity, action)
                    response = "✅ تم التنفيذ" if executed else "❌ فشل التنفيذ"
                break
        else:
            response = "🤔 لم أفهم الأمر. جرب: 'شغل النور' أو 'غير لون النور إلى أحمر'."

        # 2. تسجيل الإجراء
        routine_engine.log_action(user_id, command, response)
        await smart_home_bridge.log_action(user_id, command, response)

        return {"command": command, "response": response, "executed": executed}

    async def get_status(self, user_id: str) -> Dict[str, Any]:
        """يجلب حالة المنزل والأجهزة"""
        devices = []
        if HA_URL and HA_TOKEN:
            state = await ha_get_state("light.living_room")
            if state:
                devices.append({"name": "نور الصالة", "state": state.get("state", "unknown")})

        # اقتراحات من الروتين
        patterns = routine_engine.detect_patterns(user_id)

        # اقتراحات من التوصيات
        recommendations = []
        if REC_AVAILABLE:
            recs = await rec_engine.get_daily_recommendation(user_id)
            recommendations = recs.get("recommendations", [])

        # سياق عاطفي
        context = await smart_home_bridge.get_user_context(user_id)

        return {
            "devices": devices,
            "routines": patterns,
            "recommendations": recommendations,
            "user_emotion": context.get("emotion", "neutral"),
            "suggestion": self._adaptive_suggestion(context.get("emotion", "neutral"))
        }

    def _adaptive_suggestion(self, emotion: str) -> str:
        if emotion in ["sadness", "fear"]:
            return "أقترح إضاءة دافئة وموسيقى هادئة."
        elif emotion == "joy":
            return "الجو رائع! استمتع."
        return "المنزل جاهز لأوامرك."


# نسخة عالمية
smart_home = SmartHomeOrchestrator()
logger.info("✅ Smart Home Orchestrator initialized")
