from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.database.database import get_session
from app.models import Order, OrderItem
from app.services.cart_service import get_cart_lines, cart_totals
from app.services.order_service import create_order
from app.controllers.common import render, current_user, set_flash

router=APIRouter(tags=["orders and checkout"])

@router.get("/checkout")
def checkout_page(request: Request, db: Session=Depends(get_session)):
    user=current_user(request,db);lines=get_cart_lines(request,db,user)
    if not lines:
        set_flash(request,"Your basket is empty — choose a coastal favourite first.","error")
        return RedirectResponse("/shop",status_code=303)
    return render(request,db,"checkout.html",page_title="Checkout",cart_lines=lines,totals=cart_totals(lines))

@router.post("/checkout")
def checkout(request: Request, customer_name: str=Form(...), customer_email: str=Form(...), phone: str=Form(...), address: str=Form(...), city: str=Form(...), state: str=Form(default="Tamil Nadu"), pincode: str=Form(...), payment_method: str=Form(default="Cash on Delivery"), db: Session=Depends(get_session)):
    values={"customer_name":customer_name[:120],"customer_email":customer_email[:180],"phone":phone[:40],"address":address[:500],"city":city[:100],"state":state[:100],"pincode":pincode[:12],"payment_method":payment_method}
    if not all(str(values[key]).strip() for key in ("customer_name","customer_email","phone","address","city","pincode")) or "@" not in values["customer_email"]:
        set_flash(request,"Complete all delivery fields with a valid email address.","error")
        return RedirectResponse("/checkout",status_code=303)
    user=current_user(request,db)
    try: order=create_order(request,db,user,values)
    except ValueError as exc: set_flash(request,str(exc),"error");return RedirectResponse("/cart",status_code=303)
    if not user:
        request.session["last_guest_order_id"]=order.id
    set_flash(request,f"Demo order {order.order_number} placed. No payment was collected.")
    return RedirectResponse(f"/order/{order.id}",status_code=303)

@router.get("/orders")
def orders_page(request: Request, db: Session=Depends(get_session)):
    user=current_user(request,db)
    if not user: set_flash(request,"Sign in to view your orders.","error");return RedirectResponse("/login?next=/orders",status_code=303)
    orders=db.exec(select(Order).where(Order.user_id==user.id).order_by(Order.created_at.desc())).all()
    return render(request,db,"orders.html",page_title="My orders",orders=orders)

@router.get("/order/{order_id}")
def order_detail(order_id: int, request: Request, db: Session=Depends(get_session)):
    order=db.get(Order,order_id);user=current_user(request,db)
    guest_owns_order=not user and request.session.get("last_guest_order_id")==order_id
    allowed=bool(order and ((user and (user.role=="admin" or order.user_id==user.id)) or guest_owns_order))
    if not allowed:
        return render(request,db,"404.html",status_code=404,page_title="Order not found")
    if guest_owns_order:
        request.session.pop("last_guest_order_id",None)
    items=db.exec(select(OrderItem).where(OrderItem.order_id==order.id)).all()
    return render(request,db,"order_detail.html",page_title=f"Order {order.order_number}",order=order,items=items)
