"""
MyTwin – Model Registry v1.5
- يسجل النماذج المتاحة وتكاليفها واستخداماتها
"""
MODELS = {
    "groq": {
        "name": "groq/llama-3.3-70b-versatile",
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "capabilities": ["general", "reasoning", "coding", "search", "agent"],
    },
    "openrouter": {
        "name": "openrouter/meta-llama/llama-4-maverick",
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "capabilities": ["general", "deep_reasoning", "coding", "creative"],
    },
    "gemini": {
        "name": "gemini/gemini-2.5-flash",
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "capabilities": ["emotional", "general", "multilingual", "dream", "coaching", "planning"],
    },
    "gemini-image": {
        "name": "gemini/gemini-2.5-flash-image",
        "cost_per_1k_input": 0.0,
        "cost_per_1k_output": 0.0,
        "capabilities": ["image_generation"],
    },
}

# خرائط الاستخدام (تُستخدم بواسطة model_router)
TASK_MODEL_MAP = {
    "emotional": "gemini",
    "deep_reasoning": "openrouter",
    "reasoning": "openrouter",
    "coding": "groq",
    "search": "groq",
    "agent": "groq",
    "general": "groq",
    "coaching": "gemini",
    "dream": "gemini",
    "multilingual": "gemini",
    "planning": "gemini",
    "image_generation": "gemini-image",
}
