# Orchestrator Service Documentation

## Overview

The Orchestrator is a **high-performance coordination service** built with **Fastify** that manages task distribution, result aggregation, and summary generation.

| Property | Value |
|----------|-------|
| Port | 9000 |
| Framework | Fastify 4.28 |
| Language | TypeScript (ESM) |
| Package Name | `service3-orchestrator` |

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Framework | Fastify |
| Queue | ioredis (Redis) |
| Validation | Zod |
| Logging | Pino |
| Metrics | prom-client |
| Concurrency | p-limit |
| Security | @fastify/cors, @fastify/helmet |

---

## Directory Structure

```
orchestrator/src/orchestrator/
├── app.ts              # Fastify app initialization
├── config.ts           # Environment configuration
├── aggregator.ts       # Result aggregation logic
├── brand_registry.ts   # Brand tracking registry
├── health.ts           # Health check endpoints
├── logger.ts           # Pino logger setup
├── metrics.ts          # Prometheus metrics
├── redis_client.ts     # Redis connection
├── result_collector.ts # Collect worker results
├── summary_generator.ts # AI summary generation
├── types.ts            # TypeScript types
├── utils.ts            # Utility functions
├── http/               # HTTP route handlers
├── interfaces/         # Interfaces
└── processing/         # Processing pipelines
```

---

## Core Responsibilities

1. **Brand Registry**: Track active brands and their monitoring status
2. **Task Distribution**: Dispatch tasks to workers via Redis queues
3. **Result Collection**: Gather processed results from workers
4. **Summary Generation**: Create AI-powered summaries of mentions
5. **Health Monitoring**: Track system health and worker status
6. **Metrics Export**: Prometheus-compatible metrics endpoint

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PORT` | Server port (default: 9000) |
| `REDIS_URL` | Redis connection string |
| `LOG_LEVEL` | Logging level (debug/info/warn/error) |

---

## Scripts

```bash
npm run dev    # Development with tsx watch
npm run build  # Compile TypeScript
npm run start  # Run production build
npm run test   # Run Vitest tests
```
