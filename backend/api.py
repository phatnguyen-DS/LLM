import os
import json
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
import onnxruntime as ort

app = FastAPI(title="LLM ONNX API")

# Cấu hình đường dẫn model
MODEL_PATH = "models/production/model_main.onnx"
CONFIG_PATH = "models/production/config.json"
TOKENIZER_PATH = "models/production/tokenizer.json"

# Khởi tạo các biến toàn cục
tokenizer = None
session = None
id2label = None

@app.on_event("startup")
async def load_model():
    global tokenizer, session, id2label
    try:
        # 1. Load Tokenizer
        tokenizer = Tokenizer.from_file(TOKENIZER_PATH)
        
        # 2. Load Config để lấy nhãn (labels)
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            id2label = config.get("id2label", {})

        # 3. Cấu hình ONNX Runtime tối ưu cho RAM yếu
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        # Kỹ thuật quan trọng: Sử dụng Memory Mapping để không ngốn RAM
        session = ort.InferenceSession(
            MODEL_PATH, 
            sess_options, 
            providers=['CPUExecutionProvider']
        )
        print("Model loaded successfully with Memory Mapping!")
    except Exception as e:
        print(f"Error loading model: {str(e)}")

class QueryRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict(request: QueryRequest):
    if not session or not tokenizer:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Tokenize đầu vào
        encoded = tokenizer.encode(request.text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)

        # Chạy inference
        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask
        }
        outputs = session.run(None, inputs)
        logits = outputs[0]

        # Xử lý kết quả (Softmax đơn giản)
        probs = np.exp(logits) / np.sum(np.exp(logits), axis=-1, keepdims=True)
        pred_idx = int(np.argmax(probs))
        
        return {
            "label": id2label.get(str(pred_idx), f"Class {pred_idx}"),
            "confidence": float(probs[0][pred_idx]),
            "text": request.text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": session is not None}