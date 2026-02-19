# API Gateway Service Documentation

## Overview

The API Gateway is the **main public API** for the application, handling authentication, routing, and serving as the entry point for all client requests.

| Property | Value |
|----------|-------|
| Port | 3000 |
| Framework | Express.js |
| Language | TypeScript |
| Package Name | `@rapidquest/api-gateway` |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Express.js |
| Validation | Zod |
| Auth | JWT (jsonwebtoken), bcryptjs |
| Database | Mongoose (MongoDB), pg (PostgreSQL) |
| Cache/Queue | Redis |
| Security | Helmet, CORS, express-rate-limit |
| Logging | Pino, pino-http |
| Metrics | prom-client (Prometheus) |
| Reports | pdfmake, json2csv |
| Email | nodemailer |
| WebSockets | ws |
| Scheduler | node-cron |

---

## Directory Structure

```
api-gateway/src/
├── app.ts              # Express app setup, middleware
├── server.ts           # Server entry point
├── config/             # Environment config
├── db/                 # Database connections, migrations
│   ├── models/         # MongoDB models (via modules)
│   ├── migrations/     # PostgreSQL migrations
│   └── postgres.ts     # PostgreSQL client
├── middleware/         # Auth, rate limiting, error handling
├── routes/             # Route definitions
│   ├── auth.routes.ts
│   ├── brand.routes.ts
│   ├── ai.routes.ts
│   ├── alert.routes.ts
│   ├── competitor.routes.ts
│   ├── health.routes.ts
│   └── metrics.routes.ts
├── modules/            # Feature modules (14 total)
│   ├── admin/          # Admin dashboard
│   ├── alerts/         # Alert management
│   ├── auth/           # Authentication
│   ├── brand/          # Brand management
│   ├── competitors/    # Competition tracking
│   ├── crisis/         # Crisis detection
│   ├── ingest/         # Data ingestion
│   ├── leads/          # Money Mode
│   ├── notifications/  # Email/push notifications
│   ├── queue/          # Job queue
│   ├── reports/        # Report generation
│   ├── socket/         # WebSocket handlers
│   ├── stats/          # Statistics API
│   └── team/           # Team management
├── services/           # Business logic services
│   └── llm.service.ts  # Direct LLM access (Groq/NVIDIA)
├── types/              # TypeScript types
└── utils/              # Utilities, logger
```

---

## Route Groups

| Path Prefix | Router | Purpose |
|-------------|--------|---------|
| `/health` | healthRouter | Health checks |
| `/metrics` | metricsRouter | Prometheus metrics |
| `/api/auth` | authRouter | Authentication |
| `/api/brands` | brandRouter | Brand CRUD & data |
| `/api/*` | alertRouter | Alert management |
| `/api/*` | competitorRouter | Competitor management |
| `/api/v1/admin` | adminRouter | Admin dashboard |
| `/api/v1/leads` | leadsRouter | Money Mode |
| `/api/v1/crisis` | crisisRouter | Crisis Thermometer |
| `/api/v1/competitors` | competitorsRouter | Market Gap Analysis |
| `/api/v1/ingest` | ingestRouter | Data ingestion |
| `/api/v1/ai` | aiRouter | Direct LLM access |
| `/api/stats` | statsController | Statistics |
| `/api/brands/:brand/reports` | reportsRouter | Reports |
| `/api/brands/:brand/team` | teamRouter | Team |

---

## Key Modules

### Auth Module
- User registration/login
- JWT token management
- Email verification
- Password hashing (bcrypt)

### Brand Module
- Multi-brand management
- Mentions, analytics, trends
- Live feed, influencers
- Suggestions, entities

### Leads Module (Money Mode)
- Sales lead detection
- Intent scoring
- Lead status tracking
- AI-generated pitches

### Crisis Module
- Risk score calculation
- Velocity tracking
- Event logging

---

## LLM Service

Direct AI access without Worker roundtrip:

```typescript
// Providers (priority order)
1. Groq (GROQ_API_KEY)
2. NVIDIA NIM (NVIDIA_API_KEY)
3. OpenRouter (OPENROUTER_API_KEY)

// Functions
chat(messages, temperature)      // Generic completion
generateSalesPitch(brand, text)  // Money Mode pitches
quickSentiment(text)             // Fast sentiment
getProviderStatus()              // Check active provider
```

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Server port (default: 3000) |
| `MONGODB_URI` | MongoDB connection |
| `POSTGRES_URL` | PostgreSQL connection |
| `REDIS_URL` | Redis connection |
| `JWT_SECRET` | JWT signing key |
| `JWT_EXPIRES_IN` | Token expiry (default: 7d) |
| `ALLOWED_ORIGINS` | CORS origins |
| `RATE_LIMIT` | Requests per minute |
| `GROQ_API_KEY` | Groq LLM (Money Mode) |
| `NVIDIA_API_KEY` | NVIDIA NIM LLM |
| `OPENROUTER_API_KEY` | OpenRouter fallback |

---

## Scripts

```bash
npm run dev    # Development with hot reload
npm run build  # Compile TypeScript
npm run start  # Run production build
npm run test   # Run Jest tests
```
