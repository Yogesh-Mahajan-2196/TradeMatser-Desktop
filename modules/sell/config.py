from pydantic.v1 import BaseSettings

class SellSetting(BaseSettings):
    TAG = ["Sell"]
    BILL_EXISTS = "Sell bill exists with this number. Change sell bill number."
    BILL_NOT_EXISTS = "Sell bill not found for this number."
    
    class Config:
        env_file = ".env"

sell_settings = SellSetting()