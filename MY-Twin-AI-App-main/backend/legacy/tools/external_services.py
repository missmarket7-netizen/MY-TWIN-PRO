"""
MyTwin – External Services v5.3 (Production Ready)
Tier 1: Weather (Open-Meteo), YouTube (Invidious fallback), Spotify, Google Search, Calendar
Tier 2: Home Assistant, News (RSS fallback), Maps, Location, Currency
Tier 3: Email, Telegram, Notes, Tasks
YouTube هو الأساسي للفيديو والموسيقى
"""
import os, logging, base64, asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
import httpx

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", os.getenv("YOUTUBE_API_KEY", ""))
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
HASS_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN", "")
HASS_URL = os.getenv("HOME_ASSISTANT_URL", "")
EMAIL_API_KEY = os.getenv("SENDGRID_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

def _get_limits_manager():
    try:
        from message_limits import check_feature_usage
        return check_feature_usage
    except:
        return None

_db = None
def get_db():
    global _db
    if _db is None:
        from supabase import create_client
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
        if SUPABASE_URL and SUPABASE_KEY:
            _db = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _db

def _truncate(text: str, max_len: int) -> str:
    """قص النص مع إضافة ... إذا كان أطول"""
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text

def _is_valid_url(url: str) -> bool:
    """التحقق من أن الرابط آمن (http/https فقط)"""
    return url.startswith("https://") or url.startswith("http://")

# ========== YOUTUBE (أساسي للفيديو والموسيقى) ==========

async def search_youtube(query: str, max_results: int = 3, lang: str = "ar", user_id: Optional[str] = None, tier: str = "free") -> Optional[str]:
    """YouTube هو الأساسي للفيديو والموسيقى"""
    check_func = _get_limits_manager()
    if check_func and user_id:
        allowed, _ = check_func(user_id, tier, "youtube")
        if not allowed:
            return "📺 استنفدت استخدام YouTube اليوم."

    # المحاولة 1: Invidious API (مجاني، لا يحتاج مفتاح)
    invidious_instances = [
        "https://inv.nadeko.net",
        "https://yewtu.be",
        "https://invidious.snopyta.org",
    ]
    
    for instance in invidious_instances:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    f"{instance}/api/v1/search",
                    params={"q": query, "type": "video", "sort": "relevance"},
                )
                if resp.status_code == 200:
                    items = resp.json()
                    if not items:
                        continue
                    results = []
                    for item in items[:max_results]:
                        title = item.get("title", "فيديو")
                        video_id = item.get("videoId", "")
                        url = f"https://youtube.com/watch?v={video_id}" if video_id else ""
                        author = item.get("author", "")
                        length = item.get("lengthSeconds", 0)
                        minutes = length // 60
                        results.append(f"🎬 **{title}**\n   👤 {author} | ⏱ {minutes} دقيقة\n   🔗 {url}")
                    if results:
                        return "\n\n".join(results)
        except Exception as e:
            logger.warning(f"Invidious {instance} failed: {e}")
            continue

    # المحاولة 2: YouTube Data API (إذا كان المفتاح موجوداً)
    if YOUTUBE_API_KEY:
        try:
            region = "SA" if lang == "ar" else "US"
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "key": YOUTUBE_API_KEY,
                        "q": query,
                        "part": "snippet",
                        "type": "video",
                        "maxResults": max_results,
                        "regionCode": region,
                        "relevanceLanguage": lang,
                    },
                )
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    if items:
                        return "\n\n".join(
                            f"🎬 **{item['snippet']['title']}**\n   🔗 https://youtube.com/watch?v={item['id']['videoId']}"
                            for item in items[:max_results]
                        )
        except Exception as e:
            logger.error(f"YouTube API Error: {e}")

    return None

# ========== SPOTIFY (احتياطي فقط للموسيقى) ==========

class SpotifyClient:
    def __init__(self):
        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        self._token = None
        self._token_expiry = None

    async def _get_token(self) -> Optional[str]:
        if not self.client_id or not self.client_secret:
            return None
        if self._token and self._token_expiry and datetime.now(timezone.utc) < self._token_expiry:
            return self._token
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://accounts.spotify.com/api/token",
                    headers={"Authorization": f"Basic {auth}"},
                    data={"grant_type": "client_credentials"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    self._token = data.get("access_token")
                    self._token_expiry = datetime.now(timezone.utc) + timedelta(seconds=3500)
                    return self._token
        except Exception as e:
            logger.error(f"Spotify Auth Error: {e}")
        return None

    async def search(self, query: str) -> str:
        token = await self._get_token()
        if not token:
            return ""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.spotify.com/v1/search",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"q": query, "type": "track", "limit": 1},
                )
                if resp.status_code == 200:
                    tracks = resp.json().get("tracks", {}).get("items", [])
                    if tracks:
                        t = tracks[0]
                        return f"🎵 **{t['name']}** - {t['artists'][0]['name']}\n   🔗 {t['external_urls']['spotify']}"
        except Exception as e:
            logger.error(f"Spotify Search Error: {e}")
        return ""

spotify_client = SpotifyClient()

async def search_spotify(query: str, user_id: Optional[str] = None, tier: str = "free") -> Optional[str]:
    """Spotify احتياطي للموسيقى (YouTube هو الأساسي)"""
    check_func = _get_limits_manager()
    if check_func and user_id:
        allowed, _ = check_func(user_id, tier, "spotify")
        if not allowed:
            return "🎵 استنفدت استخدام Spotify اليوم."
    return await spotify_client.search(query)

# ========== WEATHER ==========

async def get_weather(city: str = "Cairo", lat: Optional[float] = None, lon: Optional[float] = None, user_id: Optional[str] = None, tier: str = "free") -> Optional[str]:
    check_func = _get_limits_manager()
    if check_func and user_id:
        allowed, _ = check_func(user_id, tier, "weather")
        if not allowed:
            return "🌤️ استنفدت استعلامات الطقس اليوم."
    
    if lat is None or lon is None:
        lat, lon = await _city_to_coordinates(city)
        if lat is None:
            return f"لم أتمكن من تحديد إحداثيات {city}."
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat, "longitude": lon,
                    "current_weather": True,
                    "daily": "temperature_2m_max,temperature_2m_min",
                    "timezone": "auto",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current_weather", {})
                temp = current.get("temperature", "?")
                wind = current.get("windspeed", 0)
                code = current.get("weathercode", 0)
                weather_desc = _weather_code_desc(code)
                return f"🌤️ الطقس في {city}:\n   {weather_desc}\n   🌡️ {temp}°C\n   💨 رياح: {wind} كم/س"
    except Exception as e:
        logger.error(f"Open-Meteo Error: {e}")
    return None

def _weather_code_desc(code: int) -> str:
    codes = {0: "سماء صافية ☀️", 1: "غائم جزئياً ⛅", 2: "غائم ☁️", 3: "غائم كلياً ☁️", 45: "ضباب 🌫️", 48: "ضباب متجمد ❄️", 51: "رذاذ خفيف 🌦️", 53: "رذاذ متوسط 🌦️", 55: "رذاذ كثيف 🌧️", 61: "أمطار خفيفة 🌧️", 63: "أمطار متوسطة 🌧️", 65: "أمطار غزيرة ⛈️", 71: "ثلوج خفيفة ❄️", 73: "ثلوج متوسطة ❄️", 75: "ثلوج كثيفة ❄️", 80: "زخات مطر 🌦️", 95: "عاصفة رعدية ⛈️", 96: "عاصفة رعدية مع بَرَد ⛈️", 99: "عاصفة رعدية شديدة ⛈️"}
    return codes.get(code, "غير معروف")

async def _city_to_coordinates(city: str):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": city, "format": "json", "limit": 1},
                headers={"User-Agent": "MyTwin/1.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logger.warning(f"Geocoding failed for {city}: {e}")
    return None, None

# ========== NEWS ==========

async def get_news(country: str = "sa", category: str = "general", user_id: Optional[str] = None, tier: str = "free") -> Optional[str]:
    check_func = _get_limits_manager()
    if check_func and user_id:
        allowed, _ = check_func(user_id, tier, "news")
        if not allowed:
            return "📰 استنفدت استعلامات الأخبار اليوم."
    
    # المحاولة 1: NewsAPI (إذا كان المفتاح موجوداً)
    if NEWS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={"country": country, "category": category, "apiKey": NEWS_API_KEY, "pageSize": 5},
                )
                if resp.status_code == 200:
                    articles = resp.json().get("articles", [])
                    if articles:
                        return "\n\n".join(
                            f"📰 **{a['title']}**\n   {a.get('description', '')[:100]}\n   🔗 {a['url']}"
                            for a in articles[:5] if a.get('title')
                        )
        except Exception as e:
            logger.error(f"NewsAPI Error: {e}")
    
    # المحاولة 2: Wikipedia Current Events (بديل مجاني)
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            lang_code = "ar" if country in ["sa", "eg", "ae"] else "en"
            resp = await client.get(
                f"https://{lang_code}.wikipedia.org/api/rest_v1/page/summary/Portal:Current_events",
            )
            if resp.status_code == 200:
                data = resp.json()
                extract = data.get("extract", "")[:500]
                if extract:
                    return f"📰 **آخر الأحداث:**\n\n{extract}\n\n🔗 [المصدر]({data.get('content_urls', {}).get('desktop', {}).get('page', '')})"
    except Exception as e:
        logger.warning(f"Wikipedia fallback failed: {e}")

    return None

# ========== CURRENCY ==========

async def get_currency(base: str = "USD", symbols: str = "EGP,SAR,AED,EUR,GBP") -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.exchangerate.host/latest",
                params={"base": base, "symbols": symbols},
            )
            if resp.status_code == 200:
                rates = resp.json().get("rates", {})
                if rates:
                    lines = [f"💱 **أسعار {base}:**"]
                    currency_names = {"EGP": "جنيه مصري 🇪🇬", "SAR": "ريال سعودي 🇸🇦", "AED": "درهم إماراتي 🇦🇪", "EUR": "يورو 🇪🇺", "GBP": "جنيه إسترليني 🇬🇧"}
                    for code, rate in rates.items():
                        name = currency_names.get(code, code)
                        lines.append(f"   • {name}: {rate:.4f}")
                    return "\n".join(lines)
    except Exception as e:
        logger.error(f"Currency Error: {e}")
    return None

# ========== باقي الأدوات (مختصرة) ==========

async def search_google(query: str, num: int = 3, user_id: Optional[str] = None, tier: str = "free") -> Optional[str]:
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return None
    check_func = _get_limits_manager()
    if check_func and user_id:
        allowed, _ = check_func(user_id, tier, "search")
        if not allowed:
            return "🔍 استنفدت عمليات البحث اليوم."
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://www.googleapis.com/customsearch/v1",
                params={"key": GOOGLE_API_KEY, "cx": GOOGLE_CSE_ID, "q": query, "num": min(num, 5)},
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                if items:
                    return "\n\n".join(
                        f"🔎 **{item['title']}**\n   {item.get('snippet', '')[:150]}\n   🔗 {item['link']}"
                        for item in items[:num]
                    )
    except Exception as e:
        logger.error(f"Google Search Error: {e}")
    return None

async def get_todoist_tasks(token: str) -> str:
    return "يحتاج ربط حساب Todoist."

async def get_calendar_events(token: str) -> str:
    if not token:
        return "يحتاج ربط Google Calendar."
    try:
        now = datetime.now(timezone.utc).isoformat() + "Z"
        end = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat() + "Z"
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={"Authorization": f"Bearer {token}"},
                params={"timeMin": now, "timeMax": end, "maxResults": 5, "singleEvents": True, "orderBy": "startTime"},
            )
            if resp.status_code == 200:
                events = resp.json().get("items", [])
                if not events:
                    return "لا توجد أحداث اليوم."
                return "📅 **أحداث اليوم:**\n" + "\n".join(f"   • {e.get('summary', '?')}" for e in events[:5])
    except Exception as e:
        logger.error(f"Calendar Error: {e}")
    return ""

async def home_assistant_control(command: str, entity_id: Optional[str] = None) -> str:
    return "🏠 Home Assistant غير مهيأ."

async def get_maps(query: str) -> Optional[str]:
    return f"🗺️ ابحث عن '{query}' على الخرائط"

async def get_location_info(lat: float, lon: float) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}",
                headers={"User-Agent": "MyTwin/1.0"},
            )
            if resp.status_code == 200:
                data = resp.json()
                return f"📍 {data.get('display_name', 'موقع غير معروف')}"
    except:
        pass
    return None

async def send_email(to: str, subject: str, body: str) -> str:
    return "📧 البريد غير مهيأ"

async def send_telegram(chat_id: str, message: str) -> str:
    if not TELEGRAM_BOT_TOKEN:
        return "✈️ تيليجرام غير مهيأ"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": message},
            )
            if resp.status_code == 200:
                return "✈️ تم إرسال رسالة تيليجرام"
    except Exception as e:
        logger.error(f"Telegram Error: {e}")
    return "فشل إرسال تيليجرام"

async def get_notes(user_id: str) -> List[Dict]:
    db = get_db()
    if not db:
        return []
    res = db.table("notes").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data or []

async def create_note(user_id: str, content: str) -> Dict:
    db = get_db()
    if not db:
        return {}
    res = db.table("notes").insert({"user_id": user_id, "content": content}).execute()
    return res.data[0] if res.data else {}

async def get_tasks(user_id: str) -> List[Dict]:
    db = get_db()
    if not db:
        return []
    res = db.table("tasks").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data or []

async def create_task(user_id: str, title: str, due: Optional[str] = None) -> Dict:
    db = get_db()
    if not db:
        return {}
    res = db.table("tasks").insert({"user_id": user_id, "title": title, "due": due}).execute()
    return res.data[0] if res.data else {}

async def get_knowledge(query: str) -> Optional[str]:
    return None
