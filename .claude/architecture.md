# Architecture Overview

## Core Flow
Frontend (React/Vercel) → Backend (FastAPI/Heroku) → Database (PostgreSQL)
                      ↓
                    AI Service (Meal & Carbon scoring)

## Modules
- `auth` → User management, JWT
- `onboarding` → Collect eco + health data
- `dashboard` → Aggregate metrics
- `analytics` → Carbon and wellness scores
- `meal_plans` → Generate and store meal plans
- `subscriptions` → Stripe-based payments
- `content` → Tips, badges, insights
- `reports` → Weekly summaries

## Data Flow Example: Login
1. User → POST /auth/login
2. FastAPI verifies credentials via DB (hashed passwords)
3. JWT generated and sent back
4. Frontend stores token (localStorage)
5. Authenticated requests → include Bearer token

## DevOps
- CI/CD: GitHub Actions
- Deploy: Heroku with Procfile
- DB Migrations: Alembic
- Monitoring: Logtail / Sentry (future)
