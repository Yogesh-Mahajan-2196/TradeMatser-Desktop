from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from modules.auth.api_router import get_optional_current_user
from modules.auth.models import CompanyUser

auth_router = APIRouter(
    tags= ["Auth"]
)

templates=Jinja2Templates(directory="templates")

@auth_router.get("/login")
async def login(request: Request,
                current_user: CompanyUser | None = Depends(get_optional_current_user)
                ):
    if current_user:
        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )
    
    return templates.TemplateResponse(
    request=request,
    name="/auth/login.html",
)

@auth_router.get("/company-users")
async def company_users(request: Request):
    # users = await 
    return templates.TemplateResponse(
    request=request,
    name="/auth/company_users.html",
)

@auth_router.post("/logout")
async def logout_user():

    response = RedirectResponse(
        url="/login",
        status_code=303
    )

    response.delete_cookie(
        key="access_token"
    )

    return response


@auth_router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="/auth/signup.html",
        context={}
    )