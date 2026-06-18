
# Deployment Guide - Speech-to-Text Transcriber

## Overview
This guide provides step-by-step instructions for deploying the Speech-to-Text application to various platforms.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Platforms](#cloud-platforms)
5. [Environment Configuration](#environment-configuration)
6. [Performance Tuning](#performance-tuning)
7. [Monitoring & Troubleshooting](#monitoring--troubleshooting)

---

## Prerequisites

### System Requirements
- **Python**: 3.11+
- **FFmpeg**: Required for audio processing. Install via:
  - **Ubuntu/Debian**: `apt-get install ffmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Windows**: Download from https://ffmpeg.org/download.html

### Credentials
- For cloud deployments, have API credentials or SSH keys ready
- For Render.com: Generate and copy your API key
- For Heroku: Install Heroku CLI and authenticate

---

## Local Development

### 1. Setup
```bash
cd speech_to_text
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your settings
export $(cat .env | xargs)  # Load variables
```

### 3. Run Application
```bash
python main.py --model base
# Access at http://localhost:7865
```

---

## Docker Deployment

### 1. Build Image
```bash
docker build -t speech-to-text:latest .
```

### 2. Run Container
```bash
docker run -d \
  -p 7865:7865 \
  -e WHISPER_MODEL_SIZE=base \
  -e LOG_LEVEL=INFO \
  --name speech-to-text \
  speech-to-text:latest
```

### 3. Using Docker Compose
```bash
docker-compose up -d
# View logs: docker-compose logs -f
# Stop: docker-compose down
```

### 4. Health Check
```bash
curl http://localhost:7865
```

---

## Cloud Platforms

### Render.com (Recommended for Heroku alternative)

#### Deploy Steps:
1. Push to GitHub repository
2. Go to [Render.com](https://render.com)
3. Create New → Web Service
4. Connect GitHub repository
5. Configure:
   - **Name**: `speech-to-text-app`
   - **Environment**: `Docker`
   - **Region**: Choose closest to users
   - **Plan**: Standard (or higher for production)

#### Set Environment Variables:
```
WHISPER_MODEL_SIZE=base
PYTHON_VERSION=3.11
PORT=10000
LOG_LEVEL=INFO
```

#### Deployment:
- Render automatically builds from Dockerfile
- Available at: `https://<your-app>.onrender.com`

---

### AWS EC2

#### 1. Launch Instance
- AMI: Ubuntu 22.04 LTS
- Instance Type: t3.medium (for small/medium models)
- Security Group: Allow ports 22 (SSH), 80 (HTTP), 443 (HTTPS)

#### 2. Setup
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3.11 python3-pip ffmpeg git

git clone <your-repo>
cd speech_to_text
pip install -r requirements.txt
```

#### 3. Run with Systemd
Create `/etc/systemd/system/speech-to-text.service`:
```ini
[Unit]
Description=Speech-to-Text Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/speech_to_text
Environment="PATH=/home/ubuntu/venv/bin"
ExecStart=/home/ubuntu/venv/bin/gunicorn \
  --workers 2 --worker-class sync --timeout 120 \
  --bind 0.0.0.0:7865 wsgi:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable speech-to-text
sudo systemctl start speech-to-text
```

---

### Google Cloud Run

#### Deploy
```bash
gcloud run deploy speech-to-text \
  --source . \
  --platform managed \
  --memory 2Gi \
  --timeout 600 \
  --set-env-vars "WHISPER_MODEL_SIZE=base,LOG_LEVEL=INFO"
```

---

## Environment Configuration

### Core Settings
```env
# Model Selection (tiny, base, small, medium, large)
WHISPER_MODEL_SIZE=base

# Server
PORT=7865
HOST=0.0.0.0

# Audio Processing
SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_FORMAT=wav

# Performance (CPU Threads)
WHISPER_CPU_THREADS=4
OMP_NUM_THREADS=4

# Logging
LOG_LEVEL=INFO

# Optional Output
OUTPUT_DIR=
```

### Model Size Trade-offs
| Model | Memory | Speed | Accuracy |
|-------|--------|-------|----------|
| tiny | 1GB | Very Fast | Moderate |
| base | 2GB | Fast | Good |
| small | 3GB | Moderate | Very Good |
| medium | 5GB | Slow | Excellent |
| large | 10GB | Very Slow | Best |

---

## Performance Tuning

### CPU Optimization
```bash
export WHISPER_CPU_THREADS=4
export OMP_NUM_THREADS=4
export KMP_AFFINITY=granularity=fine,compact,1,0
```

### Memory Optimization
- Use `tiny` or `base` model for limited RAM
- Use `int8` quantization (default in faster-whisper)
- Limit concurrent requests

### Network Optimization
- Enable gzip compression
- Use CDN for static assets
- Consider response caching

### Docker Optimization
```yaml
# In docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

---

## Monitoring & Troubleshooting

### View Logs
```bash
# Local
python main.py --model base 2>&1 | tee app.log

# Docker
docker logs -f speech-to-text

# Docker Compose
docker-compose logs -f

# Render.com
# View in dashboard → Logs tab
```

### Health Check
```bash
curl -v http://localhost:7865/
curl -X POST http://localhost:7865/x -H "Content-Type: application/json" \
  -d '{"a":"base64encodedaudio"}'
```

### Common Issues

#### 1. FFmpeg Not Found
```bash
# Fix: Install FFmpeg
sudo apt-get install ffmpeg  # Linux
brew install ffmpeg          # macOS
```

#### 2. Out of Memory
```bash
# Solution: Use smaller model
WHISPER_MODEL_SIZE=tiny
```

#### 3. Slow Response
```bash
# Solution: Increase CPU threads
WHISPER_CPU_THREADS=8
```

#### 4. Port Already in Use
```bash
# Fix: Use different port
python main.py --port 8000
```

### Performance Monitoring

Check transcription time in logs:
```
total=5.2s [audio=0.3s + whisper=4.5s + correct=0.4s]
```

- **audio**: FFmpeg preprocessing
- **whisper**: Model inference
- **correct**: Text correction

---

## Security Considerations

### Production Checklist
- [ ] Set `LOG_LEVEL=INFO` (not DEBUG)
- [ ] Use HTTPS with reverse proxy (nginx/CloudFlare)
- [ ] Implement rate limiting
- [ ] Enable security headers (Content-Security-Policy, etc.)
- [ ] Run as non-root user (already in Docker)
- [ ] Regular security updates: `pip install --upgrade -r requirements.txt`
- [ ] Scan for vulnerabilities: `pip install safety && safety check`

### CORS Configuration
Edit `ui/app.py` to whitelist only trusted origins:
```python
ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]
```

---

## Maintenance

### Regular Updates
```bash
pip install --upgrade -r requirements.txt
git pull origin main
docker build -t speech-to-text:latest .
```

### Backup
- Backup configurations and environment variables
- Document any custom modifications
- Version control all changes

### Logs & Monitoring
- Retain logs for at least 30 days
- Monitor transcription performance trends
- Alert on error rates > 5%

---

## Support & Troubleshooting

For issues:
1. Check logs for error messages
2. Verify FFmpeg installation: `ffmpeg -version`
3. Test locally before cloud deployment
4. Check hardware resources: `free -h`, `df -h`
5. Review configuration: `echo $WHISPER_MODEL_SIZE`

---

## References
- Faster-Whisper: https://github.com/SYSTRAN/faster-whisper
- Flask: https://flask.palletsprojects.com/
- Docker: https://docs.docker.com/
- Render.com: https://render.com/docs
