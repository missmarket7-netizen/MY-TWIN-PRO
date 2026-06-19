"""Safety Service – content filtering, sanitization."""
import re, logging
from typing import Dict

logger = logging.getLogger("safety_service")

BLOCKED_KEYWORDS = ["انتحار","أقتل","أريد الموت","suicide","kill","bomb","قنبلة","مخدرات","drugs","porn"]
HELPLINE = "🆘 خط المساعدة النفسية (مصر): 08008880700"

def check_safety(text: str) -> Dict:
    if not text: return {"safe":True,"violations":[],"severity":"safe"}
    violations = [kw for kw in BLOCKED_KEYWORDS if kw.lower() in text.lower()]
    severity = "critical" if any(v in ["انتحار","suicide","kill","bomb"] for v in violations) else "warning" if violations else "safe"
    return {"safe":len(violations)==0,"violations":violations,"severity":severity,"helpline":HELPLINE if severity=="critical" else None}

def sanitize_input(text: str) -> str:
    text = re.sub(r'<[^>]*>','',text)
    text = re.sub(r'[\'";\\]','',text)
    return re.sub(r'\s+',' ',text).strip()
