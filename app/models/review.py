from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    customer_name: str = Field(max_length=120)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(max_length=1500)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
