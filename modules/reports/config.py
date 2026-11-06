from pydantic.v1 import BaseSettings

class ReportsSetting(BaseSettings):
    TAG = ["Reports"]
    PRODUCT_NOT_FOUND = "Product not exists."
    PRODUCT_EXISTS = "Product name exists."
    class Config:
        env_file = ".env"

reports_setting = ReportsSetting()