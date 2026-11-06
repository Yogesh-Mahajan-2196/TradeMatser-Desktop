from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from modules.reports.export_purchase_report import export_purchase_report
from modules.reports.repository import daily_report, out_payables, out_receivalble, recent_purchases_data, sell_rep, purchase_rep, export_sell_report, send_daily_report
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from .config import reports_setting

report_router = APIRouter(
    tags = reports_setting.TAG
)

# Purchase Reports
@report_router.get("/recent-purchases")
async def recent_purchases(
    page: int = 1,
    page_size: int = 10,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")
    res = await recent_purchases_data(db, page, page_size)
    return res

@report_router.get("/purchase-report")
async def purchase_report(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    product_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    sort_by: str = "bill_date",
    order: str = "desc",
    page: int = 1,
    page_size: int = 10,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")
    res = await purchase_rep(from_date,to_date,product_id,payment_status,sort_by,order,page,page_size,db)
    return res

@report_router.get("/purchase-report/export")
async def export_purchase_report_api(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    product_id: Optional[int] = None,
    payment_status: Optional[str] = None,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):

    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")

    file_path = await export_purchase_report(
        db,
        from_date,
        to_date,
        product_id,
        payment_status,
    )

    return FileResponse(
        path=file_path,
        filename="Purchase_Report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )



# Sell Reports
@report_router.get("/sell-report")
async def sell_report(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    product_id: Optional[int] = None,
    bill_no: Optional[str] = None,
    payment_status: Optional[str] = None,
    sort_by: str = "bill_date",
    order: str = "desc",
    page: int = 1,
    page_size: int = 10,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")
    res = await sell_rep(from_date,to_date,product_id,bill_no,payment_status,sort_by,order,page,page_size,db)
    return res

@report_router.get("/sell-report/export")
async def export_sell_report_api(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    product_id: Optional[int] = None,
    bill_no: Optional[str] = None,
    payment_status: Optional[str] = None,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):

    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")

    file_path = await export_sell_report(
        db,
        from_date,
        to_date,
        product_id,
        bill_no,
        payment_status,
    )

    return FileResponse(
        path=file_path,
        filename="Sell_Report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )



# Outstandings
@report_router.get("/outstanding-receivables")
async def outstanding_receivables(
    page: int = 1,
    page_size: int = 10,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")
    res = await out_receivalble(db, page, page_size)
    return res

@report_router.get("/outstanding-payables")
async def outstanding_payables(
    page: int = 1,
    page_size: int = 10,
    current_user: CompanyUser = Depends(get_current_active_user), 
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.role_id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")
    res = await out_payables(db, page, page_size)
    return res


#  Daily Report for admin
@report_router.get("/daily-report")
async def get_daily_report(
    background_tasks: BackgroundTasks,
    current_user: CompanyUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
    ):
    if current_user.id == 3:
        raise HTTPException(status_code=401, detail="Unauthorised user.")

    report = await daily_report(db)

    # Email sending happens after the response
    background_tasks.add_task(
        send_daily_report,
        report,
    )


    return {
        "message": "Daily report request accepted. Email is being sent in the background."
    }

