from pydantic.v1 import BaseSettings

class ExpenseSetting(BaseSettings):
    TAG = ["Expenses"]
    class Config:
        env_file = ".env"

expense_setting = ExpenseSetting()