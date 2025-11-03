# Project Context — ECOLIFE Backend (FastAPI + PostgreSQL)

## Purpose
This backend powers the ECOLIFE web platform, helping users optimize diet and habits for better health and lower carbon footprint.

- Frontend: React + TypeScript (Vercel)
- Backend: FastAPI (Heroku)
- Database: PostgreSQL
- AI/ML: Python integration for recommendations
- Caching/Async: Redis (for Celery, optional)

## Current Scope
Core features include:
- Authentication (JWT-based)
- Onboarding data collection (eco + health)
- Dashboard stats
- Analytics & scoring
- Meal & activity plans
- Subscription handling (Stripe)
- Reports and content delivery

## Key Libraries
- fastapi
- uvicorn
- sqlalchemy[asyncio]
- psycopg2-binary
- alembic
- pydantic
- passlib[bcrypt]
- python-jose
- python-dotenv
- celery[redis]
- stripe

## Directory Convention
- `app/main.py` → Application entrypoint
- `app/routes/` → API routes
- `app/models/` → SQLAlchemy models
- `app/schemas/` → Pydantic schemas
- `app/db/session.py` → DB session and engine
- `app/services/` → Business logic
- `app/utils/` → Helpers (auth, response, etc.)
- `tests/` → Pytest integration tests

## Deployment Targets
- Backend → Heroku
- Database → Heroku Postgres
- Cache (future) → Redis Cloud
