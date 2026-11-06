from utils.database import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Boolean, DateTime
import datetime as dtm
from sqlalchemy import Enum as SQLAlchemyEnum
from enum import Enum


class ExpenseCategory(str, Enum):
    FOOD = "Food"
    TRANSPORTATION = "Transportation"
    FUEL = "Fuel"
    MISCELLANEOUS = "Miscellaneous"

class Expenses(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    expense_name = Column(String(50))
    amount = Column(Integer)
    category = Column(
        SQLAlchemyEnum(
            ExpenseCategory,
            name="expense_category",
        ),
        nullable=False,
    )
    created_at = Column(DateTime, default=dtm.datetime.utcnow)
    created_by = Column(Integer, ForeignKey("company_user.id"))