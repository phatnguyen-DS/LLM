from pathlib import Path
from typing import Dict
import numpy as np
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from tokenizers import Tokenizer
import traceback
import json

# -- CONFIG --
ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models" / "production"
ONNX_FILENAME = "model_quantized.onnx"

class PredictRequest(BaseModel):
    text: str

class Prediction(BaseModel):
    label: str
    score: float

app = FastAPI(title="Lightweight ONNX Classifier", version="2.0")

def softmax(x: np.ndarray) -> np.ndarray:
    x_max = np.max(x, axis=-1, keepdims=True)
    e_x = np.exp(x - x_max)
    return e_x / np.sum(e_x, axis=-1, keepdims=True)

def load_id2label(config_path: Path) -> Dict[int, str]:
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            id2label = cfg.get("id2label") or cfg.get("id_to_label")
            if id2label:
                return {int(k): v for k, v in id2label.items()}
    except Exception as e:
        print(f"Warning: Load config failed: {e}")
    return {0: "LABEL_0", 1: "LABEL_1"}

# -- GLOBALS --
TOKENIZER = None
SESSION = None
ID2LABEL = {}
INIT_ERROR = None

def init_model():
    global TOKENIZER, SESSION, ID2LABEL, INIT_ERROR
    try:
        tokenizer_path = MODEL_DIR / "tokenizer.json"
        if not tokenizer_path.exists():
            raise FileNotFoundError(f"Missing tokenizer.json at {tokenizer_path}")
        
        TOKENIZER = Tokenizer.from_file(str(tokenizer_path))
        
        TOKENIZER.enable_truncation(max_length=128)
        TOKENIZER.enable_padding(length=128)

        ID2LABEL = load_id2label(MODEL_DIR / "config.json")

        onnx_path = MODEL_DIR / ONNX_FILENAME
        so = ort.SessionOptions()
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        
        SESSION = ort.InferenceSession(
            str(onnx_path), 
            sess_options=so, 
            providers=["CPUExecutionProvider"]
        )
        print("Model initialized successfully!")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        INIT_ERROR = str(e)
        traceback.print_exc()

init_model()

@app.get("/health")
def health():
    return {"ready": SESSION is not None, "init_error": INIT_ERROR}

@app.post("/predict", response_model=Prediction)
def predict(req: PredictRequest):
    if SESSION is None:
        raise HTTPException(status_code=503, detail=f"Model not ready: {INIT_ERROR}")

    try:
        encoding = TOKENIZER.encode(req.text)
        
        ort_inputs = {
            "input_ids": np.array([encoding.ids], dtype=np.int64),
            "attention_mask": np.array([encoding.attention_mask], dtype=np.int64)
        }
        
        input_names = [i.name for i in SESSION.get_inputs()]
        if "token_type_ids" in input_names:
            ort_inputs["token_type_ids"] = np.array([encoding.type_ids], dtype=np.int64)

        outputs = SESSION.run(None, ort_inputs)
        logits = outputs[0]
        
        probs = softmax(logits)[0]
        top_idx = int(np.argmax(probs))
        
        return Prediction(
            label=ID2LABEL.get(top_idx, f"LABEL_{top_idx}"), 
            score=float(probs[top_idx])
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))