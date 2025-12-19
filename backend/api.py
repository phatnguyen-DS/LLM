FROM python:3.9-slim

WORKDIR /app

# 1. Cài đặt hệ thống và dọn dẹp layer ngay lập tức để tiết kiệm dung lượng
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Cài đặt thư viện và xóa cache pip trong cùng 1 RUN
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# 3. Tạo thư mục đích
RUN mkdir -p models/production

# 4. CHỈ copy những gì cần thiết, tránh dùng dấu / ở cuối bừa bãi
# Copy cấu hình
COPY models/production/tokenizer.json models/production/config.json models/production/model_main.onnx ./models/production/
# Copy trọng số (Dùng wildcard để chỉ lấy file weight, tránh lấy file rác khác)
COPY models/production/*.weight_quantized models/production/*-*-*-*-* ./models/production/ 2>/dev/null || true

# 5. Copy code API
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