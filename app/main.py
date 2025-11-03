"""
ECOLIFE Backend - Main Application
FastAPI application for optimizing diet and habits for better health and lower carbon footprint.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings, get_allowed_origins
from app.routes import auth, onboarding, dashboard, analytics, meal_plan, meal_consumption, activity

# Initialize FastAPI app
app = FastAPI(
    title="ECOLIFE Backend API",
    description="Backend API for ECOLIFE platform - Eco-friendly lifestyle optimization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(meal_plan.router)
app.include_router(meal_consumption.router)
app.include_router(activity.router)


# Health check endpoint
@app.get("/ping", tags=["Health"])
async def ping():
    """
    Health check endpoint to verify the API is running.
    Returns a simple pong response.
    """
    return {
        "status": "success",
        "message": "pong",
        "version": "1.0.0"
    }


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "name": "ECOLIFE Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/ping"
    }
