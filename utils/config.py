from pydantic.v1 import BaseSettings
# from pathlib import Path

# BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    DATABASE_URL : str
    WEB_API_URL : str
    WEB_APP_URL: str

    # Mail Config
    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_FROM : str
    MAIL_PORT : int
    MAIL_SERVER : str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS : bool
    MAIL_SSL_TLS : bool
    USE_CREDENTIALS : bool
    VALIDATE_CERTS : bool

    ADMIN_EMAIL : str

    # ==========================================
    # MARKET INFORMATION
    # ==========================================

    MARKET_NAME: str = "कृषि उत्पन्न बाजार समिती, चाळीसगाव"
    MARKET_TALUKA: str = "चाळीसगाव"
    MARKET_DISTRICT: str = "नाशिक"

    ADAT_NAME: str = "विद्या ट्रेडिंग कंपनी"

    BUYER_NAME: str = "गुरुजी ट्रेडिंग कंपनी"
    BUYER_MOBILE_1: str 
    BUYER_MOBILE_2: str 
    BUYER_MOBILE_3: str 


    # ==========================================
    # EXPENSE NAMES
    # ==========================================

    EXPENSE_1_NAME: str = "आडत"
    EXPENSE_2_NAME: str = "हमाली"
    EXPENSE_3_NAME: str = "तोलाई"
    EXPENSE_4_NAME: str = "वाराई"
    EXPENSE_5_NAME: str = "तिकीट"

    PURCHASE_EXPENSE_ADAT: float = 100
    PURCHASE_EXPENSE_HAMALI: float = 50
    PURCHASE_EXPENSE_TOLAI: float = 20
    PURCHASE_EXPENSE_VARAI: float = 30
    PURCHASE_EXPENSE_TICKET: float = 10

    BANK_NAME: str
    ACCOUNT_NO: str
    IFSC_CODE: str
    EMAIL: str

    COMPANY_NAME: str
    OWNER_NAME: str
    COMPANY_ADDRESS: str

    class Config:
        env_file = ".env"

settings = Settings() 