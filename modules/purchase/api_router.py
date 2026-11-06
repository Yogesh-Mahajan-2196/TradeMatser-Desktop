from fastapi import APIRouter, Depends
from modules.auth.models import CompanyUser
from .config import purchase_settings
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import PurchaseBillDetails, PurchaseBillHeader, UpdatePurchaseBill
from .repository import purchase_bill, get_bill, purchase_bill_update
from modules.auth.api_router import get_current_active_user
purchase_router = APIRouter(
    tags=purchase_settings.TAG
)

@purchase_router.post("/create-purchase-bill")
async def create_purchase_bill(
    bill_header: PurchaseBillHeader, 
    bill_details: PurchaseBillDetails, 
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await purchase_bill(bill_header, bill_details, current_user.id, db)
    return res

@purchase_router.get("/get-purchase-bill/{bill_no}")
async def get_purchase_bill(
    bill_no: int, 
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await get_bill(bill_no, db)
    return res

@purchase_router.put("/update-purchase-bill")
async def update_purchase_bill(
    bill_no: int,
    updated_bill: UpdatePurchaseBill,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await purchase_bill_update(bill_no, updated_bill, db)
    return res
