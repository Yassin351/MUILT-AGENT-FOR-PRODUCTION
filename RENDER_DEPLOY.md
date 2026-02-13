# 🚀 Render Deployment Guide

## Quick Deploy to Render

### Step 1: Prepare Repository
```bash
# Make sure these files exist:
# - chat_ui_pro.py
# - requirements_render.txt
# - render.yaml
# - core/safety.py
# - tools/tax_tool.py
```

### Step 2: Push to GitHub
```bash
git init
git add .
git commit -m "Deploy to Render"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 3: Deploy on Render

1. Go to https://render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect `render.yaml`
5. Add environment variable:
   - Key: `GOOGLE_API_KEY`
   - Value: Your Gemini API key
6. Click "Create Web Service"

### Step 4: Wait for Deployment
- Build time: ~5 minutes
- Your app will be live at: `https://kenya-procurement-ai.onrender.com`

## Configuration

### render.yaml
```yaml
services:
  - type: web
    name: kenya-procurement-ai
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements_render.txt
    startCommand: python chat_ui_pro.py
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: GOOGLE_API_KEY
        sync: false
```

### requirements_render.txt
Optimized dependencies for fast deployment:
- gradio (UI framework)
- requests (HTTP)
- beautifulsoup4 (Web scraping)
- python-dotenv (Environment variables)
- pydantic (Data validation)
- tenacity (Retry logic)
- lxml (HTML parsing)
- loguru (Logging)
- structlog (Structured logging)
- uvicorn (ASGI server)
- gunicorn (Production server)

## Performance Optimization

### Fast Startup
- Minimal dependencies (11 packages vs 26)
- No heavy ML libraries (Prophet, Matplotlib removed)
- Lightweight scraping only

### Speed Features
- Async HTTP requests
- Image caching from Unsplash
- Efficient HTML parsing
- No database overhead

## Troubleshooting

### Build Fails
```bash
# Check Python version
PYTHON_VERSION=3.11.0

# Verify requirements
pip install -r requirements_render.txt
```

### App Won't Start
```bash
# Test locally first
python chat_ui_pro.py

# Check PORT variable
PORT=10000 python chat_ui_pro.py
```

### Slow Performance
- Free tier has cold starts (~30 seconds)
- Upgrade to paid tier for always-on
- Images load from CDN (fast)

## Environment Variables

Required:
- `GOOGLE_API_KEY` - Your Gemini API key

Optional:
- `PORT` - Auto-set by Render
- `PYTHON_VERSION` - Set to 3.11.0

## Post-Deployment

### Test Your App
1. Visit: `https://your-app.onrender.com`
2. Type: "Samsung Galaxy A54"
3. Verify:
   - Image loads
   - Price shows
   - Links work

### Monitor
- Render Dashboard → Logs
- Check for errors
- Monitor response times

## Free Tier Limits

- 750 hours/month
- Sleeps after 15 min inactivity
- Cold start: ~30 seconds
- Bandwidth: 100 GB/month

## Upgrade Options

**Starter Plan ($7/month):**
- Always on (no sleep)
- Faster cold starts
- More bandwidth

## Success Checklist

- [ ] GitHub repo created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] GOOGLE_API_KEY added
- [ ] Deployment successful
- [ ] App accessible online
- [ ] Features working (images, prices, links)

## Your Live URL

After deployment: `https://kenya-procurement-ai.onrender.com`

Share this link for your presentation! 🎉
