from pydantic import BaseModel, Field

class ItemIn(BaseModel):
    sku: str = Field(min_length=1, max_length=80)
    name: str = Field(min_length=1, max_length=200)
    category: str = "General"
    quantity: float = Field(ge=0)
    minimum_stock: float = Field(ge=0)
    unit_cost: float = Field(ge=0)
    supplier: str = ""

