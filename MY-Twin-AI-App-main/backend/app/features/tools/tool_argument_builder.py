"""Tool Argument Builder v2.0 – بناء معطيات الأدوات."""
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("tool_argument_builder")

class ArgumentBuilder:
    def build(self, tool_name: str, message: str, user_id: str, tier: str = "free") -> Dict[str, Any]:
        return {"user_id": user_id, "query": message, "tier": tier}

argument_builder = ArgumentBuilder()
