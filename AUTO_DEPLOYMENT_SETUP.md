# Auto-Deployment Setup Guide

Complete guide to set up automatic deployment for Render (Backend) and Netlify (Frontend).

## Architecture Overview

```
GitHub Repository
       ↓ (push to main)
GitHub Actions Workflow
  ├─ Run Tests
  ├─ Deploy Backend → Render
  └─ Deploy Frontend → Netlify
       ↓
Live Application
  Frontend: https://your-site.netlify.app
  Backend: https://speech-to-text-api.onrender.com
```

## Prerequisites

✓ GitHub repository (https://github.com/Ram-kumar-S-18/speech-to-text-app)
✓ Render account with backend service created
✓ Netlify account with frontend site created
✓ All files committed to `main` branch

## Setup Steps

### 1. Create Render Backend Service

**If not already created:**

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect GitHub repository
4. Configure:
   - **Name**: `speech-to-text-backend`
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --workers 2 --worker-class sync --timeout 120 --bind 0.0.0.0:$PORT wsgi:app`
   - **Environment**: Python
   - **Plan**: Standard

5. Set Environment Variables (in Render Dashboard):
   ```
   WHISPER_MODEL_SIZE=base
   LOG_LEVEL=INFO
   WHISPER_CPU_THREADS=4
   OMP_NUM_THREADS=4
   PYTHON_VERSION=3.11
   PYTHONUNBUFFERED=1
   ```

6. Note your service details:
   - Service ID: Look in URL: `https://dashboard.render.com/web/srv-xxxxx`
   - Public URL: Something like `https://speech-to-text-api-xxxxx.onrender.com`

### 2. Create Netlify Frontend Site

**If not already created:**

1. Go to https://app.netlify.com
2. Click "Add new site" → "Import an existing project"
3. Connect GitHub repository
4. Configure:
   - **Build Command**: `python build_static.py`
   - **Publish Directory**: `dist`

5. Set Environment Variables (in Netlify):
   - Go to **Site Settings** → **Build & Deploy** → **Environment**
   - Add:
     ```
     REACT_APP_API_URL = https://your-backend.onrender.com
     PYTHON_VERSION = 3.11
     ```

6. Note your site details:
   - Site ID: From **Site Settings** → **General** → **Site ID**
   - Public URL: Something like `https://your-site.netlify.app`

### 3. Configure GitHub Actions Secrets

1. Go to GitHub Repository Settings
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add these 4 secrets:

**Secret 1: RENDER_API_KEY**
- Get from: Render Dashboard → Account Settings → API Keys
- Click "Create API Key"
- Secret name: `RENDER_API_KEY`
- Secret value: Paste the API key

**Secret 2: RENDER_SERVICE_ID**
- Get from: Service URL on Render dashboard (srv-xxxxx)
- Secret name: `RENDER_SERVICE_ID`
- Secret value: Your service ID

**Secret 3: NETLIFY_AUTH_TOKEN**
- Get from: Netlify → User Settings → Applications → Personal access tokens
- Click "New access token"
- Scope: All
- Secret name: `NETLIFY_AUTH_TOKEN`
- Secret value: Paste the token

**Secret 4: NETLIFY_SITE_ID**
- Get from: Netlify → Site Settings → General → Site ID
- Secret name: `NETLIFY_SITE_ID`
- Secret value: Paste the site ID

### 4. Update Render Backend URL

Update the frontend to point to your actual Render backend:

**Option A: Update netlify.toml**
```toml
[[redirects]]
  from = "/x"
  to = "https://your-actual-backend.onrender.com/x"
  status = 200
  force = true
```

**Option B: The config.js auto-detects automatically**
- If deployed on netlify.app, it uses Render backend
- If local (localhost), it uses local backend
- If deployed elsewhere, it uses same origin

### 5. Verify Workflow File

The workflow file `.github/workflows/deploy.yml` should be present.

If not, create it with content from `GITHUB_ACTIONS_SETUP.md`.

### 6. Test the Setup

1. Make a small change:
   ```bash
   echo "# Test deployment" >> README.md
   git add README.md
   git commit -m "test: CI/CD trigger [skip ci]"
   git push origin main
   ```

2. Go to GitHub → Actions tab
3. Watch the workflow run
4. Check Render and Netlify dashboards for deployments

## Expected Workflow

### When you push to main:

```
1. GitHub detects push to main
   ↓
2. GitHub Actions starts
   - Checkout code
   - Install dependencies
   - Run linters
   - Check configuration
   - Build frontend
   ↓
3. If tests pass:
   - Trigger Render deployment
   - Deploy to Netlify
   ↓
4. Wait for both to complete
   - Render: 2-5 minutes (first run longer with model download)
   - Netlify: 1-2 minutes
   ↓
5. Both services updated
   - Backend running with new code
   - Frontend running with new build
```

## Automatic Deployments

### What Triggers Deployment:

✓ Push to `main` branch  
✓ Pull request (tests only, no deployment)  
✓ Manual trigger (if configured)

### What Does NOT Trigger Deployment:

✗ Push to other branches  
✗ Commit message with `[skip ci]`  
✗ Changes to documentation only (if configured)

## Checking Deployment Status

### GitHub Actions:
1. Repository → Actions tab
2. Click latest run
3. See all jobs (test, deploy-backend, deploy-frontend)

### Render:
1. Dashboard → Your Service
2. Click "Logs" tab
3. See real-time deployment logs

### Netlify:
1. Dashboard → Your Site
2. Click "Deploys" tab
3. See deployment history and logs

## Monitoring

### Set Up Notifications:

**GitHub Email Notifications:**
- Settings → Notifications → Workflow runs

**Netlify Notifications:**
- Site Settings → Notifications → Deploy notifications

**Render Notifications:**
- Account Settings → Notifications

## Troubleshooting

### Deployment Stuck

**Check:**
1. GitHub Actions log for errors
2. Render deployment log
3. Netlify deployment log

**Fix:**
- Cancel and retry
- Check secrets are correct
- Verify code has no syntax errors

### Backend Not Responding

**Check:**
1. Render service status (red/green indicator)
2. View Render logs for startup errors
3. Check environment variables are set

**Common Issues:**
- Model download taking too long (normal on first deploy)
- Python version mismatch
- Missing dependencies

### Frontend Shows Old Version

**Fix:**
1. Netlify: Hard refresh (Ctrl+Shift+R)
2. Clear browser cache
3. Check Netlify deployment completed
4. Trigger manual redeploy

### API Connection Fails

**Check:**
1. Backend URL in config.js is correct
2. Render service is running (check /x endpoint)
3. CORS headers configured correctly
4. CSP header allows backend domain

## Environment-Specific Configuration

### Production (main branch):
- Backend: https://speech-to-text-api.onrender.com
- Frontend: https://your-site.netlify.app
- Model: base (balanced)

### Staging (if added):
- Backend: https://speech-to-text-staging.onrender.com
- Frontend: https://your-site-staging.netlify.app
- Model: tiny (fast testing)

### Local Development:
- Backend: http://localhost:7865
- Frontend: http://localhost (served locally)
- Model: tiny (fast iteration)

## Quick Commands

```bash
# Test locally
python build_static.py    # Build frontend
python main.py --model tiny  # Start backend

# Check deployment
git log --oneline -1      # See latest commit
git status                # Verify everything committed

# Trigger redeploy (on Render)
# Dashboard → Service → Logs → "Deploy latest commit"

# Trigger redeploy (on Netlify)
# Dashboard → Deploys → "Trigger deploy" → "Deploy site"
```

## Performance Tips

### For Render Backend:
- Use `base` model for production
- Use `tiny` for testing/development
- Monitor logs for slow requests
- Check CPU usage in Render dashboard

### For Netlify Frontend:
- Assets are cached globally
- Minimal latency from CDN
- Monitor for 404 errors (missing files)

### For GitHub Actions:
- Tests should complete in < 2 minutes
- Cache Python dependencies for speed
- Parallel jobs run faster

## Next Steps

1. ✓ Workflow file exists (.github/workflows/deploy.yml)
2. Add GitHub secrets (4 secrets as above)
3. Test with a small commit
4. Monitor both Render and Netlify dashboards
5. Verify end-to-end (frontend → backend → transcription)

## Support Resources

- **GitHub Actions**: https://docs.github.com/actions
- **Render Docs**: https://render.com/docs
- **Netlify Docs**: https://docs.netlify.com/
- **Deployment Guide**: See DEPLOYMENT.md

---

**Your CI/CD pipeline is now ready!**

Every push to main will automatically:
1. Run tests
2. Deploy backend to Render
3. Deploy frontend to Netlify

No manual intervention needed! 🚀
