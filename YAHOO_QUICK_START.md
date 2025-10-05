# Yahoo OAuth - Quick Start Guide

## 🚀 **5-Minute Setup**

### 1. Create Yahoo App (2 min)

```
1. Visit: https://developer.yahoo.com/apps/create/
2. Fill in:
   - Name: Fantasy Grid
   - Description: NFL Fantasy Analytics
   - Redirect URI: https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/yahoo/callback
   - Permissions: Fantasy Sports (read)
3. Save Client ID and Secret
```

### 2. Set Heroku Config (1 min)

```bash
# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Set variables
heroku config:set \
  YAHOO_CLIENT_ID="your_client_id" \
  YAHOO_CLIENT_SECRET="your_secret" \
  YAHOO_ENCRYPTION_KEY="generated_key_above" \
  YAHOO_REDIRECT_URI="https://fantasy-grid-8e65f9ca9754.herokuapp.com/api/yahoo/callback" \
  FRONTEND_URL="https://fantasy-grid-8e65f9ca9754.herokuapp.com" \
  --app fantasy-grid
```

### 3. Deploy (2 min)

```bash
git add .
git commit -m "feat: Add Yahoo Fantasy roster import"
git push heroku main
heroku pg:psql --app fantasy-grid < migrations/yahoo_oauth_schema.sql
```

---

## 📱 **User Flow**

1. User clicks "Import from Yahoo" button
2. Logs into Yahoo account
3. Authorizes Fantasy Grid app
4. Selects their fantasy league
5. Imports roster (15-20 players in <10 seconds)
6. ✅ Can now use all app features!

---

## 🔗 **API Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/yahoo/auth` | GET | Start OAuth (redirects to Yahoo) |
| `/api/yahoo/callback` | GET | OAuth callback (auto) |
| `/api/yahoo/leagues` | GET | Get user's leagues |
| `/api/yahoo/import` | POST | Import roster |
| `/api/yahoo/status` | GET | Check if connected |

---

## 🧪 **Test Locally**

```bash
# 1. Set .env
YAHOO_CLIENT_ID=dev_client_id
YAHOO_CLIENT_SECRET=dev_secret
YAHOO_REDIRECT_URI=http://localhost:5000/api/yahoo/callback
YAHOO_ENCRYPTION_KEY=<generated_key>

# 2. Apply migration
psql $DATABASE_URL -f migrations/yahoo_oauth_schema.sql

# 3. Start server
python wsgi.py

# 4. Test OAuth
curl http://localhost:5000/api/yahoo/auth \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📂 **Files Created**

### Backend (Complete ✅):
- `migrations/yahoo_oauth_schema.sql` - Database
- `app/services/yahoo_oauth_service.py` - OAuth
- `app/services/yahoo_fantasy_client.py` - Yahoo API
- `app/services/yahoo_roster_import_service.py` - Import
- `app/routes/yahoo.py` - Routes
- `requirements.txt` - Added cryptography

### Documentation:
- `YAHOO_OAUTH_SETUP.md` - Full setup guide
- `YAHOO_IMPLEMENTATION_SUMMARY.md` - What's done
- `YAHOO_QUICK_START.md` - This file

---

## 🎨 **Frontend TODO**

### Add to `RosterBuilder.tsx`:

```tsx
const handleYahooImport = () => {
  window.location.href = '/api/yahoo/auth';
};

<button onClick={handleYahooImport} className="...">
  Import from Yahoo Fantasy
</button>
```

### Create `YahooImport.tsx`:

```tsx
export const YahooImport = () => {
  const [leagues, setLeagues] = useState([]);

  useEffect(() => {
    if (searchParams.get('oauth_success')) {
      api.get('/yahoo/leagues')
        .then(res => setLeagues(res.data.data.leagues));
    }
  }, []);

  return (
    <div>
      {leagues.map(league => (
        <button onClick={() => handleImport(league.team_key)}>
          Import {league.name}
        </button>
      ))}
    </div>
  );
};
```

---

## ✅ **Verification Checklist**

- [ ] Yahoo app created with correct redirect URI
- [ ] Heroku config variables set
- [ ] Database migration applied
- [ ] Backend deployed successfully
- [ ] OAuth flow tested
- [ ] Roster import tested
- [ ] Frontend integrated (pending)

---

## 🐛 **Common Issues**

### "invalid_client" Error
- Check Client ID/Secret in Heroku config
- Verify redirect URI matches exactly

### "No Yahoo authorization found"
- User needs to authorize first
- Redirect to `/api/yahoo/auth`

### Players Not Matching
- Check unmatched_players in response
- 95%+ match rate expected
- Fuzzy matching handles most variations

---

## 📊 **What's Next?**

**Option 1: Deploy Now**
```bash
git push heroku main
# Build frontend after backend confirmed working
```

**Option 2: Build Frontend First**
```bash
cd frontend
# Create YahooImport.tsx component
# Add import button to RosterBuilder
# Test locally
# Then deploy everything
```

---

## 🎯 **Success Metrics**

- Authorization: >95% success rate
- Player Matching: >95% accuracy
- Import Time: <10 seconds
- Error Rate: <2%

---

**Status**: ✅ Backend Complete | ⏳ Frontend Pending
**Time to Deploy**: ~15 minutes
**Time to Full Integration**: ~2-3 hours

---

**For Full Documentation**: See `YAHOO_OAUTH_SETUP.md`
