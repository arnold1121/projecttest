from sqlmodel import Session, select
from app.models import Cart, CartItem, WishlistItem, Product

FREE_SHIPPING_AT = 799.0
FLAT_SHIPPING = 60.0

def _db_cart(session: Session, user_id: int, create=True) -> Cart | None:
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart and create:
        cart = Cart(user_id=user_id)
        session.add(cart); session.commit(); session.refresh(cart)
    return cart

def get_cart_lines(request, session: Session, user=None):
    lines=[]
    if user:
        cart=_db_cart(session,user.id,create=False)
        if not cart: return lines
        items=session.exec(select(CartItem).where(CartItem.cart_id == cart.id)).all()
        for item in items:
            product=session.get(Product,item.product_id)
            if product and product.is_active:
                price=product.discount_price if product.discount_price is not None else product.price
                lines.append({"product":product,"quantity":item.quantity,"line_total":round(price*item.quantity,2),"cart_item_id":item.id})
    else:
        guest=request.session.get("guest_cart",{})
        for raw_id, raw_qty in guest.items():
            try: pid, qty=int(raw_id), int(raw_qty)
            except (ValueError,TypeError): continue
            product=session.get(Product,pid)
            if product and product.is_active and qty>0:
                qty=min(qty,max(product.stock_quantity,1)); price=product.discount_price if product.discount_price is not None else product.price
                lines.append({"product":product,"quantity":qty,"line_total":round(price*qty,2),"cart_item_id":None})
    return lines

def cart_totals(lines):
    subtotal=round(sum(line["line_total"] for line in lines),2)
    shipping=0 if subtotal==0 or subtotal>=FREE_SHIPPING_AT else FLAT_SHIPPING
    discount=0.0
    return {"subtotal":subtotal,"shipping":shipping,"discount":discount,"grand_total":round(subtotal+shipping-discount,2)}

def add_to_cart(request, session: Session, product: Product, quantity: int, user=None):
    quantity=max(1,min(int(quantity),50))
    if product.stock_quantity<1: raise ValueError("This product is out of stock.")
    if user:
        cart=_db_cart(session,user.id)
        item=session.exec(select(CartItem).where(CartItem.cart_id==cart.id,CartItem.product_id==product.id)).first()
        total=quantity+(item.quantity if item else 0)
        if total>product.stock_quantity: raise ValueError("That quantity exceeds available stock.")
        if item: item.quantity=total
        else: session.add(CartItem(cart_id=cart.id,product_id=product.id,quantity=quantity))
        session.commit()
    else:
        guest=dict(request.session.get("guest_cart",{})); old=int(guest.get(str(product.id),0)); total=old+quantity
        if total>product.stock_quantity: raise ValueError("That quantity exceeds available stock.")
        guest[str(product.id)]=total; request.session["guest_cart"]=guest

def update_quantity(request, session: Session, product_id: int, quantity: int, user=None):
    product=session.get(Product,product_id)
    if not product: raise ValueError("Product not found.")
    if quantity<=0: return remove_from_cart(request,session,product_id,user)
    if quantity>product.stock_quantity: raise ValueError("That quantity exceeds available stock.")
    if user:
        cart=_db_cart(session,user.id,create=False)
        if cart:
            item=session.exec(select(CartItem).where(CartItem.cart_id==cart.id,CartItem.product_id==product_id)).first()
            if item: item.quantity=quantity; session.add(item); session.commit()
    else:
        guest=dict(request.session.get("guest_cart",{}));
        if str(product_id) in guest: guest[str(product_id)]=quantity
        request.session["guest_cart"]=guest

def remove_from_cart(request, session: Session, product_id: int, user=None):
    if user:
        cart=_db_cart(session,user.id,create=False)
        if cart:
            item=session.exec(select(CartItem).where(CartItem.cart_id==cart.id,CartItem.product_id==product_id)).first()
            if item: session.delete(item); session.commit()
    else:
        guest=dict(request.session.get("guest_cart",{})); guest.pop(str(product_id),None); request.session["guest_cart"]=guest

def clear_cart(request, session: Session, user=None):
    if user:
        cart=_db_cart(session,user.id,create=False)
        if cart:
            for item in session.exec(select(CartItem).where(CartItem.cart_id==cart.id)).all(): session.delete(item)
            session.commit()
    request.session.pop("guest_cart",None)

def wishlist_products(request, session: Session, user=None):
    if user:
        saved=session.exec(select(WishlistItem).where(WishlistItem.user_id==user.id)).all()
        ids=[x.product_id for x in saved]
    else:
        ids=[int(x) for x in request.session.get("guest_wishlist",[]) if str(x).isdigit()]
    return [p for pid in ids if (p:=session.get(Product,pid)) and p.is_active]

def toggle_wishlist(request, session: Session, product_id: int, user=None):
    product=session.get(Product,product_id)
    if not product or not product.is_active: raise ValueError("Product not found.")
    if user:
        row=session.exec(select(WishlistItem).where(WishlistItem.user_id==user.id,WishlistItem.product_id==product_id)).first()
        if row: session.delete(row); session.commit(); return False
        session.add(WishlistItem(user_id=user.id,product_id=product_id)); session.commit(); return True
    saved=[int(x) for x in request.session.get("guest_wishlist",[]) if str(x).isdigit()]
    if product_id in saved: saved.remove(product_id); request.session["guest_wishlist"]=saved; return False
    saved.append(product_id); request.session["guest_wishlist"]=saved; return True
