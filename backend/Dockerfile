# Minimal Dockerfile for Render Free Plan (512MB RAM)
FROM python:3.9-slim-bullseye

# Set environment variables for memory optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=10000 \
    PYTHONOPTIMIZE=2 \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgomp1 \
    && apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY backend/requirements.txt requirements.txt

# Install with minimal dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and model
RUN mkdir -p models/production backend
COPY models/production/ ./models/production/
COPY backend/api-minimal.py ./backend/api.py

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Run with minimal workers for memory optimization
CMD ["uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
