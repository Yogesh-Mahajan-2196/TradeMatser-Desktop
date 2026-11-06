import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class CreateTransportaion(BaseModel):
    truck_number: str
    owner_name: str
    owner_mobile: str
    driver_name: str
    driver_mobile: str

    @field_validator("owner_mobile","driver_mobile")
    @classmethod
    def validate_mobile(cls, value):
        value = value.strip()
        if not re.fullmatch(r"[6-9]\d{9}", value):
            raise ValueError("Mobile number must be 10 digits and start with 6-9.")
        return value
    