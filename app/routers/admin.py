from datetime import datetime, timezone
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.database.database import get_session
from app.models import User, Category, Product, Order, OrderItem, Review
from app.services.product_service import get_products, get_categories
from app.services.order_service import ORDER_STATUSES
from app.controllers.common import render, current_user, set_flash

router=APIRouter(prefix="/admin",tags=["admin"])

def guard(request,db):
    user=current_user(request,db)
    if not user or user.role!="admin":
        set_flash(request,"Please sign in with the store-admin account to open the management area.","error")
        return None
    return user

def slugify(value):
    return "-".join("".join(ch.lower() if ch.isalnum() else " " for ch in value).split())[:180] or "product"

@router.get("")
def dashboard(request: Request, db: Session=Depends(get_session)):
    admin=guard(request,db)
    if not admin: return RedirectResponse("/login?next=/admin",status_code=303)
    orders=db.exec(select(Order).order_by(Order.created_at.desc())).all();products=db.exec(select(Product).where(Product.is_active==True)).all()  # noqa: E712
    users=db.exec(select(User).where(User.role=="customer")).all()
    sales=sum(o.grand_total for o in orders if o.order_status!="Cancelled")
    pending=sum(1 for o in orders if o.order_status in ("Pending","Confirmed"))
    low_stock=sorted([p for p in products if p.stock_quantity<=7],key=lambda p:p.stock_quantity)[:8]
    bestsellers=[]
    for p in products:
        sold=sum(i.quantity for i in db.exec(select(OrderItem).where(OrderItem.product_id==p.id)).all())
        bestsellers.append({"product":p,"sold":sold})
    bestsellers.sort(key=lambda row:row["sold"],reverse=True)
    return render(request,db,"admin/dashboard.html",page_title="Admin dashboard",total_sales=sales,total_orders=len(orders),total_products=len(products),total_customers=len(users),pending_orders=pending,low_stock=low_stock,bestsellers=bestsellers[:5],latest_orders=orders[:6])

@router.get("/products")
def products_list(request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/products",status_code=303)
    return render(request,db,"admin/products.html",page_title="Manage products",products=get_products(db,include_inactive=True))

@router.get("/products/create")
def product_create_page(request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/products/create",status_code=303)
    return render(request,db,"admin/product_form.html",page_title="Create product",product=None,edit_mode=False,categories=get_categories(db,include_inactive=True))

@router.post("/products/create")
def product_create(request: Request, name: str=Form(...), description: str=Form(default=""), price: float=Form(...), discount_price: str=Form(default=""), category_id: str=Form(default=""), image_url: str=Form(default=""), weight: str=Form(default="200 g"), ingredients: str=Form(default=""), spice_level: str=Form(default="Medium"), stock_quantity: int=Form(default=0), is_featured: str|None=Form(default=None), is_active: str|None=Form(default="on"), db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/products/create",status_code=303)
    if not name.strip() or price<0 or stock_quantity<0:
        set_flash(request,"Enter a name, non-negative price and valid stock quantity.","error");return RedirectResponse("/admin/products/create",status_code=303)
    slug=slugify(name);base=slug;index=2
    while db.exec(select(Product).where(Product.slug==slug)).first(): slug=f"{base}-{index}";index+=1
    try: cat_id=int(category_id) if category_id else None
    except ValueError: cat_id=None
    discount=float(discount_price) if discount_price.strip() else None
    if discount is not None and (discount<0 or discount>price): discount=None
    product=Product(name=name.strip()[:160],slug=slug,description=description.strip()[:3000],price=price,discount_price=discount,category_id=cat_id,image_url=image_url.strip()[:1200],weight=weight.strip()[:50] or "200 g",ingredients=ingredients.strip()[:1200],spice_level=spice_level.strip()[:40] or "Medium",stock_quantity=stock_quantity,is_featured=is_featured=="on",is_active=is_active=="on")
    db.add(product);db.commit();set_flash(request,"Product created.")
    return RedirectResponse("/admin/products",status_code=303)

@router.get("/products/{product_id}/edit")
def product_edit_page(product_id: int, request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/products",status_code=303)
    product=db.get(Product,product_id)
    if not product: return render(request,db,"404.html",status_code=404,page_title="Product not found")
    return render(request,db,"admin/product_form.html",page_title="Edit product",product=product,edit_mode=True,categories=get_categories(db,include_inactive=True))

@router.post("/products/{product_id}/edit")
def product_edit(product_id: int, request: Request, name: str=Form(...), description: str=Form(default=""), price: float=Form(...), discount_price: str=Form(default=""), category_id: str=Form(default=""), image_url: str=Form(default=""), weight: str=Form(default="200 g"), ingredients: str=Form(default=""), spice_level: str=Form(default="Medium"), stock_quantity: int=Form(default=0), is_featured: str|None=Form(default=None), is_active: str|None=Form(default=None), db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/products",status_code=303)
    product=db.get(Product,product_id)
    if not product: return RedirectResponse("/admin/products",status_code=303)
    if not name.strip() or price<0 or stock_quantity<0:
        set_flash(request,"Enter a name, non-negative price and valid stock quantity.","error");return RedirectResponse(f"/admin/products/{product_id}/edit",status_code=303)
    try: cat_id=int(category_id) if category_id else None
    except ValueError: cat_id=None
    discount=float(discount_price) if discount_price.strip() else None
    if discount is not None and (discount<0 or discount>price): discount=None
    product.name=name.strip()[:160];product.description=description.strip()[:3000];product.price=price;product.discount_price=discount;product.category_id=cat_id;product.image_url=image_url.strip()[:1200];product.weight=weight.strip()[:50] or "200 g";product.ingredients=ingredients.strip()[:1200];product.spice_level=spice_level.strip()[:40] or "Medium";product.stock_quantity=stock_quantity;product.is_featured=is_featured=="on";product.is_active=is_active=="on";product.updated_at=datetime.now(timezone.utc)
    db.add(product);db.commit();set_flash(request,"Product updated.")
    return RedirectResponse("/admin/products",status_code=303)

@router.post("/products/{product_id}/delete")
def product_delete(product_id: int, request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/products",status_code=303)
    product=db.get(Product,product_id)
    if product:
        product.is_active=False;db.add(product);db.commit();set_flash(request,"Product deactivated; historical orders remain intact.")
    return RedirectResponse("/admin/products",status_code=303)

@router.get("/categories")
def categories_list(request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/categories",status_code=303)
    return render(request,db,"admin/categories.html",page_title="Manage categories",categories=get_categories(db,include_inactive=True))

@router.post("/categories/create")
def category_create(request: Request, name: str=Form(...), description: str=Form(default=""), image_url: str=Form(default=""), db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/categories",status_code=303)
    if not name.strip(): set_flash(request,"Category name is required.","error");return RedirectResponse("/admin/categories",status_code=303)
    if db.exec(select(Category).where(Category.name.ilike(name.strip()))).first():
        set_flash(request,"A category with that name already exists.","error");return RedirectResponse("/admin/categories",status_code=303)
    base=slugify(name);slug=base;n=2
    while db.exec(select(Category).where(Category.slug==slug)).first(): slug=f"{base}-{n}";n+=1
    db.add(Category(name=name.strip()[:100],slug=slug,description=description.strip()[:1000],image_url=image_url.strip()[:1200]));db.commit();set_flash(request,"Category created.")
    return RedirectResponse("/admin/categories",status_code=303)

@router.post("/categories/{category_id}/edit")
def category_edit(category_id: int, request: Request, name: str=Form(...), description: str=Form(default=""), image_url: str=Form(default=""), is_active: str|None=Form(default=None), db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/categories",status_code=303)
    category=db.get(Category,category_id)
    if category and name.strip():
        duplicate=db.exec(select(Category).where(Category.id!=category_id,Category.name.ilike(name.strip()))).first()
        if duplicate:
            set_flash(request,"Another category already uses that name.","error")
            return RedirectResponse("/admin/categories",status_code=303)
        category.name=name.strip()[:100];category.description=description.strip()[:1000];category.image_url=image_url.strip()[:1200];category.is_active=is_active=="on";db.add(category);db.commit();set_flash(request,"Category updated.")
    return RedirectResponse("/admin/categories",status_code=303)

@router.post("/categories/{category_id}/delete")
def category_delete(category_id: int, request: Request, db: Session=Depends(get_session)):
    if not guard(request,db):
        return RedirectResponse("/login?next=/admin/categories",status_code=303)
    category=db.get(Category,category_id)
    if category:
        linked=db.exec(select(Product).where(Product.category_id==category_id)).first()
        if linked:
            # Preserve the category reference for historical records and make it unavailable to shoppers.
            category.is_active=False
            db.add(category)
            db.commit()
            set_flash(request,"Category deactivated because it still contains products.")
        else:
            db.delete(category)
            db.commit()
            set_flash(request,"Category deleted.")
    return RedirectResponse("/admin/categories",status_code=303)

@router.get("/orders")
def orders_list(request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/orders",status_code=303)
    orders=db.exec(select(Order).order_by(Order.created_at.desc())).all()
    return render(request,db,"admin/orders.html",page_title="Manage orders",orders=orders,statuses=ORDER_STATUSES)

@router.post("/orders/{order_id}/status")
def order_status_update(order_id: int, request: Request, order_status: str=Form(...), db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/orders",status_code=303)
    order=db.get(Order,order_id)
    if order and order_status in ORDER_STATUSES:
        order.order_status=order_status;db.add(order);db.commit();set_flash(request,"Order status updated.")
    else: set_flash(request,"Choose a valid order status.","error")
    return RedirectResponse("/admin/orders",status_code=303)

@router.get("/customers")
def customers_list(request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/customers",status_code=303)
    users=db.exec(select(User).where(User.role=="customer").order_by(User.created_at.desc())).all()
    stats=[]
    for user in users:
        orders=db.exec(select(Order).where(Order.user_id==user.id)).all()
        stats.append({"user":user,"order_count":len(orders),"total_spending":sum(o.grand_total for o in orders if o.order_status!="Cancelled")})
    return render(request,db,"admin/customers.html",page_title="Customers",customer_stats=stats)

@router.get("/inventory")
def inventory_list(request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/inventory",status_code=303)
    products=db.exec(select(Product).order_by(Product.stock_quantity)).all()
    return render(request,db,"admin/inventory.html",page_title="Inventory",products=products)

@router.get("/reviews")
def reviews_list(request: Request, db: Session=Depends(get_session)):
    if not guard(request,db): return RedirectResponse("/login?next=/admin/reviews",status_code=303)
    reviews=db.exec(select(Review).order_by(Review.created_at.desc())).all()
    return render(request,db,"admin/reviews.html",page_title="Reviews",reviews=reviews)
