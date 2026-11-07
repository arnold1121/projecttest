from sqlmodel import Session, select
from app.database.database import engine, create_db_and_tables
from app.models import User, Category, Product, Review
from app.services.auth_service import hash_password

COAST_BOATS = "https://commons.wikimedia.org/wiki/Special:FilePath/01FishingBoats%26Kanyakumari.jpg?width=900"
PICKLE_JARS = "https://commons.wikimedia.org/wiki/Special:FilePath/Jars_filled_with_homemade_Indian_pickles.jpg?width=900"
BEACH = "https://commons.wikimedia.org/wiki/Special:FilePath/Kanyakumari_beach.jpg?width=900"

CATEGORIES = [
    ("Tuna Fish Pickle", "tuna-fish-pickle", "Rich, meaty coastal favourites.", PICKLE_JARS),
    ("Sardine & Mackerel", "sardine-mackerel", "Small-fish favourites with bold masala.", COAST_BOATS),
    ("Garlic & Spice", "garlic-spice", "Aromatic garlic, chilli and coastal spices.", PICKLE_JARS),
    ("Family Combos", "family-combos", "Discover more than one favourite in a bundle.", BEACH),
    ("Coastal Specials", "coastal-specials", "Inspired by the southern shores of Tamil Nadu.", COAST_BOATS),
]
PRODUCTS = [
    {"name":"Traditional Tuna Fish Pickle","slug":"traditional-tuna-pickle","description":"Tender tuna pieces in a bold, tangy coastal masala.","price":449,"discount_price":399,"category":"tuna-fish-pickle","image_url":PICKLE_JARS,"weight":"200 g","ingredients":"Tuna, chilli, garlic, ginger, mustard, curry leaves and sesame oil","spice_level":"Hot","stock_quantity":24,"rating":4.9,"review_count":38,"is_featured":True},
    {"name":"Kanyakumari Coastal Tuna","slug":"kanyakumari-coastal-tuna","description":"Roasted spices and a rounded, savoury finish inspired by the southern coast.","price":499,"discount_price":449,"category":"coastal-specials","image_url":PICKLE_JARS,"weight":"250 g","ingredients":"Tuna, chilli, garlic, ginger, fenugreek and sesame oil","spice_level":"Medium","stock_quantity":18,"rating":4.8,"review_count":24,"is_featured":True},
    {"name":"Colachel Spicy Fish Pickle","slug":"colachel-spicy-fish-pickle","description":"A lively chilli-forward blend inspired by Colachel’s fishing coast.","price":399,"discount_price":349,"category":"tuna-fish-pickle","image_url":PICKLE_JARS,"weight":"200 g","ingredients":"Fish, red chilli, garlic, ginger, mustard and curry leaves","spice_level":"Extra hot","stock_quantity":16,"rating":4.7,"review_count":19,"is_featured":True},
    {"name":"Garlic Tuna Pickle","slug":"garlic-tuna-pickle","description":"Garlic-rich coastal masala with a mellow savoury finish.","price":449,"discount_price":419,"category":"garlic-spice","image_url":PICKLE_JARS,"weight":"200 g","ingredients":"Tuna, garlic, chilli, ginger, mustard seeds and sesame oil","spice_level":"Medium","stock_quantity":9,"rating":4.8,"review_count":16,"is_featured":False},
    {"name":"Traditional Mackerel Pickle","slug":"traditional-mackerel-pickle","description":"Hearty fish with a fragrant southern spice mix.","price":379,"discount_price":329,"category":"sardine-mackerel","image_url":PICKLE_JARS,"weight":"200 g","ingredients":"Mackerel, chilli, turmeric, garlic, ginger and curry leaves","spice_level":"Hot","stock_quantity":5,"rating":4.6,"review_count":13,"is_featured":False},
    {"name":"Spicy Anchovy Pickle","slug":"spicy-anchovy-pickle","description":"Small-fish texture, punchy chilli and a tangy finish.","price":349,"discount_price":299,"category":"sardine-mackerel","image_url":PICKLE_JARS,"weight":"180 g","ingredients":"Anchovy, chilli, garlic, ginger and fenugreek","spice_level":"Extra hot","stock_quantity":0,"rating":4.6,"review_count":11,"is_featured":False},
    {"name":"Coastal Family Combo","slug":"coastal-family-combo","description":"Three little jars for sharing or gifting.","price":699,"discount_price":629,"category":"family-combos","image_url":PICKLE_JARS,"weight":"3 × 100 g","ingredients":"Assorted demo fish pickle varieties","spice_level":"Mixed","stock_quantity":12,"rating":4.9,"review_count":22,"is_featured":True},
]

def seed_data() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(User).where(User.email == "admin@seafishpick.local")).first():
            session.add(User(name="SeaFishPick Admin", email="admin@seafishpick.local", password_hash=hash_password("Admin@123"), role="admin", phone=""))
        if not session.exec(select(User).where(User.email == "customer@example.com")).first():
            session.add(User(name="Demo Customer", email="customer@example.com", password_hash=hash_password("Customer@123"), role="customer", phone=""))
        session.commit()
        for name, slug, desc, image in CATEGORIES:
            if not session.exec(select(Category).where(Category.slug == slug)).first():
                session.add(Category(name=name, slug=slug, description=desc, image_url=image))
        session.commit()
        category_map = {c.slug:c.id for c in session.exec(select(Category)).all()}
        for data in PRODUCTS:
            if not session.exec(select(Product).where(Product.slug == data["slug"])).first():
                row = data.copy()
                row["category_id"] = category_map[row.pop("category")]
                session.add(Product(**row))
        session.commit()
        # Demo reviews are illustrative rather than verified customer endorsements.
        sample_reviews = [
            ("traditional-tuna-pickle", "Meena R.", 5, "Bold coastal flavour and a lovely garlic note. Sample demo review."),
            ("kanyakumari-coastal-tuna", "Arun K.", 4, "Good spice balance with rice. Sample demo review."),
        ]
        products_by_slug = {p.slug:p for p in session.exec(select(Product)).all()}
        for slug, name, rating, comment in sample_reviews:
            p = products_by_slug.get(slug)
            if p and not session.exec(select(Review).where(Review.product_id == p.id, Review.customer_name == name)).first():
                session.add(Review(product_id=p.id, customer_name=name, rating=rating, comment=comment))
        session.commit()
