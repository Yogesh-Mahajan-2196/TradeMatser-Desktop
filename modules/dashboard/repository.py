from datetime import date, timedelta

from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload

from modules.products.models import Products
from modules.purchase.models import PurchaseBill, PurchaseBillItem
from modules.sell.models import SellBill, SellBillItem
from utils.financial_year import get_current_financial_year

async def total_purchase(db):

    today = date.today()

    (
        financial_year_start,
        financial_year_end
    ) = get_current_financial_year()

    total_query = await db.execute(

        select(

            func.coalesce(
                func.sum(
                    PurchaseBillItem.total_amount
                ),
                0
            )

        )
        .join(
            PurchaseBill,
            PurchaseBillItem.purchase_bill_id
            == PurchaseBill.id
        )
        .where(

            PurchaseBill.bill_date >=
            financial_year_start,

            PurchaseBill.bill_date <=
            financial_year_end

        )

    )

    total_amount = (
        total_query.scalar_one()
    )


    today_query = await db.execute(

        select(

            func.coalesce(
                func.sum(
                    PurchaseBillItem.total_amount
                ),
                0
            )

        )
        .join(
            PurchaseBill,
            PurchaseBillItem.purchase_bill_id
            == PurchaseBill.id
        )
        .where(

            PurchaseBill.bill_date >=
            financial_year_start,

            PurchaseBill.bill_date <=
            financial_year_end,

            func.date(
                PurchaseBill.bill_date
            ) == today

        )

    )

    today_amount = (
        today_query.scalar_one()
    )

    return {

        "total": float(
            total_amount
        ),

        "today": float(
            today_amount
        ),

    }

async def total_sell(db):

    today = date.today()

    (
        financial_year_start,
        financial_year_end
    ) = get_current_financial_year()

    total_query = await db.execute(

        select(

            func.coalesce(
                func.sum(
                    SellBillItem.net_amount
                ),
                0
            )

        )
        .join(
            SellBill,
            SellBillItem.sell_bill_id
            == SellBill.id
        )
        .where(

            SellBill.bill_date >=
            financial_year_start,

            SellBill.bill_date <=
            financial_year_end

        )

    )

    total_amount = (
        total_query.scalar_one()
    )


    today_query = await db.execute(

        select(

            func.coalesce(
                func.sum(
                    SellBillItem.net_amount
                ),
                0
            )

        )
        .join(
            SellBill,
            SellBillItem.sell_bill_id
            == SellBill.id
        )
        .where(

            SellBill.bill_date >=
            financial_year_start,

            SellBill.bill_date <=
            financial_year_end,

            func.date(
                SellBill.bill_date
            ) == today

        )

    )

    today_amount = (
        today_query.scalar_one()
    )

    return {

        "total": float(
            total_amount
        ),

        "today": float(
            today_amount
        ),

    }

async def total_expense(db):

    today = date.today()

    (
        financial_year_start,
        financial_year_end
    ) = get_current_financial_year()


    # Current financial-year expenses

    total_result = await db.execute(

        select(
            PurchaseBillItem.expenses
        )
        .join(
            PurchaseBill,
            PurchaseBillItem.purchase_bill_id
            == PurchaseBill.id
        )
        .where(

            PurchaseBill.bill_date >=
            financial_year_start,

            PurchaseBill.bill_date <=
            financial_year_end

        )

    )

    all_expenses = (
        total_result.scalars().all()
    )

    total_expense_amount = 0

    for expense_data in all_expenses:

        if not expense_data:
            continue

        for amount in (
            expense_data.values()
        ):

            total_expense_amount += (
                float(amount)
            )


    # Today's expenses

    today_result = await db.execute(

        select(
            PurchaseBillItem.expenses
        )
        .join(
            PurchaseBill,
            PurchaseBillItem.purchase_bill_id
            == PurchaseBill.id
        )
        .where(

            PurchaseBill.bill_date >=
            financial_year_start,

            PurchaseBill.bill_date <=
            financial_year_end,

            func.date(
                PurchaseBill.bill_date
            ) == today

        )

    )

    today_expenses = (
        today_result.scalars().all()
    )

    today_expense_amount = 0

    for expense_data in (
        today_expenses
    ):

        if not expense_data:
            continue

        for amount in (
            expense_data.values()
        ):

            today_expense_amount += (
                float(amount)
            )

    return {

        "total": round(
            total_expense_amount,
            2
        ),

        "today": round(
            today_expense_amount,
            2
        )

    }

async def net_profit(db):

    purchase_data = await total_purchase(db)

    sell_data = await total_sell(db)

    expense_data = await total_expense(db)

    total_profit = (

        sell_data["total"]

        - purchase_data["total"]

        - expense_data["total"]

    )

    today_profit = (

        sell_data["today"]

        - purchase_data["today"]

        - expense_data["today"]

    )

    return {

        "total": round(
            total_profit,
            2
        ),

        "today": round(
            today_profit,
            2
        )

    }

async def purchase_vs_sell(
    db,
    period
    ):

    today = date.today()

    # ==================================
    # 1. SET DATE RANGE
    # ==================================

    if period == "7days":

        start_date = (
            today
            - timedelta(days=6)
        )

        end_date = today

        group_type = "day"


    elif period == "1month":

        start_date = (
            today.replace(day=1)
        )

        end_date = today

        group_type = "day"


    elif period == "1year":

        # Current financial year:
        # April to March

        if today.month >= 4:

            start_date = date(
                today.year,
                4,
                1,
            )

        else:

            start_date = date(
                today.year - 1,
                4,
                1,
            )

        end_date = today

        group_type = "month"


    else:

        raise ValueError(
            "Invalid period. "
            "Use 7days, 1month, or 1year."
        )


    # ==================================
    # 2. SELECT GROUPING COLUMN
    # ==================================

    if group_type == "day":

        purchase_group_column = (
            func.date(
                PurchaseBill.bill_date
            )
        )

        sell_group_column = (
            func.date(
                SellBill.bill_date
            )
        )


    else:

        # Convert date_trunc result to DATE.
        # This makes it match current_month,
        # which is a Python date object.

        purchase_group_column = (
            func.date(
                func.date_trunc(
                    "month",
                    PurchaseBill.bill_date,
                )
            )
        )

        sell_group_column = (
            func.date(
                func.date_trunc(
                    "month",
                    SellBill.bill_date,
                )
            )
        )


    # ==================================
    # 3. PURCHASE QUERY
    # ==================================

    purchase_result = await db.execute(

        select(

            purchase_group_column.label(
                "report_date"
            ),

            func.coalesce(

                func.sum(
                    PurchaseBillItem.total_amount
                ),

                0,

            ).label(
                "amount"
            ),

        )

        .select_from(
            PurchaseBill
        )

        .join(

            PurchaseBillItem,

            PurchaseBillItem.purchase_bill_id
            == PurchaseBill.id,

        )

        .where(

            func.date(
                PurchaseBill.bill_date
            ).between(
                start_date,
                end_date,
            )

        )

        .group_by(
            purchase_group_column
        )

        .order_by(
            purchase_group_column
        )

    )

    purchase_rows = (
        purchase_result.all()
    )


    # ==================================
    # 4. SELL QUERY
    # ==================================

    sell_result = await db.execute(

        select(

            sell_group_column.label(
                "report_date"
            ),

            func.coalesce(

                func.sum(
                    SellBillItem.net_amount
                ),

                0,

            ).label(
                "amount"
            ),

        )

        .select_from(
            SellBill
        )

        .join(

            SellBillItem,

            SellBillItem.sell_bill_id
            == SellBill.id,

        )

        .where(

            func.date(
                SellBill.bill_date
            ).between(
                start_date,
                end_date,
            )

        )

        .group_by(
            sell_group_column
        )

        .order_by(
            sell_group_column
        )

    )

    sell_rows = (
        sell_result.all()
    )


    # ==================================
    # 5. CREATE DATA MAPS
    # ==================================

    purchase_map = {

        row.report_date:
        float(row.amount)

        for row in purchase_rows

    }


    sell_map = {

        row.report_date:
        float(row.amount)

        for row in sell_rows

    }


    # ==================================
    # 6. CREATE GRAPH DATA
    # ==================================

    labels = []

    purchase_values = []

    sell_values = []


    # ==================================
    # 7. DAILY GRAPH
    # 7 DAYS / CURRENT MONTH
    # ==================================

    if group_type == "day":

        current_date = start_date

        while current_date <= end_date:

            labels.append(

                current_date.strftime(
                    "%d %b"
                )

            )

            purchase_values.append(

                purchase_map.get(
                    current_date,
                    0,
                )

            )

            sell_values.append(

                sell_map.get(
                    current_date,
                    0,
                )

            )

            current_date += (
                timedelta(days=1)
            )


    # ==================================
    # 8. MONTHLY GRAPH
    # CURRENT FINANCIAL YEAR
    # ==================================

    else:

        current_month = start_date

        while current_month <= end_date:

            labels.append(

                current_month.strftime(
                    "%b"
                )

            )

            purchase_values.append(

                purchase_map.get(
                    current_month,
                    0,
                )

            )

            sell_values.append(

                sell_map.get(
                    current_month,
                    0,
                )

            )


            # Move to the first day
            # of the next month

            if current_month.month == 12:

                current_month = date(

                    current_month.year + 1,

                    1,

                    1,

                )

            else:

                current_month = date(

                    current_month.year,

                    current_month.month + 1,

                    1,

                )


    # ==================================
    # 9. RETURN GRAPH DATA
    # ==================================

    return {

        "period": period,

        "labels": labels,

        "purchase": purchase_values,

        "sell": sell_values,

    }

async def stock_summery(db):

    purchase_subquery = (
        select(
            PurchaseBillItem.product_id.label(
                "product_id"
            ),

            func.coalesce(
                func.sum(
                    PurchaseBillItem.weight
                ),
                0
            ).label(
                "purchase_quantity"
            ),

            func.coalesce(
                func.sum(
                    PurchaseBillItem.weight
                    * PurchaseBillItem.rate
                ),
                0
            ).label(
                "purchase_amount"
            )
        )
        .group_by(
            PurchaseBillItem.product_id
        )
        .subquery()
    )

    sell_subquery = (
        select(
            SellBillItem.product_id.label(
                "product_id"
            ),

            func.coalesce(
                func.sum(
                    SellBillItem.weight
                ),
                0
            ).label(
                "sell_quantity"
            )
        )
        .group_by(
            SellBillItem.product_id
        )
        .subquery()
    )

    query = (
        select(
            Products.id.label(
                "product_id"
            ),

            Products.product_name.label(
                "product_name"
            ),

            func.coalesce(
                purchase_subquery.c.purchase_quantity,
                0
            ).label(
                "purchase_quantity"
            ),

            func.coalesce(
                sell_subquery.c.sell_quantity,
                0
            ).label(
                "sell_quantity"
            ),

            func.coalesce(
                purchase_subquery.c.purchase_amount,
                0
            ).label(
                "purchase_amount"
            )
        )
        .outerjoin(
            purchase_subquery,
            Products.id
            == purchase_subquery.c.product_id
        )
        .outerjoin(
            sell_subquery,
            Products.id
            == sell_subquery.c.product_id
        )
        .order_by(
            Products.product_name
        )
    )

    result = await db.execute(
        query
    )

    stock_rows = result.mappings().all()

    response = []

    for stock in stock_rows:

        purchase_quantity = float(
            stock["purchase_quantity"]
            or 0
        )

        sell_quantity = float(
            stock["sell_quantity"]
            or 0
        )

        purchase_amount = float(
            stock["purchase_amount"]
            or 0
        )

        current_stock = (
            purchase_quantity
            - sell_quantity
        )

        if purchase_quantity > 0:

            average_rate = (
                purchase_amount
                / purchase_quantity
            )

        else:

            average_rate = 0

        stock_value = (
            current_stock
            * average_rate
        )

        # Do not show products
        # with zero or negative stock
        if current_stock <= 0:
            continue

        response.append({
            "product_id": (
                stock["product_id"]
            ),

            "product_name": (
                stock["product_name"]
            ),

            "current_stock": round(
                current_stock,
                2
            ),

            "unit": "Quintal",

            "average_rate": round(
                average_rate,
                2
            ),

            "total_value": round(
                stock_value,
                2
            )
        })

    return response


# async def daily_summery():
#     daily_summary = {
#         "summary_date": date.today(),

#         # Top cards
#         "overview": {
#             "purchase_amount": 380000,
#             "purchase_bills": 12,

#             "sales_amount": 425000,
#             "sales_bills": 9,

#             "expense_amount": 8500,
#             "expense_count": 5,

#             "estimated_profit": 36500,
#         },

#         # Payment section
#         "payments": {
#             "purchase_paid": 280000,
#             "purchase_unpaid": 100000,

#             "sales_paid": 320000,
#             "sales_unpaid": 105000,
#         },

#         # Product table
#         "products": [
#             {
#                 "product_name": "Makka",
#                 "purchase_weight": 200,
#                 "sales_weight": 150,
#                 "remaining_weight": 50,
#                 "unit": "QUINTAL",
#             },
#             {
#                 "product_name": "Wheat",
#                 "purchase_weight": 150,
#                 "sales_weight": 100,
#                 "remaining_weight": 50,
#                 "unit": "QUINTAL",
#             },
#             {
#                 "product_name": "Soybean",
#                 "purchase_weight": 100,
#                 "sales_weight": 70,
#                 "remaining_weight": 30,
#                 "unit": "QUINTAL",
#             },
#         ],

#         # Expense chart and expense list
#         "expense_categories": [
#             {
#                 "category": "Food",
#                 "amount": 2500,
#                 "percentage": 29.41,
#             },
#             {
#                 "category": "Fuel",
#                 "amount": 4000,
#                 "percentage": 47.06,
#             },
#             {
#                 "category": "Transportation",
#                 "amount": 2000,
#                 "percentage": 23.53,
#             },
#         ],

#         # Recent activity table
#         "recent_activities": [
#             {
#                 "time": "09:30 AM",
#                 "type": "Purchase",
#                 "bill_no": 101,
#                 "party_name": "Mahajan Traders",
#                 "amount": 95000,
#                 "status": "Paid",
#             },
#             {
#                 "time": "11:15 AM",
#                 "type": "Sale",
#                 "bill_no": 51,
#                 "party_name": "Shree Foods",
#                 "amount": 125000,
#                 "status": "Unpaid",
#             },
#             {
#                 "time": "01:30 PM",
#                 "type": "Expense",
#                 "bill_no": None,
#                 "party_name": "Diesel",
#                 "amount": 4000,
#                 "status": "-",
#             },
#         ],
#     }

#     return daily_summary 

from datetime import date


async def daily_summery(target_date: date | None = None):
    """
    Returns the complete data payload for the Daily Summary dashboard.
    Every field here maps directly to a widget in the UI:
      - overview            -> top 4 cards
      - payments            -> Payment Summary section
      - products            -> Top Products Summary table
      - expense_categories  -> Expenses by Category donut + list
      - hourly_activity     -> Hourly Business Activity line chart
      - bill_status         -> Bill Status Overview donut
      - recent_activities   -> Recent Activity table
      - quantity_summary    -> bottom 4 stat cards
    """

    summary_date = target_date or date.today()

    daily_summary = {
        "summary_date": summary_date,

        # ---------------------------------------------------------
        # Top 4 overview cards
        # ---------------------------------------------------------
        "overview": {
            "purchase_amount": 380000,
            "purchase_bills": 12,
            "purchase_change_pct": 8.5,          # vs yesterday

            "sales_amount": 425000,
            "sales_bills": 9,
            "sales_change_pct": 12.3,            # vs yesterday

            "expense_amount": 8500,
            "expense_count": 5,
            "expense_change_pct": -3.2,          # vs yesterday (negative = good, expenses down)

            "estimated_profit": 36500,
            "profit_change_pct": 18.6,           # vs yesterday
        },

        # ---------------------------------------------------------
        # Payment Summary section
        # ---------------------------------------------------------
        "payments": {
            "purchase_paid": 280000,
            "purchase_unpaid": 100000,

            "sales_paid": 320000,
            "sales_unpaid": 105000,
        },

        # ---------------------------------------------------------
        # Purchase vs Sales chart + Total Business donut
        # ---------------------------------------------------------
        "business_summary": {
            "total_business": 805000,            # purchase_amount + sales_amount
            "total_business_change_pct": 10.2,   # vs yesterday
        },

        # ---------------------------------------------------------
        # Top Products Summary table
        # ---------------------------------------------------------
        "products": [
            {
                "product_name": "Makka",
                "purchase_weight": 200,
                "sales_weight": 150,
                "remaining_weight": 50,
                "unit": "QUINTAL",
            },
            {
                "product_name": "Wheat",
                "purchase_weight": 150,
                "sales_weight": 100,
                "remaining_weight": 50,
                "unit": "QUINTAL",
            },
            {
                "product_name": "Soybean",
                "purchase_weight": 100,
                "sales_weight": 60,
                "remaining_weight": 40,
                "unit": "QUINTAL",
            },
            {
                "product_name": "Chana",
                "purchase_weight": 80,
                "sales_weight": 30,
                "remaining_weight": 50,
                "unit": "QUINTAL",
            },
            {
                "product_name": "Bajra",
                "purchase_weight": 60,
                "sales_weight": 20,
                "remaining_weight": 40,
                "unit": "QUINTAL",
            },
        ],

        # ---------------------------------------------------------
        # Expenses by Category donut + list
        # ---------------------------------------------------------
        "expense_categories": [
            {
                "category": "Fuel",
                "amount": 4000,
                "percentage": 47.06,
            },
            {
                "category": "Food",
                "amount": 2500,
                "percentage": 29.41,
            },
            {
                "category": "Transportation",
                "amount": 2000,
                "percentage": 23.53,
            },
        ],

        # ---------------------------------------------------------
        # Hourly Business Activity line chart
        # One point per hour the business was active (6 AM - 8 PM)
        # ---------------------------------------------------------
        "hourly_activity": [
            {"hour": "6 AM",  "purchase_amount": 5000,   "sales_amount": 8000},
            {"hour": "7 AM",  "purchase_amount": 12000,  "sales_amount": 20000},
            {"hour": "8 AM",  "purchase_amount": 35000,  "sales_amount": 55000},
            {"hour": "9 AM",  "purchase_amount": 60000,  "sales_amount": 90000},
            {"hour": "10 AM", "purchase_amount": 85000,  "sales_amount": 130000},
            {"hour": "11 AM", "purchase_amount": 95000,  "sales_amount": 150000},
            {"hour": "12 PM", "purchase_amount": 90000,  "sales_amount": 145000},
            {"hour": "1 PM",  "purchase_amount": 100000, "sales_amount": 160000},
            {"hour": "2 PM",  "purchase_amount": 92000,  "sales_amount": 155000},
            {"hour": "3 PM",  "purchase_amount": 98000,  "sales_amount": 165000},
            {"hour": "4 PM",  "purchase_amount": 88000,  "sales_amount": 140000},
            {"hour": "5 PM",  "purchase_amount": 70000,  "sales_amount": 110000},
            {"hour": "6 PM",  "purchase_amount": 45000,  "sales_amount": 75000},
            {"hour": "7 PM",  "purchase_amount": 20000,  "sales_amount": 35000},
            {"hour": "8 PM",  "purchase_amount": 8000,   "sales_amount": 15000},
        ],

        # ---------------------------------------------------------
        # Bill Status Overview donut
        # ---------------------------------------------------------
        "bill_status": {
            "total_bills": 21,
            "paid": 13,
            "paid_pct": 61.9,
            "unpaid": 6,
            "unpaid_pct": 28.6,
            "partially_paid": 2,
            "partially_paid_pct": 9.5,
        },

        # ---------------------------------------------------------
        # Recent Activity table
        # ---------------------------------------------------------
        "recent_activities": [
            {
                "time": "10:30 AM",
                "type": "Purchase",
                "bill_no": 102,
                "party_name": "ABC Traders",
                "product_name": "Makka",
                "amount": 50000,
                "status": "Paid",
            },
            {
                "time": "11:15 AM",
                "type": "Sell",
                "bill_no": 55,
                "party_name": "XYZ Foods",
                "product_name": "Wheat",
                "amount": 75000,
                "status": "Unpaid",
            },
            {
                "time": "12:10 PM",
                "type": "Expense",
                "bill_no": None,
                "party_name": "Fuel",
                "product_name": "Fuel",
                "amount": 4000,
                "status": "-",
            },
            {
                "time": "01:20 PM",
                "type": "Purchase",
                "bill_no": 103,
                "party_name": "Shree Ganesh",
                "product_name": "Soybean",
                "amount": 40000,
                "status": "Paid",
            },
            {
                "time": "03:05 PM",
                "type": "Sell",
                "bill_no": 56,
                "party_name": "Kisan Stores",
                "product_name": "Makka",
                "amount": 60000,
                "status": "Partially Paid",
            },
            {
                "time": "05:40 PM",
                "type": "Expense",
                "bill_no": None,
                "party_name": "Transportation",
                "product_name": "Transportation",
                "amount": 2000,
                "status": "-",
            },
        ],

        # ---------------------------------------------------------
        # Bottom 4 stat cards
        # ---------------------------------------------------------
        "quantity_summary": {
            "total_bills": 21,
            "total_bills_change": 5,             # vs yesterday (absolute count, not %)

            "total_quantity_purchased": 590,
            "total_quantity_purchased_unit": "QUINTAL",
            "total_quantity_purchased_change": 40,

            "total_quantity_sold": 360,
            "total_quantity_sold_unit": "QUINTAL",
            "total_quantity_sold_change": 30,

            "average_sale_rate": 1180,
            "average_sale_rate_unit": "QUINTAL",
            "average_sale_rate_change": 45,
        },
    }

    return daily_summary