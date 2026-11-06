import re
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from modules.parties.models import PartyType

class CreateUser(BaseModel):
    user_name: str = Field(min_length=3, max_length=100)
    mobile_no: str
    address: str = Field(min_length=5, max_length=255)
    city: str = Field(min_length=2, max_length=50)
    gst: Optional[str] = None
    pan_no: Optional[str] = None
    user_type: PartyType

    @field_validator("mobile_no")
    @classmethod
    def validate_mobile(cls, value):
        value = value.strip()
        if not re.fullmatch(r"[6-9]\d{9}", value):
            raise ValueError("Mobile number must be 10 digits and start with 6-9.")
        return value

    @field_validator("gst")
    @classmethod
    def validate_gst(cls, value):
        if value is None:
            return value

        value = value.upper()

        if not re.fullmatch(
            r"\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}Z[A-Z\d]{1}",
            value,
        ):
            raise ValueError("Invalid GST number.")

        return value

    @field_validator("pan_no")
    @classmethod
    def validate_pan(cls, value):
        if value is None:
            return value

        value = value.upper()

        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):
            raise ValueError("Invalid PAN number.")

        return value