"""
MyTwin – Telegram Webhook v4.0 (متكامل مع TCMA وجميع الميزات)
=================================================================
- أوامر ذكية: /study, /dream, /weather, /news, /tasks, /quote
- تكامل مع TCMA (تسجيل المشاعر والتفاعلات)
- إشعارات استباقية وربط تلقائي بالحسابات
"""
import os, logging, asyncio, httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from typing import Optional

logger = logging.getLogger("telegram_webhook")
router = APIRouter()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ========== دوال الإرسال ==========
async def send_telegram_message(chat_id: int, text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN: return False
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{TELEGRAM_API_BASE}/sendMessage",
                json={"chat_id": chat_id, "text": text[:4000], "parse_mode": "HTML"},
                timeout=10.0,
            )
            return resp.status_code == 200
    except Exception as e:
        logger.warning(f"Telegram send failed: {e}")
        return False

async def send_proactive_telegram(user_id: str, message: str, telegram_chat_id: int) -> bool:
    """إرسال إشعار استباقي لمستخدم مرتبط"""
    return await send_telegram_message(telegram_chat_id, f"💜 {message}")

async def setup_webhook():
    """تفعيل Webhook تلقائياً عند بدء التشغيل"""
    if not TELEGRAM_BOT_TOKEN: return
    base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", os.getenv("EXPO_PUBLIC_API_URL", ""))
    if not base_url: return
    webhook_url = f"{base_url}/api/telegram/webhook"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{TELEGRAM_API_BASE}/setWebhook", json={"url": webhook_url}, timeout=10.0)
            if resp.status_code == 200:
                logger.info(f"✅ Telegram webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")

# ========== البحث عن المستخدم ==========
async def _find_user_by_telegram(chat_id: int) -> Optional[str]:
    """البحث عن user_id مرتبط بـ Telegram chat_id"""
    try:
        from app.infrastructure.database.supabase_client import get_db
        db = get_db()
        profile = db.table("profiles").select("id").eq("telegram_chat_id", str(chat_id)).single().execute()
        return profile.data["id"] if profile.data else None
    except: return None

# ========== Webhook الرئيسي ==========
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

        user_id = await _find_user_by_telegram(chat_id)

        # --- أمر البدء ---
        if text.startswith("/start"):
            welcome_msg = f"""مرحباً {first_name}! 💜
أنا توأمك الرقمي من MyTwin.

✨ الأوامر المتاحة:
/weather مدينة - الطقس
/news - الأخبار
/tasks - مهامي
/study مفهوم - جلسة دراسة
/dream حلمك - تفسير حلم
/quote - اقتباس تحفيزي
/help - مساعدة"""
            await send_telegram_message(chat_id, welcome_msg)
            return JSONResponse({"status": "ok"})

        # --- أمر الطقس ---
        if text.startswith("/weather") or "طقس" in text:
            city = text.replace("/weather", "").strip() or "Cairo"
            try:
                from app.features.task_manager.external_services import get_weather
                result = await get_weather(city=city)
                if result and "temperature" in result:
                    weather_msg = f"🌤 الطقس في {result.get('city', city)}:\n🌡 الحرارة: {result['temperature']}°C\n💧 الرطوبة: {result.get('humidity', 'N/A')}%\n🌬 الرياح: {result.get('wind_speed', 'N/A')} كم/س"
                    await send_telegram_message(chat_id, weather_msg)
                else:
                    await send_telegram_message(chat_id, "لم أتمكن من جلب الطقس 💜")
            except: await send_telegram_message(chat_id, "حدث خطأ في جلب الطقس")

            # تسجيل في TCMA
            if user_id:
                try:
                    from app.memory.emotional.emotional_memory import store_emotional_memory
                    await store_emotional_memory(user_id=user_id, expressed_text=f"طلب طقس {city}", detected_emotion={"primary":"neutral","intensity":0.5,"valence":0.0}, trigger="telegram")
                except: pass
            return JSONResponse({"status": "ok"})

        # --- أمر الأخبار ---
        if text.startswith("/news") or "أخبار" in text:
            try:
                from app.features.task_manager.external_services import get_news
                result = await get_news()
                await send_telegram_message(chat_id, result.get("summary", "لم أتمكن من جلب الأخبار") if isinstance(result, dict) else str(result)[:2000])
            except: await send_telegram_message(chat_id, "حدث خطأ في جلب الأخبار")
            return JSONResponse({"status": "ok"})

        # --- أمر المهام ---
        if text.startswith("/tasks") or "مهامي" in text:
            if user_id:
                try:
                    from app.infrastructure.database.supabase_client import get_db
                    db = get_db()
                    tasks = db.table("tasks").select("*").eq("user_id", user_id).eq("status", "pending").order("due_date", asc=True).limit(5).execute()
                    if tasks.data:
                        task_list = "\n".join([f"• {t['title']}" + (f" (قبل {t['due_date']})" if t.get('due_date') else "") for t in tasks.data])
                        await send_telegram_message(chat_id, f"📋 مهامك:\n{task_list}")
                    else:
                        await send_telegram_message(chat_id, "لا توجد مهام معلقة 🎉")
                except: await send_telegram_message(chat_id, "خطأ في جلب المهام")
            else:
                await send_telegram_message(chat_id, "لم يتم ربط حسابك بعد. استخدم تطبيق MyTwin للربط.")
            return JSONResponse({"status": "ok"})

        # --- أمر الدراسة ---
        if text.startswith("/study"):
            concept = text.replace("/study", "").strip() or "الذكاء الاصطناعي"
            if user_id:
                try:
                    from app.features.study.athena_orchestrator import athena
                    result = await athena.start_study_session(user_id, concept, "teen", "ar")
                    explanation = result.get("explanation", {}).get("simplified", "جاري الدراسة...")
                    await send_telegram_message(chat_id, f"📚 {explanation[:2000]}")
                except: await send_telegram_message(chat_id, "حدث خطأ في جلسة الدراسة")
            else:
                await send_telegram_message(chat_id, "لم يتم ربط حسابك بعد.")
            return JSONResponse({"status": "ok"})

        # --- أمر تفسير الحلم ---
        if text.startswith("/dream"):
            dream_text = text.replace("/dream", "").strip()
            if dream_text and user_id:
                try:
                    from app.features.dreams.dream_orchestrator import dream_orchestrator
                    result = await dream_orchestrator.interpret(user_id, dream_text, "ar")
                    interpretation = result.get("interpretation", "حلم مثير للاهتمام...")
                    await send_telegram_message(chat_id, f"🌙 {interpretation[:2000]}")
                except: await send_telegram_message(chat_id, "حدث خطأ في تحليل الحلم")
            else:
                await send_telegram_message(chat_id, "اكتب حلمك بعد الأمر /dream")
            return JSONResponse({"status": "ok"})

        # --- أمر اقتباس ---
        if text.startswith("/quote"):
            quotes = [
                "✨ 'الشجاعة ليست غياب الخوف، بل الانتصار عليه.' - نيلسون مانديلا",
                "💪 'رحلة الألف ميل تبدأ بخطوة واحدة.' - لاو تزو",
                "🌟 'افعل ما تستطيع، بما لديك، أينما كنت.' - ثيودور روزفلت",
            ]
            import random
            await send_telegram_message(chat_id, random.choice(quotes))
            return JSONResponse({"status": "ok"})

        # --- المحادثة العادية ---
        if user_id:
            try:
                from app.orchestration.twin_orchestrator import orchestrate
                response = await orchestrate(user_id=user_id, message=text, lang="ar")
                await send_telegram_message(chat_id, response[:2000])
                
                # تسجيل في TCMA
                try:
                    from app.memory.emotional.emotional_memory import store_emotional_memory
                    await store_emotional_memory(user_id=user_id, expressed_text=text[:200], detected_emotion={"primary":"neutral","intensity":0.5,"valence":0.0}, trigger="telegram")
                except: pass
            except Exception as e:
                await send_telegram_message(chat_id, "أواجه ضغطاً تقنياً 💜")
        else:
            await send_telegram_message(chat_id, "مرحباً! استخدم تطبيق MyTwin لربط حسابك، ثم يمكنك التحدث معي هنا 💜")

        return JSONResponse({"status": "ok"})
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return JSONResponse({"status": "error"})

@router.post("/api/telegram/send")
async def send_telegram_notification(chat_id: int, message: str):
    success = await send_telegram_message(chat_id, message)
    return {"success": success}

logger.info("✅ Telegram Webhook v4.0 initialized")
