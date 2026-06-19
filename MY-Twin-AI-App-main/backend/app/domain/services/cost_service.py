"""Cost Service – optimize model selection by tier."""
MODEL_COST = {"groq":0.0,"gemini":0.0,"openrouter":0.0}

TIER_MODEL = {
    "free":    {"simple":"gemini","medium":"gemini","complex":"groq"},
    "premium": {"simple":"gemini","medium":"groq","complex":"openrouter"},
    "pro":     {"simple":"groq","medium":"openrouter","complex":"openrouter"},
}

def get_provider(tier: str, complexity: str) -> str:
    return TIER_MODEL.get(tier, TIER_MODEL["free"]).get(complexity, "gemini")

def estimate_cost(provider: str, tokens: int) -> float:
    return (tokens/1000)*MODEL_COST.get(provider, 0.0)
