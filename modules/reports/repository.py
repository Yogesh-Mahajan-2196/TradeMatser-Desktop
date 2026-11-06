from datetime import date
import math
from fastapi import HTTPException
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter
from sqlalchemy import String, cast, func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from modules.parties.models import PartyType, User
from modules.purchase.models import PurchaseBill, PurchaseBillItem, Remark
from modules.reports.daily_report_body import get_daily_report_body
from modules.sell.models import BillRemark, SellBill, SellBillItem
from utils.email import send_email
from utils.config import settings

async def get_total_purchses(db):
    total_purchase_query = await db.execute(
        select(func.count(PurchaseBill.id))
        )
    total_purchase_data = total_purchase_query.scalar()
    return total_purchase_data

def build_purchase_report_query():
    return (
        select(PurchaseBill)
        .join(PurchaseBillItem)
        .options(
            selectinload(PurchaseBill.user),
            selectinload(PurchaseBill.purchase_bill_item)
            .selectinload(PurchaseBillItem.product)
        )
        .distinct()
    )

def apply_purchase_filters(
    query,
    from_date=None,
    to_date=None,
    product_id=None,
    payment_status=None,
    ):
    if from_date:
        query = query.where(PurchaseBill.bill_date >= from_date)

    if to_date:
        query = query.where(PurchaseBill.bill_date <= to_date)

    if product_id:
        query = query.where(
            PurchaseBillItem.product_id == product_id
        )

    if payment_status:
        query = query.where(
            func.lower(cast(PurchaseBill.remarks, String))
            == payment_status.lower()
        )

    return query

async def recent_purchases_data(db, page, page_size):
    offset = (page - 1) * page_size

    pur_rec_query = await db.execute(
        select(PurchaseBill)
        .options(
            selectinload(PurchaseBill.user),
            selectinload(PurchaseBill.purchase_bill_item)
        )
        .order_by(PurchaseBill.bill_date.desc())
        .offset(offset)
        .limit(page_size)
    )

    pur_rec_exists = pur_rec_query.scalars().all()

    result = []

    for purchase in pur_rec_exists:
        purchase_item = purchase.purchase_bill_item

        result.append({
            "bill_no": purchase.bill_no,
            "customer_name": (
                purchase.user.party_name
                if purchase.user else "N/A"
            ),
            "total_amount": (
                purchase_item.total_amount
                if purchase_item and purchase_item.total_amount is not None
                else 0
            ),
            "date": purchase.bill_date
        })

    total_records = await get_total_purchses(db)

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": (
            (total_records + page_size - 1) // page_size
            if page_size > 0 else 0
        ),
        "data": result
    }


async def purchase_rep(from_date,to_date,product_id,payment_status,sort_by,order,page,page_size,db):

    purchase_rep_query = build_purchase_report_query()

    purchase_rep_query = apply_purchase_filters(
        purchase_rep_query,
        from_date,
        to_date,
        product_id,
        payment_status,
    )

    purchace_rec_count = (purchase_rep_query.with_only_columns(
        func.count(PurchaseBill.id)).order_by(None)
    )

    total_records = (await db.execute(purchace_rec_count)).scalar()

    sort_columns = {
        "bill_date": PurchaseBill.bill_date,
        "bill_no": PurchaseBill.bill_no,
    }

    column = sort_columns.get(sort_by, PurchaseBill.bill_date)

    if order == "asc":
        purchase_rep_query = purchase_rep_query.order_by(column.asc())
    else:
        purchase_rep_query = purchase_rep_query.order_by(column.desc())

    offset = (page - 1)*page_size
    purchase_rep_query = purchase_rep_query.offset(offset).limit(page_size)
    result = await db.execute(purchase_rep_query)
    purchase_report = result.scalars().all()

    res = []

    for purchase in purchase_report:
        res.append({
            "bill_no": purchase.bill_no,
            "bill_date": purchase.bill_date,
            "supplier": purchase.user.party_name,
            "vehicle_no": purchase.vehicle_no,
            "remarks": purchase.remarks,
            "product_name": purchase.purchase_bill_item.product.product_name, 
            "weight": purchase.purchase_bill_item.weight,
            "unit": purchase.purchase_bill_item.product.unit,
            "unpaid_amount": purchase.purchase_bill_item.product.unit, 
            "rate": purchase.purchase_bill_item.rate, 
            "expenses": purchase.purchase_bill_item.expenses, 
            "paid_amount": purchase.purchase_bill_item.paid_amount, 
            "unpaid_amount": purchase.purchase_bill_item.unpaid_amount, 
            "total_amount": purchase.purchase_bill_item.total_amount,
        })
    return {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": math.ceil(total_records / page_size),
            "data": res
        }



# Sells
async def get_total_sell(db):
    total_sell_query = await db.execute(
        select(func.count(SellBill.id))
        )
    total_sell_data = total_sell_query.scalar()
    return total_sell_data

def build_sell_report_query():
    return (
        select(SellBill)
        .join(SellBillItem)
        .options(
            selectinload(SellBill.sell_bill_item)
            .selectinload(SellBillItem.product)
        )
    )

def apply_sell_filters(
    query,
    from_date=None,
    to_date=None,
    product_id=None,
    bill_no=None,
    payment_status=None,
    ):
    if from_date:
        query = query.where(SellBill.bill_date >= from_date)

    if to_date:
        query = query.where(SellBill.bill_date <= to_date)

    if product_id:
        query = query.where(
            SellBillItem.product_id == product_id
        )

    if bill_no:
        query = query.where(SellBill.bill_no == int(bill_no))

    if payment_status:
        query = query.where(
            func.lower(cast(SellBill.remarks, String))
            == payment_status.lower()
        )

    return query

async def sell_rep(from_date,to_date,product_id,bill_no,payment_status,sort_by,order,page,page_size,db):

    sell_rep_query = build_sell_report_query()
    sell_rep_query = apply_sell_filters(
        sell_rep_query,
        from_date,
        to_date,
        product_id,
        bill_no,
        payment_status,
    )

    sell_rec_count = (
        sell_rep_query
        .with_only_columns(
        func.count(SellBill.id)
        )
        .order_by(None)
        )
    total_records = (await db.execute(sell_rec_count)).scalar()

    sort_column = {
        "bill_date": SellBill.bill_date,
        "bill_no": SellBill.bill_no
    }
    column = sort_column.get(sort_by, SellBill.bill_date)

    if order == "asc":
        sell_rep_query = sell_rep_query.order_by(column.asc())
    else:
        sell_rep_query = sell_rep_query.order_by(column.desc())

    offset = (page - 1) * page_size
    sell_rep_query = sell_rep_query.offset(offset).limit(page_size)
    result = await db.execute(sell_rep_query)
    sell_report = result.scalars().all()

    res = []
    for data in sell_report:
        res.append({
            "bill_no": data.bill_no,
            "company_name": data.company_name,
            "address": data.address,
            "broker": data.broker_name,
            "truck_no": data.truck_no,
            "po_no": data.po_no,
            "bags": data.bags,
            "bill_date": data.bill_date,
            "remark": data.remarks,
            "product_name": data.sell_bill_item[0].product.product_name,
            "unit": data.sell_bill_item[0].product.unit,
            "weight": data.sell_bill_item[0].weight,
            "rate": str(data.sell_bill_item[0].rate),
            "expenses": str(data.sell_bill_item[0].expense_amount),
            "gross_amount": str(data.sell_bill_item[0].gross_amount),
            "net_amount": str(data.sell_bill_item[0].net_amount),
        })
    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": (total_records + page_size - 1) // page_size,
        "data": res
    }

async def export_sell_report(
        db,
        from_date,
        to_date,
        product_id,
        bill_no,
        payment_status,
    ):

    sell_rep_query = build_sell_report_query()
    sell_rep_query = apply_sell_filters(
        sell_rep_query,
        from_date,
        to_date,
        product_id,
        bill_no,
        payment_status,
    )

    sell_rep_query = sell_rep_query.order_by(SellBill.bill_date.desc())
    result = await db.execute(sell_rep_query)
    sells = result.scalars().all()

    wb = Workbook()
    ws = wb.active

    ws.title = "Sell Report"
    ws.append(['MyTraderMaster Sell Report'])
    ws.append([])

    headers = [
        "Bill No",
        "Bill Date",
        "Buyer",
        "Truck No",
        "Bags",
        "PO No",
        "Product",
        "Weight",
        "Unit",
        "Rate",
        "Total",
        "Remark"
    ]

    ws.append(headers)

    for cell in ws[3]:
        cell.font = Font(bold=True)

    for sell in sells:
        ws.append([
            sell.bill_no,
            sell.bill_date.strftime("%d-%m-%Y"),
            sell.user.party_name,
            sell.truck_no,
            sell.bags,
            sell.po_no,
            sell.sell_bill_item[0].product.product_name,
            sell.sell_bill_item[0].weight,
            sell.sell_bill_item[0].product.unit.value,
            sell.sell_bill_item[0].rate,
            sell.sell_bill_item[0].net_amount,
            sell.remarks.value
        ])
    
    for column in ws.columns:
        max_length = 0
        column_letter = get_column_letter(column[0].column)
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except Exception:
                pass

        ws.column_dimensions[column_letter].width = max_length + 5
    path = "sell_report.xlsx"
    wb.save(path)

    return path



# Outstanding
async def out_receivalble(db, page, page_size):
    offset = (page - 1) * page_size
    query = (
        select(SellBill)
        .options(
            selectinload(SellBill.sell_bill_item)
        )
        .where(
            SellBill.remarks == BillRemark.UNPAID,
        )
    )
    count_query = (
        query.with_only_columns(func.count(SellBill.id))
        .order_by(None)
    )
    total_records = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(SellBill.bill_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    sells = result.scalars().unique().all()

    response = []

    for sell in sells:
        response.append({
            "party_name": sell.company_name,
            "outstanding_amount": sell.sell_bill_item[0].net_amount
        })

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": (total_records + page_size - 1) // page_size,
        "data": response
    }
   
async def out_payables(db, page, page_size):
    offset = (page - 1) * page_size
    query = (
        select(PurchaseBill)
        .options(
            selectinload(PurchaseBill.user),
            selectinload(PurchaseBill.purchase_bill_item)
        )
        .where(
            PurchaseBill.remarks == Remark.UNPAID,
            PurchaseBill.user.has(
                (User.party_type != PartyType.SUPPLIER) |
                (User.party_type != PartyType.CUSTOMER) 
            )
        )
    )
    count_query = (
        query.with_only_columns(func.count(PurchaseBill.id))
        .order_by(None)
    )
    total_records = (await db.execute(count_query)).scalar()
    result = await db.execute(
        query.order_by(PurchaseBill.bill_date.desc())
        .offset(offset)
        .limit(page_size)
    )
    purchases = result.scalars().unique().all()

    response = []

    for purchase in purchases:
        response.append({
            "party_name": purchase.user.party_name,
            "outstanding_amount": purchase.purchase_bill_item.unpaid_amount
        })

    return {
        "page": page,
        "page_size": page_size,
        "total_records": total_records,
        "total_pages": (total_records + page_size - 1) // page_size,
        "data": response
    }



# Daily Report
async def daily_report(db):

    today = date.today()

    # ==================================================
    # PURCHASE REPORT
    # ==================================================

    purchase_bill_result = await db.execute(
        select(
            func.count(PurchaseBill.id)
        )
        .where(
            func.date(PurchaseBill.bill_date) == today
        )
    )

    total_purchase_bills = (
        purchase_bill_result.scalar() or 0
    )

    purchase_summary_result = await db.execute(
        select(
            func.coalesce(
                func.sum(PurchaseBillItem.weight),
                0
            ).label("total_purchase_quantity"),

            func.coalesce(
                func.avg(PurchaseBillItem.rate),
                0
            ).label("average_purchase_rate"),

            func.coalesce(
                func.sum(PurchaseBillItem.total_amount),
                0
            ).label("total_purchase_amount"),
        )
        .join(
            PurchaseBill,
            PurchaseBillItem.purchase_bill_id
            == PurchaseBill.id
        )
        .where(
            func.date(PurchaseBill.bill_date)
            == today
        )
    )

    purchase_summary = (
        purchase_summary_result.mappings().one()
    )

    purchase_paid_result = await db.execute(
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
            func.date(PurchaseBill.bill_date)
            == today,
            PurchaseBill.remarks == Remark.PAID
        )
    )

    total_purchase_paid = (
        purchase_paid_result.scalar() or 0
    )

    purchase_unpaid_result = await db.execute(
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
            func.date(PurchaseBill.bill_date)
            == today,
            PurchaseBill.remarks == Remark.UNPAID
        )
    )

    total_purchase_unpaid = (
        purchase_unpaid_result.scalar() or 0
    )

    # ==================================================
    # SELL REPORT
    # ==================================================

    sell_bill_result = await db.execute(
        select(
            func.count(SellBill.id)
        )
        .where(
            func.date(SellBill.bill_date) == today
        )
    )

    total_sell_bills = (
        sell_bill_result.scalar() or 0
    )

    sell_summary_result = await db.execute(
        select(
            func.coalesce(
                func.sum(SellBill.bags),
                0
            ).label("total_bags"),

            func.coalesce(
                func.sum(SellBillItem.weight),
                0
            ).label("total_sell_weight"),

            func.coalesce(
                func.sum(SellBillItem.net_amount),
                0
            ).label("total_sell_amount"),
        )
        .join(
            SellBill,
            SellBillItem.sell_bill_id
            == SellBill.id
        )
        .where(
            func.date(SellBill.bill_date)
            == today
        )
    )

    sell_summary = (
        sell_summary_result.mappings().one()
    )

    return {
        "date": today,

        "purchase": {
            "total_bills": total_purchase_bills,
            "total_quantity": (
                purchase_summary[
                    "total_purchase_quantity"
                ]
            ),
            "average_rate": (
                purchase_summary[
                    "average_purchase_rate"
                ]
            ),
            "paid_amount": (
                total_purchase_paid
            ),
            "unpaid_amount": (
                total_purchase_unpaid
            ),
            "total_amount": (
                purchase_summary[
                    "total_purchase_amount"
                ]
            ),
        },

        "sell": {
            "total_bills": total_sell_bills,
            "total_quantity": (
                sell_summary[
                    "total_sell_weight"
                ]
            ),
            "total_bags": (
                sell_summary[
                    "total_bags"
                ]
            ),
            "total_weight": (
                sell_summary[
                    "total_sell_weight"
                ]
            ),
            "total_amount": (
                sell_summary[
                    "total_sell_amount"
                ]
            ),
        },
    }

async def send_daily_report(report: dict):

    subject = (
        f"MyTradeMaster Daily Report - "
        f"{report['date']}"
    )

    body = get_daily_report_body(report)

    await send_email(
        email=[settings.ADMIN_EMAIL],
        html=body,
        subject=subject,
    )


