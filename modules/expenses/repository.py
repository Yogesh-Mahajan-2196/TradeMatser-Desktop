from math import ceil
from sqlalchemy import func, select
from .models import Expenses
from datetime import date, datetime, time

async def create_expense(
    expense_data,
    current_user_id,
    db,
):
    expense = Expenses(
        expense_name=expense_data.expense_name.strip(),
        amount=expense_data.amount,
        category=expense_data.category,
        created_by=current_user_id,
    )

    db.add(expense)
    await db.commit()
    await db.refresh(expense)

    return expense


async def get_all_expenses(
    page,
    page_size,
    from_date,
    to_date,
    category,
    db,
):
    offset = (page - 1) * page_size

    # Base query
    query = select(Expenses)

    if category:
        query = query.where(
            Expenses.category == category
        )

    # Single date:
    # from_date exists, but to_date is empty
    if from_date and not to_date:
        start_datetime = datetime.combine(
            from_date,
            time.min,
        )

        end_datetime = datetime.combine(
            from_date,
            time.max,
        )

        query = query.where(
            Expenses.created_at >= start_datetime,
            Expenses.created_at <= end_datetime,
        )

    # Date range:
    # both from_date and to_date exist
    elif from_date and to_date:
        start_datetime = datetime.combine(
            from_date,
            time.min,
        )

        end_datetime = datetime.combine(
            to_date,
            time.max,
        )

        query = query.where(
            Expenses.created_at >= start_datetime,
            Expenses.created_at <= end_datetime,
        )

    # Count after applying filters
    count_query = (
        select(func.count())
        .select_from(
            query.subquery()
        )
    )

    total_result = await db.execute(
        count_query
    )

    total = total_result.scalar_one()

    # Apply sorting and pagination
    query = (
        query
        .order_by(
            Expenses.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)

    expenses = result.scalars().all()

    expense_list = [
        expense_to_dict(expense)
        for expense in expenses
    ]

    total_pages = (
        ceil(total / page_size)
        if total > 0
        else 0
    )

    return {
        "items": expense_list,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


async def get_expense_by_id(
    expense_id,
    db,
):
    result = await db.execute(
        select(Expenses).where(
            Expenses.id == expense_id
        )
    )

    expense = result.scalar_one_or_none()

    if expense is None:
        return None

    return expense


async def update_expense(
    expense_id,
    expense_data,
    db,
):
    expense = await get_expense_by_id(
        expense_id=expense_id,
        db=db,
    )

    if expense is None:
        return None

    update_data = expense_data.dict(
        exclude_unset=True
    )

    if "expense_name" in update_data:
        expense.expense_name = (
            update_data["expense_name"].strip()
        )
    if "amount" in update_data:
        expense.amount = update_data["amount"]

    if "category" in update_data:
        expense.category = update_data["category"]

    await db.commit()
    await db.refresh(expense)

    return expense


async def delete_expense(
    expense_id,
    db,
):
    expense = await get_expense_by_id(
        expense_id=expense_id,
        db=db,
    )

    if expense is None:
        return False

    await db.delete(expense)
    await db.commit()

    return True

def expense_to_dict(expense: Expenses):
    return {
        "id": expense.id,
        "expense_name": expense.expense_name,
        "category": expense.category.value,
        "amount": float(expense.amount),
        "created_at": (
            expense.created_at.isoformat()
            if expense.created_at
            else None
        ),
        "created_by": expense.created_by,
    }

async def get_expense_category_summary(
    from_date,
    to_date,
    category,
    db,
):
    query = select(
        Expenses.category,
        func.coalesce(
            func.sum(Expenses.amount),
            0,
        ).label("total_amount"),
    ).group_by(
        Expenses.category
    )

    if category:
        query = query.where(
            Expenses.category
            == category
        )

    # Single date
    if from_date and not to_date:
        start_datetime = datetime.combine(
            from_date,
            time.min,
        )

        end_datetime = datetime.combine(
            from_date,
            time.max,
        )

        query = query.where(
            Expenses.created_at >= start_datetime,
            Expenses.created_at <= end_datetime,
        )

    # Date range
    elif from_date and to_date:
        start_datetime = datetime.combine(
            from_date,
            time.min,
        )

        end_datetime = datetime.combine(
            to_date,
            time.max,
        )

        query = query.where(
            Expenses.created_at >= start_datetime,
            Expenses.created_at <= end_datetime,
        )

    result = await db.execute(query)

    rows = result.all()

    total_expense = sum(
        float(row.total_amount or 0)
        for row in rows
    )

    categories = []

    for row in rows:
        amount = float(
            row.total_amount or 0
        )

        percentage = (
            round(
                (amount / total_expense) * 100,
                2,
            )
            if total_expense > 0
            else 0
        )

        categories.append(
            {
                "category": (
                    row.category.value
                    if hasattr(
                        row.category,
                        "value",
                    )
                    else str(
                        row.category
                    )
                ),
                "amount": amount,
                "percentage": percentage,
            }
        )

    # Highest expense first
    categories.sort(
        key=lambda item: item["amount"],
        reverse=True,
    )

    return {
        "total_expense": total_expense,
        "categories": categories,
    }