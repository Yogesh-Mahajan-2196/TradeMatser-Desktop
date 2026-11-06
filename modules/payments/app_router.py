from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser

payment_router = APIRouter(
    tags = ["Payments"]
)
templates=Jinja2Templates(directory="templates")

@payment_router.get('/payments')
async def payments(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
                request=request,
                name="payments/payments.html",
                context={
                    "current_user" : current_user,
                    "current_date": current_date
                }
            )