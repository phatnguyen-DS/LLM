import os
import json
import gc
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
import onnxruntime as ort
from contextlib import asynccontextmanager

# --- MEMORY OPTIMIZATION ---
# Giới hạn số luồng để giảm chiếm dụng CPU/RAM
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"
os.environ["ORT_TENSORRT_FP16_ENABLE"] = "0"

# --- GLOBAL VARIABLES ---
model_session = None
tokenizer = None
id2label = {}
MAX_LENGTH = 64

# --- LIFECYCLE MANAGEMENT ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global model_session, tokenizer, id2label
    
    # Load Config (Labels)
    config_file = "models/production/config.json"
    try:
        if os.path.exists(config_file):
            with open(config_file, "r", encoding='utf-8') as f:
                config = json.load(f)
                id2label = config.get("id2label", {})
                id2label = {str(k): v for k, v in id2label.items()}
        else:
            print(f"⚠️ Không tìm thấy config tại: {config_file}. Sử dụng default labels.")
            id2label = { 
                "0": "CARD_ISSUE", "1": "APP_LOGIN", "2": "TRANSACTION",
                "3": "LOAN_SAVING", "4": "FRAUD_REPORT", "5": "OTHERS"
            }
    except Exception as e:
        print(f"Error loading config: {e}")
        id2label = { 
            "0": "CARD_ISSUE", "1": "APP_LOGIN", "2": "TRANSACTION",
            "3": "LOAN_SAVING", "4": "FRAUD_REPORT", "5": "OTHERS"
        }

    # Load Tokenizer
    tokenizer_file = "models/production/tokenizer.json"
    try:
        tokenizer = Tokenizer.from_file(tokenizer_file)
        tokenizer.enable_truncation(max_length=MAX_LENGTH)
        tokenizer.enable_padding(length=MAX_LENGTH)
    except Exception as e:
        print(f"Error loading tokenizer: {e}")
        raise e

    # Load ONNX Model with optimized settings
    model_file = "models/production/model_main.onnx"
    try:
        sess_options = ort.SessionOptions()
        # Optimize for low memory
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        # Enable memory optimization
        sess_options.enable_cpu_mem_arena = False
        sess_options.enable_mem_pattern = False
        
        model_session = ort.InferenceSession(
            model_file, 
            sess_options, 
            providers=['CPUExecutionProvider']
        )
        
        # Force garbage collection after model load
        gc.collect()
        
    except Exception as e:
        print(f"Error loading model: {e}")
        raise e
    
    yield
    
    # Shutdown
    del model_session
    del tokenizer
    gc.collect()

# --- APP INITIALIZATION ---
app = FastAPI(
    title="Text Classification API",
    description="Optimized API for low-memory environments",
    version="1.0.0",
    lifespan=lifespan
)

# --- FUNCTIONS ---
def stable_softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1, keepdims=True)

def process_text(text: str):
    """Process text with memory-efficient tokenization"""
    if not text.strip():
        text = "empty"
    
    # Tokenize with minimal memory usage
    encoding = tokenizer.encode(text)
    
    # Convert to numpy arrays directly
    input_ids = np.array([encoding.ids], dtype=np.int64)
    attention_mask = np.array([encoding.attention_mask], dtype=np.int64)
    token_type_ids = np.array([encoding.type_ids], dtype=np.int64)
    
    return input_ids, attention_mask, token_type_ids

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    return {"Health_check": "OK", "Model": "Ready"}

@app.get("/health")
async def health_check():
    status = "ok" if model_session and tokenizer else "loading"
    return {"status": status, "memory": "optimized"}

class PredictRequest(BaseModel):
    text: str

@app.post("/predict")
async def predict_endpoint(req: PredictRequest):
    if not model_session or not tokenizer:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    try:
        # Process text
        input_ids, attention_mask, token_type_ids = process_text(req.text)
        
        # Prepare input
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
        
        # Clean up to free memory
        del input_ids, attention_mask, token_type_ids, outputs, logits, probs
        gc.collect()
        
        return {
            "label": label,
            "score": round(confidence, 4)
        }
        
    except MemoryError:
        gc.collect()
        raise HTTPException(status_code=507, detail="Insufficient storage, please try again")
    except Exception as e:
        print(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")
