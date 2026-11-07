from sqlmodel import Session, select
from fastapi import Request
from app.core.templates import templates
from app.models import User, Category, Cart, CartItem, WishlistItem
from app.services.cart_service import get_cart_lines, cart_totals, wishlist_products

def current_user(request: Request, db: Session):
    user_id=request.session.get("user_id")
    try: return db.get(User,int(user_id)) if user_id else None
    except (ValueError,TypeError): return None

def set_flash(request: Request, message: str, kind="success"):
    request.session["flash"]={"message":message,"kind":kind}

def page_context(request: Request, db: Session, **extra):
    user=current_user(request,db)
    categories=db.exec(select(Category).where(Category.is_active==True).order_by(Category.name)).all()  # noqa: E712
    lines=get_cart_lines(request,db,user)
    cart_count=sum(line["quantity"] for line in lines)
    saved=wishlist_products(request,db,user)
    flash=request.session.pop("flash",None)
    context={"request":request,"user":user,"categories":categories,"cart_count":cart_count,"wishlist_count":len(saved),"flash":flash,"page_title":"SeaFishPick"}
    context.update(extra)
    return context

def render(request: Request, db: Session, name: str, status_code=200, **extra):
    return templates.TemplateResponse(request=request,name=name,context=page_context(request,db,**extra),status_code=status_code)

def local_next(value: str | None, fallback="/") -> str:
    if not value or not value.startswith("/") or value.startswith("//") or "\\" in value: return fallback
    return value
