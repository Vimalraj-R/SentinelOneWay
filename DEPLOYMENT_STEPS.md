# 🚀 SentinelOneWay - FREE Deployment Guide

## Quick Deployment to Render + Vercel (100% Free)

Follow these steps exactly to deploy your application for free!

---

## ✅ STEP 1: Push to GitHub

### 1.1 Initialize Git (if not already done)

```bash
cd C:\Users\Vimalraj\SentinelOneWay

# Check if git is initialized
git status
```

If you see "fatal: not a git repository", run:
```bash
git init
```

### 1.2 Stage and Commit All Files

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit - Ready for deployment"
```

### 1.3 Create GitHub Repository

1. Go to: **https://github.com/new**
2. Fill in:
   - **Repository name:** `SentinelOneWay`
   - **Description:** "AI-powered Network Detection and Response System"
   - **Visibility:** Public (must be public for free Render)
   - **DON'T** check "Add a README" or any other files
3. Click **"Create repository"**

### 1.4 Push to GitHub

Copy the commands from GitHub (it will show you something like this):

```bash
git remote add origin https://github.com/YOUR-USERNAME/SentinelOneWay.git
git branch -M main
git push -u origin main
```

**Replace `YOUR-USERNAME` with your actual GitHub username!**

**✅ CHECKPOINT:** Your code is now on GitHub!

---

## ✅ STEP 2: Deploy Backend to Render

### 2.1 Sign Up for Render

1. Go to: **https://render.com/**
2. Click **"Get Started"**
3. Click **"Sign in with GitHub"**
4. Authorize Render to access your GitHub
5. You're now logged in! ✅

### 2.2 Create New Web Service

1. Click **"New +"** (top right)
2. Select **"Web Service"**
3. Click **"Build and deploy from a Git repository"**
4. Click **"Connect"** next to your `SentinelOneWay` repository
5. If you don't see it, click **"Configure account"** and grant access

### 2.3 Configure Backend Service

Fill in these settings **exactly**:

**Basic Settings:**
- **Name:** `sentineloneway-backend`
- **Region:** Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- Select **"Free"** plan ✅

### 2.4 Add Environment Variables

Scroll down to **"Environment Variables"** section:

Click **"Add Environment Variable"** and add these:

1. **Key:** `PYTHON_VERSION` → **Value:** `3.11`
2. **Key:** `DATABASE_URL` → **Value:** `sqlite:///./sentineloneway.db`
3. **Key:** `PYTHONUNBUFFERED` → **Value:** `1`

### 2.5 Deploy!

1. Click **"Create Web Service"** at the bottom
2. **Wait 5-10 minutes** for first deployment
3. You'll see logs scrolling - this is normal!
4. When you see **"Your service is live 🎉"**, it's ready!

### 2.6 Get Your Backend URL

1. At the top of the page, you'll see: `sentineloneway-backend.onrender.com`
2. **Copy this URL** - you'll need it for frontend!
3. Test it: Open `https://sentineloneway-backend.onrender.com/health`
4. You should see: `{"status":"healthy"}`

**✅ CHECKPOINT:** Backend is live!

**Your Backend URL:** `https://sentineloneway-backend.onrender.com`

---

## ✅ STEP 3: Deploy Frontend to Vercel

### 3.1 Sign Up for Vercel

1. Go to: **https://vercel.com/signup**
2. Click **"Continue with GitHub"**
3. Authorize Vercel
4. You're now logged in! ✅

### 3.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Find your **"SentinelOneWay"** repository
3. Click **"Import"**

### 3.3 Configure Frontend

Fill in these settings:

**Framework Preset:**
- Vercel should auto-detect **"Vite"** ✅

**Root Directory:**
- Click **"Edit"**
- Enter: `frontend`
- Click **"Continue"**

**Build Settings:** (should auto-fill, verify these)
- **Build Command:** `npm run build`
- **Output Directory:** `dist`
- **Install Command:** `npm install`

### 3.4 Add Environment Variable

This is **CRITICAL** - your frontend needs to know where your backend is!

1. Click **"Environment Variables"**
2. Add:
   - **Name:** `VITE_API_BASE_URL`
   - **Value:** `https://sentineloneway-backend.onrender.com`
   - (Use YOUR backend URL from Step 2.6)
3. Select: **Production, Preview, and Development**

### 3.5 Deploy!

1. Click **"Deploy"**
2. **Wait 2-3 minutes**
3. You'll see a confetti animation when done! 🎉
4. Click **"Continue to Dashboard"**

### 3.6 Get Your Frontend URL

1. You'll see: `https://sentinel-one-way.vercel.app` (or similar)
2. Click **"Visit"** to open your app!
3. **Copy this URL** - this is your live app!

**✅ CHECKPOINT:** Frontend is live!

**Your App URL:** `https://sentinel-one-way.vercel.app`

---

## ✅ STEP 4: Test Your Deployment

### 4.1 Test Backend

Open: `https://sentineloneway-backend.onrender.com/health`

**Should see:**
```json
{
  "status": "healthy",
  "service": "SentinelOneWay API",
  "version": "0.2.0"
}
```

### 4.2 Test Frontend

Open: `https://sentinel-one-way.vercel.app`

**Should see:**
- ✅ Overview page loads
- ✅ KPI cards show data
- ✅ No connection errors
- ✅ Green "LIVE" indicator

**⚠️ First Load Note:**
- Backend may take **30 seconds to wake up** on first request
- This is normal for Render's free tier
- After that, it stays awake for 15 minutes
- Refresh page if you see loading screen

### 4.3 Test Features

Navigate through all pages:
- ✅ Overview
- ✅ Live Traffic
- ✅ Threat Alerts (should show 15 alerts)
- ✅ Attack Timeline
- ✅ Assets
- ✅ Simulation Lab
- ✅ System Health

**All should work!** 🎉

---

## ✅ STEP 5: Update CORS (If Needed)

If you see CORS errors in browser console:

### 5.1 Update Backend CORS

Edit `backend/main.py` on GitHub:

1. Go to your GitHub repo
2. Open `backend/main.py`
3. Click the pencil icon to edit
4. Find the CORS section (around line 34)
5. Update to:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sentinel-one-way.vercel.app",  # Your Vercel URL
        "https://sentineloneway-backend.onrender.com",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

6. Commit changes
7. Render will auto-redeploy (takes 2-3 min)

---

## 🎉 SUCCESS! Your App is Live!

### Your URLs:

**Frontend (User Access):**
`https://sentinel-one-way.vercel.app`

**Backend API:**
`https://sentineloneway-backend.onrender.com`

**API Documentation:**
`https://sentineloneway-backend.onrender.com/docs`

---

## 📝 Important Notes

### Free Tier Limitations:

**Render (Backend):**
- ✅ 750 hours/month free
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ Takes ~30 sec to wake up
- ✅ Perfect for demos/portfolio

**Vercel (Frontend):**
- ✅ Unlimited bandwidth
- ✅ No sleep mode
- ✅ Fast global CDN
- ✅ 100% free forever

### How to Keep Backend Awake:

**Option 1: Use UptimeRobot (Free)**
1. Go to: https://uptimerobot.com
2. Create monitor for: `https://sentineloneway-backend.onrender.com/health`
3. Ping every 5 minutes
4. Backend stays awake 24/7!

**Option 2: Accept the wake-up delay**
- Users wait 30 sec on first visit
- Then it's fast for 15 minutes

---

## 🔄 How to Update Your App

### Update Backend:
```bash
cd C:\Users\Vimalraj\SentinelOneWay
git add .
git commit -m "Update backend"
git push origin main
```
Render auto-deploys in 3-5 minutes! ✅

### Update Frontend:
```bash
cd C:\Users\Vimalraj\SentinelOneWay
git add .
git commit -m "Update frontend"
git push origin main
```
Vercel auto-deploys in 1-2 minutes! ✅

---

## 🆘 Troubleshooting

### Backend won't start?
- Check Render logs for errors
- Verify `requirements.txt` has all dependencies
- Check Python version is 3.11

### Frontend shows connection error?
- Verify `VITE_API_BASE_URL` is set correctly
- Check backend is awake (visit health endpoint)
- Wait 30 seconds for backend to wake

### CORS errors?
- Update `allow_origins` in `backend/main.py`
- Add your Vercel URL to the list

---

## 🎯 Next Steps

1. **Share your app:** `https://sentinel-one-way.vercel.app`
2. **Add to portfolio**
3. **Add custom domain** (free on Vercel)
4. **Setup monitoring** with UptimeRobot

---

## ✅ Deployment Summary

| Item | URL | Status |
|------|-----|--------|
| **Live App** | `https://sentinel-one-way.vercel.app` | ✅ Free Forever |
| **Backend API** | `https://sentineloneway-backend.onrender.com` | ✅ Free (with sleep) |
| **API Docs** | `https://sentineloneway-backend.onrender.com/docs` | ✅ Public |
| **GitHub Repo** | `https://github.com/YOUR-USERNAME/SentinelOneWay` | ✅ Public |

**Total Monthly Cost: $0** 🎉

---

**Congratulations! Your SentinelOneWay MVP is now live on the internet!** 🚀
