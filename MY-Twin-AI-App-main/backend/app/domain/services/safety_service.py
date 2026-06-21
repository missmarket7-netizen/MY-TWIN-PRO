"""
Safety Service v3.0 – متكامل مع Security Auditor و TCMA
=============================================================
- فحص المحتوى (باستخدام SecurityAudit)
- تنقية النصوص
- خطوط مساعدة نفسية
- تسجيل الحوادث في TCMA
"""
import re, logging
from typing import Dict, Optional

logger = logging.getLogger("safety_service")

# خطوط المساعدة النفسية
HELPLINES = {
    "ar": "🆘 خط المساعدة النفسية (مصر): 08008880700\n🆘 الخط الساخن للدعم النفسي (السعودية): 920033360",
    "en": "🆘 Crisis Helpline: 988 (US/Canada)\n🆘 Samaritans: 116 123 (UK)",
}

BLOCKED_KEYWORDS = [
    "انتحار","أقتل","أريد الموت","suicide","kill myself","bomb","قنبلة",
    "مخدرات","drugs","porn","إرهابي","terrorist"
]

def check_safety(text: str) -> Dict:
    """
    فحص سريع للمحتوى.
    يستخدم SecurityAudit للفحص المتقدم إن كان متاحاً.
    """
    if not text:
        return {"safe": True, "violations": [], "severity": "safe"}

    # 1. محاولة استخدام المدقق المتقدم
    try:
        from app.middleware.security_audit import security_audit
        result = security_audit.scan_payload(text)
        if result:
            return {
                "safe": False,
                "violations": ["security_audit_blocked"],
                "severity": "critical",
                "helpline": HELPLINES.get("ar", "")
            }
    except ImportError:
        pass

    # 2. فحص الكلمات المفتاحية (احتياطي)
    violations = [kw for kw in BLOCKED_KEYWORDS if kw.lower() in text.lower()]
    is_critical = any(v in ["انتحار","suicide","kill myself","bomb"] for v in violations)
    
    severity = "critical" if is_critical else "warning" if violations else "safe"
    
    return {
        "safe": len(violations) == 0,
        "violations": violations,
        "severity": severity,
        "helpline": HELPLINES.get("ar", "") if severity == "critical" else None
    }

def sanitize_input(text: str) -> str:
    """تنقية النص من المحتوى الضار"""
    # استخدام المدقق المتقدم إن كان متاحاً
    try:
        from app.middleware.security_audit import security_audit
        return security_audit.sanitize_input(text)
    except ImportError:
        pass
    
    # تنقية أساسية (احتياطي)
    text = re.sub(r'<[^>]*>', '', text)
    text = re.sub(r'[\'";\\]', '', text)
    return re.sub(r'\s+', ' ', text).strip()

async def log_safety_incident(user_id: str, text: str, severity: str) -> None:
    """تسجيل حادث أمان في TCMA"""
    try:
        from app.memory.emotional.emotional_memory import store_emotional_memory
        await store_emotional_memory(
            user_id=user_id,
            expressed_text=text[:100],
            detected_emotion={"primary": "fear", "intensity": 0.9, "valence": -0.8},
            trigger="safety_incident",
            cultural_context=f"severity: {severity}"
        )
        logger.warning(f"🚨 Safety incident logged: user={user_id}, severity={severity}")
    except Exception as e:
        logger.error(f"فشل تسجيل حادث الأمان: {e}")

logger.info("✅ Safety Service v3.0 initialized (Integrated with SecurityAudit + TCMA)")
