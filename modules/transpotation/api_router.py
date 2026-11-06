from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from typing import Optional
from modules.transpotation.repository import create_driver_info, delete_driver, get_all_driver, get_driver, update_driver_info
from modules.transpotation.schemas import CreateTransportaion
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from.config import transpotation_setting

transpotation_router = APIRouter(
    tags= transpotation_setting.TAG
)

@transpotation_router.post("/create-truck-info")
async def create_truck_info(
    driver_data:CreateTransportaion,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await create_driver_info(driver_data, current_user.id, db)
    return res

@transpotation_router.put("/update-truck-info")
async def update_truck_info(
    truck_id: int,
    driver_data:CreateTransportaion,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await update_driver_info(truck_id,driver_data, db)
    return res

@transpotation_router.get("/get-truck-info")
async def get_truck_info(
    truck_id: int,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await get_driver(truck_id, db)
    return res

@transpotation_router.get("/get-all-truck-info")
async def get_all_truck_info(
    page: int = 1,
    page_size: int = 8,
    truck_number: Optional[str] = None,
    current_user: CompanyUser = Depends(
        get_current_active_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    return await get_all_driver(
        page=page,
        page_size=page_size,
        truck_number=truck_number,
        db=db,
    )

@transpotation_router.delete("/delete-truck-info")
async def delete_truck_info(
    truck_id: int,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    res = await delete_driver(truck_id, db)
    return res

