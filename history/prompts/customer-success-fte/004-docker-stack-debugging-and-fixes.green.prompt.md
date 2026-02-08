---
id: "004"
title: "Docker Stack Debugging and Fixes"
stage: green
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5-20250929
feature: customer-success-fte
branch: main
user: architect
command: "docker-compose up --build"
labels: ["docker", "debugging", "port-conflicts", "kafka", "schema", "tsconfig", "credentials-security"]
links:
  spec: specs/customer-success-fte/spec.md
  ticket: null
  adr: null
  pr: null
files_changed:
  - src/web-form/tsconfig.json
  - .env.example
  - requirements.txt
  - docker-compose.yml
  - src/database/schema.sql
tests: []
---

# Prompt History Record: Docker Stack Debugging and Fixes

## Context

**Stage:** green
**Feature:** customer-success-fte
**Date:** 2026-02-08
**Surface:** agent (Claude Code)

## User Input

```
docker-compose up --build
(multiple iterations to resolve failures)
push it
create a PHR for this session
```

## Assistant Response

Diagnosed and resolved a cascade of Docker runtime issues to bring the full 6-service stack to healthy status:

1. **Web-form React build failure** (`Can't resolve './App'`): Added missing `src/web-form/tsconfig.json` — react-scripts requires it to resolve `.tsx` files.

2. **Credentials leak prevention**: Detected real OpenAI API key and Twilio tokens committed to `.env.example`; reverted to safe placeholders.

3. **requirements.txt dependency conflict**: Old pinned versions (`pydantic==2.9.2`, `openai-agents==0.0.14`) incompatible with openai-agents 0.8.1. Switched to `>=` constraints.

4. **Port conflicts** (`storyforge-*` stack already occupying 2181, 9092/9093, 5432): Remapped host ports to 2182, 9094, 5433.

5. **Kafka health check timing**: JVM startup takes 3-4 minutes; added `start_period: 60s` and `retries: 10`.

6. **Schema idempotency** (`DuplicateObjectError` on trigger re-creation): Changed `CREATE TRIGGER` to `CREATE OR REPLACE TRIGGER` (PostgreSQL 14+).

All 6 services running: postgres (healthy), zookeeper (healthy), kafka (healthy), api (running), worker (running), web-form (running). API health check confirmed: `{"status":"healthy","env":"development"}`.

Commits pushed:
- `38f9a35` — tsconfig.json, requirements fix, safe .env.example
- `b2e3725` — docker-compose port remaps, idempotent schema, Kafka start_period

## Outcome

- Full docker-compose stack operational on development machine
- Web form accessible at http://localhost:3000
- API accessible at http://localhost:8000
- All fixes committed and pushed to origin/main

## Follow-up Actions

- Set real `OPENAI_API_KEY` in `.env` (gitignored) to enable live agent responses
- Rotate the OpenAI and Twilio credentials that were briefly in .env.example
- Consider adding `.dockerignore` for faster builds

## Evaluation

- **Clarity:** 5/5
- **Completeness:** 5/5
- **Alignment:** 5/5

## Notes

- Kafka (Confluent cp-kafka:7.5.0) consistently takes 3-4 minutes to become healthy due to JVM startup + ZooKeeper registration. `start_period` is essential to prevent false health check failures.
- Multiple competing Docker stacks on the same machine require explicit port remapping in docker-compose.yml — document occupied ports in README.
- `CREATE OR REPLACE TRIGGER` requires PostgreSQL 14+; safe since schema targets PostgreSQL 16.
- Never put real credentials in `.env.example` — always use placeholder strings.
