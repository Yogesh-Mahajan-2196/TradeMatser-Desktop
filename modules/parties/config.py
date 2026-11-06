from pydantic.v1 import BaseSettings

class PartiesSetting(BaseSettings):
    TAG = ["Parties"]
    # PRODUCT_NOT_FOUND = "Product not exists."
    # PRODUCT_EXISTS = "Product name exists."
    class Config:
        env_file = ".env"

parties_setting = PartiesSetting()