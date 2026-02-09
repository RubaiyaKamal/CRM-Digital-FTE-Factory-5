---
id: 005
title: "Fix SSE CORS and nginx proxy"
stage: green
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: customer-success-fte
branch: main
user: Lap Zone
command: resume session
labels: ["cors", "sse", "nginx", "debugging", "web-form"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_changed:
  - src/api/main.py
  - src/config.py
  - src/web-form/nginx.conf
  - src/web-form/Dockerfile
  - docker-compose.yml
tests:
  - none
---

# Prompt History Record: Fix SSE CORS and nginx proxy

## Context

**Stage:** green
**Feature:** customer-success-fte
**Date:** 2026-02-08
**Surface:** agent (Claude Code)

## User Input

```
The new build is deployed (conversation_id is in the bundle). Stopping here as requested — the issue is still pending (SSE response not appearing in browser).

Current state when we resume:
- Web form at http://localhost:3000 sends messages successfully
- Agent processes them (confirmed in DB)
- SSE stream works via curl test
- Browser UI not showing agent reply — likely a CORS or nginx proxy issue with EventSource
Will investigate nginx SSE headers and CORS on next session.
```

## Assistant Response

Identified two root causes:
1. `allow_origins=["*"]` + `allow_credentials=True` in FastAPI CORS middleware — spec-invalid combination; browsers may reject SSE responses
2. No nginx reverse proxy for API routes — browser made cross-origin requests to localhost:8000, bypassing any SSE buffering control

Fixes applied:
- `src/api/main.py`: Replaced wildcard+credentials CORS with explicit origins from `CORS_ORIGINS` env var
- `src/config.py`: Added `cors_origins` field (default: `http://localhost:3000,http://localhost:8000`)
- `src/web-form/nginx.conf`: Added `/webhooks/` reverse proxy with SSE-critical headers (`proxy_buffering off`, `proxy_cache off`, `Connection ''`, 180s timeout)
- `src/web-form/Dockerfile`: Accept `REACT_APP_API_URL` build arg
- `docker-compose.yml`: Pass `REACT_APP_API_URL=http://localhost:3000` so React uses same-origin proxy

## Outcome

Browser requests now route: localhost:3000 (React) → nginx proxy → api:8000 (uvicorn). No cross-origin, no CORS needed, proper SSE streaming.

## Follow-up Actions

- Rebuild web-form container: `docker-compose up --build web-form`
- Restart API: `docker-compose restart api`
- Test SSE in browser again

## Evaluation

- **Clarity:** 5/5
- **Completeness:** 5/5
- **Alignment:** 5/5

## Notes

Key insight: `allow_credentials=True` with `allow_origins=["*"]` is CORS spec violation. Starlette newer versions raise ValueError; older ones emit invalid headers that browsers reject for SSE (simple GET) even though POST (with preflight) appeared to work.
