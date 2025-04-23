from fastapi import APIRouter, Depends, HTTPException, Form, Request, Response, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os
# Для работы с JWT используем PyJWT
import jwt
from jose import JWTError
from datetime import datetime, timedelta

from app.api.deps import get_db, get_current_user_api_key
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.config import settings
from app.crud.user import user as crud_user
from app.crud.course import course as crud_course
from app.crud.lesson import lesson as crud_lesson
from app.crud.enrollment import enrollment as crud_enrollment
from app.schemas.user import UserCreate
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def get_stats(db: Session):
    """Функция для получения статистики платформы"""
    try:
        return {
            "users_count": len(crud_user.get_multi(db)),
            "courses_count": len(crud_course.get_multi(db)),
            "lessons_count": len(crud_lesson.get_multi(db)),
            "enrollments_count": len(crud_enrollment.get_multi(db))
        }
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            "users_count": 0,
            "courses_count": 0,
            "lessons_count": 0,
            "enrollments_count": 0
        }

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, error: Optional[str] = None):
    """Отображение страницы входа в админ-панель"""
    return templates.TemplateResponse("admin/login.html", {"request": request, "error": error})

@router.post("/login", response_class=HTMLResponse)
async def admin_login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка формы входа в админ-панель"""
    # Проверяем сначала, не ввели ли нам обычное имя пользователя вместо email
    # Для простоты исходим из того, что имя пользователя хранится в поле full_name
    user = db.query(User).filter(User.full_name == username).first()
    
    # Если пользователь не найден по имени, пробуем проверить по email
    if not user:
        user = crud_user.get_by_email(db, email=username)
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "admin/login.html", 
            {"request": request, "error": "Неверное имя пользователя или пароль"}
        )
    
    if not user.is_admin:
        return templates.TemplateResponse(
            "admin/login.html", 
            {"request": request, "error": "У вас нет прав администратора"}
        )
    
    # Создаем токен доступа
    access_token = create_access_token(subject=user.email)
    
    # Сохраняем токен в куки
    response = RedirectResponse(url="/api/v1/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",  
        httponly=False,          
        max_age=1800,
        expires=1800,
        samesite="lax",          
    )
    
    return response

@router.get("/register", response_class=HTMLResponse)
async def admin_register_page(request: Request, error: Optional[str] = None):
    """Отображение страницы регистрации администратора"""
    return templates.TemplateResponse("admin/register.html", {"request": request, "error": error})

@router.post("/register", response_class=HTMLResponse)
async def admin_register(
    request: Request,
    email: str = Form(...),
    full_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Обработка формы регистрации администратора"""
    # Проверка совпадения паролей
    if password != confirm_password:
        return templates.TemplateResponse(
            "admin/register.html", 
            {"request": request, "error": "Пароли не совпадают"}
        )
    
    # Проверка существования пользователя
    existing_user = crud_user.get_by_email(db, email=email)
    if existing_user:
        return templates.TemplateResponse(
            "admin/register.html", 
            {"request": request, "error": "Пользователь с таким email уже существует"}
        )
    
    # Создание нового пользователя с правами администратора
    user_in = UserCreate(email=email, password=password, full_name=full_name, is_admin=True)
    crud_user.create(db, obj_in=user_in)
    
    # Перенаправление на страницу входа
    return RedirectResponse(
        url="/api/v1/admin/login?message=Регистрация успешна. Пожалуйста, войдите в систему.",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/logout")
async def admin_logout():
    """Выход из системы администратора"""
    response = RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: Session = Depends(get_db), access_token: Optional[str] = Cookie(None)):
    """Отображение панели управления администратора"""
    print(f"Accessing dashboard with token: {access_token}")
    
    # Проверка авторизации
    if not access_token:
        print("No access token found")
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Удостоверяемся, что токен имеет правильный формат
    token = access_token
    if access_token.startswith("Bearer "):
        token = access_token.replace("Bearer ", "")
    
    try:
        # Декодируем токен
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        
        if not email:
            print("No email in token payload")
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
            
        user = crud_user.get_by_email(db, email=email)
        if not user:
            print(f"User with email {email} not found")
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
            
        if not user.is_admin:
            print(f"User {email} is not admin")
            return templates.TemplateResponse(
                "admin/login.html", 
                {"request": request, "error": "У вас нет прав администратора"}
            )
        
        # Получаем статистику
        stats = get_stats(db)
        
        # Получаем последние курсы и пользователей
        recent_courses = crud_course.get_multi(db, limit=5)
        recent_users = crud_user.get_multi(db, limit=5)
        
        return templates.TemplateResponse(
            "admin/dashboard.html", 
            {
                "request": request, 
                "user": user, 
                "stats": stats,
                "recent_courses": recent_courses,
                "recent_users": recent_users
            }
        )
            
    except Exception as e:
        print(f"Error accessing dashboard: {e}")
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, db: Session = Depends(get_db), access_token: Optional[str] = Cookie(None)):
    """Отображение страницы управления пользователями"""
    # Проверка авторизации (такая же как в admin_dashboard)
    if not access_token or not access_token.startswith("Bearer "):
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    token = access_token.replace("Bearer ", "")
    
    try:
        # Декодируем токен для проверки прав администратора
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except Exception:
            # Если не получается, пробуем через зависимость
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
            
        email = payload.get("sub")
        if not email:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
            
        user = crud_user.get_by_email(db, email=email)
        if not user or not user.is_admin:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error checking admin rights: {e}")
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    return templates.TemplateResponse("admin/users.html", {"request": request})


@router.get("/users/{user_id}", response_class=HTMLResponse)
async def admin_user_details(request: Request, user_id: int, db: Session = Depends(get_db), access_token: Optional[str] = Cookie(None)):
    """Отображение деталей пользователя"""
    # Проверка авторизации (аналогично admin_users_page)
    if not access_token or not access_token.startswith("Bearer "):
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Получаем пользователя по ID
    user_details = crud_user.get(db, id=user_id)
    if not user_details:
        # Если пользователь не найден, возвращаем страницу с ошибкой
        return templates.TemplateResponse(
            "admin/error.html", 
            {"request": request, "error": f"Пользователь с ID {user_id} не найден"}
        )
    
    # Возвращаем страницу с информацией о пользователе
    # Пока используем шаблон с ошибкой, в дальнейшем можно создать отдельный шаблон
    return templates.TemplateResponse(
        "admin/error.html", 
        {"request": request, "error": "Функционал просмотра деталей пользователя в разработке"}
    )


@router.get("/courses", response_class=HTMLResponse)
async def admin_courses_page(request: Request, db: Session = Depends(get_db), access_token: Optional[str] = Cookie(None)):
    """Отображение страницы управления курсами"""
    # Проверка авторизации 
    if not access_token or not access_token.startswith("Bearer "):
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
        
    # Проверяем права администратора по токену
    token = access_token.replace("Bearer ", "")
    try:
        # Стандартная проверка токена
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        
        if not email:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
            
        user = crud_user.get_by_email(db, email=email)
        if not user or not user.is_admin:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error checking admin rights: {e}")
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Возвращаем страницу курсов
    return templates.TemplateResponse("admin/courses.html", {"request": request})


@router.get("/lessons", response_class=HTMLResponse)
async def admin_lessons_page(request: Request, db: Session = Depends(get_db), access_token: Optional[str] = Cookie(None)):
    """Отображение страницы управления уроками"""
    # Проверка авторизации
    if not access_token or not access_token.startswith("Bearer "):
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Проверяем права администратора по токену (аналогично courses)
    token = access_token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        
        if not email:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
            
        user = crud_user.get_by_email(db, email=email)
        if not user or not user.is_admin:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error checking admin rights: {e}")
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Возвращаем страницу уроков
    return templates.TemplateResponse("admin/lessons.html", {"request": request})


@router.get("/enrollments", response_class=HTMLResponse)
async def admin_enrollments_page(request: Request, db: Session = Depends(get_db), access_token: Optional[str] = Cookie(None)):
    """Отображение страницы управления записями на курсы"""
    # Проверка авторизации
    if not access_token or not access_token.startswith("Bearer "):
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Проверяем права администратора по токену (аналогично courses и lessons)
    token = access_token.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        
        if not email:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
            
        user = crud_user.get_by_email(db, email=email)
        if not user or not user.is_admin:
            return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error checking admin rights: {e}")
        return RedirectResponse(url="/api/v1/admin/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Возвращаем страницу записей на курсы
    return templates.TemplateResponse("admin/enrollments.html", {"request": request})
