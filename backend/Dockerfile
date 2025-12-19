FROM python:3.9-slim

WORKDIR /app

# optimize
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000

COPY backend/requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 binutils && \
    pip install -r requirements.txt && \
    find /usr/local/lib/python3.9 -name "*.so" | xargs strip && \
    apt-get remove -y binutils && \
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