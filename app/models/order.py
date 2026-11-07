from datetime import datetime, timezone
from sqlmodel import SQLModel, Field

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: int | None = Field(default=None, primary_key=True)
    order_number: str = Field(index=True, unique=True, max_length=50)
    user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    customer_name: str = Field(max_length=120)
    customer_email: str = Field(index=True, max_length=180)
    phone: str = Field(default="", max_length=40)
    address: str = Field(max_length=500)
    city: str = Field(default="", max_length=100)
    state: str = Field(default="Tamil Nadu", max_length=100)
    pincode: str = Field(default="", max_length=12)
    payment_method: str = Field(default="Cash on Delivery", max_length=40)
    payment_status: str = Field(default="Demo only", max_length=30)
    order_status: str = Field(default="Pending", max_length=30, index=True)
    subtotal: float = Field(default=0, ge=0)
    shipping: float = Field(default=0, ge=0)
    discount: float = Field(default=0, ge=0)
    grand_total: float = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)

class OrderItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    product_id: int | None = Field(default=None, foreign_key="product.id")
    product_name: str = Field(max_length=160)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    line_total: float = Field(ge=0)
