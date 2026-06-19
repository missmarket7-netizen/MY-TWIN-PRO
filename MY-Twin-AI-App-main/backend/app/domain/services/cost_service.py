"""
Cost Service – Smart task routing with specific OpenRouter models.
Each task maps to a SPECIFIC model, not just the provider.
"""
import random, logging
from typing import Dict, List

logger = logging.getLogger("cost_service")

# ========== نماذج محددة (Provider/Model) ==========
# لكل مهمة: [أساسي (50%), احتياطي ١ (30%), احتياطي ٢ (20%)]
TASK_MODELS: Dict[str, Dict[str, List[str]]] = {
    "free": {
        "general":    ["groq/llama-3.3-70b", "gemini/gemini-2.5-flash", "openrouter/qwen-2.5-72b"],
        "emotional":  ["gemini/gemini-2.5-flash", "groq/llama-3.3-70b", "openrouter/llama-4-maverick"],
        "coding":     ["openrouter/deepseek-v4-flash", "groq/llama-3.3-70b", "gemini/gemini-2.5-flash"],
        "reasoning":  ["openrouter/llama-4-maverick", "gemini/gemini-2.5-flash", "groq/llama-3.3-70b"],
        "coaching":   ["gemini/gemini-2.5-flash", "openrouter/llama-4-maverick", "groq/llama-3.3-70b"],
        "quick":      ["groq/llama-3.3-70b", "openrouter/mistral-7b", "gemini/gemini-2.5-flash"],
    },
    "plus": {
        "general":    ["groq/llama-3.3-70b", "gemini/gemini-2.5-flash", "openrouter/qwen-2.5-72b"],
        "emotional":  ["gemini/gemini-2.5-flash", "openrouter/llama-4-maverick", "groq/llama-3.3-70b"],
        "coding":     ["openrouter/deepseek-v4-flash", "groq/llama-3.3-70b", "gemini/gemini-2.5-flash"],
        "reasoning":  ["openrouter/llama-4-maverick", "gemini/gemini-2.5-flash", "groq/llama-3.3-70b"],
        "coaching":   ["gemini/gemini-2.5-flash", "groq/llama-3.3-70b", "openrouter/llama-4-maverick"],
        "quick":      ["groq/llama-3.3-70b", "openrouter/mistral-7b", "gemini/gemini-2.5-flash"],
    },
    "premium": {
        "general":    ["gemini/gemini-2.5-flash", "groq/llama-3.3-70b", "openrouter/llama-4-maverick"],
        "emotional":  ["gemini/gemini-2.5-flash", "openrouter/llama-4-maverick", "groq/llama-3.3-70b"],
        "coding":     ["openrouter/deepseek-v4-flash", "gemini/gemini-2.5-flash", "groq/llama-3.3-70b"],
        "reasoning":  ["openrouter/llama-4-maverick", "gemini/gemini-2.5-flash", "groq/llama-3.3-70b"],
        "coaching":   ["gemini/gemini-2.5-flash", "openrouter/llama-4-maverick", "groq/llama-3.3-70b"],
        "quick":      ["groq/llama-3.3-70b", "gemini/gemini-2.5-flash", "openrouter/mistral-7b"],
    },
    "pro": {
        "general":    ["gemini/gemini-2.5-flash", "openrouter/llama-4-maverick", "groq/llama-3.3-70b"],
        "emotional":  ["gemini/gemini-2.5-flash", "openrouter/llama-4-maverick", "groq/llama-3.3-70b"],
        "coding":     ["openrouter/deepseek-v4-flash", "gemini/gemini-2.5-flash", "groq/llama-3.3-70b"],
        "reasoning":  ["openrouter/llama-4-maverick", "gemini/gemini-2.5-flash", "groq/llama-3.3-70b"],
        "coaching":   ["gemini/gemini-2.5-flash", "openrouter/llama-4-maverick", "groq/llama-3.3-70b"],
        "quick":      ["groq/llama-3.3-70b", "openrouter/mistral-7b", "gemini/gemini-2.5-flash"],
    },
}

# ========== نماذج OpenRouter المتاحة ==========
OPENROUTER_MODELS = {
    "openrouter/llama-4-maverick":     "Meta Llama 4 Maverick - تفكير عميق، تحليل",
    "openrouter/qwen-2.5-72b":        "Qwen 2.5 72B - برمجة، تحليل، شرح",
    "openrouter/deepseek-v4-flash":   "DeepSeek V4 Flash - برمجة، تلخيص، سرعة",
    "openrouter/mistral-7b":          "Mistral 7B - محادثة سريعة، بسيطة",
    "openrouter/gemma-4-9b":          "Gemma 4 9B - محادثة عامة، دعم",
}

# ========== حدود الباقات ==========
TIER_LIMITS: Dict[str, Dict] = {
    "free":    {"messages": 10,  "tokens_per_msg": 200},
    "plus":    {"messages": 30,  "tokens_per_msg": 300},
    "premium": {"messages": 100, "tokens_per_msg": 500},
    "pro":     {"messages": 500, "tokens_per_msg": 800},
    "yearly":  {"messages": 9999, "tokens_per_msg": 1000},
}

# ========== دوال ==========

def get_best_model(tier: str, task: str = "general") -> str:
    """
    يُرجع أفضل نموذج (Provider/Model) للمهمة.
    توزيع عشوائي: الأساسي 50%، الاحتياطي ١ 30%، الاحتياطي ٢ 20%.
    """
    tier_map = TASK_MODELS.get(tier, TASK_MODELS["free"])
    models = tier_map.get(task, ["groq/llama-3.3-70b", "gemini/gemini-2.5-flash", "openrouter/qwen-2.5-72b"])
    
    rand = random.random()
    if rand < 0.5 and len(models) >= 1:
        return models[0]
    elif rand < 0.8 and len(models) >= 2:
        return models[1]
    elif len(models) >= 3:
        return models[2]
    return models[0]


def get_fallback_models(tier: str, task: str = "general") -> List[str]:
    """يُرجع قائمة النماذج بالترتيب (أساسي + احتياطيات)."""
    tier_map = TASK_MODELS.get(tier, TASK_MODELS["free"])
    return tier_map.get(task, ["groq/llama-3.3-70b", "gemini/gemini-2.5-flash", "openrouter/qwen-2.5-72b"])


def get_tier_limits(tier: str) -> Dict:
    """تُرجع حدود الباقة."""
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])


def estimate_cost(provider: str, tokens: int) -> float:
    """تقدير التكلفة (جميعها مجانية)."""
    return 0.0
