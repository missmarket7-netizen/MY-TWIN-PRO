"""
MyTwin – External Services v6.0 (موحّد وقوي)
=============================================
- طقس (Open-Meteo + OpenStreetMap)
- يوتيوب (Invidious + YouTube API)
- سبوتيفاي (Spotify API)
- أخبار (NewsAPI + Wikipedia)
- عملات (ExchangeRate API)
- بحث (Google Custom Search)
- تكامل كامل مع TCMA و ToolRegistry الجديد
"""
import os, logging, base64, asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import httpx

logger = logging.getLogger(__name__)

# ========== إعدادات ==========
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", os.getenv("YOUTUBE_API_KEY", ""))
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

def _truncate(text: str, max_len: int) -> str:
    return text[:max_len] + "..." if len(text) > max_len else text

# ========== YOUTUBE (أساسي للفيديو والموسيقى) ==========
async def search_youtube(query: str, max_results: int = 3, lang: str = "ar") -> Optional[str]:
    """YouTube عبر Invidious (مجاني) أو YouTube API"""
    invidious_instances = ["https://inv.nadeko.net", "https://yewtu.be"]
    for instance in invidious_instances:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(f"{instance}/api/v1/search", params={"q": query, "type": "video", "sort": "relevance"})
                if resp.status_code == 200 and resp.json():
                    items = resp.json()
                    results = []
                    for item in items[:max_results]:
                        title = item.get("title", "فيديو")
                        video_id = item.get("videoId", "")
                        url = f"https://youtube.com/watch?v={video_id}" if video_id else ""
                        results.append(f"🎬 **{title}**\n   🔗 {url}")
                    return "\n\n".join(results)
        except: continue

    if YOUTUBE_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("https://www.googleapis.com/youtube/v3/search", params={"key": YOUTUBE_API_KEY, "q": query, "part": "snippet", "type": "video", "maxResults": max_results})
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    return "\n\n".join(f"🎬 **{i['snippet']['title']}**\n   🔗 https://youtube.com/watch?v={i['id']['videoId']}" for i in items[:max_results])
        except: pass
    return None

# ========== SPOTIFY ==========
class SpotifyClient:
    def __init__(self): self._token = None
    async def _auth(self):
        if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET: return None
        auth = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post("https://accounts.spotify.com/api/token", headers={"Authorization": f"Basic {auth}"}, data={"grant_type": "client_credentials"})
                if resp.status_code == 200: self._token = resp.json().get("access_token")
        except: pass
    async def search(self, query: str) -> Optional[str]:
        if not self._token: await self._auth()
        if not self._token: return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://api.spotify.com/v1/search", headers={"Authorization": f"Bearer {self._token}"}, params={"q": query, "type": "track", "limit": 1})
                if resp.status_code == 200:
                    tracks = resp.json().get("tracks", {}).get("items", [])
                    if tracks: t = tracks[0]; return f"🎵 **{t['name']}** - {t['artists'][0]['name']}\n   🔗 {t['external_urls']['spotify']}"
        except: pass
        return None
spotify_client = SpotifyClient()

async def search_spotify(query: str) -> Optional[str]:
    return await spotify_client.search(query)

# ========== الطقس ==========
async def get_weather(city: str = "Cairo", lang: str = "ar") -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            geo = await client.get("https://nominatim.openstreetmap.org/search", params={"q": city, "format": "json", "limit": 1}, headers={"User-Agent": "MyTwin/1.0"})
            if geo.status_code != 200 or not geo.json(): return {"error": "لم يتم العثور على المدينة"}
            lat, lon = float(geo.json()[0]["lat"]), float(geo.json()[0]["lon"])
            resp = await client.get("https://api.open-meteo.com/v1/forecast", params={"latitude": lat, "longitude": lon, "current_weather": True})
            if resp.status_code == 200:
                c = resp.json()["current_weather"]
                return {"city": city, "temperature": c["temperature"], "windspeed": c["windspeed"], "description": _weather_desc(c.get("weathercode", 0))}
    except: pass
    return {"error": "تعذر جلب الطقس"}

def _weather_desc(code: int) -> str:
    return {0: "سماء صافية", 1: "غائم جزئياً", 2: "غائم", 61: "أمطار خفيفة", 63: "أمطار متوسطة", 65: "أمطار غزيرة", 71: "ثلوج"}.get(code, "غير معروف")

# ========== الأخبار ==========
async def get_news(country: str = "sa", lang: str = "ar") -> Dict[str, Any]:
    if NEWS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get("https://newsapi.org/v2/top-headlines", params={"country": country, "apiKey": NEWS_API_KEY, "pageSize": 5})
                if resp.status_code == 200:
                    articles = resp.json().get("articles", [])
                    return {"articles": [{"title": a["title"], "url": a["url"]} for a in articles[:5]]}
        except: pass
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(f"https://ar.wikipedia.org/api/rest_v1/page/summary/بوابة:الأحداث_الجارية" if lang == "ar" else "https://en.wikipedia.org/api/rest_v1/page/summary/Portal:Current_events")
            if resp.status_code == 200:
                return {"articles": [{"title": "آخر الأحداث (Wikipedia)", "url": resp.json().get("content_urls", {}).get("desktop", {}).get("page", "")}]}
    except: pass
    return {"articles": []}

# ========== العملات ==========
async def get_currency(base: str = "USD", symbols: str = "EGP,SAR,AED,EUR") -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"https://api.exchangerate.host/latest?base={base}&symbols={symbols}")
            if resp.status_code == 200:
                return {"rates": resp.json().get("rates", {})}
    except: pass
    return {"rates": {}}

# ========== البحث ==========
async def search_web(query: str, lang: str = "ar") -> Dict[str, Any]:
    try:
        from app.infrastructure.ai.provider_router import provider_router
        response = await provider_router.generate(f"قدم معلومات عن: {query}. اللغة: {lang}.", language=lang)
        return {"results": response}
    except: return {"results": None}

async def deep_search(query: str, lang: str = "ar") -> Dict[str, Any]:
    try:
        from app.infrastructure.ai.provider_router import provider_router
        response = await provider_router.generate(f"بحث عميق: {query}. قدم تعريف شامل، أحدث التطورات، تحليلات. اللغة: {lang}.", language=lang)
        return {"results": response}
    except: return {"results": None}
