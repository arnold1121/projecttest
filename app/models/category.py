from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Category(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    slug: str = Field(index=True, unique=True, max_length=120)
    description: str = Field(default="", max_length=1000)
    image_url: str = Field(default="", max_length=1200)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
