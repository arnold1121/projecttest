from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.database.database import create_db_and_tables
from app.database.seed import seed_data
from app.services.security import add_session_middleware
from app.models import User, Category, Product, Cart, CartItem, WishlistItem, Order, OrderItem, Review  # load table metadata
from app.routers import auth, products, cart, orders, admin
from app.database.database import get_session
from app.controllers.common import render
from fastapi import Depends
from sqlmodel import Session

ROOT=Path(__file__).resolve().parents[1]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_data()
    yield

app=FastAPI(title="SeaFishPick",description="A coastal fish-pickle storefront prototype inspired by southern Tamil Nadu.",version="1.0.0",lifespan=lifespan)
add_session_middleware(app)
app.mount("/static",StaticFiles(directory=str(ROOT/"app"/"static")),name="static")
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(admin.router)

@app.get("/health")
def health():
    return {"status":"ok","service":"SeaFishPick"}

@app.exception_handler(404)
async def not_found(request: Request, exc):
    # Keep not-found pages in the same visual language as the storefront.
    from app.database.database import engine
    with Session(engine) as db:
        return render(request,db,"404.html",status_code=404,page_title="Page not found")
