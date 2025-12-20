import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os
import onnxruntime
from onnxruntime.quantization import quantize_dynamic, QuantType
import warnings
import shutil
from pathlib import Path

BASE_DIR = Path.cwd()

INPUT_PATH = os.path.join(BASE_DIR, "models/raw_model")     
TEMP_PATH = os.path.join(BASE_DIR, "models/onnx_temp")       
OUTPUT_PATH = os.path.join(BASE_DIR, "models/onnx_int8")

os.makedirs(TEMP_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)

try:
    model = AutoModelForSequenceClassification.from_pretrained(INPUT_PATH).cpu()
    tokenizer = AutoTokenizer.from_pretrained(INPUT_PATH)
    model.eval()
except Exception as e:
    print(f"{e}")
    exit()

dummy_text = "Chuyển đổi model sang onnx"
inputs = tokenizer(dummy_text, return_tensors="pt")

onnx_float_file = os.path.join(TEMP_PATH, "model.onnx")
torch.onnx.export(
    model,
    (inputs['input_ids'], inputs['attention_mask'], inputs.get('token_type_ids', torch.zeros_like(inputs['input_ids']))),
    onnx_float_file,
    input_names=['input_ids', 'attention_mask', 'token_type_ids'],
    output_names=['logits'],
    dynamic_axes={
        'input_ids': {0: 'batch_size', 1: 'sequence_length'},
        'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
        'token_type_ids': {0: 'batch_size', 1: 'sequence_length'},
        'logits': {0: 'batch_size'}
    },
    opset_version=14 
)
print("complete")

final_model_file = os.path.join(OUTPUT_PATH, "model_int8.onnx")

try:
    quantize_dynamic(
        model_input=onnx_float_file,
        model_output=final_model_file,
        weight_type=QuantType.QUInt8,
        optimize_model=False
    )
except Exception as e:
    print(f"{e}")
    exit()
tokenizer.save_pretrained(OUTPUT_PATH)

print("complete!")

