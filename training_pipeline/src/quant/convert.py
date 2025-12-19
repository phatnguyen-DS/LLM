import onnx
import os
import shutil
from pathlib import Path

# root directory of the project
BASE_DIR = Path.cwd()

# Define paths
INPUT_MODEL_PATH = os.path.join(BASE_DIR, "models/onnx_int8/model_int8.onnx")
# Assuming config and tokenizer are in onnx_int8 (copied there by onnx_int8.py) 
# OR in raw_model. Let's take from onnx_int8 as it was the previous step.
SOURCE_DIR = os.path.join(BASE_DIR, "models/onnx_int8") 
OUTPUT_DIR = os.path.join(BASE_DIR, "models/production")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"🔄 Converting model to external data format...")
model = onnx.load(INPUT_MODEL_PATH)
onnx.save_model(
    model,
    os.path.join(OUTPUT_DIR, "model_main.onnx"),
    save_as_external_data=True,
    all_tensors_to_one_file=False,
    location="weights.bin",
    size_threshold=1024
)

# Copy configuration files
files_to_copy = ["tokenizer.json", "config.json"]
for file_name in files_to_copy:
    src = os.path.join(SOURCE_DIR, file_name)
    dst = os.path.join(OUTPUT_DIR, file_name)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"✅ Copied {file_name}")
    else:
        # Fallback to look in raw_model if not in onnx_int8
        raw_src = os.path.join(BASE_DIR, "models/raw_model", file_name)
        if os.path.exists(raw_src):
            shutil.copy2(raw_src, dst)
            print(f"✅ Copied {file_name} from raw_model")
        else:
            print(f"⚠️ Warning: {file_name} not found!")

print(f"🎉 Complete! Production assets ready in: {OUTPUT_DIR}")