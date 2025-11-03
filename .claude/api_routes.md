# API Routes Overview (Backend)

## Auth
- POST /auth/register
- POST /auth/login
- GET /auth/me

## Onboarding
- POST /onboarding/lifestyle
- POST /onboarding/health

## Dashboard
- GET /dashboard/{user_id}

## Analytics
- GET /analytics/score/{user_id}
- GET /analytics/recommendations/{user_id}

## Meal Plans
- POST /meal-plans/generate

## Subscriptions
- POST /subscriptions/create
- GET /subscriptions/status/{user_id}

## Reports & Content
- GET /reports/weekly/{user_id}
- GET /content/tips
- GET /content/achievements/{user_id}
