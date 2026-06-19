"""Sentry monitoring setup."""
import os, sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.asyncio import AsyncioIntegration

def init_sentry():
    dsn = os.getenv("SENTRY_DSN", "")
    if not dsn:
        print("⚠️ SENTRY_DSN غير مضبوط")
        return
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FastApiIntegration(transaction_style="endpoint"), AsyncioIntegration()],
        traces_sample_rate=0.3,
        environment=os.getenv("ENVIRONMENT", "production"),
        send_default_pii=False,
    )
    print("✅ Sentry مهيأ")
