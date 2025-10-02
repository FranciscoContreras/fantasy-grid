# Database Setup Guide

You have three options for setting up the PostgreSQL database for API v2:

---

## Option 1: Use Heroku PostgreSQL (Recommended - Already Deployed)

If you already have a Heroku app deployed, you likely already have a database:

```bash
# Check if you have Heroku app
heroku apps

# Check database addons
heroku addons --app YOUR_APP_NAME

# Apply v2 schema to Heroku database
heroku pg:psql --app YOUR_APP_NAME < schema_v2_updates.sql

# Verify tables created
heroku pg:psql --app YOUR_APP_NAME
\dt
# Should show the new tables: player_advanced_stats, play_by_play, etc.
```

---

## Option 2: Local PostgreSQL (For Development)

### Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Windows:**
Download from: https://www.postgresql.org/download/windows/

**Linux:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```

### Create Database

```bash
# Create database
createdb fantasy_grid

# Set environment variable in .env
echo "DATABASE_URL=postgresql://localhost/fantasy_grid" >> .env

# Apply base schema
psql fantasy_grid < schema.sql

# Apply v2 schema
psql fantasy_grid < schema_v2_updates.sql

# Verify
psql fantasy_grid -c "\dt"
```

---

## Option 3: Skip Database for Now (API-Only Mode)

The app can run without a local database - it will just use the external API:

```bash
# Just start the backend
python wsgi.py

# The app will work but won't cache data locally
# Advanced stats will still be fetched from Grid Iron Mind API v2
```

**Note:** Some features require database:
- User authentication/rosters (uses `users`, `rosters` tables)
- Cached advanced stats (uses `player_advanced_stats` table)
- Matchup analysis history (uses `matchup_analysis` table)

But basic player search and analysis will work without database!

---

## Quick Test: Which Option Should I Use?

### Use Option 1 (Heroku) if:
- ✅ You already deployed to Heroku
- ✅ You want to test in production
- ✅ You have `heroku` CLI installed

### Use Option 2 (Local) if:
- ✅ You want to develop locally
- ✅ You have PostgreSQL installed (or can install it)
- ✅ You want full feature testing

### Use Option 3 (Skip) if:
- ✅ You just want to test the API integration quickly
- ✅ You don't need user authentication yet
- ✅ You're okay with not caching data

---

## Current Status

Based on your `.env` file, you currently don't have `DATABASE_URL` set.

**Recommended Next Steps:**

1. **If you have Heroku already:**
   ```bash
   # Apply schema to production
   heroku pg:psql --app YOUR_APP_NAME < schema_v2_updates.sql
   ```

2. **If you want local development:**
   ```bash
   # Install PostgreSQL (if not installed)
   brew install postgresql@15  # macOS

   # Create database
   createdb fantasy_grid

   # Add to .env
   echo "DATABASE_URL=postgresql://localhost/fantasy_grid" >> .env

   # Apply schemas
   psql fantasy_grid < schema.sql
   psql fantasy_grid < schema_v2_updates.sql
   ```

3. **If you want to skip database for now:**
   Just start the backend and it will work in API-only mode!

---

## Environment Variables After Setup

Your `.env` should have:

```bash
# API v2 Configuration
API_VERSION=v2

# Database (if using local PostgreSQL)
DATABASE_URL=postgresql://localhost/fantasy_grid

# OR for Heroku (automatically set)
DATABASE_URL=postgres://...heroku.com/...

# API Keys (optional, for AI features)
API_KEY=your-grid-iron-mind-key
GROQ_API_KEY=your-groq-key
```

---

## Testing Database Connection

```bash
# If local PostgreSQL
psql $DATABASE_URL -c "SELECT version();"

# If Heroku
heroku pg:psql --app YOUR_APP_NAME -c "SELECT version();"
```

---

## I'll Continue With...

Since you don't have a local database yet, I'll proceed to test the backend server startup in API-only mode, which will still work for testing the API v2 integration!
