# =============================================================================
# Aggregator Dockerfile - Production Ready (Koyeb Compatible)
# =============================================================================
# Build context: REPOSITORY ROOT (Koyeb default)
# Usage: docker build -f aggregator/Dockerfile .
# =============================================================================

# Stage 1: Base
FROM node:20-alpine AS base
WORKDIR /app

# Stage 2: Dependencies (dev for build)
FROM base AS deps
COPY aggregator/package*.json ./
RUN npm ci --include=dev

# Stage 3: Build
FROM deps AS build
COPY aggregator/tsconfig*.json ./
COPY aggregator/src ./src
RUN npm run build

# Stage 4: Production Dependencies
FROM base AS production-deps
COPY aggregator/package*.json ./
RUN npm ci --omit=dev

# Stage 5: Runner (Production)
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Create non-root user
RUN addgroup -g 1001 -S appgroup && \
  adduser -S -G appgroup -u 1001 appuser

COPY --from=production-deps --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY aggregator/package*.json ./
COPY aggregator/.env.example ./

RUN chown appuser:appgroup ./package*.json ./.env.example

USER appuser

# Port (configurable via PORT env var, default 3001)
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD wget -qO- http://127.0.0.1:${PORT:-3001}/health || exit 1

CMD ["node", "dist/server.js"]
