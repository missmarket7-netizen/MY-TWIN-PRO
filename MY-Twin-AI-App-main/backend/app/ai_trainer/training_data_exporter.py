"""
Training Data Exporter - مصدر بيانات التدريب
=============================================
يستخرج المحادثات من Supabase، وينسقها لتدريب النموذج (JSONL).
يدعم اللغة العربية والإنجليزية. يحافظ على الخصوصية.
"""
import logging
import json
import os
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone

try:
    from app.infrastructure.database.supabase_client import get_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

logger = logging.getLogger("training_exporter")

class TrainingDataExporter:
    def __init__(self):
        self.export_path = os.path.join("training_data")

    async def export_conversations(
        self,
        user_ids: Optional[List[str]] = None,
        limit: int = 1000,
        format: str = "jsonl",  # jsonl or alpaca
        include_emotions: bool = True,
        include_identity: bool = False,
    ) -> str:
        """
        يصدر المحادثات من الأرشيف الخام إلى ملف JSONL جاهز للتدريب.
        """
        if not DB_AVAILABLE:
            raise RuntimeError("قاعدة البيانات غير متصلة")

        db = get_db()
        try:
            query = db.table("raw_conversation_archive").select("*").order("created_at", desc=True).limit(limit)
            if user_ids:
                query = query.in_("user_id", user_ids)
            result = query.execute()

            if not result.data:
                return "لا توجد بيانات للتصدير"

            # تنظيم البيانات إلى حوارات
            conversations = self._organize_conversations(result.data)

            # تنسيق الإخراج
            os.makedirs(self.export_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"mytwin_training_{timestamp}.{format}"
            filepath = os.path.join(self.export_path, filename)

            if format == "jsonl":
                lines = self._format_as_jsonl(conversations, include_emotions, include_identity)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
            elif format == "alpaca":
                data = self._format_as_alpaca(conversations, include_emotions, include_identity)
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"✅ تم تصدير {len(lines)} محادثة إلى {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"فشل التصدير: {e}")
            raise

    def _organize_conversations(self, raw_data: List[Dict]) -> List[Dict]:
        """ينظم الرسائل إلى محادثات (مستخدم ← توأم)"""
        conversations = []
        current_conv = []
        current_conv_id = None

        for msg in sorted(raw_data, key=lambda x: x.get("created_at", "")):
            conv_id = msg.get("conversation_id")
            if conv_id != current_conv_id and current_conv:
                conversations.append({"messages": current_conv})
                current_conv = []
            current_conv_id = conv_id
            current_conv.append({
                "role": msg["role"],
                "content": msg["content"],
                "emotion": msg.get("emotion_primary"),
                "intent": msg.get("detected_intent"),
            })
        if current_conv:
            conversations.append({"messages": current_conv})
        return conversations

    def _format_as_jsonl(self, conversations: List[Dict], include_emotions: bool, include_identity: bool) -> List[str]:
        """صيغة JSONL: كل سطر هو محادثة"""
        lines = []
        for conv in conversations:
            messages = conv["messages"]
            if len(messages) < 2:
                continue
            # تنسيق: {"messages": [{"role": "user", "content": "..."}, ...]}
            formatted = {"messages": []}
            for msg in messages:
                m = {"role": msg["role"], "content": msg["content"]}
                if include_emotions and msg.get("emotion"):
                    m["emotion"] = msg["emotion"]
                formatted["messages"].append(m)
            lines.append(json.dumps(formatted, ensure_ascii=False))
        return lines

    def _format_as_alpaca(self, conversations: List[Dict], include_emotions: bool, include_identity: bool) -> List[Dict]:
        """صيغة Alpaca للتدريب الدقيق"""
        data = []
        for conv in conversations:
            messages = conv["messages"]
            for i in range(len(messages) - 1):
                if messages[i]["role"] == "user" and messages[i+1]["role"] == "twin":
                    entry = {
                        "instruction": "أنت توأم رقمي، صديق مقرب ومستشار حكيم. أجب بلطف.",
                        "input": messages[i]["content"],
                        "output": messages[i+1]["content"],
                    }
                    if include_emotions and messages[i].get("emotion"):
                        entry["emotion"] = messages[i]["emotion"]
                    data.append(entry)
        return data

logger.info("✅ Training Data Exporter initialized")
