# AgentMarket — Technical Documentation

> **Version:** v0.2.0 | **Stack:** Docker · FastAPI · PostgreSQL · React · MinIO · Stripe
> **Repo:** github.com/washingtoneimae-dot/agent | **License:** Private

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Database Schema](#2-database-schema)
3. [API Reference](#3-api-reference)
4. [Key Subsystems](#4-key-subsystems)
5. [Environment Variables](#5-environment-variables)
6. [Local Development](#6-local-development)
7. [Deployment](#7-deployment)
8. [Troubleshooting](#8-troubleshooting)
9. [Design Decisions](#9-design-decisions)

---

## 1. Architecture Overview

### Service Topology

```
Browser ──► nginx (:80/:443)
               │
               ├── /api/*     ──► api (FastAPI + uvicorn, :8000)
               ├── /          ──► frontend (nginx serving built React, :3000)
               │
               ├── postgres   (:5432) — primary database
               ├── redis      (:6379) — cache + session store
               └── minio      (:9000) — S3-compatible file/blob storage
```

Six services defined in `docker-compose.yml`. All internal container-to-container communication happens on a Docker bridge network. Only nginx exposes ports 80/443 to the host.

### Data Flow

| Action | Flow |
|--------|------|
| Browse/search | Browser → nginx → API → PostgreSQL (full-text search) |
| Upload file | Browser → nginx → API (JWT auth) → PostgreSQL + MinIO |
| Download | Browser/agent → nginx → API (JWT or X-API-Key) → PostgreSQL (increment counters) |
| Subscribe | Browser → nginx → API → Stripe Checkout → webhook → API |
| AI review summary | On review POST → API → OpenRouter/DeepSeek/OpenAI → PostgreSQL |

### Request Path

1. nginx terminates TLS (SSL certs in `docker/nginx/ssl/`)
2. `/api/*` proxied to FastAPI backend
3. Frontend is default catch-all — React SPA with client-side routing
4. Backend uses async SQLAlchemy (`asyncpg` driver) for all DB access

## 2. Database Schema

### Entity-Relationship Diagram

```
users (1) ──────< files (many) ──────< ratings (many)
  │                  │                      │
  │                  │ (parent/child self-ref)
  │                  │
  ├──< api_keys      ├──< chat_messages
  ├──< transactions  ├──< review_summaries (1:1 per file)
  │                  ├──< companion_files
  │                  └──< contributor_payouts
  │
  └──< settings (system-wide key-value)
```

All tables use auto-increment integer PKs and `created_at`/`updated_at` timestamps with timezone.

### Table: `users`

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | Auto-increment |
| email | VARCHAR(255) UNIQUE | Used for login |
| password_hash | VARCHAR(255) | bcrypt hashed |
| display_name | VARCHAR(100) | Shown in UI |
| is_subscribed | BOOLEAN | Paid $9/mo |
| subscribed_since | TIMESTAMPTZ | NULL if never subscribed |
| stripe_customer_id | VARCHAR(100) | Stripe customer ref |
| reputation_score | FLOAT | Unused currently |
| is_verified | BOOLEAN | **This means admin.** First user to register gets this. |
| is_active | BOOLEAN | Soft-delete flag |

**Critical:** `is_verified` doubles as the admin flag. The first user to register anywhere in the system gets `is_verified=True` automatically (see `auth.py` register endpoint). All `/admin/*` endpoints check `is_verified`, not a separate role column.

### Table: `files`

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| contributor_id | FK → users.id | Who uploaded it |
| parent_id | FK → files.id (self-ref) | NULL = root/parent file. Set = child specialization |
| title | VARCHAR(200) | |
| description | TEXT | **The actual file content.** This is what gets downloaded. |
| category | ENUM | data_analysis, coding, marketing, research, content, other |
| product_tier | ENUM | skill_creation_file, complete_skill, workflow_template |
| tags | VARCHAR(500) | Comma-separated, used in search index |
| download_count | INTEGER | Incremented on download |
| extraction_count | INTEGER | Incremented on API key download (primary ranking signal) |
| children_count | INTEGER | Denormalized count of direct children |
| score | FLOAT | Composite ranking score (see §4.1) |
| status | ENUM | pending, active, flagged, removed, archived |
| storage_path, file_size, original_filename | | For future binary upload support |

**Tree structure:** `parent_id` creates a parent→child→grandchild hierarchy. Parents appear in browse. Children appear in search results based on query depth. A root file has `parent_id=NULL`. A child/specialization has `parent_id` pointing to its parent.

### Table: `ratings`

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| user_id, file_id | FK | Who rated what |
| score | INTEGER | 1-5 |
| review_text | TEXT | Optional free text |
| agent_used | VARCHAR(50) | claude, gpt4o, gemini, deepseek |
| use_case | VARCHAR(50) | What they used it for |
| synthesis_rounds | VARCHAR(10) | 1-2, 3-5, 5+ |
| paired_file_ids | VARCHAR(255) | Comma-separated file IDs used together |
| verified_download | BOOLEAN | True if user actually downloaded first |

### Table: `review_summaries` (singular, one per file)

AI-generated structured summary of all reviews for a file. `summary_json` contains: `overall_sentiment`, `strengths[]`, `weaknesses[]`, `best_agent`, `use_case_fit`, `pairing_insights`, `iteration_needed`. Generated automatically when a new review is posted.

### Table: `transactions`

Tracks token economy. Types: purchase, download, earn, payout, admin_credit. Currently partially implemented — subscriptions replaced token purchases.

### Table: `chat_messages`

Per-file threaded chatroom. Parent messages have `parent_id=NULL`. Replies have `parent_id` pointing to the message they reply to. Upvoting increments `upvotes` counter.

### Table: `api_keys`

SHA-256 hashed. `key_prefix` stores first ~14 chars for UI display. `scope` is comma-separated: `read:files,download:files`. `monthly_limit` defaults to 1000.

### Table: `settings`

Key-value store for runtime configuration (AI provider, API keys, etc.). Allows admin to change AI provider without restarting containers.

## 3. API Reference

Base: `/api/v1`. See `API.md` for full endpoint reference with curl examples. This section covers architecture, not individual endpoints.

### Route Modules (8 files in `api/app/routes/`)

| Module | Prefix | Auth | Purpose |
|--------|--------|------|---------|
| auth.py | /auth | Public + JWT | Register, login, refresh, me |
| files.py | /files | Mixed | Browse (public), upload/download (auth) |
| search.py | /search | Public | PostgreSQL full-text search, query-depth-aware |
| chat.py | /chat | Read: public, Write: subscriber | Per-file threaded chatrooms |
| reviews.py | /reviews | JWT | Submit reviews, get AI summaries |
| payments.py | /payments | JWT + Stripe | Subscribe, webhook handler |
| api_keys.py | /api-keys | JWT | Create/list/revoke API keys |
| admin.py | /admin | Admin (is_verified) | Stats, file moderation, user management, rank recalculation, settings |
| users.py | /users | JWT | User profile |

### Authentication Dual System

The system supports two auth methods simultaneously:

1. **JWT (browser users):** `Authorization: Bearer <token>`. Access token expires in 30 min, refresh token in 7 days. Tokens contain `sub` (user_id) and `type` (access/refresh).

2. **API Key (agent dashboards):** `X-API-Key: amk_...`. SHA-256 hashed. Usage tracked per key. Monthly limit of 1,000 requests.

The `get_api_or_jwt_user()` dependency in `deps.py` accepts either. Endpoints that use it (like file download) work for both browser users and API-integrated agents.

### Dual Counter System

Downloads increment both `download_count` and `extraction_count`. But `extraction_count` is the heavier weight in the scoring formula (0.35 vs 0.15). This means API-key-authenticated agent downloads (which call the same endpoint) have more ranking impact than UI downloads — intentional, since agent extractions signal real synthesis value.

### Query-Depth-Aware Search (`/search`)

Implemented in `services/search.py`. Classifies queries into three depths:

| Depth | Trigger | Response Shape |
|-------|---------|----------------|
| **broad** | 1-2 words, no technical terms | Parent files + their children preview |
| **moderate** | 3-4 words, some technical | Best match + parent context + siblings |
| **specific** | 5+ words or 2+ technical terms | Leaf file + full parent path |

Uses PostgreSQL `tsvector` full-text search with `to_tsquery` prefix matching (`word:*`). Falls back to `LIKE '%word%'` if full-text returns nothing.

### Admin Auth Model

**Critical:** Admin = `is_verified = True` on the User model. There is no separate role table or permissions system. The `require_admin` dependency in `admin.py` checks `user.is_verified`. The first user to register gets `is_verified=True` automatically. Additional admins are added via `POST /admin/users/{id}/invite-admin`.

### Rate Limiting

| Auth | Limit |
|------|-------|
| JWT (browser) | 30 req/s |
| API Key | 1,000 req/month |
| Unauthenticated | 10 req/s |

Rate limits are declared in `API.md` but enforced at the nginx level (not yet implemented in code — nginx config needs `limit_req_zone` directives).

## 4. Key Subsystems

### 4.1 Scoring Algorithm

Implemented in `api/app/services/ranking.py`. Recalculated via `POST /admin/recalculate-ranks`.

```
score = (extraction_norm × 0.35) + (children_norm × 0.20) + (downloads_norm × 0.15) 
      + (review_norm × 0.15) + (chat_norm × 0.10) + 5.0
```

All signals are normalized to 0-100 against the max value across all active files:

- **extraction_norm** = (file.extraction_count / max_extractions) × 100
- **children_norm** = (file.children_count / max_children) × 100
- **downloads_norm** = (file.download_count / max_downloads) × 100
- **review_norm** = (avg_rating / 5) × 100
- **chat_norm** = (unique_chatters_last_30_days / 10) × 100, capped at 100
- **+5.0** is a "contributor engagement bonus" (flat, not normalized)

Score floor: 10.0. This means even brand-new files start at 10.0.

Normalization is relative — if one file dominates extractions, everyone else's extraction score drops. This creates a competitive ranking dynamic.

### 4.2 Subscription System

**Flow:**
1. User clicks Subscribe → `POST /payments/subscribe`
2. If `STRIPE_SECRET_KEY` is empty → **demo mode**: sets `is_subscribed=True` instantly
3. If live → creates Stripe Checkout session, returns URL
4. User completes Stripe payment → Stripe POSTs to `/payments/webhook`
5. Webhook handler verifies signature, sets `is_subscribed=True`, stores `stripe_customer_id`
6. On cancellation → Stripe POSTs `customer.subscription.deleted` → sets `is_subscribed=False`

**Gating:** File downloads (`POST /files/{id}/download`) check `user.is_subscribed` and return 402 if false. Chat posting also requires subscription.

### 4.3 AI Provider Abstraction

The system supports three AI providers for review summary generation: OpenRouter, DeepSeek, OpenAI.

**Runtime switching:** Admin can change provider via `POST /admin/settings/ai` without restarting. Settings stored in the `settings` DB table.

**Fallback chain in `services/settings.py`:**
- Settings table → env vars → hardcoded defaults
- If a provider's API key is empty, `generate_review_summary()` returns `None` silently

**Models by provider:**
- OpenRouter: `deepseek/deepseek-v4-flash`
- DeepSeek: `deepseek-v4-flash`
- OpenAI: `gpt-4o-mini`

Override via `AI_MODEL` env var or admin settings.

### 4.4 File Tree Structure

Files are organized as a parent→child→grandchild tree via the `parent_id` self-referential foreign key.

**Rules:**
- Root files: `parent_id = NULL`, appear in browse
- Children: `parent_id` set, represent specializations of the parent
- When a child is uploaded, `parent.children_count` is updated
- Uploaded files start as `status=pending` — admin must approve before they appear publicly

**Search behavior by tree depth:**
- Broad queries return parents + their children preview
- Specific queries traverse up the tree to show parent_path

### 4.5 Chatrooms

Per-file threaded discussions. Implemented in `chat.py`.

- Top-level messages have `parent_id=NULL`
- Replies have `parent_id` pointing to the message they reply to
- Sorted by `upvotes DESC, created_at DESC`
- Author of original file can mark responses as `is_contributor_response`
- Reading is public, posting requires subscription

## 5. Environment Variables

File: `.env` (gitignored). Template: `.env.example`.

### Required

| Variable | Purpose | Example |
|----------|---------|---------|
| DOMAIN | Public domain for CORS, Stripe callbacks | `agentmarket.com` or `localhost` |
| DB_USER | PostgreSQL user | `agentmarket` |
| DB_PASSWORD | PostgreSQL password | `change_me_in_production` |
| JWT_SECRET | HS256 signing key | `openssl rand -hex 32` |
| MINIO_ACCESS_KEY | S3 access key | `agentmarket` |
| MINIO_SECRET_KEY | S3 secret key | `change_me_in_production` |

### Optional (but needed for features)

| Variable | Required For |
|----------|-------------|
| STRIPE_SECRET_KEY | Live payments. Without it, demo mode. |
| STRIPE_PUBLISHABLE_KEY | Stripe Checkout UI |
| STRIPE_WEBHOOK_SECRET | Verifying Stripe webhook signatures |
| STRIPE_SUBSCRIPTION_PRICE_ID | Must be created in Stripe Dashboard as $9/mo product |
| AI_PROVIDER | One of: `openrouter`, `deepseek`, `openai` |
| OPENROUTER_API_KEY | Review summary generation via OpenRouter |
| DEEPSEEK_API_KEY | Review summary generation via DeepSeek |
| OPENAI_API_KEY | Review summary generation via OpenAI |
| AI_MODEL | Override default model (optional) |
| DEBUG | Set `true` for SQL query logging, verbose errors |
| CORS_ORIGINS | Comma-separated allowed origins |

### Connection Strings (auto-generated in docker-compose)

These are set in `docker-compose.yml` environment, not in `.env`:

```
DATABASE_URL = postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@postgres:5432/agentmarket
REDIS_URL = redis://redis:6379/0
MINIO_ENDPOINT = minio:9000
```

### Removed Dependencies

N8N env vars (`N8N_ENCRYPTION_KEY`, `N8N_USER_MANAGEMENT_JWT_SECRET`) are still in `.env.example` but no longer used since n8n was removed from the stack (July 2026). They're harmless — `pydantic-settings` with `extra="ignore"` silences unknown vars.

## 6. Local Development

### Prerequisites

- Docker + Docker Compose v2
- Node.js 22+ (for frontend dev outside Docker)
- Python 3.14+ (for backend dev outside Docker)

### Full Stack (Docker)

```bash
git clone https://github.com/washingtoneimae-dot/agent.git
cd agent
cp .env.example .env
# Edit .env — at minimum set a JWT_SECRET
nano .env
docker compose up -d
```

Services available at:
- Frontend: http://localhost:80
- API: http://localhost:80/api/v1/health
- MinIO Console: http://localhost:9001

The first user to register at `/dashboard` becomes admin automatically.

### Backend Only (outside Docker)

```bash
cd api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set env vars or create .env in api/
DATABASE_URL=postgresql+asyncpg://agentmarket:password@localhost:5432/agentmarket
JWT_SECRET=dev_secret

uvicorn app.main:app --reload --port 8000
```

Requires running PostgreSQL, Redis, and MinIO locally or via Docker (`docker compose up -d postgres redis minio`).

### Frontend Only (outside Docker)

```bash
cd frontend
npm install
npm run dev
# Served at http://localhost:3000
```

API calls proxy through Vite config to the backend. Edit `vite.config.js` to point to your API.

### Seeding Test Data

```bash
docker compose exec api python -m app.seed
```

This creates sample files (parent/child/grandchild tree) and a test user.

### Running Tests

Tests use pytest with async support:

```bash
cd api
pip install pytest pytest-asyncio httpx
pytest -v
```

### Makefile Commands

```bash
make up          # docker compose up -d
make down        # docker compose down
make logs        # docker compose logs -f
make build       # docker compose build --no-cache
make reset       # Full teardown + rebuild (destroys volumes!)
make seed        # Seed sample data
make shell-db    # psql into postgres
make shell-api   # bash into API container
```

### Project Structure

```
agent/
├── docker-compose.yml          # 6-service stack (was 7, n8n removed)
├── .env.example                # Environment template
├── API.md                      # Endpoint reference (curl examples)
├── FORMAT.md                   # Skill Creation File spec
├── TECHNICAL.md                # This document
├── Makefile                    # Convenience commands
├── README.md                   # Marketing-facing readme
│
├── api/
│   ├── Dockerfile              # Python 3.14-slim
│   ├── requirements.txt        # 15 direct dependencies
│   └── app/
│       ├── main.py             # FastAPI entry, lifespan, router registration
│       ├── config.py           # Pydantic Settings (env → config)
│       ├── database.py         # Async SQLAlchemy engine + session
│       ├── deps.py             # Auth dependencies (JWT + API key)
│       ├── models/             # 9 SQLAlchemy models
│       │   ├── user.py
│       │   ├── file.py         # Includes tree self-reference
│       │   ├── rating.py
│       │   ├── review_summary.py
│       │   ├── transaction.py
│       │   ├── api_key.py
│       │   ├── chat_message.py
│       │   ├── companion_file.py
│       │   ├── contributor_payout.py
│       │   └── setting.py      # Key-value runtime config
│       ├── routes/             # 8 route modules
│       ├── schemas/            # Pydantic request/response models
│       └── services/           # Business logic
│           ├── ai.py           # AI review summary generation
│           ├── search.py       # Query-depth detection
│           ├── ranking.py      # Score recalculation
│           └── settings.py     # Runtime settings CRUD
│
├── frontend/
│   ├── Dockerfile              # Multi-stage: node build → nginx serve
│   ├── package.json            # React 18, Tailwind, Vite, Axios
│   └── src/
│       ├── App.jsx             # Router + navbar + auth state
│       ├── main.jsx            # React entry
│       ├── index.css           # Tailwind imports
│       └── pages/
│           ├── Browse.jsx      # Marketplace grid
│           ├── FileDetail.jsx  # Single file view + chatroom
│           ├── Upload.jsx      # File upload form
│           ├── Dashboard.jsx   # Auth (login/register) + subscription
│           └── AdminPage.jsx   # Admin panel
│
├── docker/
│   └── nginx/
│       ├── nginx.conf          # Reverse proxy config
│       ├── ssl/                # TLS certificates
│       └── certbot_www/        # Let's Encrypt challenges
│
└── deploy/
    └── setup.sh                # VPS one-click deploy script
```

## 7. Deployment

### VPS One-Click

```bash
git clone https://github.com/washingtoneimae-dot/agent.git /opt/agentmarket
cd /opt/agentmarket
cp .env.example .env
nano .env   # Set DOMAIN, passwords, Stripe keys, AI keys
docker compose up -d
```

Or use the deploy script: `bash deploy/setup.sh`

### Domain & SSL

1. Point your domain's DNS A record to the VPS IP
2. Set `DOMAIN=yourdomain.com` in `.env`
3. Place SSL certs in `docker/nginx/ssl/` or use certbot:
   ```bash
   docker compose run --rm certbot certonly --webroot ...
   ```
4. Restart nginx: `docker compose restart nginx`

### Production Checklist

- [ ] Change `JWT_SECRET` to `openssl rand -hex 32`
- [ ] Change all passwords (`DB_PASSWORD`, `MINIO_SECRET_KEY`)
- [ ] Set `DEBUG=false`
- [ ] Configure Stripe live keys (not test keys)
- [ ] Create Stripe $9/mo subscription product, set `STRIPE_SUBSCRIPTION_PRICE_ID`
- [ ] Set up Stripe webhook endpoint: `https://yourdomain.com/api/v1/payments/webhook`
- [ ] Configure at least one AI provider API key
- [ ] Set up SSL certificates
- [ ] Set up database backups (pg_dump cron)

### Database Backups

```bash
# Manual backup
docker compose exec postgres pg_dump -U agentmarket agentmarket > backup_$(date +%Y%m%d).sql

# Restore
docker compose exec -T postgres psql -U agentmarket agentmarket < backup.sql
```

### Upgrading

```bash
git pull
docker compose pull
docker compose up -d --build
```

Database migrations are handled automatically — `init_db()` in `database.py` calls `Base.metadata.create_all()` on startup, which creates any missing tables. This is safe for new tables/columns but does NOT handle renames or destructive changes.

### Volumes (Persistent Data)

| Volume | Content | Destroyed by `make reset`? |
|--------|---------|---------------------------|
| postgres_data | All database data | YES |
| redis_data | Cache, sessions | YES |
| minio_data | Uploaded files/blobs | YES |

Back up volumes before running `make reset` or `docker compose down -v`.

## 8. Troubleshooting

### "402 Subscription Required" on download

User needs an active subscription. Check `users.is_subscribed` in DB:
```bash
docker compose exec postgres psql -U agentmarket -d agentmarket -c \
  "SELECT id, email, is_subscribed FROM users WHERE id = <user_id>;"
```
If using demo mode (no `STRIPE_SECRET_KEY`), subscribing via the dashboard sets it instantly.

### AI summaries not generating

Check three things:
1. Is an AI provider API key configured? Check admin settings page or DB:
   ```sql
   SELECT * FROM settings WHERE key LIKE '%api_key%';
   ```
2. Is the review summary endpoint being hit? Check API container logs:
   ```bash
   docker compose logs api | grep "AI summary error"
   ```
3. Are there enough reviews? The system needs at least 1 review to generate.

### Search returns nothing

PostgreSQL full-text search requires English text. Check:
1. The file's `status` is `active` (not pending)
2. The search query has words > 2 characters (shorter words are filtered)
3. Try the LIKE fallback — it runs automatically if tsvector returns nothing

### Frontend shows blank page

- Check browser console for API errors (CORS is configured for the DOMAIN env var)
- Verify frontend is built: `docker compose logs frontend`
- Check nginx is routing correctly: `docker compose logs nginx`

### Database connection refused

- PostgreSQL healthcheck may still be running — wait 10 seconds after `docker compose up`
- Check: `docker compose exec postgres pg_isready -U agentmarket -d agentmarket`
- If persistent: `docker compose down -v && docker compose up -d` (destroys data!)

### "Permission denied (publickey)" on git push

Local git is configured for SSH but the SSH key isn't available in this session. Option: switch remote to HTTPS:
```bash
git remote set-url origin https://github.com/washingtoneimae-dot/agent.git
```

### Environment variables not taking effect

`docker compose up -d` reuses existing containers. If you changed `.env`:
```bash
docker compose down && docker compose up -d
```
Or force recreate: `docker compose up -d --force-recreate`

---

## 9. Design Decisions

### Why asyncpg not psycopg2?

Async throughout. FastAPI + async SQLAlchemy + asyncpg means no thread pool bottlenecks. Every DB call is `await`-ed. The connection pool is sized at 5 + 10 overflow.

### Why MinIO not direct filesystem?

S3 compatibility means the storage layer is swappable. Local dev uses MinIO. Production can point to AWS S3, Cloudflare R2, or any S3-compatible service without code changes. Currently only used for future binary upload support.

### Why "description" stores file content?

The marketplace files ARE markdown text. There's no separate "content" column — `description` serves double duty as search index and download payload. This keeps the model simple. Binary file support (via `storage_path` in MinIO) is in the schema but not yet implemented in routes.

### Why bcrypt not argon2?

`bcrypt==5.0.0` is simpler to install (no C dependencies on some platforms). For a marketplace where accounts hold no sensitive financial data beyond Stripe IDs, bcrypt is adequate.

### Why JWT + API Key dual auth?

Different use cases: JWT for browser sessions (short-lived, refreshable), API keys for agent dashboards (long-lived, revocable). API keys also enable usage tracking per integration, which powers the extraction-based ranking.

### Why score normalization is relative?

If one file dominates, others drop. This creates a competitive ranking that naturally surfaces the best files rather than letting scores inflate over time. Trade-off: adding a single mega-popular file depresses everyone else's score.

### Why "is_verified" means admin?

Simplicity over complexity. No separate roles table, no permissions matrix. First user is admin. Admin can add more admins. This works for a marketplace where the admin surface is small. If the admin feature set grows, a proper RBAC system should be extracted.

### Why no database migrations (Alembic unused)?

Alembic is in `requirements.txt` but not configured. `init_db()` uses `create_all()` on startup — auto-creates missing tables. This works for greenfield development but is dangerous for production schema changes (no down migrations, no rename detection). Should be replaced with proper Alembic migration management before any destructive schema change.

---

*Last updated: July 5, 2026. Maintained by washingtoneimae-dot.*
