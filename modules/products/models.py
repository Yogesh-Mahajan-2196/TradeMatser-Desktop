from utils.database import Base
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime, Boolean
from sqlalchemy import Enum as SQLAlchemyEnum
import datetime as dtm
from enum import Enum
from sqlalchemy.orm import relationship

class Unit(Enum):
    QUINTAL = "QUINTAL"
    KG = "KG"
    BAGS = "BAGS"
    TON = "TON"

class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String)
    unit = Column(SQLAlchemyEnum(Unit), default=Unit.QUINTAL)
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=dtm.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("company_user.id"))
    purchase_bill_items = relationship("PurchaseBillItem",back_populates="product")
    sale_bill_items = relationship("SellBillItem",back_populates="product")



    
