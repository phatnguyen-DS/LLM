FROM debian:buster-slim as builder
# Cập nhật sources.list để dùng archive repo vì Buster đã EOL
RUN echo "deb http://archive.debian.org/debian buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list && \
    apt-get -o Acquire::Check-Valid-Until=false update && \
    apt-get install -y --no-install-recommends prelink

FROM python:3.9-slim-bullseye

WORKDIR /app

# Tối ưu hóa biến môi trường
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000

COPY backend/requirements.txt .

# Copy execstack từ stage builder vào final stage
COPY --from=builder /usr/bin/execstack /usr/bin/execstack

# Gộp lệnh RUN để giảm layer
# QUAN TRỌNG: Cần libelf1 để chạy execstack
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 libelf1 && \
    pip install -r requirements.txt && \
    # FIX LỖI "cannot enable executable stack" TRÊN RENDER
    execstack -c /usr/local/lib/python3.9/site-packages/onnxruntime/capi/onnxruntime_pybind11_state.cpython-39-x86_64-linux-gnu.so || true && \
    # Cleanup
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache/pip && \
    find /usr/local/lib/python3.9 -name '*.pyc' -delete && \
    find /usr/local/lib/python3.9 -name '__pycache__' -delete

RUN mkdir -p models/production backend
COPY models/production/ ./models/production/
COPY backend/api.py ./backend/

CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "10000"]