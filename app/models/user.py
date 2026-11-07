from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=120)
    email: str = Field(index=True, unique=True, max_length=180)
    password_hash: str
    role: str = Field(default="customer", max_length=20)
    phone: str = Field(default="", max_length=40)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
