"""
Security Auditor v3.0 – أعلى درجات الأمان والحماية
=====================================================
- SQL Injection (متقدم)
- XSS (شامل)
- Path Traversal
- Command Injection
- DoS / Rate Limiting
- JWT Validation
- Input Sanitization
- Sensitive Data Masking
- Audit Logging (تكامل مع Observability)
"""
import re, os, time, logging, hashlib
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("security_audit")

# ============================================================
# إعدادات الأمان
# ============================================================
MAX_INPUT_LENGTH = 5000
MAX_REQUESTS_PER_MINUTE = 30
RATE_LIMIT_WINDOW = 60  # ثانية
_request_counts: Dict[str, list] = {}  # IP -> [timestamps]

# ============================================================
# المراجع (Regex Patterns)
# ============================================================
SQL_INJECTION_PATTERNS = [
    r"(?i)(\bUNION\b.*\bSELECT\b)",
    r"(?i)(\bDROP\s+TABLE\b)",
    r"(?i)(\bINSERT\s+INTO\b)",
    r"(?i)(\bDELETE\s+FROM\b)",
    r"(?i)(\bUPDATE\b.*\bSET\b)",
    r"(?i)(\bALTER\s+TABLE\b)",
    r"(?i)(\bCREATE\s+TABLE\b)",
    r"(?i)(\bEXEC\b|\bEXECUTE\b)",
    r"(?i)(\bOR\s+1\s*=\s*1\b)",
    r"(?i)(\bAND\s+1\s*=\s*1\b)",
    r"(?i)(--\s*\n|#\s*\n|\/\*.*\*\/)",
]

XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript\s*:",
    r"onerror\s*=",
    r"onload\s*=",
    r"onclick\s*=",
    r"onmouseover\s*=",
    r"<iframe[^>]*>",
    r"<embed[^>]*>",
    r"<object[^>]*>",
    r"<link[^>]*>",
    r"expression\s*\(|eval\s*\(|alert\s*\(",
    r"document\.\s*cookie",
]

COMMAND_INJECTION_PATTERNS = [
    r"(?i)(\|.*\b(sh|bash|cmd|powershell|python|perl)\b)",
    r"(?i)(\brm\s+-rf\b|\bdel\s+/[fq]\b)",
    r"(?i)(\bwget\b.*\|.*\bsh\b)",
    r"(?i)(\bcurl\b.*\|.*\bsh\b)",
]

PATH_TRAVERSAL_PATTERNS = [
    r"\.\.\/",
    r"\.\.\\",
    r"\/etc\/passwd",
    r"\/etc\/shadow",
    r"C:\\Windows\\System32",
]

class SecurityAudit:
    """مدقق أمان متقدم"""

    # ============================================================
    # فحص المحتوى
    # ============================================================
    @staticmethod
    def scan_payload(text: str) -> Optional[str]:
        """فحص شامل للمحتوى"""
        if not text:
            return None

        # 1. فحص الطول
        if len(text) > MAX_INPUT_LENGTH:
            logger.warning("Input exceeds max length")
            return "Input too long"

        # 2. فحص SQL Injection
        for pattern in SQL_INJECTION_PATTERNS:
            if re.search(pattern, text):
                SecurityAudit._log_attack("sql_injection", text[:100])
                return "Malicious input detected"

        # 3. فحص XSS
        for pattern in XSS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                SecurityAudit._log_attack("xss", text[:100])
                return "Malicious input detected"

        # 4. فحص Command Injection
        for pattern in COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, text):
                SecurityAudit._log_attack("command_injection", text[:100])
                return "Malicious input detected"

        # 5. فحص Path Traversal
        for pattern in PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, text):
                SecurityAudit._log_attack("path_traversal", text[:100])
                return "Malicious input detected"

        return None

    @staticmethod
    def sanitize_input(text: str) -> str:
        """تنظيف النص من المحتوى الضار"""
        # إزالة HTML tags
        text = re.sub(r"<[^>]*>", "", text)
        # إزالة javascript/code injections
        text = re.sub(r"javascript\s*:", "", text, flags=re.IGNORECASE)
        text = re.sub(r"on\w+\s*=", "", text, flags=re.IGNORECASE)
        # تقليم الأطراف
        text = text.strip()
        # تحديد الطول
        if len(text) > MAX_INPUT_LENGTH:
            text = text[:MAX_INPUT_LENGTH]
        return text

    @staticmethod
    def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """إخفاء البيانات الحساسة في السجلات"""
        sensitive_keys = {"password", "token", "secret", "api_key", "authorization", "jwt"}
        masked = {}
        for k, v in data.items():
            if any(s in k.lower() for s in sensitive_keys):
                masked[k] = "***MASKED***"
            else:
                masked[k] = v
        return masked

    # ============================================================
    # Rate Limiting
    # ============================================================
    @staticmethod
    def check_rate_limit(client_ip: str, max_requests: int = None) -> bool:
        """فحص حدود الطلبات"""
        if max_requests is None:
            max_requests = MAX_REQUESTS_PER_MINUTE

        now = time.time()
        if client_ip not in _request_counts:
            _request_counts[client_ip] = []

        # تنظيف السجلات القديمة
        _request_counts[client_ip] = [
            t for t in _request_counts[client_ip]
            if now - t < RATE_LIMIT_WINDOW
        ]

        if len(_request_counts[client_ip]) >= max_requests:
            logger.warning(f"Rate limit exceeded for {client_ip}")
            return False

        _request_counts[client_ip].append(now)
        return True

    # ============================================================
    # JWT / Token Validation
    # ============================================================
    @staticmethod
    def validate_token(token: str) -> Tuple[bool, Optional[Dict]]:
        """التحقق من صحة JWT Token"""
        if not token:
            return False, None
        try:
            import jwt
            from app.core.config import config
            payload = jwt.decode(
                token,
                config.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_exp": True}
            )
            return True, payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return False, None
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return False, None

    # ============================================================
    # معالجة الأخطاء
    # ============================================================
    @staticmethod
    def safe_error(e: Exception, context: str = "") -> str:
        """تسجيل خطأ آمن دون كشف التفاصيل"""
        error_id = hashlib.md5(f"{time.time()}{str(e)}".encode()).hexdigest()[:8]
        logger.error(f"Internal Error [{error_id}]: {context} - {e}")

        # تكامل مع Observability
        try:
            from app.observability.logging_service import log_error
            import asyncio
            asyncio.create_task(log_error(e, context, "error"))
        except: pass

        return f"حدث خطأ داخلي. رقم المرجع: {error_id}"

    # ============================================================
    # تسجيل محاولات الاختراق
    # ============================================================
    @staticmethod
    def _log_attack(attack_type: str, content: str):
        """تسجيل محاولة اختراق"""
        logger.warning(f"🚨 {attack_type.upper()} attempt blocked")

        try:
            from app.infrastructure.database.supabase_client import get_db
            db = get_db()
            db.table("security_logs").insert({
                "attack_type": attack_type,
                "content_sample": content[:200],
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
        except: pass

# نسخة عالمية
security_audit = SecurityAudit()
logger.info("✅ Security Auditor v3.0 initialized")
