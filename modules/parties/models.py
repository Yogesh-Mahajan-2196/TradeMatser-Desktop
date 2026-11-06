from utils.database import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
import datetime as dtm
from enum import Enum
from sqlalchemy.orm import relationship

class PartyType(Enum):
    CUSTOMER = "CUSTOMER"
    SUPPLIER = "SUPPLIER"
    BROKER = "BROKER"

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    party_name = Column(String)
    mobile_number = Column(String(15), unique=True)
    address = Column(String)
    city = Column(String)
    gst_no = Column(String)
    pan_no = Column(String)
    party_type = Column(SQLAlchemyEnum(PartyType),default=PartyType.CUSTOMER)
    created_at = Column(DateTime, default=dtm.datetime.utcnow())
    created_by = Column(Integer, ForeignKey("company_user.id"))
    purchase_bills = relationship("PurchaseBill",back_populates="user")
