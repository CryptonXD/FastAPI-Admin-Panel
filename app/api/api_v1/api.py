from fastapi import APIRouter

from app.api.api_v1.endpoints import users, login, courses, lessons, comments, ratings, stats, enrollments, admin, admin_auth

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
api_router.include_router(comments.router, prefix="/comments", tags=["comments"])
api_router.include_router(ratings.router, prefix="/ratings", tags=["ratings"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(admin_auth.router, prefix="/admin", tags=["admin-auth"])