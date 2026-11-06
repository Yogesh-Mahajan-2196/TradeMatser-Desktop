import datetime as dtm
from utils.database import Base
from sqlalchemy import Column, ForeignKey, String, Integer, DateTime

class Truck(Base):
    __tablename__ = "trucks"
    id = Column(Integer,  primary_key=True)
    truck_number = Column(String, index=True, unique=True)
    owner_name = Column(String)
    owner_mobile = Column(String(10))
    driver_name = Column(String)
    driver_mobile = Column(String(10))
    created_date = Column(DateTime, default=dtm.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("company_user.id"))
