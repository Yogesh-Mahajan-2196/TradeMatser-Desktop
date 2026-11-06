from utils.database import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
import datetime as dtm
from enum import Enum
from sqlalchemy.orm import relationship


class Role(Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    USER = "USER"

class Company(Base):
    __tablename__ = "company"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_date = Column(
        DateTime,
        default=dtm.datetime.utcnow
    )

class CompanyUser(Base):
    __tablename__ = "company_user"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email_id = Column(String, unique=True)
    password = Column(String(255), nullable=False)
    mobile_number = Column(String(10))
    role_id = Column(SQLAlchemyEnum(Role),default=Role.USER)
    is_active = Column(Boolean, default=True)
    company_id = Column(
        Integer,
        ForeignKey("company.id"),
        nullable=True,
        index=True
    )
    created_date = Column(DateTime, default=dtm.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("company_user.id"))
    company = relationship("Company")