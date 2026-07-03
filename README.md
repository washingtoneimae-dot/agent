# AgentMarket

**The Infrastructure Layer of the Agentic Economy**

Token-powered marketplace for AI agent capabilities — Skill Creation Files, Complete Skills, and Workflow Templates. Built on Docker, n8n, FastAPI, DeepSeek API.

> **Status:** Pre-MVP (Planning Phase)
> **Stack:** Docker · n8n · FastAPI · PostgreSQL · Redis · MinIO · React + Tailwind
> **License:** Private — all rights reserved

---

## Core Thesis

The AI industry has solved the brain (models) and the muscles (agents). Nobody has solved the body — the design language, skill ecosystem, and operating environment that ties it all together. AgentMarket builds that layer from the bottom up.

---

## What This Repository Contains

This repo holds the full technical specification and architecture for the AgentMarket platform:

| Document | Description |
|---|---|
| [Business Plan & Technical Spec](#business-plan--technical-specification) | Full product architecture, token economy, API design, investor brief |
| [AI Review Summary Layer](#ai-review-summary-layer) | Domain-aware structured review summaries as a trust engine |
| [Mitigation Loop Architecture](#mitigation-loop-architecture) | How platform weaknesses become content generation engines |

---

## Business Plan & Technical Specification

**VISION:** AgentMarket is the first phase of a four-level vertical ascent:

| Level | Product Layer | Timeline |
|---|---|---|
| 1 | Skill Creation Files + Complete Skills Marketplace | Now — Month 6 |
| 2 | Workflow Templates (n8n, Zapier, Make.com) | Month 3 – Year 1 |
| 3 | Design Templates for Agentic Interfaces | Year 1 – 2 |
| 4 | Full Agentic OS — UI/UX infrastructure for AI | Year 2 – 4 |

### The Problem

Agentic AI platforms (AutoGPT, LangGraph, CrewAI, Claude, n8n AI agents) are proliferating rapidly. Every team faces the same three problems:

- **Generic skills produce generic results** — a data analysis skill built for everyone works perfectly for no one.
- **Building custom skills from scratch** requires deep technical knowledge most users don't have.
- **No trusted, ranked repository** of agent skills, creation frameworks, or workflow templates — every team reinvents the wheel.

### The Solution: 3-Tier Product Structure

| Tier | Product | User Type | Value Proposition |
|---|---|---|---|
| 1 | Skill Creation Files | Power users, AI developers | Framework/description to synthesise a custom-fit skill using their own agent |
| 2 | Complete Skills | Beginners, busy professionals | Ready-to-use skills for immediate deployment |
| 3 | Workflow Templates | Automation builders, SMBs | n8n, Zapier, Make.com templates for full agent pipelines |

### The 4-File Synthesis Model (Core Innovation)

The platform's core innovation: a user browses the marketplace, selects up to 4 Skill Creation Files relevant to their domain, pastes them into their agent, and has a discussion with the agent to synthesise a near-perfect custom skill.

- The platform does **not** do the customisation — the user's own AI does.
- Each person gets a **different output** from the same files, preserving the value of the source descriptions.
- Files remain **platform-agnostic** — they work with Claude, GPT-4, Gemini, DeepSeek, or any instruction-following model.
- Contributors **cannot be easily undercut** — their description files gain reputation over time through rankings.

### Product Architecture

#### Marketplace Core

| Component | Function |
|---|---|
| File Registry | Stores metadata, descriptions, tags, pricing, contributor ID for every asset |
| Token Wallet | Per-user balance tracked in PostgreSQL; transactional ledger for audit |
| Ranking Engine | Composite score: downloads (40%) + verified user ratings (40%) + report rate (20%) |
| Review Queue | New uploads enter a pending state; auto-flagged by keyword filter + community reports |
| Contributor Profile | Reputation score, total earnings, published files, badges, verified status |
| Search & Discovery | Tag-based + semantic search; category filters; trending and top-ranked feeds |

#### API Layer (B2B Backbone)

| Endpoint | Method | Description |
|---|---|---|
| `/api/v1/files` | GET | List files with filters (category, rank, price, tags) |
| `/api/v1/files/:id` | GET | Retrieve full file metadata and description |
| `/api/v1/files/:id/download` | POST | Download file — deducts tokens, logs usage |
| `/api/v1/search` | GET | Semantic + tag search across all files |
| `/api/v1/recommend` | POST | AI-powered: submit a goal, receive 4 suggested files |
| `/api/v1/tokens/balance` | GET | Current token balance for authenticated user |
| `/api/v1/workflows` | GET | List workflow templates by platform |

#### Token Economy

| Flow | Mechanism |
|---|---|
| User buys tokens | Fiat → tokens at fixed rate (e.g. 100 tokens = $1.00) |
| User downloads file | Token deducted; contributor credited; platform fee taken |
| Contributor earns | 70% of file price in tokens; redeemable for fiat monthly |
| Platform revenue | 30% spread on all transactions + API subscription fees |
| Anti-inflation | Demand-driven supply (bought only when needed, not pre-minted at scale) |
| Quality staking (v2) | Contributors stake tokens to publish; lose stake if file is flagged |

#### Ranking System

- **Download velocity (40%)** — weighted toward recent downloads, not all-time totals
- **Verified user ratings (40%)** — only users who downloaded and used the file can rate it
- **Community health (20%)** — inverse of report rate
- **Contributor reputation bonus** — verified experts receive a 5–10% rank boost

### MVP Technical Specification

#### Stack

| Component | Technology | Rationale |
|---|---|---|
| Containerisation | Docker + Docker Compose | Portable, consistent, hand-off ready for any VPS |
| Workflow Engine | n8n (self-hosted) | Visual automation, handles all business logic flows |
| AI Engine | DeepSeek API | Fraction of OpenAI cost, strong reasoning for synthesis |
| Backend API | FastAPI (Python) | Fast, async, auto-generates OpenAPI docs |
| Frontend (MVP) | React + Tailwind CSS | Component-based, fast to iterate, mobile responsive |
| Primary Database | PostgreSQL | Reliable ACID transactions for token ledger integrity |
| Cache / Sessions | Redis | Token balance caching, session management, rate limit |
| File Storage | MinIO (self-hosted S3) | S3-compatible, runs in Docker, no external cloud dependency |
| Authentication | JWT + refresh tokens | Stateless, API-compatible, works across web and agent clients |

#### Docker Compose Architecture

```
frontend — React app served via Nginx
api — FastAPI backend on port 8000
n8n — workflow engine on port 5678
postgres — primary database
redis — cache and session store
minio — file storage (S3-compatible)
nginx — reverse proxy routing all services
```

Deployment to a VPS requires only: `git clone → docker-compose up -d`.

#### Core n8n Workflow Flows

| Workflow | Trigger | Steps |
|---|---|---|
| User Registration | POST /register | Create user → generate wallet → send welcome email |
| Token Purchase | Payment webhook | Verify payment → credit wallet → log transaction |
| File Upload | POST /upload | Validate metadata → store file → add to review queue → notify admin |
| File Download | POST /download | Check balance → deduct tokens → credit contributor → return file → log usage |
| Ranking Update | Hourly CRON | Pull download + rating data → recalculate scores → update ranks |
| AI Recommend | POST /recommend | Accept user goal → DeepSeek prompt → return top 4 file IDs |
| API Key Generate | POST /api-keys | Create scoped API key → store hash → return to user |
| Contributor Payout | Monthly CRON | Sum balances → trigger payout → zero balance → email receipt |

#### Database Schema (Core Tables)

| Table | Key Columns |
|---|---|
| `users` | id, email, password_hash, wallet_balance, reputation_score, created_at |
| `files` | id, contributor_id, title, description, category, tags, price_tokens, rank_score, download_count, status |
| `transactions` | id, user_id, file_id, type (purchase/download/payout), amount, timestamp |
| `ratings` | id, user_id, file_id, score (1-5), review_text, verified_download (bool) |
| `api_keys` | id, user_id, key_hash, scope, monthly_limit, usage_count, active |
| `discussions` | id, file_id, user_id, parent_id, content, upvotes, created_at |
| `contributor_payouts` | id, contributor_id, amount, period, status, processed_at |
| `review_summaries` | id, file_id, summary_json, dimensions_json, generated_at |
| `companion_files` | id, file_id, companion_file_id, pair_strength, created_at |

#### AI Provider Abstraction

DeepSeek is the default provider. All AI calls route through a provider abstraction layer — the underlying model can be swapped via environment variable with zero code changes. Recommended: OpenRouter as the unified API gateway, enabling fallback to GPT-4o, Claude, or Gemini.

### Investor Brief

| Metric | Value |
|---|---|
| MVP Build Time | 4–6 weeks |
| MVP Capital Required | $500 – $1,000 |
| Investor Ask | $2,500 – $5,000 (6-month runway) |
| Suggested Equity | 5–10% or revenue share on first $50K |

#### Token Pricing

| Pack | Price | Value |
|---|---|---|
| Starter — 500 tokens | $4.99 | ~5–10 file downloads |
| Builder — 2,000 tokens | $17.99 | Best value for regular users |
| Pro — 10,000 tokens | $79.99 | Power users and small teams |
| Enterprise — custom | Custom | Unlimited or high-volume with API SLA |

#### Revenue Projections

| Period | Driver | Conservative |
|---|---|---|
| Month 1–2 | Soft launch, no paid marketing | $0 – $200 |
| Month 3 | ProductHunt + Reddit | $500 – $1,500 |
| Month 4–6 | API tier opens, workflow templates | $1,500 – $4,000/mo |
| Month 7–12 | Enterprise API + growing contributors | $5,000 – $15,000/mo |
| Year 2 | Design templates + partnerships | $20,000 – $60,000/mo |

### Revenue Streams

| Stream | Model | Margin |
|---|---|---|
| Token Sales | Pay-per-download (30% platform fee) | ~70% |
| API — Starter | $29/mo — 1,000 fetches | ~85% |
| API — Pro | $99/mo — 10,000 fetches | ~85% |
| API — Enterprise | Custom pricing + SLA | ~80% |
| Workflow Templates | Token + subscription bundles | ~75% |
| Design Templates (Y1–2) | Per-template + design system license | ~90% |
| Complete Skill Bundles | Domain packs (e.g. 'Finance AI Stack') | ~80% |
| White Label (Y2+) | Platform white-label for enterprises | ~60% |

### Go-to-Market Strategy

**Phase 1: Seeding (Month 1–2)**
- Recruit 10–15 domain expert contributors before public launch
- Offer: founding contributor status + 100% revenue share for first 3 months
- Manually curate 20–30 high-quality skill creation files across 5 core categories

**Phase 2: Launch (Month 3)**
- ProductHunt launch — target top 5 in Developer Tools
- Reddit: r/n8n, r/ChatGPT, r/LocalLLaMA, r/SideProject, r/MachineLearning
- X/Twitter — demo video showing 4-file synthesis workflow

**Phase 3: API & B2B (Month 4–6)**
- Open API tier publicly with self-serve key generation
- Target developers building agent dashboards — offer 1 month free API access
- n8n and Zapier ecosystem builders directly

### Competitive Moat

| Moat | Build Time |
|---|---|
| Network effects (two-sided marketplace) | 3–6 months |
| Data moat (proprietary usage patterns) | Ongoing from day 1 |
| Reputation system (contributor trust scores) | 6–12 months |
| Community lock-in (discussion threads, relationships) | 6–12 months |
| API integration (switching cost for developers) | Month 3 onwards |
| First-mover in category | Diminishes — must exploit fast |
| Design system standard (Material Design for agents) | Year 1–2 |

### Competitive Landscape

| Competitor | What They Do | Where AgentMarket Wins |
|---|---|---|
| PromptBase | Sells prompts for ChatGPT/Midjourney | No synthesis workflow, no rankings, no API, no community |
| Hugging Face | Model and dataset repository | Not focused on skills/workflows; no token economy; no design layer |
| Unity Asset Store | Game assets marketplace | Not AI-native; validates the model but leaves agent market unaddressed |
| n8n Template Library | Built-in n8n templates | Platform-locked to n8n only; no token economy; no cross-platform synthesis |
| LangChain Hub | Prompt and chain repository | Developer-only; no consumer tier; no design layer; no token economy |

### Milestones

| Phase | Period | Milestone | Success Metric |
|---|---|---|---|
| Build | Week 1–2 | Docker + n8n + FastAPI + PostgreSQL running | All 8 n8n flows operational; API returns files |
| Build | Week 3–4 | Frontend MVP: browse, upload, purchase, download | End-to-end token transaction works |
| Seed | Month 2 | 10–15 high-quality creation files across 5 categories | Files pass internal quality review |
| Seed | Month 2 | Investor demo with live working product | Capital secured: $2,500 – $5,000 |
| Launch | Month 3 | VPS deployment + ProductHunt launch | 500+ upvotes; 200+ registrations |
| Growth | Month 4 | API tier open: self-serve key generation | 10+ active API integrations |
| Expand | Month 5–6 | Workflow template category live | 50+ templates; $1,500+/mo revenue |
| Scale | Month 7–12 | Enterprise API; contributor payout system | $5,000+/mo revenue; 50+ active contributors |
| Design | Year 1–2 | Agent interface design template system | 10+ startups licensing the design system |
| OS | Year 2–4 | Agentic OS beta: browser-based shell | 1,000+ active daily users |

### Long-Term Vision: Agentic OS

The AI industry in 2024–2026 has invested billions in models and agent frameworks. What it has not invested in is the **experience layer** — the interface, design language, and operating environment that makes agents accessible, trustworthy, and usable.

| Problem | Current State | What the Agentic OS Solves |
|---|---|---|
| No standard agent UI | Every team builds a bespoke dashboard | Standardised components and patterns |
| Agent state is invisible | Users cannot see what their agent is doing | Real-time status visualisation layer |
| Memory is opaque | No UI convention for displaying agent memory | Memory browser interface standard |
| Permissions are confusing | No standard trust/safety UX exists | Consistent permission grant/revoke flow |
| Async breaks normal UI | Buttons/forms not designed for 20-min tasks | Async-native UI patterns and components |
| Multi-agent is chaotic | No standard for agent-to-agent communication | Agent communication thread component |

**Historical Parallel:**
- 1984 — Apple Macintosh: desktop metaphor (windows, icons, menus, pointer)
- 2008 — iOS/App Store: mobile app design language (tap, swipe, icons on grid)
- 2013 — Google Material Design: standardised Android app interfaces
- **2026+ — Nobody has established the agentic interface language yet**

#### Agentic OS Architecture

- **Agent Registry** — installed agents as first-class OS citizens, like apps on a home screen
- **Task Manager** — async-native job queue with live status, progress, interrupt controls
- **Knowledge Layer** — replaces traditional file system with memory/context management
- **Permission Manager** — unified trust dashboard for agent tool/data access
- **Skill Store** — direct integration with AgentMarket marketplace
- **Agent Communication Log** — multi-agent coordination as readable thread format
- **Human-in-the-Loop Console** — standardised interface for agent requests for input

---

## AI Review Summary Layer

**A domain-aware structured review system that functions as a trust engine for the marketplace.**

### Why This Matters

Generic review summarisers say "users liked this." AgentMarket's can say: *"This data analysis creation file showed strong performance in financial reporting workflows but users noted it needed refinement for real-time streaming data."*

That specificity is the difference between a feature and a trust engine.

### The Structured Summary Panel

Every file page displays an AI-generated summary derived from all user reviews:

```
📊 DATA ANALYSIS SKILL CREATION FILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⭐ 4.7  •  143 reviews  •  Updated 2 days ago

"Strong performance for structured data cleaning and
financial reporting. Users consistently report faster
insight generation. Works best when combined with a
visualisation workflow template."

WHAT IT EXCELS AT          WHAT TO WATCH
✓ CSV and Excel analysis   ⚠ Real-time streaming data
✓ Financial reporting      ⚠ Unstructured text inputs
✓ Dashboard preparation    ⚠ Needs a SQL file to pair

BEST COMBINED WITH
→ SQL Query Creation File (87% of users pair these)
→ Data Visualisation Template
```

### Extracted Review Dimensions

| Dimension | What It Captures | Example Output |
|---|---|---|
| Performance | How well the synthesised skill works | "Consistently strong for tabular data, variable for text" |
| Ease of synthesis | How easy the 4-file method was with this file | "Straightforward to combine — clear instructions" |
| Agent compatibility | Which agents users tested it on | "Best results on Claude and GPT-4o, limited on smaller models" |
| Use case fit | Which domains it actually works for | "Finance and marketing strong, scientific data needs pairing" |
| Time to results | How quickly users got a working skill | "Most users had a working skill within 20 minutes" |
| Pairing insights | Which other files users combined it with | "87% paired with SQL Creation File" |
| Iteration needed | How much back-and-forth with the agent was required | "Low iteration — 1-2 synthesis rounds typical" |

### Technical Pipeline

```
New review submitted by verified user
        ↓
Stored in reviews table with structured metadata
        ↓
Review aggregation trigger fires (every 10 new reviews
OR every 24 hours, whichever comes first)
        ↓
n8n workflow pulls all reviews for that file
        ↓
DeepSeek prompt analyses batch with domain-aware context:
  - File category fed as context
  - Structured output requested (JSON)
  - Extracts: strengths, weaknesses, use case fit,
    compatibility, pairing suggestions
        ↓
Summary stored in file_summaries table
        ↓
File page updates summary panel in real time
        ↓
Contributor receives notification:
"Your file has new review insights —
 users are pairing it with SQL Creation File 87% of the time"
```

### Why This Helps Every Stakeholder

**For buyers** — eliminates review paralysis. One panel tells them whether this file fits their use case. Conversion goes up.

**For contributors** — the summary becomes a feedback loop. A contributor who sees "weak on real-time streaming data" knows exactly what to address in v2.

**For the platform** — review summaries become SEO content. A user Googling "best data analysis skill for n8n agents" lands on a file page because the summary naturally contains that language.

**For the ranking engine** — structured dimensions feed directly into ranking signals. A file with "low iteration needed" and "strong agent compatibility" ranks higher.

### The Verified Review Gate

Only users who have actually downloaded and used the file can leave a review. The review form is structured:

```
Rate your experience: ★★★★★

Which agent did you use this with?
○ Claude  ○ GPT-4o  ○ Gemini  ○ DeepSeek  ○ Other

What did you use it for?
○ Data analysis  ○ Marketing  ○ Coding  ○ Research  ○ Other

Did you combine it with other files?
○ Yes → which ones? [dropdown of marketplace files]
○ No

How many synthesis rounds did it take?
○ 1-2  ○ 3-5  ○ 5+

Write your review: [________________________]
```

This structured input makes the AI summary dramatically more accurate because it is working with semi-structured data, not just unstructured prose.

### Contributor Response Feature

Contributors can post a public response to the review summary, similar to App Store developer responses:

> "Thanks for the streaming data feedback — v2 of this file now includes a real-time data handling section. Re-test and let me know if it solves the issue."

This signals an active, responsive contributor — improving trust and ranking simultaneously.

### Review Prompt

After a user has been active for 7 days post-download:

> *"How did your agent handle the synthesis? Share what worked — even the mitigations you found — so the next person starts further ahead."*

Not "leave a review." Not "rate this file." *Share what worked.* This framing gets qualitative, process-aware responses rather than star ratings and one-liners.

---

## Mitigation Loop Architecture

**How the platform's weaknesses become its content generation engine.**

### The Core Loop

```
User reads review summary on file page
        ↓
Summary shows: "Weak on real-time streaming data"
        ↓
User pastes file into agent dashboard
        ↓
User prompts: "Research how we can mitigate
the real-time streaming data limitation"
        ↓
Agent searches, finds solutions, synthesises fixes
        ↓
User incorporates improvements into their skill file
        ↓
User now has a custom-optimised skill
        ↓
User feels genuine accomplishment — they built this
        ↓
User leaves an authentic, detailed review
        ↓
Review improves the summary for the next person
        ↓
Next person sees more specific mitigation guidance
```

### Why This Loop Is Psychologically Brilliant

The accomplishment is real, not synthetic. Most platforms try to manufacture engagement. This one generates it naturally because the user genuinely did something — they identified a gap, researched a solution, and built something better.

| Platform Type | Review Motivation | Review Quality |
|---|---|---|
| App Store | "I used this, here's my opinion" | Surface level |
| Amazon | "I bought this, it worked/didn't" | Product focused |
| **AgentMarket** | **"I built something with this and improved it"** | **Deep, specific, process-aware** |

### The Language Pattern

Review summary phrases become naturally researchable:

- "showed limited performance on real-time data"
- "needs refinement for unstructured text inputs"
- "works best when paired with a SQL query file"

These are agent-ready research prompts. The platform pre-writes the user's research brief without them realising it.

| Bad Summary Language | Good Summary Language |
|---|---|
| "Does not work well with streaming data" | "Real-time streaming data handling can be improved — users have found mitigation strategies worth exploring" |
| The good version is an invitation. | The bad version is a verdict. |

### The Cascade Effect

Every user who researches and solves a mitigation has two options:

**Option A** — keep it to themselves, just write a review.

**Option B** — publish their mitigation as a new Skill Creation File on the marketplace.

Option B turns platform weaknesses into a content generation engine:

```
File has a known weakness (visible in review summary)
        ↓
Multiple users research mitigations independently
        ↓
Some users publish their mitigation as a new file
        ↓
New file gets tagged as "pairs well with [original file]"
        ↓
Original file's review summary updates:
"Mitigation available — see [new file]"
        ↓
Both files get downloads
        ↓
Both contributors earn tokens
        ↓
Platform catalogue grows organically from its own gaps
```

### Impact on Contributor Economy

Contributors no longer need to create perfect, complete files. They can create **intentionally scoped files** — deep and excellent at one thing — knowing that:

- The review summary will honestly describe the scope
- Users will research mitigations for anything outside that scope
- Some of those mitigations become companion files
- The original contributor's file gets a "pairs with" tag driving cross-purchases

Focused files + community-researched mitigations + companion file tags = a collaborative catalogue that grows with nuance.

### The Trust Architecture

| Transparency | User Agency |
|---|---|
| Review summary shows gaps | User researches the gaps |
| Weaknesses stated clearly | Weaknesses become prompts |
| No file is oversold | User sets their own expectations |
| Platform shows what's hard | User feels capable of solving it |

Trust usually comes from either perfection (everything works) or honesty (here's what doesn't work). Most platforms try to sell perfection. AgentMarket's architecture sells honesty — and then gives the user the tools to address the imperfections themselves.

### Business Plan Updates

This concept strengthens three areas:

**Moat** — the mitigation research loop means the platform's value compounds with every user session. Usage data, review language, and companion file relationships are proprietary assets that deepen over time.

**Retention** — users who feel accomplished with a file don't churn. They come back to find the next file to improve. The agent research session creates investment in the outcome.

**Contributor acquisition** — contributors see their files improve through community research. The review summary becomes a product roadmap for v2 of their file. That's a professional tool serious contributors want access to.

---

## Vertical Integration

Each layer of the product stack feeds the next:

| Level | Layer | What It Produces for the Next Level |
|---|---|---|
| 1 | Skill Creation Files + Marketplace | Usage data: which domains need skills; which synthesis patterns work |
| 2 | Workflow Templates | End-to-end automation patterns; most valuable agent pipelines |
| 3 | Design Templates for Agent Interfaces | Standardised UI components from real workflow data |
| 4 | Agentic OS | Unified operating environment from accumulated knowledge |

### The Flywheel

Skill creation files build community → community creates complete skills → skills get wrapped into workflows → workflow data defines design templates → design templates become the Agentic OS → the OS runs on the marketplace → new users enter through the OS and feed the marketplace.

---

## Risk Analysis

| Risk | Severity | Mitigation |
|---|---|---|
| Cold start — not enough quality files | High | Manually seed 20–30 files; recruit 10 domain experts as founding contributors |
| DeepSeek API instability / geopolitical risk | Medium | Provider abstraction via OpenRouter; GPT-4o or Claude as fallback |
| Token economy inflation | Medium | Demand-driven supply; monthly payout caps in early phase |
| Quality floods from junk uploads | Medium | Review queue; staking mechanism (v2); community reports |
| Platform fragmentation (n8n vs Zapier vs LangGraph) | Low | Description files are platform-agnostic; templates tagged by platform |
| Larger competitor copies the model | Medium | Build community and reputation data as fast as possible — the network is the moat |
| VPS goes down / data loss | Low | Daily automated backups; Docker volumes; documented restore procedure |

---

**AgentMarket is being built at the optimal intersection of timing, technical feasibility, and market need. The window to own the agentic asset infrastructure layer is open now.**
