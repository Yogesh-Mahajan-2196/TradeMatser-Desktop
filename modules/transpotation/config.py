from pydantic.v1 import BaseSettings

class TranspotaionSetting(BaseSettings):
    TAG = ["Transpotation"]
    TRUCK_NO_NOT_FOUND = "Truck number not exists."
    TRUCK_NO_EXISTS = "Truck number exists."
    class Config:
        env_file = ".env"

transpotation_setting = TranspotaionSetting()