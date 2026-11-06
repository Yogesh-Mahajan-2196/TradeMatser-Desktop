from pydantic.v1 import BaseSettings

class PurchaseSetting(BaseSettings):
    TAG = ["Purchase"]
    BILL_EXISTS = "Purchase bill exists with this number. Change purchase bill number."
    BILL_NOT_EXISTS = "Purchase bill not found for this number."
    
    class Config:
        env_file = ".env"

purchase_settings = PurchaseSetting()