# Text Classification LLM

Dự án phân loại văn bản sử dụng mô hình Deep Learning/Transformer, bao gồm quy trình Training, và Deploy thành 2 service Backnet (FastAPI) & Frontend (Streamlit).

## Cấu trúc thư mục

```
text-classification-llm/
│
├── .github/                   # CI/CD workflows
├── .gitignore                 # Ignore venv, __pycache__, models nặng (.bin)
├── README.md                  # Tài liệu dự án
│
├── data/                      # --- QUẢN LÝ DỮ LIỆU ---
│   ├── raw/                   # Dữ liệu thô (csv, excel) chưa xử lý
│   ├── processed/             # Dữ liệu đã làm sạch & map teencode (dùng để train)
│   └── teencode.json          # Dictionary Teencode (File quan trọng dùng chung)
│
├── models/                    # --- MODEL ARTIFACTS ---
│   ├── raw_pytorch/           # Model sau khi fine-tune (nhưng chưa tối ưu)
│   └── production/            # Model ONNX Int8 (Chỉ deploy file này)
│       └── model_int8.onnx
│
├── training_pipeline/         # --- KHÔNG GIAN TRAINING & ANALYTICS (Local/Colab) ---
│   ├── requirements.txt       # Thư viện nặng: torch, transformers, pandas, scikit-learn
│   │
│   ├── notebooks/             # Jupyter Notebooks (Phân tích & Thử nghiệm)
│   │   ├── 01_eda_analysis.ipynb   # Phân tích phân bố nhãn, độ dài câu
│   │   └── 02_teencode_test.ipynb  # Test logic replace teencode
│   │
│   └── src/                   # Source code xử lý logic chính
│       ├── __init__.py
│       ├── preprocessing.py   # Class load teencode.json và clean text
│       ├── dataset.py         # Class PyTorch Dataset
│       ├── train.py           # Script chạy Fine-tuning (Trainer loop)
│       └── export_quantize.py # Script convert PyTorch -> ONNX -> Int8
│
├── backend/                   # --- SERVICE 1: FASTAPI (Deploy Render) ---
│   ├── Dockerfile             # Dockerfile tối ưu cho Backend
│   ├── requirements.txt       # Chỉ chứa: onnxruntime, fastapi, uvicorn
│   ├── main.py                # API Endpoint
│   ├── schemas.py             # Pydantic Models
│   ├── inference.py           # Logic load ONNX model
│   └── utils.py               # Copy logic từ preprocessing.py sang đây
│
└── frontend/                  # --- SERVICE 2: STREAMLIT (Deploy Render) ---
    ├── Dockerfile             # Dockerfile tối ưu cho Frontend
    ├── requirements.txt       # Chỉ chứa: streamlit, requests
    └── app.py                 # Giao diện Chat tạo cấu trúc thư mục như trên
```
