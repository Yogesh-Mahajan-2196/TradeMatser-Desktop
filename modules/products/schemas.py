from pydantic import BaseModel, field_validator, model_validator
from modules.auth.schemas import is_html
from modules.products.models import Unit

class CreateProduct(BaseModel):
    product_name: str
    unit: Unit

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value):
        if len(value) == 0:
            raise ValueError("Product name can not be empty")
        if value:
            if is_html(value):
                raise ValueError('Product Name should not contain HTML')
            # value = value.clean()
        return value.strip()
    
class ProductUpdate(BaseModel):
    id: int
    product_name: str
    unit: Unit

    @field_validator("product_name")
    @classmethod
    def validate_product_name(cls, value):
        if len(value) == 0:
            raise ValueError("Product name can not be empty")
        if value:
            if is_html(value):
                raise ValueError('Product Name should not contain HTML')
            # value = value.clean()
        return value.strip()
