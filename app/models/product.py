from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Product(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=160)
    slug: str = Field(index=True, unique=True, max_length=180)
    description: str = Field(default="", max_length=3000)
    price: float = Field(ge=0)
    discount_price: float | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, foreign_key="category.id", index=True)
    image_url: str = Field(default="", max_length=1200)
    weight: str = Field(default="200 g", max_length=50)
    ingredients: str = Field(default="", max_length=1200)
    spice_level: str = Field(default="Medium", max_length=40)
    stock_quantity: int = Field(default=0, ge=0)
    rating: float = Field(default=4.7, ge=0, le=5)
    review_count: int = Field(default=0, ge=0)
    is_featured: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
