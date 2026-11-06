from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from datetime import datetime
from zoneinfo import ZoneInfo

expense_router = APIRouter(
    tags = ["Expenses"]
)
templates=Jinja2Templates(directory="templates")

@expense_router.get('/expenses')
async def get_espenses(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
            request=request,
            name="expense_section/expenses.html",
            context={
                "current_user" : current_user,
                "current_date": current_date
            }
        )