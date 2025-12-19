from pathlib import Path
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
import json

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "production"

class PredictRequest(BaseModel):
    text: str

app = FastAPI()

# Biến toàn cục
TOKENIZER = None
SESSION = None
ID2LABEL = {}

def init_model():
    global TOKENIZER, SESSION, ID2LABEL
    try:
        # 1. Load Tokenizer (Sử dụng trực tiếp file json để cực nhẹ)
        TOKENIZER = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
        TOKENIZER.enable_truncation(max_length=128)
        TOKENIZER.enable_padding(length=128)

        # 2. Load Label Map tối giản
        config_path = MODEL_DIR / "config.json"
        if config_path.exists():
            with open(config_path, "r") as f:
                cfg = json.load(f)
                labels = cfg.get("id2label") or cfg.get("id_to_label")
                if labels:
                    ID2LABEL = {int(k): v for k, v in labels.items()}

        # 3. ONNX Runtime - Cấu hình tiết kiệm RAM mức tối đa
        so = ort.SessionOptions()
        so.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        
        # Ép giải phóng bộ nhớ ngay lập tức
        so.add_session_config_entry("session.use_device_allocator_for_initializers", "0")
        # Tắt Memory Pattern để giảm RAM tĩnh
        so.enable_mem_pattern = False 

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
        encoding = TOKENIZER.encode(req.text)
        ort_inputs = {
            "input_ids": np.array([encoding.ids], dtype=np.int64),
            "attention_mask": np.array([encoding.attention_mask], dtype=np.int64)
        }
        
        # Tự động khớp với input name của model
        input_names = [i.name for i in SESSION.get_inputs()]
        if "token_type_ids" in input_names:
            ort_inputs["token_type_ids"] = np.array([encoding.type_ids], dtype=np.int64)

        logits = SESSION.run(None, ort_inputs)[0]
        
        # Softmax tối giản top 1
        e_x = np.exp(logits - np.max(logits))
        probs = e_x / e_x.sum()
        idx = int(np.argmax(probs))
        
        return {
            "label": ID2LABEL.get(idx, str(idx)),
            "score": round(float(probs[0][idx]), 4)
        }
    except Exception:
        raise HTTPException(status_code=500, detail="Prediction failed")