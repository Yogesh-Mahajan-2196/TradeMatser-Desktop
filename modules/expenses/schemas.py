from datetime import datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field

class ExpenseCategory(str, Enum):
    FOOD = "Food"
    TRANSPORTATION = "Transportation"
    FUEL = "Fuel"
    MISCELLANEOUS = "Miscellaneous"


class ExpenseCreate(BaseModel):
    expense_name: str = Field(
        min_length=1,
        max_length=50,
    )
    category: ExpenseCategory
    amount: Decimal = Field(
        gt=0,
    )


class ExpenseUpdate(BaseModel):
    expense_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )
    category: ExpenseCategory
    amount: Decimal | None = Field(
        default=None,
        gt=0,
    )


class ExpenseResponse(BaseModel):
    id: int
    expense_name: str
    amount: Decimal
    created_at: datetime
    created_by: int

    class Config:
        orm_mode = True