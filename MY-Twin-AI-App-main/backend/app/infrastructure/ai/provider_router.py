"""
Provider Router v3.0 – موازن ذكي متعدد المزودين مع إدارة متقدمة للمفاتيح
==========================================================================
- إدارة مفاتيح API متعددة (Gemini, Groq, OpenRouter)
- توزيع الحمل واستهلاك الحدود اليومية
- توجيه ذكي حسب المهمة، الباقة، والحالة العاطفية
- Circuit Breaker للمزودين المتعطلين
- تكامل كامل مع Observability (Metrics, Tracing)
"""
import os, logging, asyncio, random, time
from typing import Tuple, Optional, List, Dict
from collections import defaultdict
from datetime import datetime, timezone, timedelta

logger = logging.getLogger("provider_router")

# ============================================================
# إدارة مفاتيح API (متقدمة)
# ============================================================
class APIKeyManager:
    def __init__(self):
        self._keys: Dict[str, List[Dict]] = {
            "gemini": [], "groq": [], "openrouter": [],
        }
        self._daily_limits: Dict[str, int] = {
            "gemini": 1500, "groq": 1000, "openrouter": 200,
        }
        self._usage_reset_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0) + timedelta(days=1)
        self._load_keys()
    
    def _load_keys(self):
        for var in ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]:
            k = os.getenv(var, "")
            if k: self._keys["gemini"].append({"key": k, "usage": 0, "failures": 0, "last_error": None})
        for var in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]:
            k = os.getenv(var, "")
            if k: self._keys["groq"].append({"key": k, "usage": 0, "failures": 0, "last_error": None})
        for var in ["OPENROUTER_API_KEY", "OPENROUTER_API_KEY_2", "OPENROUTER_API_KEY_3"]:
            k = os.getenv(var, "")
            if k: self._keys["openrouter"].append({"key": k, "usage": 0, "failures": 0, "last_error": None})
        logger.info(f"🔑 Keys loaded: G={len(self._keys['gemini'])}, Gr={len(self._keys['groq'])}, O={len(self._keys['openrouter'])}")
    
    def _check_reset(self):
        if datetime.now(timezone.utc) >= self._usage_reset_time:
            for provider in self._keys:
                for k in self._keys[provider]:
                    k["usage"] = 0
            self._usage_reset_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0) + timedelta(days=1)
            logger.info("🔄 Daily API usage reset")

    def get_available_provider(self, preferred: List[str], user_tier: str = "free") -> Tuple[str, str]:
        self._check_reset()
        
        if user_tier in ["premium", "pro", "yearly"]:
            priority = [p for p in preferred if p in self._keys] + [p for p in ["gemini", "groq", "openrouter"] if p not in preferred]
        else:
            priority = ["groq"] + [p for p in preferred if p != "groq"]
        
        for provider in priority:
            if provider not in self._keys: continue
            available_keys = [k for k in self._keys[provider] if k["usage"] < self._daily_limits[provider] and k["failures"] < 3]
            if available_keys:
                chosen = random.choice(available_keys)
                chosen["usage"] += 1
                return provider, chosen["key"]
        
        for provider in ["groq", "gemini", "openrouter"]:
            if self._keys.get(provider):
                k = self._keys[provider][0]
                k["usage"] += 1
                return provider, k["key"]
        raise AIUnavailable("All API keys exhausted")
    
    def mark_failure(self, provider: str, key: str):
        for k in self._keys.get(provider, []):
            if k["key"] == key:
                k["failures"] += 1
                k["last_error"] = datetime.now(timezone.utc).isoformat()
                break

# ============================================================
# استثناءات
# ============================================================
class AIUnavailable(Exception):
    pass

# ============================================================
# Circuit Breaker (حماية من المزودين المتعطلين)
# ============================================================
class CircuitBreaker:
    def __init__(self):
        self._failures: Dict[str, int] = defaultdict(int)
        self._cooldown: Dict[str, float] = {}
        self._threshold = 5
        self._cooldown_seconds = 60

    def can_use(self, provider: str) -> bool:
        if provider in self._cooldown:
            if time.time() - self._cooldown[provider] < self._cooldown_seconds:
                return False
            del self._cooldown[provider]
            self._failures[provider] = 0
        return True

    def record_failure(self, provider: str):
        self._failures[provider] += 1
        if self._failures[provider] >= self._threshold:
            self._cooldown[provider] = time.time()
            logger.warning(f"🔴 Circuit Breaker: {provider} disabled for {self._cooldown_seconds}s")

# ============================================================
# موجه المزودين (الرئيسي)
# ============================================================
class ProviderRouter:
    def __init__(self):
        self.key_manager = APIKeyManager()
        self.circuit_breaker = CircuitBreaker()
        self._clients = {}

    def _get_client(self, provider: str, key: str):
        cache_key = f"{provider}:{key[:10]}"
        if cache_key not in self._clients:
            if provider in ["groq", "openrouter"]:
                from openai import OpenAI
                base = "https://api.groq.com/openai/v1" if provider == "groq" else "https://openrouter.ai/api/v1"
                self._clients[cache_key] = OpenAI(base_url=base, api_key=key)
            elif provider == "gemini":
                from google import genai
                self._clients[cache_key] = genai.Client(api_key=key)
        return self._clients[cache_key]

    async def route(
        self,
        prompt: str,
        task: str = "general",
        emotion: Optional[str] = None,
        tier: str = "free",
        timeout: float = 12.0,
        user_id: Optional[str] = None,
    ) -> Tuple[str, str]:
        start_time = time.time()

        # تحديد المزودين المفضلين حسب المهمة والعاطفة
        task_providers = {
            "emotional": ["gemini", "groq"],
            "deep_reasoning": ["gemini", "openrouter"],
            "coaching": ["gemini"],
            "coding": ["groq", "openrouter", "gemini"],
            "general": ["groq", "gemini"],
            "quick_reply": ["groq"],
            "summarization": ["groq", "openrouter"],
        }
        preferred = task_providers.get(task, ["groq", "gemini"])

        # استبعاد المزودين المعطلين
        preferred = [p for p in preferred if self.circuit_breaker.can_use(p)]

        # محاولة مع كل مزود
        max_retries = len(preferred)
        for attempt in range(max_retries):
            try:
                provider, key = self.key_manager.get_available_provider(preferred, tier)
                client = self._get_client(provider, key)

                if provider in ["groq", "openrouter"]:
                    model = "llama-3.3-70b-versatile" if provider == "groq" else "meta-llama/llama-4-maverick"
                    resp = await asyncio.wait_for(
                        client.chat.completions.create(
                            model=model, messages=[{"role": "user", "content": prompt}],
                            max_tokens=500, temperature=0.7, timeout=10,
                        ),
                        timeout=timeout
                    )
                    text = resp.choices[0].message.content
                elif provider == "gemini":
                    loop = asyncio.get_running_loop()
                    response = await asyncio.wait_for(
                        loop.run_in_executor(None, lambda: client.models.generate_content(model="gemini-2.5-flash", contents=prompt)),
                        timeout=timeout
                    )
                    text = response.text if response else ""

                if text and len(text.strip()) > 5:
                    duration = (time.time() - start_time) * 1000
                    logger.info(f"✅ {provider} ({task}): {len(text)} حرف, {duration:.0f}ms")
                    
                    # تكامل مع Metrics
                    try:
                        from app.observability.metrics_service import metrics
                        metrics.record_request(f"ai:{provider}", 200, duration, user_id, tier)
                    except: pass
                    
                    return text, provider
                else:
                    self.key_manager.mark_failure(provider, key)
            except (asyncio.TimeoutError, Exception) as e:
                logger.warning(f"⚠️ {provider} failed ({attempt+1}/{max_retries}): {e}")
                self.circuit_breaker.record_failure(provider)
                self.key_manager.mark_failure(provider, key)
                preferred = [p for p in preferred if p != provider]

        raise AIUnavailable("All providers failed")

    async def generate(self, prompt: str, language: str = "ar", task: str = "general", user_id: Optional[str] = None) -> Optional[str]:
        try:
            text, _ = await self.route(prompt, task=task, user_id=user_id)
            return text
        except AIUnavailable:
            return None

    async def health_check_all(self) -> Dict[str, bool]:
        return {
            "groq": len(self.key_manager._keys["groq"]) > 0,
            "gemini": len(self.key_manager._keys["gemini"]) > 0,
            "openrouter": len(self.key_manager._keys["openrouter"]) > 0,
        }

# نسخة عالمية
provider_router = ProviderRouter()

# ========== التوافق مع الكود القديم ==========
class MultiAIClient:
    def __init__(self): pass
    async def get_best_reply(self, prompt: str, task: str = "general") -> str:
        return await provider_router.generate(prompt, task=task)

