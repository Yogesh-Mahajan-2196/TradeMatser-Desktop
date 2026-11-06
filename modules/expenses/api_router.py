from datetime import date

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from modules.auth.api_router import get_current_active_user
from modules.auth.models import CompanyUser
from utils.database import get_db
from .config import expense_setting
from .schemas import (
    ExpenseCategory,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
)
from .repository import (
    create_expense,
    delete_expense,
    get_all_expenses,
    update_expense,
    get_expense_category_summary
)


expense_router = APIRouter(
    tags= expense_setting.TAG,
)

@expense_router.post("/create-expense")
async def create_new_expense(
    expense_data: ExpenseCreate,
    current_user: CompanyUser = Depends(
        get_current_active_user
    ),
    db: AsyncSession = Depends(get_db),
):
    expense = await create_expense(
        expense_data=expense_data,
        current_user_id=current_user.id,
        db=db,
    )

    return expense


@expense_router.get("/get-expenses")
async def get_expense_data(
    page: int = 1,
    page_size: int = 10,
    from_date: date | None = Query(
        default=None,
    ),
    to_date: date | None = Query(
        default=None,
    ),
    category: ExpenseCategory | None = None,
    current_user: CompanyUser = Depends(
        get_current_active_user
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await get_all_expenses(
        page,
        page_size,
        from_date,
        to_date,
        category,
        db,
    )

    return result

@expense_router.put("/update-expense/{expense_id}")
async def update_existing_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    current_user: CompanyUser = Depends(
        get_current_active_user
    ),
    db: AsyncSession = Depends(get_db),
):
    expense = await update_expense(
        expense_id=expense_id,
        expense_data=expense_data,
        db=db,
    )

    if expense is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    return expense

@expense_router.delete("/delete-expense/{expense_id}")
async def remove_expense(
    expense_id: int,
    current_user: CompanyUser = Depends(
        get_current_active_user
    ),
    db: AsyncSession = Depends(get_db),
):
    deleted = await delete_expense(
        expense_id=expense_id,
        db=db,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found.",
        )

    return {
        "message": "Expense deleted successfully."
    }

@expense_router.get("/expense-category-summary")
async def expense_category_summary(
    from_date: date | None = Query(
        default=None,
    ),
    to_date: date | None = Query(
        default=None,
    ),
    category: (
        ExpenseCategory | None
    ) = None,
    current_user: CompanyUser = Depends(
        get_current_active_user
    ),
    db: AsyncSession = Depends(
        get_db
    ),
):
    return await get_expense_category_summary(
        from_date,
        to_date,
        category,
        db,
    )