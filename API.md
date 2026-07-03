# AgentMarket API Documentation

Base URL: `http://localhost:80/api/v1` (or your deployed domain)

**Authentication:** All endpoints except health/search/chat-read require either a JWT token or API key.

| Method | Header | Used For |
|---|---|---|
| JWT | `Authorization: Bearer <token>` | Web UI, user actions |
| API Key | `X-API-Key: amk_...` | Agent dashboards, programmatic access |

---

## Authentication

### Register
```bash
POST /auth/register
Content-Type: application/json

{"email": "user@example.com", "password": "mypassword", "display_name": "My Name"}
```
**Response:** `{"access_token": "...", "refresh_token": "...", "token_type": "bearer"}`

> **First user ever to register becomes admin automatically.** Subsequent users are normal.

### Login
```bash
POST /auth/login
Content-Type: application/json

{"email": "user@example.com", "password": "mypassword"}
```
**Response:** Same as register — returns JWT pair.

### Get Current User
```bash
GET /auth/me
Authorization: Bearer <token>
```
**Response:** `{"id": 1, "email": "...", "display_name": "...", "is_subscribed": false, "is_verified": true, ...}`

### Refresh Token
```bash
POST /auth/refresh
Content-Type: application/json

{"refresh_token": "..."}
```

---

## Files & Marketplace

### Browse Files
```bash
GET /files?sort=score&category=data_analysis&limit=50
```
Returns **parent files only** (files without a parent_id). Children are accessible via search or direct ID.

**Parameters:**
| Param | Values | Default |
|---|---|---|
| `sort` | `score`, `newest`, `downloads` | `score` |
| `category` | `data_analysis`, `coding`, `marketing`, `research`, `content`, `other` | all |
| `limit` | 1–100 | 50 |
| `offset` | 0+ | 0 |

### Get File Detail
```bash
GET /files/5
```
Returns full file metadata including `parent_id`, `children_count`, `extraction_count`, `score`.

### Upload File
```bash
POST /files
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My Skill Creation File",
  "description": "Description (first 300 chars are the search index)",
  "category": "coding",
  "tags": "testing,tdd,meta,creation-file",
  "parent_id": null
}
```
Set `parent_id` to an existing file's ID to create a **child** (fork/specialization).

### Download File
```bash
POST /files/5/download
```
**Requires subscription.** Returns the file's description/content that an agent can use for synthesis.

> **Note:** API key authenticated downloads increment `extraction_count`. UI downloads increment `download_count`. Both require subscription.

---

## Search (Tree-Aware)

### Search Files
```bash
GET /search?q=data+analysis&limit=3
```
Query-depth-aware search. Returns different response shapes based on query specificity.

**Parameters:**
| Param | Default | Description |
|---|---|---|
| `q` | (required) | Search query |
| `limit` | 3 | Max results (capped at 10) |

**Response shapes by query depth:**

**Broad** (1-2 words, no technical terms — e.g. "data analysis"):
```json
{
  "query": "data analysis",
  "query_depth": "broad",
  "results": [
    {
      "id": 5,
      "title": "Data Analysis Skill Creation",
      "children_count": 2,
      "children": [
        {"id": 6, "title": "Solar Energy Soiling Analysis", "extraction_count": 0}
      ]
    }
  ]
}
```

**Moderate** (3-4 words, some technical):
```json
{
  "query": "solar energy analysis",
  "query_depth": "moderate",
  "results": [
    {
      "id": 6,
      "title": "Solar Energy Soiling Analysis",
      "parent": {"id": 5, "title": "Data Analysis Skill Creation"},
      "siblings": [{"id": 7, "title": "Solar Panel Cleaning ROI Calculator"}]
    }
  ]
}
```

**Specific** (5+ words, or 2+ technical terms):
```json
{
  "query": "solar panel cleaning roi calculator",
  "query_depth": "specific",
  "results": [
    {
      "id": 7,
      "title": "Solar Panel Cleaning ROI Calculator",
      "parent_path": [
        {"id": 5, "title": "Data Analysis Skill Creation"},
        {"id": 6, "title": "Solar Energy Soiling Analysis"}
      ]
    }
  ]
}
```

---

## Chatrooms (Per-File Tips)

### Read Messages
```bash
GET /chat/5
```
No auth required. Returns messages with threaded replies.

### Post a Tip
```bash
POST /chat/5
Authorization: Bearer <token>
Content-Type: application/json

{"content": "Used this with Pandas — had to add index reset after groupby."}
```
**Requires subscription.**

### Reply to a Tip
```bash
POST /chat/5/12/reply
Authorization: Bearer <token>
Content-Type: application/json

{"content": "Try: df = df.reset_index(drop=True)"}
```

### Upvote a Tip
```bash
POST /chat/5/12/upvote
Authorization: Bearer <token>
```

---

## Reviews

### Submit Review
```bash
POST /reviews
Authorization: Bearer <token>
Content-Type: application/json

{"file_id": 5, "score": 4, "review_text": "Great for structured data", "agent_used": "claude"}
```

### Get Reviews
```bash
GET /reviews/5
```

### Get AI Summary
```bash
GET /reviews/5/summary
```

---

## API Keys

### Create Key
```bash
POST /api-keys
Authorization: Bearer <token>
Content-Type: application/json

{"name": "My Agent Dashboard", "scope": "read:files,download:files"}
```
**Response includes `full_key` — show it once, it won't be returned again.**

### List Keys
```bash
GET /api-keys
Authorization: Bearer <token>
```

### Revoke Key
```bash
DELETE /api-keys/5
Authorization: Bearer <token>
```

---

## Subscription & Payments

### Subscribe ($9/month)
```bash
POST /payments/subscribe
Authorization: Bearer <token>
```
**Demo mode** (no Stripe key configured): subscribes instantly.
**Live mode**: returns Stripe Checkout URL to redirect to.

### Check Status
```bash
GET /payments/status
Authorization: Bearer <token>
```

---

## Admin

> All admin endpoints require `is_verified=true`.

### Dashboard Stats
```bash
GET /admin/stats
Authorization: Bearer <token>
```

### Manage Files
```bash
GET /admin/files
GET /admin/files/pending
POST /admin/files/5/approve
POST /admin/files/5/reject
```

### Manage Users
```bash
GET /admin/users
POST /admin/users/3/invite-admin
POST /admin/users/3/toggle-admin
POST /admin/users/3/deactivate
```

### API Keys (Global)
```bash
GET /admin/api-keys
POST /admin/api-keys/5/revoke
```

### Transactions
```bash
GET /admin/transactions
```

### System Settings
```bash
GET /admin/settings
```

---

## Example: Agent Dashboard Integration (Python)

```python
import requests

API_KEY = "amk_your_key_here"
BASE = "http://localhost:80/api/v1"

# Search for files
res = requests.get(f"{BASE}/search", params={"q": "data analysis"}, headers={"X-API-Key": API_KEY})
files = res.json()["results"]

# Download the best match
file_id = files[0]["id"]
res = requests.post(f"{BASE}/files/{file_id}/download", headers={"X-API-Key": API_KEY})
skill_content = res.json()["content"]
print(skill_content)
```

## curl Quickstart
```bash
# Search
curl "http://localhost:80/api/v1/search?q=data+analysis"

# Download via API key
curl -X POST "http://localhost:80/api/v1/files/5/download" -H "X-API-Key: amk_..."

# Download via JWT
curl -X POST "http://localhost:80/api/v1/files/5/download" -H "Authorization: Bearer eyJhbG..."
```

---

## Rate Limits

| Auth Method | Limit |
|---|---|
| JWT (browser) | 30 requests/second |
| API Key | 1,000 requests/month per key |
| Unauthenticated (read-only) | 10 requests/second |

---

## Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Bad request |
| 401 | Not authenticated |
| 402 | Subscription required |
| 403 | Forbidden |
| 404 | Not found |
| 409 | Conflict (email exists) |
| 422 | Validation error |
| 500 | Internal server error |
