"""
MyTwin – Telegram Webhook v3.0 (Proactive + Task Reminders + Commands)
"""
import os, logging, asyncio, httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.infrastructure.database.supabase_client import get_db

logger = logging.getLogger("telegram_webhook")
router = APIRouter()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

async def send_telegram_message(chat_id: int, text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN:
        return False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{TELEGRAM_API_BASE}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
                timeout=10.0,
            )
            return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Telegram send failed: {e}")
        return False

async def send_proactive_telegram(user_id: str, message: str, telegram_chat_id: int) -> bool:
    return await send_telegram_message(telegram_chat_id, message)

async def setup_webhook():
    if not TELEGRAM_BOT_TOKEN:
        return
    base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", os.getenv("EXPO_PUBLIC_API_URL", ""))
    if not base_url:
        return
    webhook_url = f"{base_url}/api/telegram/webhook"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{TELEGRAM_API_BASE}/setWebhook", json={"url": webhook_url}, timeout=10.0)
            if resp.status_code == 200:
                logger.info(f"✅ Telegram webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")

@router.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    if not TELEGRAM_BOT_TOKEN:
        return JSONResponse({"status": "error"})

    try:
        body = await request.json()
        message = body.get("message", {})
        chat = message.get("chat", {})
        text = message.get("text", "").strip()
        chat_id = chat.get("id")
        first_name = message.get("from", {}).get("first_name", "صديقي")

        if not text or not chat_id:
            return JSONResponse({"status": "ok"})

        # أمر البدء
        if text.startswith("/start"):
            await send_telegram_message(chat_id, f"مرحباً {first_name}! 💜\nأنا توأمك الرقمي من MyTwin.\n\nالأوامر:\n/weather مدينة - الطقس\n/news - الأخبار\n/tasks - مهامي\n/help - مساعدة")
            return JSONResponse({"status": "ok"})

        # أمر الطقس
        if text.startswith("/weather") or "طقس" in text.lower():
            city = text.replace("/weather", "").strip() or "Cairo"
            try:
                from app.infrastructure.tools.external_services import get_weather
                result = await get_weather(city=city)
                await send_telegram_message(chat_id, result or "لم أتمكن من جلب الطقس")
            except Exception as e:
                await send_telegram_message(chat_id, f"خطأ: {e}")
            return JSONResponse({"status": "ok"})

        # أمر الأخبار
        if text.startswith("/news") or "أخبار" in text.lower():
            try:
                from app.infrastructure.tools.external_services import get_news
                result = await get_news()
                await send_telegram_message(chat_id, result or "لم أتمكن من جلب الأخبار")
            except Exception as e:
                await send_telegram_message(chat_id, f"خطأ: {e}")
            return JSONResponse({"status": "ok"})

        # أمر المهام
        if text.startswith("/tasks") or "مهامي" in text.lower():
            try:
                db = get_db()
                # البحث عن user_id المرتبط بـ telegram_chat_id
                profile = db.table("profiles").select("id").eq("telegram_chat_id", str(chat_id)).single().execute()
                if profile.data:
                    user_id = profile.data["id"]
                    tasks = db.table("tasks").select("*").eq("user_id", user_id).eq("status", "pending").order("due_date", asc=True).limit(5).execute()
                    if tasks.data:
                        task_list = "\n".join([f"• {t['title']}" + (f" (قبل {t['due_date']})" if t.get('due_date') else "") for t in tasks.data])
                        await send_telegram_message(chat_id, f"📋 مهامك:\n{task_list}")
                    else:
                        await send_telegram_message(chat_id, "لا توجد مهام معلقة 🎉")
                else:
                    await send_telegram_message(chat_id, "لم يتم ربط حسابك بعد. استخدم تطبيق MyTwin للربط.")
            except Exception as e:
                await send_telegram_message(chat_id, f"خطأ: {e}")
            return JSONResponse({"status": "ok"})

        # المحادثة العادية
        try:
            from app.orchestration.twin_orchestrator import orchestrate
            # البحث عن user_id
            db = get_db()
            profile = db.table("profiles").select("id").eq("telegram_chat_id", str(chat_id)).single().execute()
            if profile.data:
                user_id = profile.data["id"]
                response = await orchestrate(user_id=user_id, message=text, lang="ar")
                await send_telegram_message(chat_id, response[:2000])
            else:
                await send_telegram_message(chat_id, "مرحباً! استخدم تطبيق MyTwin لربط حسابك، ثم يمكنك التحدث معي هنا 💜")
        except Exception as e:
            await send_telegram_message(chat_id, "أواجه ضغطاً تقنياً 💜")

        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return JSONResponse({"status": "error"})

@router.post("/api/telegram/send")
async def send_telegram_notification(chat_id: int, message: str):
    success = await send_telegram_message(chat_id, message)
    return {"success": success}
