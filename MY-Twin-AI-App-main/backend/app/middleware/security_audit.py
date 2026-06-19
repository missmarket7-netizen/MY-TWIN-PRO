"""Security Auditor – Input Validation & Error Sanitization."""
import re, logging

logger = logging.getLogger("security_audit")

class SecurityAudit:
    @staticmethod
    def scan_payload(text: str) -> str | None:
        if not text: return None
        if re.search(r"(?i)(\bUNION\b.*\bSELECT\b|\bDROP\b|\bINSERT\b|\bDELETE\b|\bUPDATE\b)", text):
            logger.warning("SQL Injection attempt blocked")
            return "Malicious input detected"
        if "../" in text or "..\\" in text:
            logger.warning("Path traversal attempt blocked")
            return "Malicious input detected"
        if re.search(r"<script[^>]*>.*?</script>|javascript:|onerror\s*=|onload\s*=", text, re.IGNORECASE):
            logger.warning("XSS attempt blocked")
            return "Malicious input detected"
        return None

    @staticmethod
    def safe_error(e: Exception) -> str:
        logger.error(f"Internal Error: {e}")
        return "حدث خطأ داخلي. تم تسجيل المشكلة وسيتم حلها قريباً."

security_audit = SecurityAudit()
