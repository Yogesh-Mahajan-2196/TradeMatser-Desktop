from pydantic.v1 import BaseSettings

class ProductSetting(BaseSettings):
    TAG = ["Product"]
    PRODUCT_NOT_FOUND = "Product not exists."
    PRODUCT_EXISTS = "Product name exists."
    class Config:
        env_file = ".env"

product_setting = ProductSetting()