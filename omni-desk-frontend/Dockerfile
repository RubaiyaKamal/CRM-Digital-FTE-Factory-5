# ============================================================================
# Multi-Stage Dockerfile for Next.js Frontend (omni-desk-frontend)
# ============================================================================
# Target size: <200MB (optimized with standalone output)
#
# Usage:
#   docker build -t crm-fte-frontend:latest .
#   docker run -p 3000:3000 -e API_BASE_URL=http://backend:8000 crm-fte-frontend
#
# ============================================================================

# ============================================================================
# Stage 1: Dependencies (Production Only)
# ============================================================================
FROM node:20-alpine AS deps

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install only production dependencies for the final image
RUN npm ci --only=production

# ============================================================================
# Stage 2: Builder (All Dependencies)
# ============================================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json* ./

# Install ALL dependencies (including devDependencies for building)
RUN npm ci

# Copy application code
COPY . .

# Set environment variables for build
# These can be overridden at runtime
ENV NEXT_TELEMETRY_DISABLED=1

# Build Next.js application with standalone output
RUN npm run build

# ============================================================================
# Stage 3: Runner - Minimal production image
# ============================================================================
FROM node:20-alpine AS runner

WORKDIR /app

# Set to production
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/', (res) => process.exit(res.statusCode === 200 ? 0 : 1))"

# Start Next.js
CMD ["node", "server.js"]
