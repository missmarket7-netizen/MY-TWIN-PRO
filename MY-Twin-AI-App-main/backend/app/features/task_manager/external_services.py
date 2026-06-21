"""
External Services Provider – خدمات خارجية متكاملة
==================================================
الطقس، الأخبار، العملات، والبحث.
تتكامل مع P.A.S.S. و TCMA.
"""
import logging, asyncio, httpx
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger("external_services")

async def get_weather(city: str = "Cairo", lang: str = "ar") -> Dict[str, Any]:
    """جلب حالة الطقس الحالية (wttr.in – مجاني)"""
    try:
        url = f"https://wttr.in/{city}?format=j1&lang={lang[:2]}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_condition", [{}])[0]
                weather_desc = current.get("lang_ar", [{}])[0].get("value", "غائم جزئياً") if lang == "ar" else current.get("weatherDesc", [{}])[0].get("value", "Partly cloudy")
                return {
                    "city": city,
                    "temperature": current.get("temp_C", "N/A"),
                    "description": weather_desc,
                    "humidity": current.get("humidity", "N/A"),
                    "wind_speed": current.get("windspeedKmph", "N/A"),
                    "feels_like": current.get("FeelsLikeC", "N/A"),
                    "source": "wttr.in"
                }
    except Exception as e:
        logger.error(f"Weather fetch failed: {e}")
    return {"error": "تعذر جلب الطقس"}

async def get_news(country: str = "sa", lang: str = "ar", limit: int = 5) -> Dict[str, Any]:
    """جلب آخر الأخبار (NewsAPI – مجاني جزئياً)"""
    try:
        # في النسخة الإنتاجية: استخدم مفتاح API من newsapi.org
        return {
            "country": country,
            "articles": [
                {"title": "أهم الأخبار اليوم", "source": "MyTwin News", "url": ""},
                {"title": "تطورات الذكاء الاصطناعي", "source": "MyTwin News", "url": ""},
            ],
            "source": "simulated"
        }
    except Exception as e:
        logger.error(f"News fetch failed: {e}")
    return {"error": "تعذر جلب الأخبار"}

async def get_currency(base: str = "USD", symbols: str = "EUR,GBP,JPY,SAR,EGP") -> Dict[str, Any]:
    """جلب أسعار الصرف (exchangerate-api – مجاني)"""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                rates = data.get("rates", {})
                filtered = {s: rates[s] for s in symbols.split(",") if s in rates}
                return {"base": base, "rates": filtered, "source": "exchangerate-api"}
    except Exception as e:
        logger.error(f"Currency fetch failed: {e}")
    return {"error": "تعذر جلب أسعار الصرف"}

async def search_web(query: str, lang: str = "ar") -> Dict[str, Any]:
    """بحث عام (محاكاة – يستخدم AI داخلياً)"""
    try:
        from app.infrastructure.ai.provider_router import provider_router
        prompt = f"قدم معلومات حديثة عن: {query}. أجب بإيجاز. اللغة: {lang}."
        response = await provider_router.generate(prompt, language=lang)
        return {"query": query, "results": response, "source": "ai_search"}
    except Exception as e:
        logger.error(f"Search failed: {e}")
    return {"error": "تعذر البحث"}

async def deep_search(query: str, lang: str = "ar") -> Dict[str, Any]:
    """بحث عميق (باستخدام AI)"""
    try:
        from app.infrastructure.ai.provider_router import provider_router
        prompt = f"""أنت مساعد بحث متقدم. ابحث بعمق عن: {query}.
        قدم: 1. تعريف شامل 2. أحدث التطورات 3. مصادر موثوقة 4. تحليلات.
        اللغة: {lang}."""
        response = await provider_router.generate(prompt, language=lang)
        return {"query": query, "deep_results": response, "source": "ai_deep_search"}
    except Exception as e:
        logger.error(f"Deep search failed: {e}")
    return {"error": "تعذر البحث العميق"}
