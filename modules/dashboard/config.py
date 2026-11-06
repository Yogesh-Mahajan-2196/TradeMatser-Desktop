from pydantic.v1 import BaseSettings

class DashboardSetting(BaseSettings):
    TAG = ["Dashboard"]
    PRODUCT_NOT_FOUND = "Product not exists."
    PRODUCT_EXISTS = "Product name exists."
    class Config:
        env_file = ".env"

dashboard_setting = DashboardSetting()