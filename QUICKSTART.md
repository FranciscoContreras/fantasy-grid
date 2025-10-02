# 🚀 QUICKSTART - API v2

**Ready to launch in 2 commands!**

---

## ⚡ Launch Now

### Step 1: Backend (Terminal 1)

```bash
./launch-v2.sh
```

Expected output:
```
✅ API_VERSION=v2 configured
✅ Python found: Python 3.13.7
✅ Dependencies already installed
FantasyAPIClient initialized with API v2
* Running on http://0.0.0.0:5000
```

### Step 2: Frontend (Terminal 2)

```bash
./launch-frontend.sh
```

Expected output:
```
✅ Node.js found
✅ Dependencies already installed
VITE ready in X ms
➜ Local: http://localhost:5173
```

### Step 3: Open Browser

**http://localhost:5173**

---

## 🚨 Common Issues

### "Port 5000 already in use"

**Fix:**
```bash
lsof -ti:5000 | xargs kill -9
```

Or disable AirPlay Receiver:
- System Preferences → General → AirDrop & Handoff → AirPlay Receiver → **Off**

---

## ✅ Verify It's Working

### 1. Check Backend Health

```bash
curl http://localhost:5000/health | python3 -m json.tool
```

Should return:
```json
{
  "status": "healthy",
  "api_version": "v2",
  "timestamp": "2025-10-02T..."
}
```

### 2. Test API v2 Endpoint

```bash
curl "http://localhost:5000/api/advanced/standings?season=2024" | python3 -m json.tool
```

Should return NFL standings data.

### 3. Check Frontend

1. Open http://localhost:5173
2. Register/Login (or skip if no database)
3. Search for "Mahomes"
4. Click player card
5. Scroll down - see **"Advanced Stats (Next Gen Stats)"** panel

---

## 📊 What You Have

✅ **Next Gen Stats** - CPOE, EPA, separation, YAC, WOPR
✅ **AI Predictions** - Claude-powered analysis
✅ **Play-by-Play** - EPA/WPA tracking
✅ **Defense Rankings** - Advanced metrics
✅ **Natural Language** - Ask questions in plain English

---

## 🎯 Quick Test

Search for any NFL player and you'll see:

**QB Stats:**
- Completion % Over Expected (CPOE)
- EPA per play
- Time to throw
- Success rate

**WR/TE Stats:**
- Average separation
- Yards after catch
- Target share
- WOPR (opportunity rating)

**RB Stats:**
- Yards over expected
- Snap share
- Success rate
- EPA contributions

---

## 📚 More Info

- **READY_TO_LAUNCH.md** - Complete launch guide
- **DEPLOYMENT_VERIFIED.md** - Testing verification
- **DATABASE_SETUP.md** - Optional database setup
- **API_V2_MIGRATION_GUIDE.md** - Full documentation

---

## 💡 Tips

**Works without database!**
- Basic features work in API-only mode
- Set up database later for full features

**API Keys (Optional):**
- Add `API_KEY` to `.env` for AI features
- Add `GROQ_API_KEY` for additional AI capabilities

**Environment:**
```bash
# Your .env file
API_VERSION=v2  # ✅ Already set!
DATABASE_URL=<optional>
API_KEY=<optional>
GROQ_API_KEY=<optional>
```

---

## 🎉 You're Ready!

Run the two launch commands and start using your NFL-grade analytics app!

**Questions?** Check the documentation files or review the logs.

---

**Happy analyzing!** 🏈📊✨
