from typing import Optional

from fastapi import APIRouter, Depends
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from modules.parties.config import parties_setting
from modules.parties.schemas import CreateUser
from modules.parties.repository import user_create, customer_data, all_customers_data

parties_router = APIRouter(
    tags=parties_setting.TAG
)

@parties_router.post("/create-customer")
async def create_user(
    user_data: CreateUser,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await user_create(user_data, current_user, db)
    return res


@parties_router.get("/get-customer")
async def get_customers(
    page: int = 1,
    page_size: int = 8,
    mob_no: Optional[str] = None,
    name: Optional[str] = None,
    party_type: Optional[str] = None,
    current_user: CompanyUser = Depends(
        get_current_active_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    return await customer_data(
        mob_no=mob_no,
        name=name,
        party_type=party_type,
        page=page,
        page_size=page_size,
        db=db,
    )

@parties_router.get("/get-all-customers")
async def get_all_customers(
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await all_customers_data(db)
    return res