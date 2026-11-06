from datetime import timedelta 
from fastapi.responses import JSONResponse
from .models import CompanyUser
from .config import auth_setting
from fastapi import APIRouter, Cookie, Depends, HTTPException, Header, Request, status
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from typing import Annotated
from .schemas import ChangePassword, CreateCompany, CreateUser, UpdateCompanyUser
from .repository import get_user, user_register, authenticate_user,create_access_token, password_change, role_change, company_user_update
from jose import jwt
from jose.exceptions import JWTError

# oauth2_scheme = OAuth2PasswordBearer(
#     tokenUrl="/login",
#     auto_error=False
# )

auth_router = APIRouter(
    tags= auth_setting.TAG
)

async def get_access_token(
    authorization: str | None = Header(
        default=None
    ),
    access_token: str | None = Cookie(
        default=None
    )
) -> str:
    # First check Authorization header
    if authorization:
        scheme, _, token = authorization.partition(" ")

        if (
            scheme.lower() == "bearer"
            and token
        ):
            return token

    # If header is not available,
    # check browser cookie
    if access_token:
        return access_token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication token is missing",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

async def get_current_user(
    token: Annotated[
        str,
        Depends(get_access_token)
    ],
    db: AsyncSession = Depends(get_db)
) -> CompanyUser:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = jwt.decode(
            token,
            auth_setting.SECRET_KEY,
            algorithms=[
                auth_setting.ALGORITHM
            ]
        )

        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = await get_user(
        username,
        db
    )

    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: Annotated[CompanyUser, Depends(get_current_user)],
):
    return current_user

@auth_router.post("/register")
async def register_user(user_data: CreateUser, db:AsyncSession = Depends(get_db)):
    create_user = await user_register(user_data, db)
    return create_user

@auth_router.post("/login")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:AsyncSession = Depends(get_db)):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth_setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email_id}, exp_time=access_token_expires)
    
    response = JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer",
            "role_id": user.role_id.value
        }
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        path="/",
        max_age=(
            auth_setting
            .ACCESS_TOKEN_EXPIRE_MINUTES
            * 60
        ),
    )

    return response
    

@auth_router.get("/users/me/")
async def read_users_me(
    current_user: Annotated[CompanyUser, Depends(get_current_active_user)]):
    return current_user

@auth_router.patch("/change-password")
async def change_password(data: ChangePassword, current_user: CompanyUser = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    res = await password_change(data, current_user, db)
    return res

@auth_router.patch("/change-role")
async def change_role(user_id: int, updated_role: int, current_user: CompanyUser = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    if current_user.role_id != 1:
        raise HTTPException(status_code=401, detail=auth_setting.UNAUTHORISED)
    if updated_role > 3:
        raise HTTPException(status_code=404, detail=auth_setting.ROLE_NOT_FOUND)
    if current_user.id == user_id:
        raise HTTPException(status_code=401, detail=auth_setting.UNAUTHORISED)
    
    res = await role_change(user_id,updated_role, db)
    return res

@auth_router.put("/update-company-user")
async def update_company_user(company_user_data: UpdateCompanyUser,  current_user: CompanyUser = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail=auth_setting.UNAUTHORISED)
    res = await company_user_update(company_user_data, db)
    return res

@auth_router.post("/logout")
async def logout_user():

    response = JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Logout successful"
        }
    )

    response.delete_cookie(
        key="access_token",
        path="/"
    )

    return response


async def get_optional_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    access_token = request.cookies.get(
        "access_token"
    )

    # User is not logged in
    if not access_token:
        return None

    try:
        payload = jwt.decode(
            access_token,
            auth_setting.SECRET_KEY,
            algorithms=[
                auth_setting.ALGORITHM
            ]
        )

        username = payload.get("sub")

        if not username:
            return None

        user = await get_user(
            username,
            db
        )

        return user

    except JWTError:
        return None


@auth_router.post("/create-company")
async def create_company(company_data: CreateCompany, db:AsyncSession = Depends(get_db)):
    create_company = await company_register(company_data, db)
    return create_company