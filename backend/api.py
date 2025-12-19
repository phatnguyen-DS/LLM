from pathlib import Path
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
import json

# -- CONFIG --
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "production"

class PredictRequest(BaseModel):
    text: str

app = FastAPI()

# -- GLOBALS --
TOKENIZER = None
SESSION = None
ID2LABEL = {}

def init_model():
    global TOKENIZER, SESSION, ID2LABEL
    try:
        # 1. Load Tokenizer rút gọn (tokenizer.json)
        TOKENIZER = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
        TOKENIZER.enable_truncation(max_length=128)
        TOKENIZER.enable_padding(length=128)

        # 2. Load Label Map
        config_path = MODEL_DIR / "config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                cfg = json.load(f)
                id2map = cfg.get("id2label") or cfg.get("id_to_label")
                if id2map:
                    ID2LABEL = {int(k): v for k, v in id2map.items()}

        # 3. Cấu hình ONNX Runtime cực hạn cho RAM 512MB
        so = ort.SessionOptions()
        # Chạy tuần tự để không tốn RAM cho xử lý song song
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL 
        # Giảm tối ưu hóa đồ thị xuống mức cơ bản để tránh dùng nhiều RAM lúc load
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        # Tắt bộ nhớ đệm khởi tạo
        so.add_session_config_entry("session.use_device_allocator_for_initializers", "0")

        SESSION = ort.InferenceSession(
            str(MODEL_DIR / "model_quantized.onnx"), 
            sess_options=so, 
            providers=["CPUExecutionProvider"]
        )
    except Exception:
        pass

init_model()

@app.post("/predict")
def predict(req: PredictRequest):
    if SESSION is None:
        raise HTTPException(status_code=503, detail="Model Loading Error")

    try:
        # Tokenize
        encoding = TOKENIZER.encode(req.text)
        
        # Chuẩn bị input
        ort_inputs = {
            "input_ids": np.array([encoding.ids], dtype=np.int64),
            "attention_mask": np.array([encoding.attention_mask], dtype=np.int64)
        }
        
        # Kiểm tra token_type_ids
        if "token_type_ids" in [i.name for i in SESSION.get_inputs()]:
            ort_inputs["token_type_ids"] = np.array([encoding.type_ids], dtype=np.int64)

        # Inference
        logits = SESSION.run(None, ort_inputs)[0]
        
        # Softmax tối giản (chỉ lấy top 1)
        probs = np.exp(logits - np.max(logits))
        probs /= probs.sum()
        
        idx = int(np.argmax(probs))
        
        return {
            "label": ID2LABEL.get(idx, str(idx)),
            "score": round(float(probs[0][idx]), 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))