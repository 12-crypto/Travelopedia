# 🚀 Deploy Travelopedia to Streamlit Cloud (FREE)

## Quick Deployment Guide - 5 Minutes!

### Step 1: Create GitHub Repository (2 minutes)

1. Go to [github.com/new](https://github.com/new)
2. Repository name: `Travelopedia`
3. Make it **Public** ✅
4. **Don't** check "Add README" (we already have one)
5. Click **"Create repository"**

### Step 2: Push Your Code (1 minute)

Open PowerShell in your project folder and run:

```powershell
cd "c:\Users\divya\Downloads\Travelopedia-main\Travelopedia-main"

git init
git add .
git commit -m "Deploy Travelopedia AI Travel Planner"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/Travelopedia.git
git push -u origin main
```

**Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username!**

### Step 3: Deploy on Streamlit Cloud (2 minutes)

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"Sign in with GitHub"**
3. Click **"New app"**
4. Fill in:
   - **Repository**: `YOUR_GITHUB_USERNAME/Travelopedia`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
5. Click **"Advanced settings"**
6. Set **Python version**: `3.9` or higher
7. Click **"Deploy"**

### Step 4: Add API Keys (1 minute)

After deployment starts:

1. Click **"⚙️ Settings"** in your app dashboard
2. Click **"Secrets"**
3. Paste this (replace with your actual keys):

```toml
SERPAPI_API_KEY = "your_serpapi_key_here"
OPENWEATHER_API_KEY = "your_openweather_key_here"
```

4. Click **"Save"**

---

## 🎉 Done!

Your app will be live at:
**`https://travelopedia.streamlit.app`**

(Or a similar URL if that name is taken)

---

## 📝 Notes:

- **Free Forever**: Streamlit Community Cloud is 100% free
- **Auto-Deploy**: Every time you push to GitHub, it auto-updates
- **Custom URL**: You can request a custom subdomain name
- **HTTPS**: Automatic SSL certificate included

---

## 🔑 Where to Get API Keys:

### SERPAPI (Required for flights/hotels)
1. Go to [serpapi.com](https://serpapi.com)
2. Sign up for free account
3. Get your API key from dashboard
4. Free tier: 100 searches/month

### OpenWeather (Optional for weather)
1. Go to [openweathermap.org/api](https://openweathermap.org/api)
2. Sign up for free account
3. Get your API key
4. Free tier: 1000 calls/day

---

## ❓ Troubleshooting:

**If deployment fails:**
- Check that `frontend/app.py` path is correct
- Ensure Python version is 3.9+
- Check that all dependencies are in `requirements.txt`

**If app crashes:**
- Check the logs in Streamlit Cloud dashboard
- Verify API keys are correctly added to Secrets

---

## 🔄 Update Your App:

To update your deployed app:

```powershell
git add .
git commit -m "Update description"
git push
```

Streamlit Cloud will automatically redeploy!

---

**Need help?** Check [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)
