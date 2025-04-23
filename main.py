from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from sqlalchemy.orm import Session

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.db.session import engine
from app.db.base import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    # Перенаправляем на страницу входа в админ-панель
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/v1/admin/login")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)