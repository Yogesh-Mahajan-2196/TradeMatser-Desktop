from fastapi import APIRouter, Depends
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from modules.products.repository import product_create, product_list, product_update
from modules.products.schemas import CreateProduct, ProductUpdate
from .config import product_setting
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

product_router = APIRouter(
    tags=product_setting.TAG
)

@product_router.post("/create-product")
async def create_product(
    prod_data: CreateProduct,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await product_create(prod_data,current_user.id,db)
    return res

@product_router.get("/get-products")
async def get_products(
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    return await product_list(db)

@product_router.put("/update-product")
async def update_product(
    update_data: ProductUpdate,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    return await product_update(update_data,db)