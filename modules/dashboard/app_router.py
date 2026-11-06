from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates
from rich import status
from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from modules.dashboard.repository import daily_summery, net_profit, purchase_vs_sell, stock_summery, total_expense, total_purchase, total_sell
from modules.reports.repository import out_payables, out_receivalble, recent_purchases_data
from utils.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

dashboard_router = APIRouter(
    tags = ["Dashboard"]
)
templates=Jinja2Templates(directory="templates")

@dashboard_router.get("/dashboard")
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: CompanyUser = Depends(get_current_active_user)
    ):
    
    if current_user.role_id == 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access the dashboard.",
        )

    page = 1
    page_size = 5
    period = "1month"
    
    total_purchase_data = await total_purchase(db)
    total_sell_data = await total_sell(db)
    total_expense_data = await total_expense(db)
    net_profit_data = await net_profit(db)
    purchase_vs_sell_data = await get_purchase_vs_sell_graph(period,db)
    recent_purchases = await recent_purchases_data(db, page, page_size)
    stock_summery_data = await stock_summery(db)
    outstanding_receivables = await out_receivalble(db, page, page_size)
    outstanding_payables = await out_payables(db, page, page_size)
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))

    return templates.TemplateResponse(
        request=request,
        name="dashboard/dashboard.html",
        context={
            "total_purchases": total_purchase_data,
            "total_sells": total_sell_data,
            "total_expenses": total_expense_data,
            "net_profit": net_profit_data,
            "purchase_vs_sell_data": purchase_vs_sell_data,
            "recent_purchases": recent_purchases,
            "stock_summery_data": stock_summery_data,
            "outstanding_receivables": outstanding_receivables,
            "outstanding_payables": outstanding_payables,
            "current_user" : current_user,
            "current_date": current_date
        },
    )


@dashboard_router.get("/purchase-vs-sell")
async def get_purchase_vs_sell_graph(
    period: str = "1month",
    db: AsyncSession = Depends(get_db)
    ):

    graph_data = (
        await purchase_vs_sell(
            db=db,
            period=period,
        )
    )
    return graph_data

# @dashboard_router.get("/daily-summary")
# async def daily_summary_page(
#     request: Request,
#     current_user: CompanyUser = Depends(
#         get_current_active_user
#     ),
# ):

#     daily_summary = await daily_summery()
#     return templates.TemplateResponse(
#         request=request,
#         name="reports/daily_summary.html",
#         context={
#             "current_user": current_user,
#             "daily_summary": daily_summary,
#         },
#     )

@dashboard_router.get("/daily-summary")
async def daily_summary_page(
    request: Request,
    target_date: date | None = Query(None, alias="date"),
    current_user: CompanyUser = Depends(get_current_active_user),
):
    daily_summary = await daily_summery(target_date)
    current_date = datetime.now(ZoneInfo("Asia/Kolkata"))
    return templates.TemplateResponse(
        request=request,
        name="reports/daily_summary.html",
        context={
            "current_user": current_user,
            "current_date": current_date,
            "daily_summary": daily_summary,
            "timedelta": timedelta,   # needed for the prev/next date arrows in the template
        },
    )