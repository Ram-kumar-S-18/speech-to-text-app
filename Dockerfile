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
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Download and bake Whisper model weights into the image
RUN python download_model.py

# Ensure tmp directory exists and is writable
RUN mkdir -p tmp && chown -R appuser:appuser /app

# Run as root to support persistent volume mounts and avoid home folder permission restrictions

EXPOSE 7860

# Configuration defaults for production
ENV WHISPER_MODEL_SIZE=base \
    PORT=7860 \
    HOST=0.0.0.0 \
    TMP_DIR=/tmp \
    WHISPER_CPU_THREADS=2 \
    OMP_NUM_THREADS=2 \
    LOG_LEVEL=INFO \
    PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
