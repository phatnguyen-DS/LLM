import os
import json
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# --- CẤU HÌNH RENDER FREE TIER  ---
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["ORT_TENSORRT_FP16_ENABLE"] = "0"

# --- BIẾN TOÀN CỤC ---
model = None
tokenizer = None
labels = {}
MAX_LEN = 32  # Giữ mức thấp để tiết kiệm RAM

# --- QUẢN LÝ VÒNG ĐỜI (Load 1 lần duy nhất) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer, labels
    
    # 1. Load Labels
    try:
        with open("models/production/config.json", "r", encoding='utf-8') as f:
            cfg = json.load(f)
            labels = {str(k): v for k, v in cfg.get("id2label", {}).items()}
    except:
        # Fallback nếu lỗi file
        labels = {"0": "CARD", "1": "LOGIN", "2": "TRANS", "3": "LOAN", "4": "FRAUD", "5": "OTHER"}

    # 2. Load Tokenizer & Model
    try:
        tokenizer = Tokenizer.from_file("models/production/tokenizer.json")
        tokenizer.enable_truncation(max_length=MAX_LEN)
        tokenizer.enable_padding(length=MAX_LEN)

        # Config ONNX tiết kiệm RAM tối đa
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 1
        opts.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        opts.enable_cpu_mem_arena = False
        
        model = ort.InferenceSession("models/production/model_main.onnx", opts, providers=['CPUExecutionProvider'])
        print(">>> AI Model Loaded Successfully")
    except Exception as e:
        print(f">>> Error loading model: {e}")

    yield
    # Dọn dẹp khi tắt app
    model = None
    tokenizer = None

# --- KHỞI TẠO APP ---
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    text: str

# --- XỬ LÝ ---
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1, keepdims=True)

@app.get("/health")
def health():
    return {"status": "ok"} if model else {"status": "error"}

@app.post("/predict")
def predict(item: Item): 
    if not model:
        raise HTTPException(503, "Model not ready")

    text = item.text.strip() or "empty"
    
    # 1. Tokenize nhanh
    enc = tokenizer.encode(text)
    inputs = {
        "input_ids": np.array([enc.ids], dtype=np.int64),
        "attention_mask": np.array([enc.attention_mask], dtype=np.int64),
        "token_type_ids": np.array([enc.type_ids], dtype=np.int64)
    }

    # 2. Inference & Post-process
    try:
        logits = model.run(None, inputs)[0][0]
        probs = softmax(logits)
        pred_idx = np.argmax(probs)
        
        return {
            "label": labels.get(str(pred_idx), "Unknown"),
            "score": round(float(probs[pred_idx]), 4)
        }
    except Exception:
        raise HTTPException(500, "Inference Failed")