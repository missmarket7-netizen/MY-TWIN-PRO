"""
Internal Model Provider – النموذج الداخلي لـ MyTwin
=====================================================
يحمّل النموذج المُدرَّب (LLaMA 3 LoRA) ويوفّر واجهة توليد موحّدة.
يتكامل مع provider_router ليكون بديلاً عن Gemini/Groq.
"""
import logging
import os
from typing import Optional, Dict, Any

logger = logging.getLogger("internal_model")

try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
    from peft import PeftModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class InternalModelProvider:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.base_model_name = "NousResearch/Meta-Llama-3-8B"
        self.lora_path = os.getenv("MYTWIN_MODEL_PATH", "./mytwin-llama3-lora")
        self._loaded = False

    async def load_model(self) -> bool:
        """تحميل النموذج المُدرَّب في الذاكرة"""
        if self._loaded:
            return True
        
        if not TRANSFORMERS_AVAILABLE:
            logger.error("❌ مكتبات transformers غير متوفرة")
            return False

        try:
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.base_model_name, trust_remote_code=True
            )
            self.tokenizer.pad_token = self.tokenizer.eos_token

            base_model = AutoModelForCausalLM.from_pretrained(
                self.base_model_name,
                quantization_config=bnb_config,
                device_map="auto",
                trust_remote_code=True,
            )

            # تحميل LoRA المُدرَّب
            if os.path.exists(self.lora_path):
                self.model = PeftModel.from_pretrained(base_model, self.lora_path)
                logger.info("✅ تم تحميل نموذج MyTwin الداخلي (LoRA)")
            else:
                self.model = base_model
                logger.warning("⚠️ لم يتم العثور على LoRA، استخدام النموذج الأساسي فقط")

            self._loaded = True
            return True

        except Exception as e:
            logger.error(f"❌ فشل تحميل النموذج الداخلي: {e}")
            return False

    async def generate(self, prompt: str, max_tokens: int = 256, temperature: float = 0.7) -> Optional[str]:
        """توليد رد من النموذج الداخلي"""
        if not self._loaded:
            loaded = await self.load_model()
            if not loaded:
                return None

        try:
            # تنسيق الموجه بصيغة LLaMA 3
            formatted_prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nأنت توأم رقمي، صديق مقرب ومستشار حكيم. أجب بلطف وبالعربية.<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"

            inputs = self.tokenizer(formatted_prompt, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.eos_token_id,
                )

            response = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
            return response.strip()

        except Exception as e:
            logger.error(f"❌ فشل التوليد من النموذج الداخلي: {e}")
            return None

    async def unload_model(self):
        """تفريغ النموذج من الذاكرة"""
        if self.model:
            del self.model
            self.model = None
        if self.tokenizer:
            del self.tokenizer
            self.tokenizer = None
        self._loaded = False
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        logger.info("🗑️ تم تفريغ النموذج الداخلي من الذاكرة")


# نسخة عالمية
internal_model = InternalModelProvider()
logger.info("✅ Internal Model Provider جاهز")
