from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from modules.parties.repository import customer_data
from utils.database import get_db
from datetime import datetime
from zoneinfo import ZoneInfo


parties_router = APIRouter(
    tags = ["Parties"]
)
templates=Jinja2Templates(directory="templates")

@parties_router.get('/customers')
async def get_parties(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
            request=request,
            name="parties_section/customers.html",
            context={
                "current_user" : current_user,
                "current_date": current_date
            }
        )

@parties_router.get('/customer/{mob_no}')
async def get_customer(mob_no: str, request: Request, db: AsyncSession = Depends(get_db),current_user: CompanyUser = Depends(get_current_active_user)):

    customers = await customer_data(mob_no, db)
    return templates.TemplateResponse(
            request=request,
            name="parties_section/customer.html",
            context={
                    "customers": customers,
                    "current_user" : current_user
                },
        )

