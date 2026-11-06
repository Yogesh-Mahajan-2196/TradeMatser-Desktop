from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.templating import Jinja2Templates

from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from datetime import datetime
from zoneinfo import ZoneInfo


transpotation_router = APIRouter(
    tags = ["Transpotation"]
)
templates=Jinja2Templates(directory="templates")

@transpotation_router.get('/transpotation')
async def get_transpotation(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
                        request=request,
                        name="transpotation_section/transpotation.html",
                        context={
                            "current_user" : current_user,
                            "current_date": current_date
                        }
                    )