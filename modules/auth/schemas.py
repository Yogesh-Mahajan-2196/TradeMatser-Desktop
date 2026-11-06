import re
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from .models import Role

def is_html(value: str) -> bool:
    return bool(re.search(r"<[^>]+>", value))

def clean(value: str) -> str:
    return re.sub(r"<[^>]+>", "", value)

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    confirm_password: str
    mobile_no: str
    role_id: Role = Field(
        default=Role.USER
    )

    @field_validator("first_name", mode="before")
    def check_first_name(cls, value):
        if not value:
            raise ValueError("First Name is Mandetory")
        if value:
            if is_html(value):
                raise ValueError('First Name should not contain HTML')
            value = clean(value)
        return value.strip()
    
    @field_validator("last_name", mode="before")
    def check_last_name(cls, value):
        if not value:
            raise ValueError("Last Name is Mandetory")
        if value:
            if is_html(value):
                raise ValueError('Last Name should not contain HTML')
            value = clean(value)
        return value.strip()
    
    @field_validator("email", mode="before")
    def check_email(cls, value):
        if not value:
            raise ValueError("Email is Mandetory")
        if value:
            if is_html(value):
                raise ValueError('Email should not contain HTML')
            value = clean(value)
        return value.strip()
    
    @field_validator("password", mode="before")
    def check_password(cls, value):
        if not value:
            raise ValueError("Password is required")
         
        if is_html(value):
            raise ValueError("Password should not contain HTML")
        
        value = clean(value)
        
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if len(value) > 20:
            raise ValueError("Password must not exceed 20 characters")

        if " " in value:
            raise ValueError("Password must not contain spaces")

        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one number")

        if not re.search(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]", value):
            raise ValueError("Password must contain at least one special character")

        return value
        
    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Password and Confirm Password do not match")
        return self
    
    @field_validator("mobile_no", mode="before")
    def check_mobile_no(cls, value):
        if value:
            if is_html(value):
                raise ValueError('Email should not contain HTML')
            value = clean(value)

        if len(value)<10:
           raise ValueError("Mobile number must be 10 digits.")
        return value.strip()

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class UpdateCompanyUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    mobile_no: str

    @field_validator("first_name", mode="before")
    def check_first_name(cls, value):
        if not value:
            raise ValueError("First Name is Mandetory")
        if value:
            if is_html(value):
                raise ValueError('First Name should not contain HTML')
            value = clean(value)
        return value.strip()
    
    @field_validator("last_name", mode="before")
    def check_last_name(cls, value):
        if not value:
            raise ValueError("Last Name is Mandetory")
        if value:
            if is_html(value):
                raise ValueError('Last Name should not contain HTML')
            value = clean(value)
        return value.strip()
    
    @field_validator("email", mode="before")
    def check_email(cls, value):
        if not value:
            raise ValueError("Email is Mandetory")
        if value:
            if is_html(value):
                raise ValueError('Email should not contain HTML')
            value = clean(value)
        return value.strip()
    
    @field_validator("mobile_no", mode="before")
    def check_mobile_no(cls, value):
        if value:
            if is_html(value):
                raise ValueError('Email should not contain HTML')
            value = clean(value)

        if len(value)<10:
           raise ValueError("Mobile number must be 10 digits.")
        return value.strip()

class CreateCompany(BaseModel):
    company_name : str