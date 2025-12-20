# Hệ thống Phân loại Văn bản Tiếng Việt ứng dụng trong xử lý khiếu nạinại

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Dự án là một hệ thống phân loại văn bản khiếu nại bằng tiếng Việt sử dụng mô hình mini LLMLLM. Hệ thống được xây dựng với kiến trúc backend-frontend, cho phép người dùng nhập văn bản khiếu nại và hệ thống sẽ tự động phân loại vào các lớp phù hợp => mục tiêu đưa các yêu cầu đến phòng ban xử các vấn đề chuyên trách.

live app for test : https://llmfontend.vercel.app/

## Tính năng chính

- **Phân loại chính xác**: Phân loại văn bản khiếu nại tiếng Việt vào 6 lớp chuyên biệt
- **Tối ưu hóa**: Sử dụng kỹ thuật quantization INT8 để giảm kích thước mô hình và tăng tốc độ
- **API RESTful**: Cung cấp API endpoint để tích hợp với các hệ thống khác
- **Giao diện thân thiện**: Web interface đơn giản, dễ sử dụng
- **Triển khai dễ dàng**: Hỗ trợ Docker container và cloud deployment

##  Kiến trúc hệ thống

```
Frontend (HTML/CSS/JS) ←→ Backend API (FastAPI) ←→ mini LLM Model (ONNX)
```

##  Cấu trúc dự án

```
LLM/
├── backend/                 # Backend API
│   ├── api.py              # FastAPI server
│   ├── Dockerfile          # Docker configuration
│   └── requirements.txt   # Dependencies
├── frontend/               # Frontend UI
│   ├── index.html         # Giao diện chính
│   ├── script.js          # JavaScript logic
│   └── styles.css         # Styling
├── data/                   # Dữ liệu
├── models/                 # Mô hình ML
├── training_pipeline/     # Training scripts
└── README.md              # File này
```

## ccác lớp phân loại

1. **CARD_ISSUE** - Các vấn đề liên quan đến thẻ ngân hàng
2. **APP_LOGIN** - Vấn đề đăng nhập ứng dụng
3. **TRANSACTION** - Các vấn đề giao dịch
4. **LOAN_SAVING** - Các vấn đề vay và tiết kiệm
5. **FRAUD_REPORT** - Báo cáo gian lận
6. **OTHERS** - Các vấn đề khác

## Hiệu suất mô hình
### model fine turning float 32

### model fine turning convert to onnx + int8

## Quick Start

### 1. Clone repository
```bash
git clone https://github.com/yourusername/LLM.git
cd LLM
```

### 2. Cài đặt dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Nếu cần huấn luyện lại mô hình
cd ../training_pipeline
pip install -r requirements.txt
```

### 3. Chạy API server
```bash
cd backend
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 4. Mở frontend
Mở file `frontend/index.html` trong trình duyệt hoặc truy cập `http://localhost:8000` (nếu được cấu hình)

## 🐳 Docker Deployment

```bash
# Build image
docker build -t text-classification .

# Run container
docker run -p 8000:8000 text-classification
```

## ☁️ Cloud Deployment

### Production Deployment
- **Frontend**: https://llmfontend.vercel.app/ (Vercel)
- **Backend**: https://llm-vhhs.onrender.com (Render Free Plan)
- **Resources**: 1 CPU, 512MB RAM

### Render (Backend)
1. Kết nối repository GitHub với Render
2. Sử dụng Dockerfile trong thư mục backend
3. Cấu hình môi trường 1 CPU, 512MB RAM (Free Plan)
4. Tự động deploy khi push code lên main branch

### Vercel (Frontend)
1. Kết nối repository GitHub với Vercel
2. Đặt thư mục frontend làm root directory
3. Cấu hình biến môi trường nếu cần
4. Tự động deploy khi có thay đổi

### Heroku (Alternative)
```bash
# Build và deploy
heroku create your-app-name
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
```

## API Documentation

### Health Check
```http
GET /health
```
Trả về trạng thái của API và mô hình.

### Phân loại văn bản
```http
POST /predict
Content-Type: application/json

{
  "text": "Thẻ của tôi bị lỗi không thể thanh toán được"
}
```
Kết quả trả về:
```json
{
  "label": "CARD_ISSUE",
  "score": 0.95
}
```

## 🛠️ Huấn luyện lại mô hình

Nếu bạn muốn huấn luyện lại mô hình với dữ liệu mới:

```bash
cd training_pipeline/src

# 1. Làm sạch và chuẩn bị dữ liệu
python -m cleaning.clean

# 2. Huấn luyện mô hình
python -m training.train

# 3. Quantization để tối ưu
python -m quant.onnx_int8

# 4. Chuẩn bị cho production
python -m quant.convert
```

## 📈 Hiệu năng

- **Độ chính xác**: ~87%
- **Thời gian suy luận**: <100ms mỗi yêu cầu
- **Kích thước mô hình**: ~129MB (sau quantization)
- **Bộ nhớ sử dụng**: <100MB mỗi yêu cầu
- **Tối ưu cho phần cứng yếu**: Hoạt động ổn định trên 0.1 CPU, 512MB RAM

## ⚡ Tối ưu hóa cho Phần cứng Yếu

### Backend Optimization
- Sử dụng Dynamic Quantization (INT8) giảm 75% kích thước mô hình
- ONNX Runtime thay cho PyTorch cho inference nhanh hơn
- Giới hạn số luồng xử lý (`OMP_NUM_THREADS=1`)
- Tối ưu memory usage cho 512MB RAM

### Frontend Optimization
- Sử dụng CDN cho các tài nguyên tĩnh
- Responsive design cho mobile devices
- Tối giản animations và transitions
- Error handling gracefully khi API unavailable


##  Giấy phép

Dự án này được phân phối dưới giấy phép MIT - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## Tác giả

**TAN PHAT**
- Email: tanphat6406@gmail.com
- SĐT: 0333786257

## Cảm ơn

- Hugging Face Transformers cho mô hình pre-trained
- FastAPI team cho framework API mạnh mẽ
- Bootstrap cho UI components
- Render và Vercel cho hosting miễn phí
