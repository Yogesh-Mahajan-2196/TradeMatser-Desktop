from fastapi import APIRouter, Depends, HTTPException
from modules.auth.models import CompanyUser
from modules.auth.api_router import get_current_active_user
from modules.sell.repository import sell_bill, get_bill, update_bill
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import SellBillHeader, SellBillDetails, UpdateSellBill
from .config import sell_settings

sell_router = APIRouter(
    tags=[sell_settings.TAG]
)

@sell_router.post("/create-sell-bill")
async def create_sell_bill(
    bill_header: SellBillHeader,
    bill_details: SellBillDetails,
    current_user: CompanyUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised")
    
    res = await sell_bill(bill_header, bill_details, current_user.id, db)
    return res


@sell_router.get("/get-sell-bill")
async def get_sell_bill(
    bill_no: int,
    current_user: CompanyUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised")
    res = await get_bill(bill_no,db)
    return res


@sell_router.put("/update-sell-bill")
async def update_sell_bill(
    updated_data: UpdateSellBill,
    current_user: CompanyUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role_id == 3:
        raise HTTPException(
            status_code=403,
            detail="Unauthorised",
        )

    result = await update_bill(
        bill_no=updated_data.bill_no,
        expense=updated_data.expense,
        remark=updated_data.remark,
        db=db,
    )

    return result
