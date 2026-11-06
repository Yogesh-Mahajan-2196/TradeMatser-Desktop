from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from utils.config import settings
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from modules.purchase.repository import get_bill, get_next_purchase_bill_no
from utils.database import get_db
from datetime import datetime
from zoneinfo import ZoneInfo

purchase_router = APIRouter(
    tags = ["Purchase"]
)
templates=Jinja2Templates(directory="templates")

@purchase_router.get("/purchase-bill/{bill_no}")
async def purchase_bill_detail(
    bill_no: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: CompanyUser = Depends(get_current_active_user)
):
    purchase_bill = await get_bill(bill_no, db)
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
        request=request,
        name="purchase_section/purchase_bill_detail.html",
        context={
            "purchase": purchase_bill,
            "current_user" : current_user,
            "current_date": current_date
        },
    )

@purchase_router.get("/recent-purchase-bills")
async def purchase_bills_page(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
        request=request,
        name="purchase_section/recent_purchase_list.html",
        context={
            "current_user" : current_user,
            "current_date": current_date
        }
    )

@purchase_router.get("/export-purchase-bills")
async def export_purchase_bills(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
        request=request,
        name="purchase_section/export_purchase_bill.html",
        context={
            "current_user" : current_user,
            "current_date": current_date
        }
    )

@purchase_router.get("/purchase-bill")
async def purchase_bill_page(
    request: Request,
    current_user: CompanyUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)    
):
    next_bill_no = await get_next_purchase_bill_no(db)
    purchase_bill_config = {
    "market_name": settings.MARKET_NAME,
    "market_taluka": settings.MARKET_TALUKA,
    "market_district": settings.MARKET_DISTRICT,

    "adat_name": settings.ADAT_NAME,

    "buyer_name": settings.BUYER_NAME,
    "buyer_mobile_1": settings.BUYER_MOBILE_1,
    "buyer_mobile_2": settings.BUYER_MOBILE_2,

    "expenses": [
        {
            "key": "additionalProp1",
            "name": settings.EXPENSE_1_NAME,
            "amount": settings.PURCHASE_EXPENSE_ADAT,
        },
        {
            "key": "additionalProp2",
            "name": settings.EXPENSE_2_NAME,
            "amount": settings.PURCHASE_EXPENSE_HAMALI,
        },
        {
            "key": "additionalProp3",
            "name": settings.EXPENSE_3_NAME,
            "amount": settings.PURCHASE_EXPENSE_TOLAI,
        },
        {
            "key": "additionalProp4",
            "name": settings.EXPENSE_4_NAME,
            "amount": settings.PURCHASE_EXPENSE_VARAI,
        },
        {
            "key": "additionalProp5",
            "name": settings.EXPENSE_5_NAME,
            "amount": settings.PURCHASE_EXPENSE_TICKET,
        },
    ],
}
    return templates.TemplateResponse(
        request =  request,
        name="purchase_bill/purchase_bill.html",
        context = {
            "current_user": current_user,
            "bill_config": purchase_bill_config,
            "next_bill_no": next_bill_no,
        }
    )