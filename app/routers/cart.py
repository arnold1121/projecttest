from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.database.database import get_session
from app.models import Product, WishlistItem
from app.services.cart_service import get_cart_lines, cart_totals, add_to_cart, update_quantity, remove_from_cart, wishlist_products, toggle_wishlist
from app.controllers.common import render, current_user, set_flash, local_next

router=APIRouter(tags=["cart and wishlist"])

@router.get("/cart")
def cart_page(request: Request, db: Session=Depends(get_session)):
    user=current_user(request,db); lines=get_cart_lines(request,db,user)
    return render(request,db,"cart.html",page_title="Your sea basket",cart_lines=lines,totals=cart_totals(lines))

@router.post("/cart/add")
def cart_add(request: Request, product_id: int=Form(...), quantity: int=Form(default=1), next_url: str=Form(default="/shop",alias="next"), db: Session=Depends(get_session)):
    user=current_user(request,db); product=db.get(Product,product_id)
    if not product or not product.is_active:
        set_flash(request,"That product is not available.","error");return RedirectResponse("/shop",status_code=303)
    try: add_to_cart(request,db,product,quantity,user)
    except ValueError as exc: set_flash(request,str(exc),"error");return RedirectResponse(local_next(next_url,"/shop"),status_code=303)
    set_flash(request,f"{product.name} added to your basket.")
    return RedirectResponse(local_next(next_url,"/shop"),status_code=303)

@router.post("/cart/update")
def cart_update(request: Request, product_id: int=Form(...), quantity: int=Form(...), db: Session=Depends(get_session)):
    try: update_quantity(request,db,product_id,quantity,current_user(request,db));set_flash(request,"Basket quantity updated.")
    except ValueError as exc: set_flash(request,str(exc),"error")
    return RedirectResponse("/cart",status_code=303)

@router.post("/cart/remove")
def cart_remove(request: Request, product_id: int=Form(...), db: Session=Depends(get_session)):
    remove_from_cart(request,db,product_id,current_user(request,db));set_flash(request,"Item removed from your basket.")
    return RedirectResponse("/cart",status_code=303)

@router.get("/wishlist")
def wishlist_page(request: Request, db: Session=Depends(get_session)):
    user=current_user(request,db);products=wishlist_products(request,db,user)
    return render(request,db,"wishlist.html",page_title="Your wishlist",products=products)

@router.post("/wishlist/add")
def wishlist_add(request: Request, product_id: int=Form(...), next_url: str=Form(default="/shop",alias="next"), db: Session=Depends(get_session)):
    try: added=toggle_wishlist(request,db,product_id,current_user(request,db));set_flash(request,"Saved to your wishlist." if added else "Removed from your wishlist.")
    except ValueError as exc: set_flash(request,str(exc),"error")
    return RedirectResponse(local_next(next_url,"/shop"),status_code=303)

@router.post("/wishlist/remove")
def wishlist_remove(request: Request, product_id: int=Form(...), db: Session=Depends(get_session)):
    user=current_user(request,db)
    if user:
        row=db.exec(select(WishlistItem).where(WishlistItem.user_id==user.id,WishlistItem.product_id==product_id)).first()
        if row: db.delete(row);db.commit()
    else:
        saved=[int(x) for x in request.session.get("guest_wishlist",[]) if str(x).isdigit() and int(x)!=product_id]
        request.session["guest_wishlist"]=saved
    set_flash(request,"Removed from your wishlist.")
    return RedirectResponse("/wishlist",status_code=303)
