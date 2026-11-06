from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from modules.purchase.models import Remark
from modules.sell.models import BillRemark

class SellBillHeader(BaseModel):
    bill_no: int = Field(gt=0)
    company_name: str
    address: str
    broker_name: str
    bill_date: date
    truck_no: str = Field(min_length=6, max_length=15)
    po_no: Optional[str]
    bags: int
    remarks: Remark

    @field_validator("truck_no")
    @classmethod
    def validate_vehicle(cls, value: str):
        return value.strip().upper()


class SellBillDetails(BaseModel):
    product_id: int = Field(gt=0)
    weight: Decimal = Field(gt=0)
    rate: Decimal = Field(gt=0)
    expenses: Optional[int] 


class UpdateSellBill(BaseModel):
    bill_no: int
    expense: Decimal = Field(gt=0)
    remark: BillRemark