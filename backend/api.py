import os

# --- TỐI ƯU HÓA MÔI TRƯỜNG ---
# Giới hạn số luồng để giảm chiếm dụng CPU/RAM
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["ORT_TENSORRT_FP16_ENABLE"] = "0"

import json
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
import onnxruntime as ort

app = FastAPI(title="High-Performance ONNX API")

# --- paths ---
BASE_MODEL_PATH = "models/production"
MODEL_FILE = os.path.join(BASE_MODEL_PATH, "model_main.onnx")
TOKENIZER_FILE = os.path.join(BASE_MODEL_PATH, "tokenizer.json")
CONFIG_FILE = os.path.join(BASE_MODEL_PATH, "config.json")

# --- GLOBAL VARIABLES ---
model_session = None
tokenizer = None
id2label = {}
MAX_LENGTH = 64

# --- functions ---
def stable_softmax(x):
    """Tính softmax ổn định về số học (tránh overflow)."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1, keepdims=True)

@app.on_event("startup")
async def startup_event():
    global model_session, tokenizer, id2label
    # Load Config (Labels)
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding='utf-8') as f:
                config = json.load(f)
                id2label = config.get("id2label", {})

                id2label = {str(k): v for k, v in id2label.items()}
        else:
            print(f"⚠️ Không tìm thấy config tại: {CONFIG_FILE}. Sử dụng default labels.")
            id2label = { "0": "Negative", "1": "Positive" } # Fallback
    except Exception as e:
        print(e)

    # Load Tokenizer (Rust-based Fast Tokenizer)
    try:
        tokenizer = Tokenizer.from_file(TOKENIZER_FILE)
        tokenizer.enable_truncation(max_length=MAX_LENGTH)
        tokenizer.enable_padding(length=MAX_LENGTH)
    except Exception as e:
        print(e)
        raise e

    # Load ONNX Model 
    try:
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        model_session = ort.InferenceSession(
            MODEL_FILE, 
            sess_options, 
            providers=['CPUExecutionProvider']
        )
    except Exception as e:
        print(e)
        raise e

class PredictRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict_endpoint(req: PredictRequest):
    if not model_session or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    try:
        # Tokenize
        encoding = tokenizer.encode(req.text)
        
        # Chuẩn bị Input Feed
        input_ids = np.array([encoding.ids], dtype=np.int64)
        attention_mask = np.array([encoding.attention_mask], dtype=np.int64)
        token_type_ids = np.array([encoding.type_ids], dtype=np.int64)
        
        ort_inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "token_type_ids": token_type_ids
        }
        
        # Inference
        outputs = model_session.run(None, ort_inputs)
        logits = outputs[0][0]
        
        # Post-processing
        probs = stable_softmax(logits)
        pred_id = np.argmax(probs)
        confidence = float(probs[pred_id])
        label = id2label.get(str(pred_id), f"Unknown_{pred_id}")
        
        return {
            "label": label,
            "score": round(confidence, 4),
            "latency": "fast" 
        }
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.get("/health")
async def health_check():
    status = "ok" if model_session else "loading"
    return {"status": status}
