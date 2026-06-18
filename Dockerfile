FROM python:3.11-slim

# Set security headers and environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with cleanup
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure tmp directory exists and is writable
RUN mkdir -p tmp && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

EXPOSE 7865

# Configuration defaults for production
ENV WHISPER_MODEL_SIZE=base \
    PORT=7865 \
    HOST=0.0.0.0 \
    TMP_DIR=/app/tmp \
    WHISPER_CPU_THREADS=4 \
    OMP_NUM_THREADS=4 \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:7865').read()" || exit 1

CMD ["python", "main.py"]
