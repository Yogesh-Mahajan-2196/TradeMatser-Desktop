from utils.database import Base
from sqlalchemy import Column, ForeignKey, Numeric, String, Integer, Float, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
import datetime as dtm
from enum import Enum
from sqlalchemy.orm import relationship

class BillRemark(Enum):
    UNPAID= "Unpaid"
    PAID= "Paid"

class SellBill(Base):
    __tablename__ = "sell_bill"
    id = Column(Integer, primary_key=True, index=True)
    bill_no = Column(Integer, unique=True, index=True)
    bill_date = Column(DateTime, default=dtm.datetime.utcnow)
    company_name = Column(String(100))
    address = Column(String(250))
    broker_name = Column(String(50))
    truck_no = Column(String)
    po_no = Column(String)
    bags = Column(Integer)
    created_date = Column(DateTime, default=dtm.datetime.utcnow)
    remarks = Column(SQLAlchemyEnum(BillRemark),default=BillRemark.UNPAID)
    created_by = Column(Integer, ForeignKey("company_user.id"))
    sell_bill_item = relationship("SellBillItem", back_populates="sell_bill", cascade="all, delete-orphan")

class SellBillItem(Base):
    __tablename__ = 'sell_bill_item'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    weight = Column(Float)
    rate = Column(Numeric(12,2))
    gross_amount = Column(Numeric(12,2))
    expense_amount = Column(Numeric(12,2))
    net_amount = Column(Numeric(12,2))
    sell_bill_id = Column(Integer, ForeignKey("sell_bill.id"))
    sell_bill = relationship("SellBill", back_populates='sell_bill_item', lazy="selectin")
    product = relationship("Products",back_populates='sale_bill_items',lazy="selectin")