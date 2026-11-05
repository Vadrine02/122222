from datetime import datetime
from pydantic import BaseModel, Field

class LocationIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)

class ProductOffer(BaseModel):
    product_id: int
    name: str
    unit: str | None
    store_id: int
    chain: str
    store_name: str
    price: float
    currency: str
    scraped_at: datetime
    distance_m: float

class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    lat: float | None = None
    lng: float | None = None

class ShoppingItem(BaseModel):
    ingredient: str
    offer: ProductOffer | None

class ChatOut(BaseModel):
    reply: str
    items: list[ShoppingItem] = []
    total: float = 0
