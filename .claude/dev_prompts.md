# Ready-to-Run Claude CLI Prompts (FastAPI + PostgreSQL)

---

## 🗓 Day 1 — Environment Setup
```bash
claude ask "
Goal: Create FastAPI backend environment.

Tasks:
1. Initialize Python virtual environment.
2. Install FastAPI, Uvicorn, and basic deps.
3. Create folder structure and main.py.
4. Add /ping route and enable CORS for Vercel frontend.
5. Update .claude/changelog.md.

Deliverables:
- Working FastAPI app at localhost:8000
"
## 🗓 Day 2 — Auth System
claude ask "
Goal: Implement user auth (JWT + password hashing).

Tasks:
1. Add models/User.py.
2. Add /auth/register, /auth/login, /auth/me routes.
3. Use SQLAlchemy async engine for Postgres.
4. JWT with python-jose and bcrypt hashing.
5. Update changelog.md.
"
## 🗓 Day 3 — Onboarding Data
claude ask "
Goal: Build onboarding routes.

Tasks:
1. Create schemas and models for LifestyleData and HealthData.
2. Add /onboarding/lifestyle and /onboarding/health.
3. Save data to DB with foreign key to User.
4. Return computed eco_score and wellness_score.
"
## 🗓 Day 4— Dashboard & Analytics
claude ask "
Goal: Implement dashboard and analytics endpoints.

Tasks:
1. Create dashboard service to aggregate user meal/activity data.
2. Add analytics routes to compute carbon & wellness scores.
3. Return formatted JSON for React frontend.
"
## 🗓 Day 5 — Meal Plan Generator
claude ask "
Goal: Create async meal plan generation system.

Tasks:
1. Setup Redis + Celery.
2. Add meal_plan_service.py for async jobs.
3. Add POST /meal-plans/generate route.
4. Save generated data to DB.
"