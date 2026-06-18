FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 7865

ENV WHISPER_MODEL_SIZE=base
ENV PORT=7865
ENV HOST=0.0.0.0
ENV TMP_DIR=/app/tmp
ENV WHISPER_CPU_THREADS=4
ENV OMP_NUM_THREADS=4

CMD ["python", "main.py"]
