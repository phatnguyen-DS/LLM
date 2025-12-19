import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import os
import onnxruntime
from onnxruntime.quantization import quantize_matmul_4bits
import warnings

# Tắt cảnh báo
warnings.filterwarnings("ignore")

print(f"💻 Đang chạy trên Windows - Bypass Optimum...")

# --- 1. CẤU HÌNH ĐƯỜNG DẪN CHÍNH XÁC ---
# Dựa trên đường dẫn trong ảnh bạn gửi
BASE_DIR = r"C:\Users\TAN PHAT\OneDrive\Desktop\LLM\models"

INPUT_PATH = os.path.join(BASE_DIR, "raw_pytorch")     # Folder chứa model gốc
TEMP_PATH = os.path.join(BASE_DIR, "onnx_temp")        # Folder lưu tạm
OUTPUT_PATH = os.path.join(BASE_DIR, "production_int4") # Folder thành phẩm

# Tạo thư mục
os.makedirs(TEMP_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)

# --- 2. EXPORT DÙNG PYTORCH THUẦN (KHÔNG DÙNG OPTIMUM) ---
print(f"⏳ Đang load model từ: {INPUT_PATH}")
try:
    # Load model lên CPU
    model = AutoModelForSequenceClassification.from_pretrained(INPUT_PATH).cpu()
    tokenizer = AutoTokenizer.from_pretrained(INPUT_PATH)
    model.eval()
except Exception as e:
    print(f"\n❌ LỖI LOAD MODEL: {e}")
    print(f"👉 Hãy kiểm tra lại folder '{INPUT_PATH}' có file model.safetensors hoặc pytorch_model.bin không.")
    exit()

print("🔄 Đang export sang ONNX (Float32)...")
# Tạo input giả
dummy_text = "Chuyển đổi model sang onnx"
inputs = tokenizer(dummy_text, return_tensors="pt")

onnx_float_file = os.path.join(TEMP_PATH, "model.onnx")

# Dùng torch.onnx.export (Tính năng có sẵn của PyTorch, cực kỳ ổn định)
torch.onnx.export(
    model,
    (inputs['input_ids'], inputs['attention_mask']),
    onnx_float_file,
    input_names=['input_ids', 'attention_mask'],
    output_names=['logits'],
    dynamic_axes={
        'input_ids': {0: 'batch_size', 1: 'sequence_length'},
        'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
        'logits': {0: 'batch_size'}
    },
    opset_version=14 
)
print("✅ Export ONNX gốc thành công!")

# --- 3. NÉN INT4 (DÙNG ONNXRUNTIME) ---
print("🔨 Đang nén model xuống Int4...")
final_model_file = os.path.join(OUTPUT_PATH, "model_int4.onnx")

try:
    quantize_matmul_4bits(
        onnx_float_file,
        final_model_file,
        block_size=32,
        is_symmetric=True
    )
except Exception as e:
    print(f"❌ Lỗi khi nén: {e}")
    exit()

# Copy tokenizer sang đích
tokenizer.save_pretrained(OUTPUT_PATH)

print("-" * 50)
print("🎉 THÀNH CÔNG! BẠN ĐÃ CÓ MODEL INT4.")
print(f"📂 Thư mục deploy: {OUTPUT_PATH}")
print("-" * 50)