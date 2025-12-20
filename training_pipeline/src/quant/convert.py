import onnx
import os
import shutil
from pathlib import Path

# root directory of the project
BASE_DIR = Path.cwd()

# Define paths
INPUT_MODEL_PATH = os.path.join(BASE_DIR, "models/onnx_int8/model_int8.onnx")
SOURCE_DIR = os.path.join(BASE_DIR, "models/onnx_int8") 
OUTPUT_DIR = os.path.join(BASE_DIR, "models/production")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

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
    else:
        raw_src = os.path.join(BASE_DIR, "models/raw_model", file_name)
        if os.path.exists(raw_src):
            shutil.copy2(raw_src, dst)
        else:
            print(f"not found!")

print(f":{OUTPUT_DIR}")
