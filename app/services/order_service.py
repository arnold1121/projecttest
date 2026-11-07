import secrets
from datetime import datetime, timezone
from sqlmodel import Session
from app.models import Order, OrderItem, Product
from app.services.cart_service import get_cart_lines, cart_totals, clear_cart

ORDER_STATUSES=["Pending","Confirmed","Packed","Shipped","Delivered","Cancelled"]

def create_order(request, session: Session, user, form_data: dict):
    lines=get_cart_lines(request,session,user)
    if not lines: raise ValueError("Your cart is empty.")
    for line in lines:
        p=line["product"]
        if line["quantity"]>p.stock_quantity: raise ValueError(f"{p.name} does not have enough stock for that quantity.")
    totals=cart_totals(lines)
    order_no=f"SFP-{datetime.now(timezone.utc):%y%m%d}-{secrets.token_hex(3).upper()}"
    payment=form_data.get("payment_method","Cash on Delivery")
    if payment not in ("Cash on Delivery","Demo Online Payment"): payment="Cash on Delivery"
    order=Order(order_number=order_no,user_id=user.id if user else None,
        customer_name=form_data["customer_name"].strip(),customer_email=form_data["customer_email"].strip().lower(),
        phone=form_data["phone"].strip(),address=form_data["address"].strip(),city=form_data["city"].strip(),
        state=form_data["state"].strip() or "Tamil Nadu",pincode=form_data["pincode"].strip(),
        payment_method=payment,payment_status="Demo only",order_status="Pending",**totals)
    session.add(order);session.commit();session.refresh(order)
    for line in lines:
        p=line["product"]; qty=line["quantity"]; price=p.discount_price if p.discount_price is not None else p.price
        session.add(OrderItem(order_id=order.id,product_id=p.id,product_name=p.name,quantity=qty,unit_price=price,line_total=round(price*qty,2)))
        p.stock_quantity-=qty;session.add(p)
    session.commit();clear_cart(request,session,user)
    return order
