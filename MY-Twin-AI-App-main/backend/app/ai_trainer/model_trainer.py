"""
Model Trainer v2.0 - مدير تدريب النموذج الخاص (محدث)
======================================================
يقوم تلقائياً بتحويل البيانات إلى صيغة LLaMA 3 قبل بدء التدريب.
"""
import logging
import os
import subprocess
import json
from typing import Dict, Any, Optional

logger = logging.getLogger("model_trainer")

class ModelTrainer:
    def __init__(self):
        self.default_base_model = "NousResearch/Meta-Llama-3-8B"
        self.output_dir = "mytwin_model_output"

    async def prepare_and_train(
        self,
        training_file: str,
        base_model: Optional[str] = None,
        num_epochs: int = 3,
        learning_rate: float = 2e-4,
        use_lora: bool = True,
    ) -> Dict[str, Any]:
        """
        1. يحول البيانات إلى صيغة LLaMA 3
        2. يبدأ التدريب
        """
        if not os.path.exists(training_file):
            return {"error": f"ملف التدريب غير موجود: {training_file}"}

        # 1. التحويل التلقائي إلى صيغة LLaMA 3
        converted_file = training_file.replace(".jsonl", "_llama3.jsonl")
        try:
            # استدعاء دالة التحويل مباشرة
            from app.ai_trainer.convert_to_llama3 import convert_messages_to_llama3
            with open(training_file, "r", encoding="utf-8") as fin, open(converted_file, "w", encoding="utf-8") as fout:
                for line in fin:
                    data = json.loads(line)
                    messages = data.get("messages", [])
                    if len(messages) >= 2:
                        llama3_text = convert_messages_to_llama3(messages)
                        fout.write(json.dumps({"text": llama3_text}, ensure_ascii=False) + "\n")
            logger.info(f"✅ تم تحويل البيانات تلقائياً: {converted_file}")
        except Exception as e:
            logger.error(f"فشل التحويل التلقائي: {e}")
            return {"error": f"فشل تحويل البيانات: {str(e)}"}

        # 2. إعداد التدريب
        base = base_model or self.default_base_model
        output = os.path.join(self.output_dir, f"mytwin_lora_{os.path.basename(training_file).split('.')[0]}")

        training_script = self._generate_training_script(
            converted_file, base, output, num_epochs, learning_rate, use_lora
        )

        script_path = "run_training.py"
        with open(script_path, "w") as f:
            f.write(training_script)

        logger.info(f"سكريبت التدريب جاهز: {script_path}")
        logger.info(f"النموذج الأساسي: {base}")
        logger.info(f"المخرجات: {output}")

        return {
            "status": "ready",
            "script_path": script_path,
            "command": f"python {script_path}",
            "base_model": base,
            "output_dir": output,
            "num_epochs": num_epochs,
            "learning_rate": learning_rate,
        }

    def _generate_training_script(self, data_file, base_model, output, epochs, lr, use_lora):
        lora_config = ""
        if use_lora:
            lora_config = """
    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()
"""
        script = f"""
import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType
import os

base_model = "{base_model}"
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(base_model, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

{lora_config}

data_files = {{"train": "{data_file}"}}
dataset = load_dataset("json", data_files=data_files, split="train")

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, max_length=512, padding="max_length")

tokenized_dataset = dataset.map(tokenize_function, batched=True, remove_columns=["text"])

data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

training_args = TrainingArguments(
    output_dir="{output}",
    num_train_epochs={epochs},
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate={lr},
    fp16=True,
    logging_steps=10,
    save_strategy="epoch",
    report_to="none",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=data_collator,
)

trainer.train()
model.save_pretrained("{output}")
tokenizer.save_pretrained("{output}")
print("✅ Training complete!")
"""
        return script

logger.info("✅ Model Trainer v2.0 initialized")
