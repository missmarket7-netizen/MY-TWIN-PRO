"""
MyTwin – Rate Limiter
حماية السيرفر مع مراعاة الباقة
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from fastapi.responses import JSONResponse

def get_user_or_ip(request: Request) -> str:
    """استخدام user_id لو موجود، وإلا IP"""
    uid = getattr(request.state, "uid", None)
    return uid if uid else get_remote_address(request)

# حدود المعدل حسب الباقة
TIER_RATES = {
    "free":             "10/minute",
    "free_week1":       "15/minute",
    "plus":             "30/minute",
    "premium":          "60/minute",
    "pro":              "120/minute",
    "yearly":           "200/minute",
}

limiter = Limiter(
    key_func=get_user_or_ip,
    default_limits=["30/minute"],
)

async def rate_limit_exceeded_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "أبطئ قليلاً... أنا هنا ومش رايح 💜",
            "retry_after": 60,
        },
    )
