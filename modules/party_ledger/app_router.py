from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser

party_leadger_router = APIRouter(
    tags = ["Party Ledger"]
)
templates=Jinja2Templates(directory="templates")

@party_leadger_router.get('/party-ledger')
async def party_ledger(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
                request=request,
                name="party_ledger/party_ledger.html",
                context={
                    "current_user" : current_user,
                    "current_date": current_date
                }
            )
