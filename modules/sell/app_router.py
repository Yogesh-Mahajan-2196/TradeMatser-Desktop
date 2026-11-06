from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from modules.sell.repository import get_bill, get_next_sell_bill_no
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from utils.config import settings
from datetime import datetime
from zoneinfo import ZoneInfo

sell_router = APIRouter(
    tags = ["Sell"]
)
templates=Jinja2Templates(directory="templates")

@sell_router.get('/export-sell-reports')
async def get_sell_reports(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
                    request=request,
                    name="sell_section/sell_reports.html",
                    context={
                        "current_user" : current_user,
                        "current_date": current_date
                    }
                )

@sell_router.get('/sell-report/{bill_no}')
async def get_sell_report(bill_no: int, request: Request, db: AsyncSession = Depends(get_db), current_user: CompanyUser = Depends(get_current_active_user)):
    sell_report = await get_bill(bill_no. db)
    return templates.TemplateResponse(
                    request=request,
                    name="sell_section/sell_report.html",
                    context={
                        "sell_report": sell_report,
                        "current_user" : current_user
                    },
                )


@sell_router.get('/sell-bill')
async def get_sell_reports(request: Request, current_user: CompanyUser = Depends(get_current_active_user),
db: AsyncSession = Depends(get_db) ):
    sell_bill_config = {
        "bank_name": settings.BANK_NAME,
        "account_no": settings.ACCOUNT_NO,
        "ifsc_code": settings.IFSC_CODE,
        "email": settings.EMAIL,
        "company_name": settings.COMPANY_NAME,
        "owner_name": settings.OWNER_NAME,
        "company_address": settings.COMPANY_ADDRESS,
        "mobile_no_1": settings.BUYER_MOBILE_1,
        "mobile_no_2": settings.BUYER_MOBILE_2,
        "mobile_no_3": settings.BUYER_MOBILE_3

    }
    next_bill_no = await get_next_sell_bill_no(db)
    return templates.TemplateResponse(
                    request=request,
                    name="sell_bill/sell_bill.html",
                    context={
                        "current_user" : current_user,
                        "bill_config": sell_bill_config,
                        "next_bill_no": next_bill_no,
                    }
                )