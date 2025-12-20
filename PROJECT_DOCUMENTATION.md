# TÀI LIỆU DỰ ÁN: HỆ THỐNG PHÂN LỚP VĂN BẢN TIẾNG VIỆT ỨNG DỤNG TRONG XỬ LÝ KHIẾU NẠI 

## TỔNG QUAN

Dự án là một hệ thống phân loại văn bản khiếu nại bằng tiếng Việt sử dụng mô hình mini LLMLLM. Hệ thống được xây dựng với kiến trúc backend-frontend, cho phép người dùng nhập văn bản khiếu nại và hệ thống sẽ tự động phân loại vào các lớp phù hợp => mục tiêu đưa các yêu cầu đến phòng ban xử các vấn đề chuyên trách.

### Chức năng chính
- Phân loại văn bản khiếu nại tiếng Việt thành 6 lớp chính
- Cung cấp API RESTful để phục vụ dự đoán
- Giao diện web thân thiện với người dùng
- Tối ưu hóa mô hình với kỹ thuật quantization để giảm kích thước và tăng tốc độ

## KIẾN TRÚC HỆ THỐNG

### 1. Backend
- **Ngôn ngữ**: Python
- **Framework**: FastAPI
- **Mô hình ML**: paraphrase-multilingual-MiniLM-L12-v2 (fine-tuned)
- **Kỹ thuật tối ưu**: Quantization INT8 với ONNX
- **API Endpoints**:
  - `GET /health`: Kiểm tra trạng thái API
  - `POST /predict`: Phân loại văn bản đầu vào

### 2. Frontend
- **Công nghệ**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Framework UI**: Bootstrap 5
- **Tính năng**:
  - Giao diện nhập liệu trực quan
  - Hiển thị kết quả phân loại với độ tin cậy
  - Cung cấp ví dụ văn bản minh họa
  - Kiểm tra trạng thái API theo thời gian thực

### 3. Training Pipeline
- **Thư viện chính**: Transformers, PyTorch, Scikit-learn
- **Mô hình cơ sở**: paraphrase-multilingual-MiniLM-L12-v2
- **Kỹ thuật tối ưu**:
  - Transfer learning với fine-tuning
  - Dynamic quantization (INT8)
  - ONNX cho inference tối ưu

## CẤU TRÚC THƯ MỤC

```
LLM/
├── backend/                 # Backend API
│   ├── api.py              # API FastAPI chính
│   ├── Dockerfile          # Docker configuration
│   └── requirements.txt   # Dependencies cho backend
├── frontend/               # Frontend UI
│   ├── index.html         # Giao diện chính
│   ├── script.js          # Logic JavaScript
│   └── styles.css         # CSS styling
├── data/                   # Dữ liệu
│   ├── raw/               # Dữ liệu thô
│   │   └── banking_text.csv
│   └── processed/         # Dữ liệu đã xử lý
│       ├── train.csv
│       ├── val.csv
│       └── test.csv
├── models/                 # Mô hình ML
│   ├── production/        # Mô hình triển khaikhai
│   │   ├── model_main.onnx
│   │   ├── tokenizer.json
│   │   └── config.json
│   ├── raw_model/         # Mô hình thô
│   └── onnx_int8/         # Mô hình ONNX quantized
└── training_pipeline/     # Quy trình huấn luyện
    ├── notebooks/         # Jupyter notebooks
    │   └── 01_eda_analysis.ipynb
    ├── requirements.txt    # Dependencies cho training
    └── src/               # Source code
        ├── cleaning/       # Module làm sạch dữ liệu
        ├── quant/         # Module quantization
        └── training/      # Module huấn luyện
```

## CHI TIẾT CÁC THÀNH PHẦN

### 1. Backend API

#### `api.py`:
- Khởi tạo mô hình ONNX và tokenizer
- Cung cấp API endpoints cho phân loại văn bản
- Tối ưu hóa cho môi trường low-memory (0.1 cpu/ 512MB RAM)
- Cấu hình CORS để cho phép giao tiếp từ frontend

#### `Dockerfile`:
- Cấu hình Docker container tối giản
- Tối ưu hóa cho môi trường Render Free Plan
- Cài đặt dependencies và copy các file cần thiết

### 2. Frontend

#### `index.html`:
- Giao diện người dùng responsive
- Form nhập liệu và hiển thị kết quả
- Modal loading và thông tin mô hình

#### `script.js`:
- Xử lý logic phân loại phía client
- Gọi API backend để dự đoán
- Hiển thị kết quả với độ tin cậy
- Xử lý lỗi và trạng thái API

#### `styles.css`:
- Styling với Bootstrap và custom CSS
- Responsive design cho mobile và desktop
- Animations và transitions mượt mà

### 3. Training Pipeline

#### `src/cleaning/clean.py`:
- Làm sạch và chuẩn hóa văn bản tiếng Việt
- Loại bỏ ký tự đặc biệt và chuẩn hóa Unicode
- Chia dữ liệu thành train/validation/test sets

#### `src/training/train.py`:
- Fine-tune mô hình paraphrase-multilingual-MiniLM-L12-v2
- Cấu hình training arguments và metrics
- Lưu mô hình đã fine-tuned

#### `src/quant/onnx_int8.py`:
- Chuyển đổi mô hình PyTorch sang ONNX
- Áp dụng dynamic quantization (INT8)
- Tối ưu hóa kích thước và tốc độ inference

#### `src/quant/convert.py`:
- Chuẩn bị mô hình cho môi trường sản xuất
- Tách riêng weights để tối ưu hóa lưu trữ

## DỮ LIỆU

### Dataset gốc
- File: `data/raw/banking_text.csv`
- Kích thước: ~4640 mẫu
- Định dạng: text, label
- Các lớp phân loại:
  1. CARD_ISSUE - Các vấn đề liên quan đến thẻ ngân hàng
  2. APP_LOGIN - Vấn đề đăng nhập ứng dụng
  3. TRANSACTION - Các vấn đề giao dịch
  4. LOAN_SAVING - Các vấn đề vay và tiết kiệm
  5. FRAUD_REPORT - Báo cáo gian lận
  6. OTHERS - Các vấn đề khác

### Phân chia dữ liệu
- Train: 80%
- Validation: 10%
- Test: 10%

## MÔ HÌNH

### Mô hình cơ sở
- Tên: paraphrase-multilingual-MiniLM-L12-v2
- Kiến trúc: BERT-based sentence transformer
- Đặc điểm: Hỗ trợ đa ngôn ngữ, bao gồm tiếng Việt

### Fine-tuning
- Tham số được điều chỉnh:
  - Learning rate: 2e-5
  - Batch size: 32
  - Epochs: 5
  - Max length: 64
- Metrics: Accuracy và F1-score

### Tối ưu hóa
- Dynamic quantization: Chuyển đổi weights sang INT8
- ONNX Runtime: Tối ưu hóa inference
- Model size: Giảm ~75% sau quantization

## CÀI ĐẶT VÀ TRIỂN KHAI

### Môi trường phát triển
```bash
# Backend
cd backend
pip install -r requirements.txt

# Training Pipeline
cd training_pipeline
pip install -r requirements.txt
```

### Huấn luyện mô hình
```bash
cd training_pipeline/src
python -m cleaning.clean        # Làm sạch dữ liệu
python -m training.train         # Huấn luyện mô hình
python -m quant.onnx_int8        # Quantization
python -m quant.convert          # Chuẩn bị cho production
```

### Triển khai với Docker
```bash
# Build image
docker build -t text-classification .

# Run container
docker run -p 8000:8000 text-classification
```

### Triển khai trên Render (Backend)
- Kết nối repository GitHub với Render
- Sử dụng Dockerfile trong thư mục backend
- Cấu hình môi trường 1 CPU 512MB RAM (Free Plan)
- URL triển khai: https://llm-vhhs.onrender.com/

### Triển khai trên Vercel (Frontend)
- Kết nối repository GitHub với Vercel
- Cấu hình với thư mục frontend làm root
- URL triển khai: https://llmfontend.vercel.app/
- Cấu hình CORS cho phép giao tiếp giữa frontend và backend

## TỐI ƯU HÓA CHO PHẦN CỨNG YẾU

### 1. Backend Optimization
- **Memory Optimization**:
  - Sử dụng biến môi trường `OMP_NUM_THREADS=1` để giới hạn số luồng
  - Tắt `ORT_TENSORRT_FP16_ENABLE` để giảm sử dụng RAM
  - Cấu hình ONNX Runtime với `intra_op_num_threads=1`
  - Tắt `enable_cpu_mem_arena` để giảm overhead

- **Model Optimization**:
  - Dynamic quantization (INT8) giảm kích thước mô hình ~75%
  - Sử dụng ONNX Runtime thay cho PyTorch cho inference nhanh hơn
  - Chỉ tải mô hình khi cần thiết (lazy loading)

- **FastAPI Configuration**:
  - Sử dụng `uvicorn` với 1 worker duy nhất
  - Tắt auto-reload trong production
  - Sử dụng context manager để quản lý vòng đời mô hình

### 2. Frontend Optimization
- **Asset Optimization**:
  - Sử dụng CDN cho Bootstrap và Font Awesome
  - Tối ưu CSS với variables để giảm kích thước file
  - Lazy loading cho các thành phần không cần thiết ngay

- **JavaScript Optimization**:
  - Sử dụng async/await cho API calls
  - Throttling cho API health check (30 giây/lần)
  - Xử lý lỗi gracefully với fallback UI

- **UI/UX for Low-end Devices**:
  - Tối giản animations và transitions
  - Sử dụng CSS transforms thay vì animations JavaScript
  - Responsive design cho mobile devices

### 3. Network Optimization
- **API Communication**:
  - Gzip compression cho responses
  - Minimal payload với chỉ dữ liệu cần thiết
  - Keep-alive connections để giảm latency

- **Error Handling**:
  - Retry logic cho failed requests
  - Toast notifications thay vì alerts
  - Graceful degradation khi API unavailable

## HIỆU NĂNG

### Metrics
- Accuracy: ~87%
- F1-score: ~87%
- Inference time: <100ms per request

### Tối ưu hóa
- Memory usage: <100MB per request (tối ưu cho 512MB RAM)
- CPU usage: Tối thiểu với single thread (tối ưu cho 1 CPU)
- Startup time: <10s trên Render Free Plan
- Inference time: <100ms trên phần cứng yếu

## HƯỚNG PHÁT TRIỂN

1. **Cải tiến mô hình**:
   - Thử nghiệm với các mô hình khác (PhoBERT, XLM-R)
   - Fine-tuning với dữ liệu lớn hơn
   - Áp dụng các kỹ thuật quantization khác

2. **Mở rộng chức năng**:
   - Thêm nhiều lớp phân loại
   - Hỗ trợ ngôn ngữ khác
   - API endpoints cho batch processing

3. **Cải thiện UX**:
   - Thêm history của các lần phân loại
   - Export kết quả
   - Real-time typing suggestions

## DEPLOYMENT PRODUCTION

### Current Deployment
- **Frontend**: https://llmfontend.vercel.app/ (Vercel)
- **Backend**: https://llm-vhhs.onrender.com (Render Free Plan)
- **Resources**: 0.1 CPU, 512MB RAM
- **Status**: Đang hoạt động ổn định

### Deployment Process
1. **Backend Deployment**:
   - Tự động deploy khi push code lên GitHub
   - Sử dụng Dockerfile để build container
   - Render tự động scale down khi không active (free tier)

2. **Frontend Deployment**:
   - Vercel tự động deploy khi có thay đổi
   - Sử dụng Preview Deployments cho testing
   - Custom domain cho production

3. **Monitoring**:
   - Render Dashboard cho backend metrics
   - Vercel Analytics cho frontend performance
   - Custom health check endpoint

## KẾT LUẬN

Hệ thống phân loại văn bản tiếng Việt này cung cấp một giải pháp hiệu quả và tối ưu để phân loại các khiếu nại ngân hàng. Với kiến trúc hiện đại, mô hình được tối ưu hóa và giao diện thân thiện, hệ thống có thể triển khai trên các nền tảng cloud với chi phí tối thiểu.

Đặc biệt, hệ thống đã được triển khai thành công trên nền tảng miễn phí (Render và Vercel) với cấu hình phần cứng yếu (0.1 CPU, 512MB RAM) nhưng vẫn hoạt động hiệu quả nhờ các kỹ thuật tối ưu hóa chuyên sâu. Điều này chứng minh khả năng mở rộng và tiết kiệm chi phí của giải pháp.
