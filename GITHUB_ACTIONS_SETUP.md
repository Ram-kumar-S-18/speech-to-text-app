# GitHub Actions CI/CD Setup Guide

This guide explains how to set up automatic deployment to Render and Netlify using GitHub Actions.

## Overview

The workflow automatically:
1. Runs tests on every push and pull request
2. Deploys backend to Render on successful tests
3. Deploys frontend to Netlify on successful tests
4. Notifies of deployment status

## Prerequisites

- [ ] GitHub repository with code pushed to `main` branch
- [ ] Render account with backend service created
- [ ] Netlify account with frontend site created
- [ ] GitHub API access (automatic)

## Step 1: Get Required Credentials

### Render API Key & Service ID

1. Go to https://dashboard.render.com
2. Click your profile → Account Settings
3. Scroll to "API Keys"
4. Click "Create API Key"
5. Copy and save the key somewhere safe
6. Note your Service ID:
   - Dashboard → Your Service → Settings
   - Look for URL like: `https://dashboard.render.com/web/srv-xxxxx`
   - Service ID is the `srv-xxxxx` part

### Netlify Auth Token & Site ID

1. Go to https://app.netlify.com
2. Click your profile (top right) → User settings
3. Go to Applications → Personal access tokens
4. Click "New access token"
5. Name it "GitHub Actions"
6. Generate and copy the token
7. For Site ID:
   - Dashboard → Site settings → General
   - Look for "Site ID" (looks like `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

## Step 2: Add GitHub Secrets

1. Go to your GitHub repository
2. Click Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add each secret:

### Secret 1: RENDER_API_KEY
- Name: `RENDER_API_KEY`
- Value: Paste your Render API key

### Secret 2: RENDER_SERVICE_ID
- Name: `RENDER_SERVICE_ID`
- Value: Paste your Render Service ID (srv-xxxxx)

### Secret 3: NETLIFY_AUTH_TOKEN
- Name: `NETLIFY_AUTH_TOKEN`
- Value: Paste your Netlify auth token

### Secret 4: NETLIFY_SITE_ID
- Name: `NETLIFY_SITE_ID`
- Value: Paste your Netlify Site ID

## Step 3: Verify Workflow File

The workflow file is already in your repository:
```
.github/workflows/deploy.yml
```

This file:
- Runs on every push to `main` and pull requests
- Tests code with Python 3.11
- Validates all imports and configurations
- Builds frontend with `python build_static.py`
- Deploys backend to Render
- Deploys frontend to Netlify

## Step 4: Test the Workflow

1. Make a small change to your code
2. Commit and push to `main`:
   ```bash
   git add .
   git commit -m "test: CI/CD workflow"
   git push origin main
   ```
3. Go to GitHub → Actions tab
4. Watch the workflow run
5. Click on the run to see details

### Expected Flow:

```
✓ test (always runs)
  ├─ Checkout code
  ├─ Set up Python
  ├─ Install dependencies
  ├─ Lint code
  ├─ Check configuration
  └─ Verify build_static.py

✓ deploy-backend (if push to main and tests pass)
  ├─ Trigger Render deployment
  └─ Log status

✓ deploy-frontend (if push to main and tests pass)
  ├─ Build with python build_static.py
  └─ Deploy to Netlify

✓ status (final status check)
```

## Step 5: Monitor Deployments

### Watch GitHub Actions:
1. Go to repository → Actions tab
2. Click latest workflow run
3. See detailed logs for each step
4. Green checkmark = success, Red X = failure

### Watch Render Deployment:
1. Go to Render Dashboard
2. Click your service
3. See deployment logs in real-time
4. Check if build succeeded

### Watch Netlify Deployment:
1. Go to Netlify Dashboard
2. Click your site
3. Go to Deploys tab
4. See deployment status and logs
5. Preview link available

## Troubleshooting

### Workflow Not Running

**Problem**: Actions tab is empty
- Solution: Ensure workflow file exists at `.github/workflows/deploy.yml`
- Solution: Check file is committed and pushed
- Solution: Repository Actions might be disabled (Settings → Actions)

### Deployment Fails with "Invalid secret"

**Problem**: GitHub Actions shows error about secrets
- Solution: Verify all 4 secrets are added correctly
- Solution: Check secret names exactly match workflow file
- Solution: Make sure no extra spaces or newlines in values

### Test Fails

**Problem**: "✗ Lint with flake8" fails
- Solution: Fix Python syntax errors locally first
- Solution: Run `flake8 .` locally to see issues

**Problem**: "✗ Check configuration" fails
- Solution: Ensure all imports work: `python -c "import config"`
- Solution: Check requirements.txt has all dependencies

**Problem**: "✗ Verify build_static.py" fails
- Solution: Run locally: `python build_static.py`
- Solution: Check ui/templates/index.html exists
- Solution: Check ui/static/ directory exists

### Render Deployment Fails

**Problem**: "Deploy to Render" returns error
- Solution: Verify RENDER_API_KEY is correct
- Solution: Verify RENDER_SERVICE_ID is correct (srv-xxxxx format)
- Solution: Check Render service exists and is connected to GitHub

**Problem**: Render build times out
- Solution: Check Render logs for actual errors
- Solution: Reduce model size: `WHISPER_MODEL_SIZE=tiny`

### Netlify Deployment Fails

**Problem**: "Deploy to Netlify" fails
- Solution: Verify NETLIFY_AUTH_TOKEN is correct
- Solution: Verify NETLIFY_SITE_ID is correct
- Solution: Check Netlify site is connected properly

**Problem**: Netlify build succeeds but site shows old version
- Solution: Clear Netlify cache and redeploy
- Solution: Check dist/ directory was built correctly

## Advanced Configuration

### Skip Deployment on Certain Commits

Add `[skip ci]` to commit message:
```bash
git commit -m "docs: Update README [skip ci]"
git push
```

### Deploy to Different Branches

Edit `.github/workflows/deploy.yml`:
```yaml
on:
  push:
    branches:
      - main
      - staging    # Add this line
```

### Add Email Notifications

Add to workflow file:
```yaml
- name: Send notification
  if: failure()
  run: echo "Deployment failed!"
```

### Deploy Only Backend or Frontend

Modify conditions in workflow:
```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main' && contains(github.event.head_commit.modified, 'requirements.txt')
```

## Environment-Specific Deployments

### Current Setup:
- **main branch** → Production (Render + Netlify)

### To Add Staging:
1. Create `staging` branch
2. Update workflow to deploy to staging on `staging` branch
3. Configure Render/Netlify staging services
4. Set different environment variables

## Checking Deployment Status

### Quick Check:
```bash
# Check GitHub workflow status
gh run list --branch main --limit 5

# Check recent commits
git log --oneline -n 5

# Check if main is up to date
git status
```

### Detailed Check:
1. GitHub Actions tab → Latest run → Workflow name
2. Each job shows (✓ or ✗)
3. Click job name for detailed logs
4. Look for errors or warnings

## Best Practices

1. **Always test locally first**:
   ```bash
   python build_static.py
   python main.py --model tiny
   ```

2. **Meaningful commit messages**:
   ```bash
   git commit -m "feat: Add new transcription feature"
   # ✓ Good: Describes what changed

   git commit -m "update"
   # ✗ Bad: Not descriptive
   ```

3. **Review GitHub Actions logs** before checking services
4. **Set up Slack/Email notifications** for failures
5. **Keep dependencies up to date**: `pip install --upgrade -r requirements.txt`
6. **Test pull requests** before merging to main

## Support

If deployment fails:

1. Check GitHub Actions logs first
2. Check Render deployment logs
3. Check Netlify deployment logs
4. Verify secrets are set correctly
5. Test commands locally

Common issues usually appear in logs with helpful error messages.

## Next Steps

1. ✓ Workflow file committed (already done)
2. Add GitHub secrets (see Step 2)
3. Make a test push to trigger workflow
4. Monitor deployment progress
5. Verify both services are updated

Your CI/CD pipeline is now ready! 🚀
