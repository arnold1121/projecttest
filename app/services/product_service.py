from sqlmodel import Session, select
from app.models import Product, Category

def get_products(session: Session, *, include_inactive=False, q="", category_id=None, min_price=None, max_price=None, rating=None, spice_level=None, availability=None, sort="featured", limit=None):
    statement = select(Product)
    if not include_inactive:
        statement = statement.where(Product.is_active == True)  # noqa: E712
    if category_id:
        statement = statement.where(Product.category_id == category_id)
    if q:
        needle = f"%{q.strip()}%"
        statement = statement.where((Product.name.ilike(needle)) | (Product.description.ilike(needle)) | (Product.ingredients.ilike(needle)))
    rows = session.exec(statement).all()
    if min_price is not None: rows = [p for p in rows if (p.discount_price if p.discount_price is not None else p.price) >= min_price]
    if max_price is not None: rows = [p for p in rows if (p.discount_price if p.discount_price is not None else p.price) <= max_price]
    if rating is not None: rows = [p for p in rows if p.rating >= rating]
    if spice_level: rows = [p for p in rows if p.spice_level.lower() == spice_level.lower()]
    if availability == "in-stock": rows = [p for p in rows if p.stock_quantity > 0]
    if availability == "out-of-stock": rows = [p for p in rows if p.stock_quantity <= 0]
    key_price = lambda p: p.discount_price if p.discount_price is not None else p.price
    if sort == "price-asc": rows.sort(key=key_price)
    elif sort == "price-desc": rows.sort(key=key_price, reverse=True)
    elif sort == "popular": rows.sort(key=lambda p:(p.rating,p.review_count), reverse=True)
    elif sort == "newest": rows.sort(key=lambda p:p.created_at, reverse=True)
    else: rows.sort(key=lambda p:(not p.is_featured,p.created_at), reverse=False)
    return rows[:limit] if limit else rows

def get_categories(session: Session, include_inactive=False):
    statement = select(Category)
    if not include_inactive: statement = statement.where(Category.is_active == True)  # noqa: E712
    return session.exec(statement.order_by(Category.name)).all()
