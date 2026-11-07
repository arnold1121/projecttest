from pathlib import Path
from fastapi.templating import Jinja2Templates
ROOT=Path(__file__).resolve().parents[2]
templates=Jinja2Templates(directory=str(ROOT/"app"/"templates"))
templates.env.filters["inr"]=lambda value: f"₹{float(value or 0):,.0f}"
templates.env.filters["discount_price"]=lambda product: float(product.discount_price if product.discount_price is not None else product.price)
