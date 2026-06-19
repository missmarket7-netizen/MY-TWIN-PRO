"""Provider Router – Multi-AI Load Balancer with API Key Manager."""
import os, logging, asyncio, random, time
from typing import Tuple, Optional, List, Dict
from collections import defaultdict

logger = logging.getLogger("provider_router")

class APIKeyManager:
    """يدير مفاتيح API ويتتبع استخدامها اليومي."""
    
    def __init__(self):
        self._keys: Dict[str, List[str]] = {
            "gemini": [], "groq": [], "openrouter": [],
        }
        self._daily_usage: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        self._daily_limits: Dict[str, int] = {
            "gemini": 1500, "groq": 1000, "openrouter": 200,
        }
        self._load_keys()
    
    def _load_keys(self):
        """تحميل المفاتيح من متغيرات البيئة."""
        for var in ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3"]:
            k = os.getenv(var, "")
            if k: self._keys["gemini"].append(k)
        for var in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]:
            k = os.getenv(var, "")
            if k: self._keys["groq"].append(k)
        for var in ["OPENROUTER_API_KEY", "OPENROUTER_API_KEY_2", "OPENROUTER_API_KEY_3"]:
            k = os.getenv(var, "")
            if k: self._keys["openrouter"].append(k)
        logger.info(f"🔑 Keys loaded: G={len(self._keys['gemini'])}, Gr={len(self._keys['groq'])}, O={len(self._keys['openrouter'])}")
    
    def get_available_provider(self, preferred: List[str], user_tier: str = "free") -> Tuple[str, str]:
        """
        يختار أفضل مزود ومفتاح متاح.
        user_tier: free يفضل groq، المميز يفضل gemini.
        يُرجع (provider_name, api_key).
        """
        # ترتيب المزودين حسب الباقة
        if user_tier in ["premium", "pro", "yearly"]:
            priority = [p for p in preferred if p in self._keys] + [p for p in ["gemini", "groq", "openrouter"] if p not in preferred]
        else:
            priority = ["groq"] + [p for p in preferred if p != "groq"]
        
        for provider in priority:
            if provider not in self._keys:
                continue
            for idx, key in enumerate(self._keys[provider]):
                if self._daily_usage[provider][idx] < self._daily_limits[provider]:
                    self._daily_usage[provider][idx] += 1
                    return provider, key
        # كل المفاتيح مستنفدة – استخدم الأول
        for provider in ["groq", "gemini", "openrouter"]:
            if self._keys.get(provider):
                idx = 0
                self._daily_usage[provider][idx] += 1
                return provider, self._keys[provider][idx]
        raise AIUnavailable("All API keys exhausted")
    
    def get_usage_stats(self) -> Dict:
        return {
            p: {str(i): u for i, u in keys.items()}
            for p, keys in self._daily_usage.items()
        }

class AIUnavailable(Exception):
    pass

class ProviderRouter:
    def __init__(self):
        self.key_manager = APIKeyManager()
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
    
    async def route(self, prompt: str, task: str = "general", emotion: Optional[str] = None, tier: str = "free", timeout: float = 12.0) -> Tuple[str, str]:
        # تحديد المزودين المفضلين حسب المهمة
        task_providers = {
            "emotional": ["gemini"], "deep_reasoning": ["gemini"], "coaching": ["gemini"],
            "coding": ["groq", "openrouter"], "general": ["groq", "gemini"],
            "quick_reply": ["groq"], "summarization": ["groq"],
        }
        preferred = task_providers.get(task, ["groq", "gemini"])
        
        # الحصول على مفتاح متاح
        provider, key = self.key_manager.get_available_provider(preferred, tier)
        client = self._get_client(provider, key)
        
        try:
            if provider in ["groq", "openrouter"]:
                model = "llama-3.3-70b-versatile" if provider == "groq" else "meta-llama/llama-4-maverick"
                resp = client.chat.completions.create(
                    model=model, messages=[{"role":"user","content":prompt}],
                    max_tokens=500, temperature=0.7, timeout=10,
                )
                return resp.choices[0].message.content, provider
            elif provider == "gemini":
                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                )
                return response.text if response else "", "gemini"
        except Exception as e:
            logger.warning(f"{provider} failed: {e}")
            raise AIUnavailable(str(e))

provider_router = ProviderRouter()
