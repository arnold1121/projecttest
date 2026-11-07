from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.database.database import get_session
from app.models import Product, Category, Review
from app.services.product_service import get_products, get_categories
from app.controllers.common import render, current_user, set_flash

router=APIRouter(tags=["storefront"])

@router.get("/")
def home(request: Request, db: Session=Depends(get_session)):
    featured=get_products(db,limit=4)
    categories=get_categories(db)
    return render(request,db,"index.html",page_title="Taste the Sea. Preserve the Tradition.",featured_products=featured,story_categories=categories[:3])

@router.get("/shop")
def shop(request: Request, q: str="", category_id: int|None=None, min_price: float|None=None, max_price: float|None=None, rating: float|None=None, spice_level: str|None=None, availability: str|None=None, sort: str="featured", db: Session=Depends(get_session)):
    products=get_products(db,q=q,category_id=category_id,min_price=min_price,max_price=max_price,rating=rating,spice_level=spice_level,availability=availability,sort=sort)
    return render(request,db,"shop.html",page_title="Shop fish pickles",products=products,filters={"q":q,"category_id":category_id,"min_price":min_price,"max_price":max_price,"rating":rating,"spice_level":spice_level,"availability":availability,"sort":sort})

@router.get("/category/{category_id}")
def category_page(category_id: int, request: Request, db: Session=Depends(get_session)):
    category=db.get(Category,category_id)
    if not category or not category.is_active: return render(request,db,"404.html",status_code=404,page_title="Category not found")
    return render(request,db,"shop.html",page_title=category.name,products=get_products(db,category_id=category_id),filters={"q":"","category_id":category_id,"sort":"featured"},active_category=category)

@router.get("/product/{product_id}")
def product_detail(product_id: int, request: Request, db: Session=Depends(get_session)):
    product=db.get(Product,product_id)
    if not product or not product.is_active: return render(request,db,"404.html",status_code=404,page_title="Product not found")
    category=db.get(Category,product.category_id) if product.category_id else None
    reviews=db.exec(select(Review).where(Review.product_id==product_id).order_by(Review.created_at.desc())).all()
    related=[p for p in get_products(db,category_id=product.category_id,limit=5) if p.id!=product_id][:4]
    return render(request,db,"product_detail.html",page_title=product.name,product=product,category=category,reviews=reviews,related_products=related)

@router.post("/product/{product_id}/review")
def add_review(product_id: int, request: Request, rating: int=Form(...), comment: str=Form(...), db: Session=Depends(get_session)):
    user=current_user(request,db)
    if not user:
        set_flash(request,"Please sign in to leave a review.","error")
        return RedirectResponse(f"/login?next=/product/{product_id}",status_code=303)
    product=db.get(Product,product_id)
    if not product or not product.is_active: return RedirectResponse("/shop",status_code=303)
    if rating<1 or rating>5 or not comment.strip():
        set_flash(request,"Choose a rating and write a short review.","error")
        return RedirectResponse(f"/product/{product_id}",status_code=303)
    review=Review(product_id=product_id,user_id=user.id,customer_name=user.name,rating=rating,comment=comment.strip()[:1500])
    old_count=product.review_count
    product.rating=round(((product.rating*old_count)+rating)/(old_count+1),1);product.review_count=old_count+1
    db.add(review);db.add(product);db.commit();set_flash(request,"Thank you for sharing your feedback.")
    return RedirectResponse(f"/product/{product_id}#reviews",status_code=303)
