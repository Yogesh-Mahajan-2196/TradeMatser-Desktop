from decimal import Decimal
from typing import Dict
from pydantic import BaseModel, Field, field_validator, model_validator

from modules.purchase.models import Remark

class PurchaseBillHeader(BaseModel):
    bill_no: int = Field(gt=0)
    supplier_name: str
    vehicle_no: str = Field(min_length=6, max_length=15)
    remark: Remark

    @field_validator("vehicle_no")
    @classmethod
    def validate_vehicle(cls, value: str):
        return value.strip().upper()


class PurchaseBillDetails(BaseModel):
    product_id: int = Field(gt=0)
    weight: Decimal = Field(gt=0)
    rate: Decimal = Field(gt=0)
    expenses: Dict[str, Decimal]
    paid_amount: Decimal = Field(ge=0)

    @field_validator("expenses")
    @classmethod
    def validate_expenses(cls, value):

        if not isinstance(value, dict):
            raise ValueError("Expenses must be a dictionary.")

        for key, amount in value.items():

            if not key.strip():
                raise ValueError("Expense name cannot be empty.")

            if amount < 0:
                raise ValueError(
                    f"{key} cannot be negative."
                )

        return value

    
class UpdatePurchaseBill(BaseModel):
    paid_amount: Decimal = Field(ge=0)
