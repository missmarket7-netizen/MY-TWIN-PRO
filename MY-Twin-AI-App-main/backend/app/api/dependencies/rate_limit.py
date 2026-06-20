"""Rate Limiter for feature routes."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])

def get_tier_limit(tier: str) -> str:
    limits = {"free": "5/minute", "plus": "15/minute", "premium": "30/minute", "pro": "60/minute", "yearly": "120/minute"}
    return limits.get(tier, "10/minute")
