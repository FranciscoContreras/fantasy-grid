# Fantasy Grid API Documentation

**Base URL**: `https://fantasy-grid-8e65f9ca9754.herokuapp.com`
**Version**: 1.0.0
**Last Updated**: October 2, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [Rosters](#rosters)
3. [Matchups](#matchups)
4. [Players](#players)
5. [Error Handling](#error-handling)
6. [Rate Limits](#rate-limits)

---

## Authentication

All roster, matchup, and user-specific endpoints require authentication via JWT tokens.

### Authentication Flow

1. Register a new user account OR login with existing credentials
2. Receive a JWT token in the response
3. Include the token in the `Authorization` header for all protected requests:
   ```
   Authorization: Bearer <your-jwt-token>
   ```

### Register New User

**Endpoint**: `POST /api/auth/register`

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "myusername",
  "password": "securepassword123",
  "first_name": "John",  // optional
  "last_name": "Doe"      // optional
}
```

**Validation Rules**:
- Email: Must be valid email format, max 255 characters
- Username: 3-100 characters, must be unique
- Password: Minimum 8 characters
- First/Last name: Max 100 characters (optional)

**Response** (201 Created):
```json
{
  "message": "User created successfully",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "myusername",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "created_at": "2025-10-02T10:30:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Errors**:
- `400`: User already exists, validation error
- `500`: Server error

---

### Login

**Endpoint**: `POST /api/auth/login`

**Request Body**:
```json
{
  "email_or_username": "user@example.com",  // or "myusername"
  "password": "securepassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "myusername",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "is_verified": false,
      "last_login_at": "2025-10-02T10:35:00Z"
    },
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

**Errors**:
- `401`: Invalid credentials
- `500`: Server error

---

### Get Current User

**Endpoint**: `GET /api/auth/me`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "data": {
    "id": 1,
    "email": "user@example.com",
    "username": "myusername",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "last_login_at": "2025-10-02T10:35:00Z"
  }
}
```

---

### Update User Profile

**Endpoint**: `PUT /api/auth/me`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (all fields optional):
```json
{
  "first_name": "Jane",
  "last_name": "Smith",
  "email": "newemail@example.com",
  "username": "newusername"
}
```

**Response** (200 OK):
```json
{
  "message": "User updated successfully",
  "data": {
    "id": 1,
    "email": "newemail@example.com",
    "username": "newusername",
    "first_name": "Jane",
    "last_name": "Smith",
    "updated_at": "2025-10-02T10:40:00Z"
  }
}
```

---

### Change Password

**Endpoint**: `POST /api/auth/change-password`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "old_password": "currentpassword",
  "new_password": "newsecurepassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Password changed successfully"
}
```

**Errors**:
- `400`: Invalid old password
- `401`: Unauthorized

---

### Verify Token

**Endpoint**: `POST /api/auth/verify-token`

**Request Body**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "message": "Token is valid",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "username": "myusername"
    }
  }
}
```

---

## Rosters

All roster endpoints require authentication.

### Get All Rosters

**Endpoint**: `GET /api/rosters`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "name": "My Championship Team",
      "league_name": "Friends League",
      "scoring_type": "PPR",
      "is_active": true,
      "created_at": "2025-10-01T12:00:00Z"
    }
  ],
  "count": 1
}
```

---

### Create Roster

**Endpoint**: `POST /api/rosters`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "name": "My Team",
  "league_name": "My League",  // optional
  "scoring_type": "PPR"  // optional: PPR, STANDARD, HALF_PPR (default: PPR)
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": 1,
    "user_id": 1,
    "name": "My Team",
    "league_name": "My League",
    "scoring_type": "PPR",
    "is_active": true,
    "created_at": "2025-10-02T11:00:00Z"
  }
}
```

---

### Get Roster Details

**Endpoint**: `GET /api/rosters/{roster_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "data": {
    "roster": {
      "id": 1,
      "user_id": 1,
      "name": "My Team",
      "league_name": "My League",
      "scoring_type": "PPR",
      "is_active": true
    },
    "players": [
      {
        "id": 1,
        "player_id": "12345",
        "player_name": "Patrick Mahomes",
        "position": "QB",
        "team": "KC",
        "roster_slot": "QB",
        "is_starter": true,
        "injury_status": "HEALTHY",
        "added_at": "2025-10-01T12:00:00Z"
      }
    ]
  }
}
```

**Errors**:
- `403`: Unauthorized (not your roster)
- `404`: Roster not found

---

### Update Roster

**Endpoint**: `PUT /api/rosters/{roster_id}`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (all fields optional):
```json
{
  "name": "Updated Team Name",
  "league_name": "New League",
  "scoring_type": "HALF_PPR",
  "is_active": false
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": 1,
    "name": "Updated Team Name",
    "league_name": "New League",
    "scoring_type": "HALF_PPR",
    "is_active": false,
    "updated_at": "2025-10-02T11:30:00Z"
  }
}
```

---

### Delete Roster

**Endpoint**: `DELETE /api/rosters/{roster_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Roster deleted successfully"
}
```

---

### Add Player to Roster

**Endpoint**: `POST /api/rosters/{roster_id}/players`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "player_id": "12345",  // optional
  "player_name": "Patrick Mahomes",
  "position": "QB",
  "team": "KC",
  "roster_slot": "QB",  // QB, RB1, RB2, WR1, WR2, WR3, TE, FLEX, K, DEF, BENCH
  "is_starter": true,  // optional, default: true
  "injury_status": "HEALTHY"  // optional: OUT, DOUBTFUL, QUESTIONABLE, PROBABLE, HEALTHY
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": 1,
    "player_id": "12345",
    "player_name": "Patrick Mahomes",
    "position": "QB",
    "team": "KC",
    "roster_slot": "QB",
    "is_starter": true,
    "injury_status": "HEALTHY",
    "added_at": "2025-10-02T12:00:00Z"
  }
}
```

---

### Update Roster Player

**Endpoint**: `PUT /api/rosters/{roster_id}/players/{player_roster_id}`

**Headers**: `Authorization: Bearer <token>`

**Request Body** (all fields optional):
```json
{
  "roster_slot": "BENCH",
  "is_starter": false,
  "injury_status": "QUESTIONABLE"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": 1,
    "roster_slot": "BENCH",
    "is_starter": false,
    "injury_status": "QUESTIONABLE"
  }
}
```

---

### Remove Player from Roster

**Endpoint**: `DELETE /api/rosters/{roster_id}/players/{player_roster_id}`

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Player removed successfully"
}
```

---

## Matchups

Create and analyze head-to-head matchups between rosters.

### Create Matchup

**Endpoint**: `POST /api/matchups`

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "user_roster_id": 1,
  "opponent_roster_id": 2,
  "week": 5,
  "season": 2024,
  "user_roster_name": "My Team",  // optional
  "opponent_roster_name": "Rival Team"  // optional
}
```

**Validation**:
- Week: 1-18
- Season: 2020-2030
- Rosters must be different

**Response** (201 Created):
```json
{
  "data": {
    "id": 1,
    "week": 5,
    "season": 2024,
    "user_roster_id": 1,
    "opponent_roster_id": 2,
    "user_roster_name": "My Team",
    "opponent_roster_name": "Rival Team",
    "analyzed": false,
    "created_at": "2025-10-02T13:00:00Z"
  }
}
```

---

### Analyze Matchup

**Endpoint**: `POST /api/matchups/{matchup_id}/analyze`

**Headers**: `Authorization: Bearer <token>`

**Description**: Triggers AI-powered analysis of all players in the matchup. This runs asynchronously in the background.

**Response** (202 Accepted):
```json
{
  "message": "Matchup analysis started",
  "data": {
    "matchup_id": 1,
    "status": "analyzing",
    "estimated_completion": "2-3 minutes"
  }
}
```

---

### Get Matchup Analysis

**Endpoint**: `GET /api/matchups/{matchup_id}`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `detailed=true` (optional): Include full player analysis

**Response** (200 OK):
```json
{
  "data": {
    "matchup": {
      "id": 1,
      "week": 5,
      "season": 2024,
      "analyzed": true,
      "analyzed_at": "2025-10-02T13:05:00Z"
    },
    "user_roster": {
      "id": 1,
      "name": "My Team",
      "players": [
        {
          "player_name": "Patrick Mahomes",
          "position": "QB",
          "team": "KC",
          "matchup_score": 85,
          "projected_points": 24.5,
          "ai_grade": "A",
          "recommendation": "START",
          "confidence": "HIGH",
          "reasoning": "Elite matchup against weak secondary..."
        }
      ],
      "total_projected": 125.5
    },
    "opponent_roster": {
      "id": 2,
      "name": "Rival Team",
      "players": [...],
      "total_projected": 118.3
    },
    "prediction": {
      "winner": "user",
      "confidence": 0.65,
      "projected_margin": 7.2
    }
  }
}
```

---

### Get User Matchups

**Endpoint**: `GET /api/matchups`

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
- `week` (optional): Filter by week
- `season` (optional): Filter by season

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": 1,
      "week": 5,
      "season": 2024,
      "user_roster_name": "My Team",
      "opponent_roster_name": "Rival Team",
      "analyzed": true,
      "created_at": "2025-10-02T13:00:00Z"
    }
  ],
  "count": 1
}
```

---

## Players

Search and analyze players.

### Search Players

**Endpoint**: `GET /api/players/search`

**Query Parameters**:
- `query` (optional): Player name search
- `position` (optional): QB, RB, WR, TE, K, DEF

**Response** (200 OK):
```json
{
  "data": [
    {
      "player_id": "12345",
      "name": "Patrick Mahomes",
      "position": "QB",
      "team": "KC",
      "avg_points": 24.5
    }
  ],
  "meta": {
    "query": "mahomes",
    "position": null,
    "count": 1
  }
}
```

---

### Get Player Details

**Endpoint**: `GET /api/players/{player_id}`

**Response** (200 OK):
```json
{
  "data": {
    "player_id": "12345",
    "name": "Patrick Mahomes",
    "position": "QB",
    "team": "KC",
    "avg_points": 24.5,
    "injury_status": "HEALTHY"
  }
}
```

---

### Analyze Player

**Endpoint**: `GET /api/players/{player_id}/analysis`

**Query Parameters**:
- `opponent`: Opponent team (required)
- `location`: Game location (optional, for weather)

**Response** (200 OK):
```json
{
  "data": {
    "player": {
      "player_id": "12345",
      "name": "Patrick Mahomes",
      "position": "QB",
      "team": "KC"
    },
    "matchup_score": 85,
    "weather_impact": 95,
    "ai_grade": {
      "grade": "A",
      "predicted_points": 24.5,
      "confidence": 0.85
    },
    "recommendation": {
      "status": "START",
      "confidence": "HIGH",
      "reason": "Elite matchup with favorable conditions"
    }
  }
}
```

---

## Error Handling

All errors follow a consistent format:

```json
{
  "error": "Error message description"
}
```

### HTTP Status Codes

- `200 OK`: Successful GET request
- `201 Created`: Successful POST request (resource created)
- `202 Accepted`: Request accepted for async processing
- `400 Bad Request`: Validation error or malformed request
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Authenticated but not authorized (e.g., accessing another user's roster)
- `404 Not Found`: Resource doesn't exist
- `500 Internal Server Error`: Server-side error

### Common Error Responses

**Validation Error** (400):
```json
{
  "error": "Validation error: week must be between 1 and 18"
}
```

**Authentication Error** (401):
```json
{
  "error": "Missing or invalid authorization header"
}
```

**Authorization Error** (403):
```json
{
  "error": "Unauthorized access to this roster"
}
```

---

## Response Headers

All responses include:
- `X-Request-ID`: Unique request identifier for logging/debugging
- `Content-Type: application/json`

---

## Best Practices

1. **Store the JWT token securely**: Use httpOnly cookies or secure storage
2. **Token expiration**: Tokens expire after 24 hours - handle 401 errors by redirecting to login
3. **Request IDs**: Include `X-Request-ID` from error responses when reporting issues
4. **Async operations**: Matchup analysis runs in background - poll the GET endpoint to check status
5. **Caching**: Player data is cached for 30 minutes, roster data for 1 hour

---

## Examples

### Complete Authentication Flow

```javascript
// 1. Register
const registerResponse = await fetch('/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    username: 'myuser',
    password: 'securepass123'
  })
});
const { data: { token } } = await registerResponse.json();

// 2. Store token
localStorage.setItem('auth_token', token);

// 3. Use token for protected requests
const rostersResponse = await fetch('/api/rosters', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### Create and Analyze Matchup

```javascript
// 1. Create matchup
const matchup = await fetch('/api/matchups', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_roster_id: 1,
    opponent_roster_id: 2,
    week: 5,
    season: 2024
  })
}).then(r => r.json());

// 2. Start analysis
await fetch(`/api/matchups/${matchup.data.id}/analyze`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

// 3. Poll for results (every 10 seconds)
const pollAnalysis = async () => {
  const result = await fetch(`/api/matchups/${matchup.data.id}?detailed=true`, {
    headers: { 'Authorization': `Bearer ${token}` }
  }).then(r => r.json());

  if (result.data.matchup.analyzed) {
    console.log('Analysis complete!', result.data);
  } else {
    setTimeout(pollAnalysis, 10000);
  }
};
pollAnalysis();
```

---

## Support

For issues or questions:
- Check the `X-Request-ID` header in error responses
- Review Heroku logs for detailed error traces
- Ensure JWT tokens haven't expired (24-hour lifetime)

---

**Last Updated**: October 2, 2025
**API Version**: 1.0.0
