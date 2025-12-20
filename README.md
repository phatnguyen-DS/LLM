# Text Classification LLM

Dự án phân loại văn bản tiếng Việt sử dụng mô hình Transformer, triển khai với kiến trúc microservices và tối ưu hóa hiệu suất với ONNX.

## 🚀 Overview

Dự án này là một hệ thống phân loại văn bản hoàn chỉnh từ end-to-end, được xây dựng với kiến trúc microservices, bao gồm:
- **Backend API**: FastAPI với ONNX Runtime để phục vụ inference hiệu suất cao
- **Frontend UI**: Streamlit cho giao diện người dùng tương tác
- **Training Pipeline**: Quy trình MLOps hoàn chỉnh từ xử lý dữ liệu đến huấn luyện và triển khai
- **Model Optimization**: Quantization và tối ưu hóa model để giảm kích thước và tăng tốc độ inference

## 📁 Cấu trúc thư mục

```
text-classification-llm/
│
├── .github/                   # CI/CD workflows (sẽ được thêm)
├── .gitignore                 # Ignore venv, __pycache__, models nặng (.bin)
├── README.md                  # Tài liệu dự án
│
├── data/                      # --- QUẢN LÝ DỮ LIỆU ---
│   ├── raw/                   # Dữ liệu thô (csv, excel) chưa xử lý
│   │   └── banking_text.csv   # Dataset văn bản ngân hàng tiếng Việt
│   ├── processed/             # Dữ liệu đã làm sạch (dùng để train)
│   │   ├── train.csv          # Dữ liệu huấn luyện
│   │   ├── val.csv            # Dữ liệu validation
│   │   └── test.csv           # Dữ liệu test
│
├── models/                    # --- MODEL ARTIFACTS ---
│   ├── raw_model/             # Model PyTorch sau khi fine-tune
│   ├── onnx_int8/             # Model ONNX Int8 (tạm thời)
│   └── production/            # Model ONNX Int8 (sẵn sàng deploy)
│       ├── model_main.onnx    # Model chính
│       ├── tokenizer.json     # Tokenizer
│       └── config.json        # Cấu hình model
│
├── training_pipeline/         # --- PIPELINE TRAINING ---
│   ├── requirements.txt       # Dependencies cho training
│   │
│   ├── notebooks/             # Jupyter Notebooks
│   │   └── 01_eda_analysis.ipynb  # Phân tích dữ liệu
│   │
│   └── src/                   # Source code xử lý logic
│       ├── __init__.py
│       ├── cleaning/          # Module làm sạch dữ liệu
│       │   ├── __init__.py
│       │   └── clean.py       # Script làm sạch và split data
│       ├── training/          # Module huấn luyện model
│       │   ├── __init__.py
│       │   └── train.py       # Script fine-tuning model
│       └── quant/             # Module quantization
│           ├── __init__.py
│           ├── onnx_int8.py   # Script quantize ONNX
│           └── convert.py     # Script chuyển đổi model
│
├── backend/                   # --- SERVICE 1: FASTAPI ---
│   ├── api.py                 # API endpoints
│   ├── requirements.txt       # Dependencies cho inference
│   └── Dockerfile             # Dockerfile cho backend
│
└── frontend/                  # --- SERVICE 2: STREAMLIT ---
    ├── streamlit.py           # Giao diện người dùng
    ├── requirements.txt       # Dependencies cho frontend
    └── Dockerfile             # Dockerfile cho frontend
```

## 🛠️ Cài đặt và sử dụng

### Yêu cầu
- Python 3.9+
- Docker (nếu chạy với container)
- GPU (nếu huấn luyện)

### 1. Huấn luyện model mới

```bash
# Clone repository
git clone https://github.com/username/text-classification-llm.git
cd text-classification-llm

# Cài đặt dependencies cho training
cd training_pipeline
pip install -r requirements.txt

# Xử lý dữ liệu
python src/cleaning/clean.py

# Huấn luyện model
python src/training/train.py

# Quantize model
python src/quant/onnx_int8.py

# Chuyển đổi model sang production
python src/quant/convert.py
```

### 2. Chạy backend API

```bash
# Cài đặt dependencies
cd backend
pip install -r requirements.txt

# Chạy API server
uvicorn api:app --host 0.0.0.0 --port 10000 --reload
```

### 3. Chạy frontend UI

```bash
# Cài đặt dependencies
cd frontend
pip install -r requirements.txt

# Chạy Streamlit app
streamlit run streamlit.py --server.port 8501
```

### 4. Sử dụng Docker

```bash
# Build và chạy backend
docker build -f backend/Dockerfile -t llm-backend .
docker run -p 10000:10000 llm-backend

# Build và chạy frontend
docker build -f frontend/Dockerfile -t llm-frontend .
docker run -p 8501:8501 llm-frontend
```

### 5. Sử dụng API

```python
import requests

# Gửi request đến API
response = requests.post(
    "http://localhost:10000/predict",
    json={"text": "Thẻ của tôi bị lỗi không thể sử dụng"}
)

# Xem kết quả
result = response.json()
print(f"Label: {result['label']}")
print(f"Score: {result['score']}")
```

## 📊 Thông số kỹ thuật

### Model
- **Base Model**: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- **Architecture**: Transformer-based encoder
- **Classes**: 6
  - CARD_ISSUE: Vấn đề liên quan đến thẻ
  - APP_LOGIN: Vấn đề đăng nhập ứng dụng
  - TRANSACTION: Vấn đề giao dịch
  - LOAN_SAVING: Vấn đề vay/tiết kiệm
  - FRAUD_REPORT: Báo cáo lừa đảo
  - OTHERS: Các vấn đề khác
- **Max Sequence Length**: 64 tokens
- **Optimization**: Dynamic Quantization (INT8)

### Performance Metrics
- **Accuracy**: TBD (sẽ được cập nhật sau khi đánh giá)
- **F1 Score**: TBD
- **Model Size**: ~650KB (sau quantization)
- **Inference Time**: <50ms (CPU)
- **Throughput**: TBD requests/second

## 🏗️ Kiến trúc hệ thống

### Microservices Architecture
- **Backend Service**: FastAPI với ONNX Runtime
  - Endpoint `/predict`: Dự đoán lớp văn bản
  - Endpoint `/health`: Kiểm tra trạng thái hệ thống
- **Frontend Service**: Streamlit UI
  - Giao diện người dùng thân thiện
  - Tương tác với backend qua REST API

### Data Flow
1. Người dùng nhập văn bản vào frontend
2. Frontend gửi request đến backend API
3. Backend tiền xử lý text và chuyển thành tokens
4. ONNX model thực hiện inference
5. Backend trả về kết quả cho frontend
6. Frontend hiển thị kết quả cho người dùng

### Model Deployment Pipeline
1. Raw Data → Cleaned Data (clean.py)
2. Cleaned Data → Trained Model (train.py)
3. Trained Model → ONNX Model (onnx_int8.py)
4. ONNX Model → Production Model (convert.py)
5. Production Model → Containerized API (Docker)

## 🔧 Best Practices và Optimizations

### Backend Optimizations
- Giới hạn số luồng CPU để tối ưu tài nguyên
- Sử dụng ONNX Runtime cho inference hiệu suất cao
- Caching model và tokenizer để tránh tải lại nhiều lần
- Error handling và logging chi tiết
- FastAPI với automatic docs generation

### Frontend Features
- Responsive design cho nhiều thiết bị
- Xử lý lỗi người dùng thân thiện
- Health check và status indicators
- Ví dụ mẫu để hướng dẫn người dùng
- Non-blocking UI với loading states

### Model Optimizations
- Dynamic quantization để giảm kích thước model
- Multi-stage Docker builds để tối ưu image size
- Separate production and training environments

## 🚀 Triển khai

### Local Development
```bash
# Backend
cd backend && uvicorn api:app --reload

# Frontend
cd frontend && streamlit run streamlit.py
```

### Production (Render)
- **Backend**: Deploy FastAPI service với Docker
- **Frontend**: Deploy Streamlit app với Docker
- **Database**: (Optional) Ghi log và metrics
- **Monitoring**: Health checks và uptime monitoring

### Image Sizes
- **Backend Image**: ~200MB (bao gồm model)
- **Frontend Image**: ~50MB
- **Total**: ~250MB (nằm trong giới hạn của Render Free)

## 📝 Todo List (Middle Level Features)

### Testing
- [ ] Unit tests cho tất cả modules
- [ ] Integration tests cho API endpoints
- [ ] Model performance regression tests
- [ ] End-to-end tests cho toàn bộ pipeline

### Monitoring & Logging
- [ ] Structured logging với ELK stack
- [ ] Prometheus metrics cho performance
- [ ] Grafana dashboard visualization
- [ ] Alert system cho lỗi và anomalies

### Security
- [ ] API authentication với JWT
- [ ] Rate limiting để bảo vệ API
- [ ] Input validation và sanitization
- [ ] HTTPS và secure headers

### CI/CD
- [ ] GitHub Actions cho automated testing
- [ ] Automated model validation
- [ ] Blue-green deployment strategy
- [ ] Rollback mechanisms

### Performance
- [ ] Redis caching cho frequent requests
- [ ] Batch processing cho multiple texts
- [ ] Model versioning and A/B testing
- [ ] Load balancing và horizontal scaling

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

Dự án này được cấp phép theo MIT License - xem file [LICENSE](LICENSE) để biết chi tiết.

## 👥 Team

- **Lead AI Engineer**: [Tên]
- **ML Engineer**: [Tên]
- **Backend Developer**: [Tên]
- **Frontend Developer**: [Tên]

## 📞 Liên hệ

- **Project Link**: [https://github.com/username/text-classification-llm](https://github.com/username/text-classification-llm)
- **Issues**: [https://github.com/username/text-classification-llm/issues](https://github.com/username/text-classification-llm/issues)