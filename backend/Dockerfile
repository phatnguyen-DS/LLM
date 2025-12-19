FROM python:3.9-slim

WORKDIR /app

# 1. Cài đặt libgomp1 và prelink (thay thế cho execstack)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    prelink \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Cài đặt thư viện Python
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# 3. Sử dụng lệnh 'execstack' (nằm trong gói prelink) để fix lỗi Shared Object
RUN execstack -c /usr/local/lib/python3.9/site-packages/onnxruntime/capi/onnxruntime_pybind11_state.cpython-39-x86_64-linux-gnu.so || true

# 4. Copy dữ liệu
RUN mkdir -p models/production backend
COPY models/production/ ./models/production/
COPY backend/api.py ./backend/

# 5. Cấu hình môi trường tối ưu cho Render
ENV PORT=10000 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    ONNXRUNTIME_EXECUTION_MODE=SEQUENTIAL

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["sh", "-c", "uvicorn backend.api:app --host 0.0.0.0 --port ${PORT} --workers 1 --limit-concurrency 2"]