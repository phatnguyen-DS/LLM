FROM python:3.9-slim

WORKDIR /app

# Gộp cài đặt hệ thống và dọn dẹp ngay để không tốn thêm MB nào
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt thư viện và xóa cache pip NGAY TRONG CÙNG 1 LỚP
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# Tạo thư mục và copy file có chọn lọc
RUN mkdir -p models/production backend

# Chỉ copy đúng những file cần thiết để chạy
COPY models/production/tokenizer.json \
    models/production/config.json \
    models/production/model_main.onnx \
    ./models/production/

# Copy các file trọng số rời (nếu có)
# Thay cho dòng COPY cũ bị lỗi
COPY models/production/*.weight_quantized ./models/production/
COPY models/production/*-*-*-*-* ./models/production/

COPY backend/api.py ./backend/

ENV PORT=10000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    ONNXRUNTIME_EXECUTION_MODE=SEQUENTIAL

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["sh", "-c", "uvicorn backend.api:app --host 0.0.0.0 --port ${PORT} --workers 1 --limit-concurrency 2"]