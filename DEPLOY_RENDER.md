### Deployment Guide: Render (Free)

**Render offers a free tier** with 750 hours/month (enough for continuous hosting).

#### Quick Deploy Steps:

1. **Push to GitHub** (if not already):
   ```bash
   git add .
   git commit -m "Add Docker deployment config"
   git push origin main
   ```

2. **Go to [Render Dashboard](https://dashboard.render.com)**:
   - Sign up/login with GitHub
   - Click **"New +"** → **"Web Service"**
   - Connect your `Intelligent-Course-Creator` repository

3. **Configure Service**:
   - **Name**: `intelligent-course-creator`
   - **Runtime**: Docker
   - **Region**: Oregon (or closest to you)
   - **Instance Type**: Free
   - **Auto-Deploy**: Yes

4. **Add Environment Variable**:
   - In the dashboard, go to **Environment** tab
   - Add: `GEMINI_API_KEY` = `your-actual-api-key`

5. **Deploy**:
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for first build
   - Your app will be live at: `https://intelligent-course-creator.onrender.com`

#### Notes:
- Free tier spins down after 15 mins of inactivity (first request takes ~30s to wake up)
- No schema introspection issues - runs standard Docker container
- Automatic SSL certificate included

---

### Alternative: Railway (Free Trial)

Railway gives $5 free credit (good for ~1 month of light usage):

1. **Go to [Railway.app](https://railway.app)**
2. Click **"Start a New Project"** → **"Deploy from GitHub repo"**
3. Select your repo
4. Railway auto-detects Dockerfile
5. Add `GEMINI_API_KEY` in Variables tab
6. Deploy completes in ~5 mins

**Railway advantages**:
- Faster cold starts (no spin-down delay)
- Better free tier performance
- Disadvantage: Only $5 trial credit (not truly free forever)

---

### Recommendation:
Use **Render** for free hosting. If you need faster response times and don't mind paying ~$5/month after trial, use **Railway**.
