from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.database.database import get_session
from app.models import User
from app.services.auth_service import hash_password, verify_password
from app.controllers.common import render, current_user, set_flash, local_next

router=APIRouter(tags=["authentication"])

@router.get("/register")
def register_page(request: Request, db: Session=Depends(get_session)):
    if current_user(request,db): return RedirectResponse("/profile",status_code=303)
    return render(request,db,"register.html",page_title="Create an account")

@router.post("/register")
def register(request: Request, name: str=Form(...), email: str=Form(...), password: str=Form(...), confirm_password: str=Form(...), db: Session=Depends(get_session)):
    name=name.strip()[:120]; email=email.strip().lower()[:180]
    if not name or "@" not in email:
        set_flash(request,"Enter a valid name and email address.","error")
        return RedirectResponse("/register",status_code=303)
    if len(password)<8:
        set_flash(request,"Use a password with at least 8 characters.","error")
        return RedirectResponse("/register",status_code=303)
    if password != confirm_password:
        set_flash(request,"The passwords do not match.","error")
        return RedirectResponse("/register",status_code=303)
    if db.exec(select(User).where(User.email==email)).first():
        set_flash(request,"An account with that email already exists.","error")
        return RedirectResponse("/register",status_code=303)
    user=User(name=name,email=email,password_hash=hash_password(password),role="customer")
    db.add(user);db.commit();db.refresh(user)
    request.session["user_id"]=user.id
    set_flash(request,"Welcome to SeaFishPick.")
    return RedirectResponse("/profile",status_code=303)

@router.get("/login")
def login_page(request: Request, next_url: str=Query(default="/",alias="next"), db: Session=Depends(get_session)):
    if current_user(request,db): return RedirectResponse(local_next(next_url),status_code=303)
    return render(request,db,"login.html",page_title="Sign in",next_url=local_next(next_url))

@router.post("/login")
def login(request: Request, email: str=Form(...), password: str=Form(...), next_url: str=Form(default="/",alias="next"), db: Session=Depends(get_session)):
    user=db.exec(select(User).where(User.email==email.strip().lower())).first()
    if not user or not verify_password(password,user.password_hash):
        set_flash(request,"Email or password was not recognised.","error")
        return RedirectResponse("/login?next="+local_next(next_url,"/").replace(" ","%20"),status_code=303)
    request.session["user_id"]=user.id
    set_flash(request,f"Welcome back, {user.name.split()[0]}.")
    return RedirectResponse(local_next(next_url,"/"),status_code=303)

@router.post("/logout")
def logout(request: Request):
    request.session.pop("user_id",None)
    set_flash(request,"You have signed out.")
    return RedirectResponse("/",status_code=303)

@router.get("/profile")
def profile_page(request: Request, db: Session=Depends(get_session)):
    user=current_user(request,db)
    if not user:
        set_flash(request,"Please sign in to view your account.","error")
        return RedirectResponse("/login?next=/profile",status_code=303)
    return render(request,db,"profile.html",page_title="My account")

@router.post("/profile")
def profile_update(request: Request, name: str=Form(...), phone: str=Form(default=""), new_password: str=Form(default=""), db: Session=Depends(get_session)):
    user=current_user(request,db)
    if not user: return RedirectResponse("/login?next=/profile",status_code=303)
    if not name.strip():
        set_flash(request,"Name cannot be empty.","error");return RedirectResponse("/profile",status_code=303)
    user.name=name.strip()[:120];user.phone=phone.strip()[:40]
    if new_password:
        if len(new_password)<8:
            set_flash(request,"New password must be at least 8 characters.","error");return RedirectResponse("/profile",status_code=303)
        user.password_hash=hash_password(new_password)
    db.add(user);db.commit();set_flash(request,"Your profile has been updated.")
    return RedirectResponse("/profile",status_code=303)
