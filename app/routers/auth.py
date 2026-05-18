from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import create_user, authenticate_user, get_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    existing = get_user_by_username(db, username)
    if existing:
        return RedirectResponse(url="/register?error=user_exists", status_code=303)
    user = create_user(db, username, password)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if not user:
        return RedirectResponse(url="/login?error=invalid_credentials", status_code=303)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)

@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

@router.get("/me")
async def get_current_user_info(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return {"authenticated": False}
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "username": user.username, "user_id": user.id}