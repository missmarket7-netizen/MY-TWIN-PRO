"""
تحويل بيانات MyTwin من JSONL إلى صيغة LLaMA 3 للتدريب
"""
import json
import sys

def convert_messages_to_llama3(messages):
    text = "<|begin_of_text|>"
    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "user":
            text += f"<|start_header_id|>user<|end_header_id|>\n\n{content}<|eot_id|>"
        elif role in ("twin", "assistant"):
            text += f"<|start_header_id|>assistant<|end_header_id|>\n\n{content}<|eot_id|>"
    return text

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "training_data/mytwin_training_latest.jsonl"
    output_file = input_file.replace(".jsonl", "_llama3.jsonl")
    with open(input_file, "r", encoding="utf-8") as fin, open(output_file, "w", encoding="utf-8") as fout:
        for line in fin:
            data = json.loads(line)
            messages = data.get("messages", [])
            if len(messages) >= 2:
                llama3_text = convert_messages_to_llama3(messages)
                fout.write(json.dumps({"text": llama3_text}, ensure_ascii=False) + "\n")
    print(f"✅ تم التحويل: {output_file}")
