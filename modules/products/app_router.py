from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser

product_router = APIRouter(
    tags = ["Product"]
)
templates=Jinja2Templates(directory="templates")

@product_router.get('/products')
async def get_products(request: Request, current_user: CompanyUser = Depends(get_current_active_user)):
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
                request=request,
                name="product_section/products.html",
                context={
                    "current_user" : current_user,
                    "current_date": current_date
                }
            )
