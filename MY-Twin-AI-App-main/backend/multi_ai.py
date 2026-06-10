import os, logging, asyncio
from typing import Optional, AsyncGenerator
import google.generativeai as genai
from openai import OpenAI

logger = logging.getLogger("multi_ai")

class AIUnavailable(Exception):
    pass

class MultiAIClient:
    def __init__(self):
        # Gemini (local)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_flash = genai.GenerativeModel("gemini-2.0-flash")
            except Exception as e:
                logger.error(f"Gemini init failed: {e}")
                self.gemini_flash = None
        else:
            self.gemini_flash = None

        # Groq
        groq_key = os.getenv("GROQ_API_KEY")
        self.groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_key) if groq_key else None

        # OpenRouter
        or_key = os.getenv("OPENROUTER_API_KEY")
        self.or_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=or_key) if or_key else None

    def _groq(self, model: str, prompt: str) -> Optional[str]:
        if not self.groq_client: return None
        try:
            resp = self.groq_client.chat.completions.create(
                model=model, messages=[{"role":"user","content":prompt}],
                temperature=0.7, max_tokens=150
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning(f"Groq [{model}]: {e}")
            return None

    def _or(self, model: str, prompt: str) -> Optional[str]:
        if not self.or_client: return None
        try:
            resp = self.or_client.chat.completions.create(
                model=model, messages=[{"role":"user","content":prompt}],
                temperature=0.7, max_tokens=150
            )
            return resp.choices[0].message.content
        except Exception as e:
            logger.warning(f"OpenRouter [{model}]: {e}")
            return None

    # نماذج Groq
    def groq_chat(self, p): return self._groq("llama-3.3-70b-versatile", p)

    # نماذج OpenRouter المجانية الصحيحة (آخر تحديث)
    def gemini25_flash(self, p): return self._or("google/gemini-2.5-flash-lite", p)
    def llama4_maverick(self, p): return self._or("meta-llama/llama-4-maverick", p)
    def deepseek_v4(self, p): return self._or("deepseek/deepseek-v4-flash", p)
    def qwen2_5(self, p): return self._or("qwen/qwen2.5-72b-instruct", p)
    def phi3_mini(self, p): return self._or("microsoft/phi-3-mini-128k-instruct", p)

    def gemini_chat(self, p: str) -> str:
        if not self.gemini_flash:
            return "أنا هنا معاك 💜"
        try:
            resp = self.gemini_flash.generate_content(p)
            return resp.text.strip() if resp.text else "أنا هنا معاك 💜"
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return "أنا هنا معاك 💜"

    async def get_best_reply(self, prompt: str, task: str = "general") -> str:
        chains = {
            "general":        [self.groq_chat, self.llama4_maverick, self.gemini25_flash, self.gemini_chat],
            "emotional":      [self.groq_chat, self.llama4_maverick, self.gemini_chat],
            "coding":         [self.deepseek_v4, self.phi3_mini, self.groq_chat, self.gemini_chat],
            "deep_reasoning": [self.deepseek_v4, self.qwen2_5, self.groq_chat, self.gemini_chat],
            "multilingual":   [self.llama4_maverick, self.qwen2_5, self.groq_chat, self.gemini_chat],
            "planning":       [self.qwen2_5, self.llama4_maverick, self.groq_chat, self.gemini_chat],
            "coaching":       [self.groq_chat, self.llama4_maverick, self.gemini_chat],
            "dream":          [self.groq_chat, self.llama4_maverick, self.gemini_chat],
            "search":         [self.deepseek_v4, self.groq_chat, self.gemini_chat],
            "agent":          [self.qwen2_5, self.llama4_maverick, self.gemini_chat],
        }
        loop = asyncio.get_running_loop()
        for fn in chains.get(task, chains["general"]):
            try:
                result = await loop.run_in_executor(None, fn, prompt)
                if result and len(result.strip()) >= 1:
                    return result.strip()
            except Exception:
                continue
        return "أنا هنا معاك 💜"

    async def stream_reply(self, prompt: str, task: str = "general") -> AsyncGenerator[str, None]:
        if self.groq_client:
            try:
                stream = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role":"user","content":prompt}],
                    temperature=0.7, max_tokens=150, stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:
                logger.warning(f"Groq stream failed: {e}")
        full = await self.get_best_reply(prompt, task)
        yield full
