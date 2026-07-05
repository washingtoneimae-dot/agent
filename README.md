# Openfield — The Agentic Asset Marketplace

> **Your agent is as unique as you.**

A review-powered marketplace for **Skill Creation Files** — recipes that teach any AI agent how to build custom skills for specific domains. The infrastructure layer of the agentic economy.

> **Status:** MVP v0.2.0
> **Stack:** Docker · FastAPI · PostgreSQL · React · MinIO · Stripe
> **License:** Private — all rights reserved

---

## What Is a Skill Creation File?

A **Skill Creation File** is a recipe for **building** a skill, not a skill itself.

| | Skill File | Skill Creation File |
|---|---|---|
| **What it is** | Instructions an agent follows to DO a task | A recipe that tells an agent how to BUILD a new skill |
| **Example** | "How to analyze CSV data" | "How to write an agent skill that analyzes CSV data" |
| **Value** | A finished product | Domain-specific prompt engineering knowledge |

The platform's core innovation: a user selects up to 4 Skill Creation Files, pastes them into their agent, and the agent synthesizes a custom skill optimized for their specific use case.

## Quick Start

```bash
git clone https://github.com/washingtoneimae-dot/agent.git
cd agent
cp .env.example .env
# Edit .env: set DOMAIN, JWT_SECRET, and any API keys you want to use
nano .env
docker compose up -d
```

> **First build takes 2-3 minutes** (compiling asyncpg + npm install). Subsequent starts are instant.

Open http://localhost:80 — register as the first user (auto-admin).

**Ports used:** 80 (nginx), 443 (SSL), 5432 (Postgres), 6379 (Redis), 9000-9001 (MinIO). Free these ports if something else is using them.

## Architecture

```
User (Browser / Agent Dashboard)
        │
        ▼
  nginx (:80) ──► frontend (React + Tailwind, :3000)
        │       └─► api (FastAPI, :8000)
        │
        ├── postgres (:5432) — primary DB
        ├── redis (:6379) — cache + sessions
        └── minio (:9000) — S3 file storage
```

## Core Features

### Tree-Structured File System
Files form a parent → child → grandchild tree. A "Data Analysis" parent spawns "Solar Energy Soiling Analysis" child, which spawns "ROI Calculator" grandchild. Each level is a specialization.

### Query-Depth-Aware Search
- **Broad** (1-2 words): Shows parent files with child suggestions
- **Moderate** (3-4 words): Shows best match with parent context and siblings
- **Specific** (5+ words or technical): Shows leaf file with full parent path

### Per-File Chatrooms
Every file has a discussion thread where subscribers can post tips, edge cases, and optimizations. Threaded replies, upvotes, and author-pinned responses.

### API Key Auth
Agent dashboards can authenticate via `X-API-Key` header. API key downloads increment `extraction_count` — the primary ranking signal.

### Scoring System
```
score = (extractions × 0.35) + (children × 0.20) + (downloads × 0.15) + (reviews × 0.15) + (chat_users × 0.10) + (engagement × 0.05)
```
Floor: 10.0. Recalculated via admin endpoint.

## Subscription Model

| Tier | Price | What You Get |
|---|---|---|
| Free | $0 | Browse marketplace, read chatrooms, view files |
| Subscriber | $9/mo | Unlimited downloads, post tips, fork children, API access |

## Documentation

- **[API.md](./API.md)** — Full endpoint reference with curl examples
- **[TECHNICAL.md](./TECHNICAL.md)** — Architecture, database schema, subsystems, dev setup, deployment, troubleshooting
- **[FORMAT.md](./FORMAT.md)** — Skill Creation File format specification
- **[VISION.md](./VISION.md)** — Four-level roadmap from marketplace to Agentic OS
- **[SCORECARD.md](./SCORECARD.md)** — 10-dimension project scorecard with competitive analysis

## Marketplace Contents (Seeded)

| File | Category | Type |
|---|---|---|
| Test-Driven Development Skill Creation File | Coding | Parent |
| JavaScript TDD Skill Creation File | Coding | Child |
| Plan Writing Skill Creation File | Coding | Parent |
| Notion Integration Skill Creation File | Other | Parent |
| Data Analysis Skill Creation | Data Analysis | Parent |
| Solar Energy Soiling Analysis | Data Analysis | Child |
| Solar Panel Cleaning ROI Calculator | Data Analysis | Grandchild |

## Tech Stack

| Component | Technology |
|---|---|
| Backend | FastAPI (Python 3.14, async) |
| Frontend | React 18 + Tailwind CSS + Vite |
| Database | PostgreSQL 16 + asyncpg |
| Cache | Redis 7 |
| File Storage | MinIO (S3-compatible) |
| Reverse Proxy | nginx |
| Payments | Stripe (subscriptions) |
| AI | OpenRouter / DeepSeek / OpenAI (abstraction layer) |
| Auth | JWT + API keys |

## Environment Variables

See [.env.example](./.env.example) for all required vars. At minimum you need `DOMAIN`, `DB_USER`, `DB_PASSWORD`, `JWT_SECRET`, `MINIO_ACCESS_KEY`, and `MINIO_SECRET_KEY`. Stripe and AI provider keys are optional — the app runs in demo mode without them.

## Project Structure

```
openfield/
├── docker-compose.yml        # 6-service stack
├── API.md                    # Full API documentation
├── TECHNICAL.md              # Technical deep-dive
├── FORMAT.md                 # Skill Creation File spec
├── VISION.md                 # Long-term roadmap
├── SCORECARD.md              # Competitive scorecard
├── api/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Settings (env-based)
│   │   ├── database.py       # Async SQLAlchemy setup
│   │   ├── deps.py           # JWT + API key auth
│   │   ├── models/           # 9 SQLAlchemy models
│   │   ├── routes/           # 8 route modules
│   │   ├── schemas/          # Pydantic request/response schemas
│   │   └── services/         # Business logic (search, ranking, AI)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── App.jsx           # Router + navbar
│       └── pages/            # Browse, FileDetail, Upload, Dashboard, Admin
├── docker/
│   └── nginx/                # nginx config + SSL
├── deploy/                   # VPS deployment scripts
└── marketing/                # X threads and outreach
```

## License

Private — all rights reserved. washingtoneimae-dot
