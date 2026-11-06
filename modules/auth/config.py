from pydantic.v1 import BaseSettings

class AuthSetting(BaseSettings):
    TAG = ["AUTH"]
    SECRET_KEY : str
    ALGORITHM : str
    ACCESS_TOKEN_EXPIRE_MINUTES = 300
    REFRESH_TOKEN_EXPIRE_DAYS = 1
    USER_EXIST = "User exists with same Email ID, Please change the Email ID."
    WRONG_CURRENT_PASSWORD = "Enter current password is wrong. Please check!"
    USER_NOT_FOUND = "User not found."
    UNAUTHORISED = "Unauthorised person."
    ROLE_NOT_FOUND = "Role not present. Please check!"
    SAME_PASSWORD_ERROR = "New password cannot be same as current password."
    COMPANY_EXIST = "Company exists with same name."
    class Config:
        env_file = ".env"

auth_setting = AuthSetting()