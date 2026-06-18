# Deployment Environment Variables Guide

This document outlines all environment variables needed for Render and Netlify deployments.

## Render Backend Configuration

### Set these variables in Render Dashboard → Environment Variables

```
# Model Configuration
WHISPER_MODEL_SIZE=base              # Options: tiny, base, small, medium, large

# Server Configuration
PORT=10000                            # Render assigns this automatically
HOST=0.0.0.0
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR

# Audio Processing
SAMPLE_RATE=16000
AUDIO_CHANNELS=1
AUDIO_FORMAT=wav

# Performance Tuning
WHISPER_CPU_THREADS=4
OMP_NUM_THREADS=4

# Python Configuration
PYTHON_VERSION=3.11
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1

# Build Environment (optional)
PIP_NO_CACHE_DIR=1
PIP_DISABLE_PIP_VERSION_CHECK=1
```

### Environment Variable Descriptions

| Variable | Value | Purpose |
|----------|-------|---------|
| `WHISPER_MODEL_SIZE` | tiny/base/small/medium/large | Whisper model size (affects speed & accuracy) |
| `PORT` | 10000 | Backend API port (Render default) |
| `HOST` | 0.0.0.0 | Bind to all interfaces |
| `LOG_LEVEL` | INFO | Logging level for debugging |
| `WHISPER_CPU_THREADS` | 4 | CPU threads for inference |
| `OMP_NUM_THREADS` | 4 | OpenMP threads |
| `SAMPLE_RATE` | 16000 | Audio sample rate in Hz |
| `AUDIO_CHANNELS` | 1 | Mono audio (1) or Stereo (2) |
| `PYTHON_VERSION` | 3.11 | Python runtime version |

---

## Netlify Frontend Configuration

### Set these in Netlify Dashboard → Site Settings → Build & Deploy → Environment

```
# API Configuration
REACT_APP_API_URL=https://speech-to-text-api.onrender.com

# Environment
REACT_APP_ENVIRONMENT=production

# Python Build Environment
PYTHON_VERSION=3.11
```

### Build Settings in Netlify

- **Build Command**: `python build_static.py`
- **Publish Directory**: `dist`
- **Node Version**: Not required (Python build)
- **Runtime**: Python 3.11

### Netlify Dashboard Configuration

1. Go to **Site Settings** → **Build & Deploy** → **Environment**
2. Add these Build variables:
   ```
   REACT_APP_API_URL = https://speech-to-text-api.onrender.com
   REACT_APP_ENVIRONMENT = production
   PYTHON_VERSION = 3.11
   ```

3. Ensure **Continuous Deployment** is enabled:
   - Go to **Deploys** → **Deploy Settings**
   - Click "Link site" or verify GitHub connection
   - Production branch: `main`
   - Auto publish enabled

---

## GitHub Secrets for CI/CD

Set these in GitHub Repo → Settings → Secrets and variables → Actions

### Render Secrets:
```
RENDER_SERVICE_ID      = srv-xxxxxxxxxxxxx  (your Render service ID)
RENDER_API_KEY         = xxxxxxxxxxxxxxxx   (your Render API key)
```

### Netlify Secrets:
```
NETLIFY_AUTH_TOKEN     = xxxxxxxxxxxxxxxx   (your Netlify auth token)
NETLIFY_SITE_ID        = xxxxxxxxxxxxxxxx   (your Netlify site ID)
```

### How to Get These Values:

#### Render:
1. Dashboard → Your Service → Settings
2. Copy Service ID (srv-...)
3. Account Settings → API Keys → Create key

#### Netlify:
1. User Settings → Applications → Personal access tokens
2. Create token with netlify-cli scope
3. Site Settings → General → Site ID

---

## Backend-Frontend Connection

### Current Setup:
- **Backend URL**: `https://speech-to-text-api.onrender.com`
- **Frontend URL**: `https://speech-to-text.netlify.app` (or your custom domain)

### Transcription Endpoint:
- Frontend sends audio to: `/x` endpoint
- Netlify redirects to: `https://speech-to-text-api.onrender.com/x`

### CORS Headers:
- Frontend can make requests to backend
- Backend allows requests from frontend domain
- Microphone permission: `microphone=(self)` in Permissions-Policy

---

## Deployment Workflow

### Automatic Deployments:

1. **Push to GitHub main branch**
   ↓
2. **GitHub Actions runs tests**
   ↓
3. **Tests pass → Deploy Backend to Render**
   ↓
4. **Tests pass → Deploy Frontend to Netlify**
   ↓
5. **Both services updated**

### Manual Testing:

```bash
# Test frontend locally
python build_static.py
# Open dist/index.html in browser

# Test backend locally
export $(cat .env | xargs)
python main.py --model tiny

# Test API endpoint
curl -X POST http://localhost:7865/x \
  -H "Content-Type: application/json" \
  -d '{"a":"base64_encoded_audio"}'
```

---

## Quick Setup Checklist

### Render Backend:
- [ ] Service created and connected to GitHub
- [ ] Environment variables set (see above)
- [ ] Dockerfile building successfully
- [ ] Health check passing: `/`
- [ ] Domain configured

### Netlify Frontend:
- [ ] Site connected to GitHub
- [ ] Build command: `python build_static.py`
- [ ] Publish directory: `dist`
- [ ] Environment variables set (see above)
- [ ] Build & deploy working

### GitHub Actions:
- [ ] Repository secrets set (Render & Netlify)
- [ ] Workflow file committed (.github/workflows/deploy.yml)
- [ ] Tests passing
- [ ] Auto-deployment enabled

### Connection:
- [ ] Frontend can reach backend API
- [ ] CORS headers configured correctly
- [ ] Transcription requests working end-to-end

---

## Troubleshooting

### Render Deployment Issues:

**Build fails**:
- Check logs: Render Dashboard → Logs
- Verify requirements.txt has all dependencies
- Ensure Python version is 3.11

**Timeout on /x endpoint**:
- Increase timeout in Procfile (currently 120s)
- Use smaller model (tiny/base instead of large)

**Out of memory**:
- Use smaller model: `WHISPER_MODEL_SIZE=tiny`
- Reduce `WHISPER_CPU_THREADS` to 2

### Netlify Deployment Issues:

**Build command fails**:
- Verify build_static.py works locally
- Check Python version: `python --version`
- Ensure ui/templates/index.html exists

**API calls failing**:
- Check REACT_APP_API_URL is correct
- Verify backend is running
- Check CORS headers in Render backend

**Stuck on "Building"**:
- Cancel and retry
- Check GitHub push completed
- Verify webhook is connected

### Connection Issues:

**Frontend can't reach backend**:
1. Check backend URL in netlify.toml
2. Verify Render service is running
3. Test with curl: `curl https://your-backend.onrender.com/`

**CORS errors**:
1. Check CSP header in netlify.toml
2. Verify Render domain is whitelisted
3. Test OPTIONS request

---

## Environment-Specific Configuration

### Development (Local):
```
REACT_APP_API_URL=http://localhost:7865
WHISPER_MODEL_SIZE=tiny
LOG_LEVEL=DEBUG
```

### Preview (Staging):
```
REACT_APP_API_URL=https://speech-to-text-api-staging.onrender.com
WHISPER_MODEL_SIZE=base
LOG_LEVEL=INFO
```

### Production:
```
REACT_APP_API_URL=https://speech-to-text-api.onrender.com
WHISPER_MODEL_SIZE=base
LOG_LEVEL=INFO
```

---

## Performance Recommendations

### For Render Backend:
- **Standard Plan** (2GB RAM) + `base` model = Good balance
- **Pro Plan** (4GB RAM) + `small` model = Better accuracy
- Set `WHISPER_CPU_THREADS=2` on smaller plans

### For Netlify Frontend:
- Static deployment (no compute)
- CDN-distributed globally
- Cache static assets aggressively

### Expected Performance:
- Frontend load: < 2s
- API request: 1-3s (with base model)
- Total: < 5s per transcription

---

## Next Steps

1. **Set Render variables**: Dashboard → Environment Variables
2. **Set Netlify variables**: Dashboard → Deploy → Environment
3. **Add GitHub secrets**: Repository Settings → Secrets
4. **Verify workflow**: Commit and push to see auto-deployment
5. **Test end-to-end**: Use the deployed application

For help, check the deployment logs in each platform's dashboard.
