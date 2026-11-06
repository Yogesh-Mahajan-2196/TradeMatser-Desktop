from utils.database import Base
from sqlalchemy import Column, ForeignKey, Numeric, String, Integer, DateTime
from enum import Enum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SQLAlchemyEnum
import datetime as dtm
from sqlalchemy.orm import relationship

class Remark(Enum):
    PAID = "Paid"
    UNPAID = "Unpaid"

class PurchaseBill(Base):
    __tablename__ = "purchase_bill"
    id = Column(Integer, primary_key=True, index=True)
    bill_no = Column(Integer, unique=True, index=True)
    bill_date = Column(DateTime, default=dtm.datetime.utcnow)
    supplier_id  = Column(Integer, ForeignKey("user.id"))
    vehicle_no = Column(String)
    remarks = Column(SQLAlchemyEnum(Remark),default=Remark.UNPAID)
    created_date = Column(DateTime, default=dtm.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("company_user.id"))
    purchase_bill_item = relationship("PurchaseBillItem", back_populates="purchase_bill",cascade="all, delete-orphan", uselist=False,
    lazy="selectin")
    user = relationship("User",back_populates="purchase_bills")

class PurchaseBillItem(Base):
    __tablename__ = 'purchase_bill_item'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    weight = Column(Numeric(12,2))
    rate = Column(Numeric(12,2))
    expenses = Column(JSONB)
    paid_amount = Column(Numeric(12,2))
    unpaid_amount = Column(Numeric(12,2))
    total_amount = Column(Numeric(12,2))
    purchase_bill_id = Column(Integer, ForeignKey("purchase_bill.id"))
    purchase_bill = relationship("PurchaseBill", back_populates='purchase_bill_item', lazy="selectin")
    product = relationship("Products",back_populates='purchase_bill_items',lazy="selectin")
