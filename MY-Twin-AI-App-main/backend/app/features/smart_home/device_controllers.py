"""
Device Controllers – وحدات التحكم بالأجهزة
=============================================
Home Assistant، WLED، ESPHome، MQTT.
مأخوذ من الملف الأصلي ومطور.
"""
import os, logging, asyncio
from typing import Dict, Optional, Any
import httpx

logger = logging.getLogger("device_controllers")

# ========== الإعدادات ==========
HA_URL = os.getenv("HOME_ASSISTANT_URL", "").rstrip("/")
HA_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN", "")
WLED_BASE_URL = os.getenv("WLED_BASE_URL", "")
ESPHOME_BASE_URL = os.getenv("ESPHOME_BASE_URL", "")
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# ========== Home Assistant ==========
async def ha_call_service(service: str, entity_id: str, data: Optional[Dict] = None) -> bool:
    if not HA_URL or not HA_TOKEN: return False
    try:
        domain, service_name = service.split(".")
        url = f"{HA_URL}/api/services/{domain}/{service_name}"
        headers = {"Authorization": f"Bearer {HA_TOKEN}", "Content-Type": "application/json"}
        payload = {"entity_id": entity_id}
        if data: payload.update(data)
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=10.0)
            return resp.status_code in [200, 201]
    except Exception as e:
        logger.error(f"HA error: {e}")
        return False

async def ha_get_state(entity_id: str) -> Optional[Dict]:
    if not HA_URL or not HA_TOKEN: return None
    try:
        url = f"{HA_URL}/api/states/{entity_id}"
        headers = {"Authorization": f"Bearer {HA_TOKEN}"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers, timeout=10.0)
            return resp.json() if resp.status_code == 200 else None
    except Exception as e:
        logger.error(f"HA get state error: {e}")
        return None

# ========== WLED ==========
COLORS_RGB = {
    "أحمر": [255,0,0], "أخضر": [0,255,0], "أزرق": [0,0,255],
    "بنفسجي": [128,0,128], "أصفر": [255,255,0], "برتقالي": [255,165,0],
    "أبيض": [255,255,255], "وردي": [255,20,147], "سماوي": [0,255,255],
}

async def wled_set_color(color: str, brightness: int = 255, effect: Optional[str] = None) -> bool:
    if not WLED_BASE_URL: return False
    if color in COLORS_RGB:
        rgb = COLORS_RGB[color]
    else:
        try:
            rgb = [int(x) for x in color.split(",")]
            if len(rgb) != 3: return False
        except: return False
    try:
        payload = {"on": True, "bri": brightness, "seg": [{"col": [rgb]}]}
        if effect: payload["seg"][0]["fx"] = effect
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{WLED_BASE_URL}/json/state", json=payload, timeout=5.0)
            return resp.status_code == 200
    except Exception as e:
        logger.error(f"WLED error: {e}")
        return False

async def wled_turn_off() -> bool:
    if not WLED_BASE_URL: return False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{WLED_BASE_URL}/json/state", json={"on": False}, timeout=5.0)
            return resp.status_code == 200
    except: return False

# ========== ESPHome ==========
async def esphome_control(entity_id: str, action: str = "toggle") -> bool:
    if not ESPHOME_BASE_URL: return False
    try:
        domain, name = entity_id.split(".")
        url = f"{ESPHOME_BASE_URL}/{domain}/{name}/{action}"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, timeout=5.0)
            return resp.status_code == 200
    except: return False

logger.info("✅ Device Controllers ready (HA, WLED, ESPHome)")
