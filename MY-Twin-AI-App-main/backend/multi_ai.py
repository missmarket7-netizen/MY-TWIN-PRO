import os, logging, asyncio
from typing import Optional, Tuple, List, Dict

logger = logging.getLogger("multi_ai")

class AIUnavailable(Exception):
    pass

class MultiAIClient:
    def __init__(self):
        self._openai_client = None
        self._groq_client = None
        self._genai_client = None
        self.max_retries = 1
        self.timeout = 12

    async def get_best(self, prompt: str, preferred_providers: Optional[List[str]] = None,
                       task: str = "general", lang: str = "ar") -> Tuple[str, str]:
        all_providers = [
            ("groq", self._try_groq, "llama-3.3-70b-versatile"),
            ("openrouter", self._try_openrouter, "meta-llama/llama-4-maverick"),
            ("gemini", self._try_gemini, "gemini-2.5-flash"),
        ]
        if preferred_providers:
            ordered = []
            for p in preferred_providers:
                match = next((x for x in all_providers if x[0] == p), None)
                if match: ordered.append(match)
            for x in all_providers:
                if x not in ordered: ordered.append(x)
            all_providers = ordered

        last_error = None
        for name, func, model_name in all_providers:
            for attempt in range(self.max_retries + 1):
                try:
                    result_text = await asyncio.wait_for(func(prompt), timeout=self.timeout)
                    if result_text and len(result_text) > 5:
                        return result_text, f"{name}/{model_name}"
                except asyncio.TimeoutError:
                    logger.warning(f"{name} timeout")
                except Exception as e:
                    last_error = e
                    logger.warning(f"{name} failed: {e}")
                await asyncio.sleep(0.3)
        raise AIUnavailable(f"All providers failed. Last: {last_error}")

    async def get_best_reply(self, prompt: str, task: str = "general", lang: str = "ar") -> str:
        text, _ = await self.get_best(prompt, task=task, lang=lang)
        return text

    async def health_check(self) -> Dict[str, bool]:
        test_prompt = "Say 'ok'"
        results = {}
        providers = [
            ("groq", self._try_groq, "llama-3.3-70b-versatile"),
            ("openrouter", self._try_openrouter, "meta-llama/llama-4-maverick"),
            ("gemini", self._try_gemini, "gemini-2.5-flash"),
        ]
        for name, func, _ in providers:
            try:
                res = await asyncio.wait_for(func(test_prompt), timeout=5)
                results[name] = bool(res and len(res) > 1)
            except Exception:
                results[name] = False
        return results

    async def _try_groq(self, prompt: str) -> Optional[str]:
        try:
            from openai import OpenAI
            key = os.getenv("GROQ_API_KEY")
            if not key: return None
            if not self._groq_client:
                self._groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
            for model in ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]:
                try:
                    resp = self._groq_client.chat.completions.create(
                        model=model, messages=[{"role":"user","content":prompt}],
                        max_tokens=500, temperature=0.7, timeout=10
                    )
                    return resp.choices[0].message.content
                except Exception: continue
        except Exception: pass
        return None

    async def _try_openrouter(self, prompt: str) -> Optional[str]:
        try:
            from openai import OpenAI
            key = os.getenv("OPENROUTER_API_KEY")
            if not key: return None
            if not self._openai_client:
                self._openai_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)
            for model in ["meta-llama/llama-4-maverick", "qwen/qwen-2.5-72b-instruct"]:
                try:
                    resp = self._openai_client.chat.completions.create(
                        model=model, messages=[{"role":"user","content":prompt}],
                        max_tokens=500, temperature=0.7, timeout=10
                    )
                    return resp.choices[0].message.content
                except Exception: continue
        except Exception: pass
        return None

    async def _try_gemini(self, prompt: str) -> Optional[str]:
        try:
            from google import genai
            key = os.getenv("GEMINI_API_KEY")
            if not key: return None
            if not self._genai_client:
                self._genai_client = genai.Client(api_key=key)
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self._genai_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config={"max_output_tokens": 500, "temperature": 0.7}
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            logger.warning(f"Gemini error: {e}")
        return None
