# Meal Plan System - Day 5 Implementation

## Overview
The meal plan system uses **Celery + Redis** for asynchronous meal plan generation. This allows users to request a 7-day personalized meal plan without waiting, and check the status later.

---

## Architecture

### Components:
1. **FastAPI Backend** - API endpoints for meal plan requests
2. **PostgreSQL Database** - Stores meal plan data and status
3. **Redis** - Message broker and result backend for Celery
4. **Celery Workers** - Background workers that generate meal plans

### Flow:
```
1. User → POST /meal-plans/generate → FastAPI
2. FastAPI creates MealPlan record → PostgreSQL
3. FastAPI triggers Celery task → Redis queue
4. Celery Worker picks up task → Generates meal plan
5. Worker updates MealPlan record → PostgreSQL
6. User → GET /meal-plans/{id} → Returns completed meal plan
```

---

## Setup Instructions

### 1. Install Redis (if not already installed)

**Windows:**
```bash
# Download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases
# Or use WSL/Docker

# Using Docker (recommended):
docker run -d -p 6379:6379 redis:latest
```

**Mac:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

### 2. Verify Redis is Running
```bash
redis-cli ping
# Should return: PONG
```

### 3. Install Python Dependencies
Already done! Dependencies installed:
- celery[redis]==5.3.4
- redis==4.6.0
- flower==2.0.1

---

## Running the System

### Terminal 1: Start FastAPI Backend
```bash
cd E:\1\ CaludeCode\Ecolife_Backend
.\\venv\\Scripts\\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Start Celery Worker
```bash
cd E:\1\ CaludeCode\Ecolife_Backend
.\\venv\\Scripts\\python start_worker.py
```

### Terminal 3 (Optional): Start Flower (Celery Monitoring UI)
```bash
cd E:\1\ CaludeCode\Ecolife_Backend
.\\venv\\Scripts\\celery -A app.celery_app flower --port=5555
```
Then visit: http://localhost:5555

---

## API Endpoints

### 1. Generate Meal Plan (Async)
```http
POST /meal-plans/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "dietary_preference": "vegan",
  "calorie_target": 2000,
  "exclude_ingredients": ["nuts", "soy"]
}
```

**Response (202 Accepted):**
```json
{
  "id": 1,
  "task_id": "abc-123-def-456",
  "status": "pending",
  "message": "Meal plan generation started",
  "progress": 0
}
```

### 2. Check Status
```http
GET /meal-plans/status/{task_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "task_id": "abc-123-def-456",
  "status": "processing",
  "message": "Generating meals",
  "progress": 50
}
```

### 3. Get Completed Meal Plan
```http
GET /meal-plans/{meal_plan_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": 1,
  "user_id": 5,
  "status": "completed",
  "meals": [
    {
      "day": 1,
      "date": "2025-11-01",
      "breakfast": {
        "name": "Overnight Oats with Berries",
        "description": "Creamy oats...",
        "calories": 350,
        "protein": 12,
        "carbs": 58,
        "fats": 8,
        "carbon_footprint": 0.3,
        "ingredients": ["oats", "berries"],
        "cooking_time": 5
      },
      "lunch": { /* ... */ },
      "dinner": { /* ... */ },
      "total_calories": 1300,
      "total_carbon": 1.8
    },
    /* ... 6 more days */
  ],
  "dietary_preference": "vegan",
  "calorie_target": 2000,
  "total_calories_week": 9100,
  "total_carbon_week": 12.6,
  "avg_calories_day": 1300
}
```

### 4. Get User's Meal Plans
```http
GET /meal-plans/user/my-plans?limit=10&offset=0
Authorization: Bearer <token>
```

### 5. Delete Meal Plan
```http
DELETE /meal-plans/{meal_plan_id}
Authorization: Bearer <token>
```

---

## Database Schema

### meal_plans Table
```sql
CREATE TABLE meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    task_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'pending',
    meals JSONB,
    dietary_preference VARCHAR(100),
    calorie_target INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

---

## Meal Plan Features

### Supported Dietary Preferences:
- **vegan** - Plant-based only
- **vegetarian** - Includes dairy and eggs
- **pescatarian** - Vegetarian + fish
- **flexitarian** - Mostly plant-based with occasional meat
- **omnivore** - All food types
- **balanced** - Mix of everything

### Each Meal Includes:
- Name and description
- Calories, protein, carbs, fats
- Carbon footprint (kg CO2)
- Ingredients list
- Cooking time

### Weekly Summary:
- Total calories for the week
- Total carbon footprint
- Average daily calories

---

## Testing the System

### 1. Start Redis
```bash
# Check if Redis is running
redis-cli ping
```

### 2. Test Meal Plan Generation
```bash
# Use the FastAPI docs UI: http://localhost:8000/docs
# Or use curl:

curl -X POST "http://localhost:8000/meal-plans/generate" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "dietary_preference": "vegan",
    "calorie_target": 2000
  }'
```

### 3. Monitor Celery Tasks
Check Flower UI: http://localhost:5555

---

## Troubleshooting

### Issue: "Connection refused" to Redis
**Solution:** Make sure Redis is running:
```bash
redis-cli ping  # Should return PONG
```

### Issue: Celery worker not picking up tasks
**Solution:** Check worker logs and ensure queues are configured:
```bash
celery -A app.celery_app inspect active_queues
```

### Issue: Task fails with "generate_7_day_meal_plan not found"
**Solution:** Restart the Celery worker after code changes:
```bash
# Stop worker (Ctrl+C) and restart
python start_worker.py
```

---

## Next Steps

### Frontend Integration:
1. Create meal plan request UI
2. Show task progress (polling or WebSocket)
3. Display 7-day meal plan grid
4. Add ability to regenerate plans

### Enhancements:
1. Add more meals to the database
2. Integrate with nutrition API for real recipes
3. Allow users to swap individual meals
4. Export meal plans to PDF/Calendar
5. Shopping list generation from ingredients

---

## Files Created

- `app/celery_app.py` - Celery configuration
- `app/models/meal_plan.py` - MealPlan database model
- `app/schemas/meal_plan.py` - Pydantic schemas for API
- `app/tasks/meal_plan.py` - Celery task for meal generation
- `app/services/meal_plan_service.py` - Meal plan generation logic
- `app/routes/meal_plan.py` - FastAPI routes for meal plans
- `start_worker.py` - Celery worker startup script
- `alembic/versions/xxx_add_meal_plans_table.py` - Database migration

---

**Day 5 Complete!** ✅

Meal plan system is fully implemented with asynchronous processing.
