from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from modules.parties.models import User
from modules.products.models import Products
from modules.sell.models import SellBill, SellBillItem, BillRemark
from .config import sell_settings
from modules.auth.config import auth_setting
from modules.products.config import product_setting

async def check_bill_no_exist(bill_no, db):
    sell_bill_query = await db.execute(select(SellBill).where(SellBill.bill_no == bill_no))
    sell_bill_exist = sell_bill_query.scalars().first()
    return sell_bill_exist

async def check_user_exist(user_id, db):
    user_query = await db.execute(select(User).filter(User.id == user_id))
    user_exist = user_query.scalars().first()
    return user_exist

async def check_product_exist(prod_id, db):
    product_query = await db.execute(select(Products).filter(Products.id == prod_id))
    product_exist = product_query.scalars().first()
    return product_exist


async def sell_bill(bill_header, bill_details, curr_user, db):
    sell_bill_exist = await check_bill_no_exist(bill_header.bill_no, db)

    if sell_bill_exist:
        raise HTTPException(status_code=409, detail=sell_settings.BILL_EXISTS)
    
    product_exist = await check_product_exist(bill_details.product_id,db)

    if not product_exist:
        raise HTTPException(status_code=404, detail=product_setting.PRODUCT_NOT_FOUND)
    
    sell_bill_header = SellBill(
        bill_no= bill_header.bill_no,
        bill_date= bill_header.bill_date,
        company_name=  bill_header.company_name,
        address = bill_header.address,
        broker_name=  bill_header.broker_name,
        truck_no= bill_header.truck_no,
        po_no= bill_header.po_no,
        bags= bill_header.bags,
        created_by= curr_user
    )
    db.add(sell_bill_header)
    await db.flush()

    total_expenses = bill_details.expenses
    gross_amount = bill_details.weight * bill_details.rate
    total_amount = float(gross_amount) - float(total_expenses)

    sell_bill_item_details = SellBillItem(
        product_id = bill_details.product_id,
        weight =  bill_details.weight,
        rate = bill_details.rate,
        gross_amount = gross_amount,
        expense_amount = total_expenses,
        net_amount = total_amount,
        sell_bill_id = sell_bill_header.id
    )

    db.add(sell_bill_item_details)
    await db.flush()

    data = {
        "bill_no": sell_bill_header.bill_no,
        "company_name": sell_bill_header.company_name,
        "address": sell_bill_header.address,
        "broker_name": sell_bill_header.broker_name,
        "truck_no": sell_bill_header.truck_no,
        "po_no": sell_bill_header.po_no,
        "bags": sell_bill_header.bags,
        "bill_date": sell_bill_header.bill_date,
        "remark": sell_bill_header.remarks,
        "product": {
            "product_id": sell_bill_item_details.product_id,
            "product_name": product_exist.product_name,
            "weight": sell_bill_item_details.weight,
            "rate": str(sell_bill_item_details.rate),
            "expenses": total_expenses,
            "gross_amount": str(sell_bill_item_details.gross_amount),
        }
    }

    await db.commit()
    await db.refresh(sell_bill_header)
    await db.refresh(sell_bill_item_details)

    return {
        "message": "Sell bill saved.",
        "data": data
    }


async def get_bill(bill_no,db):
    sell_bill_query = await db.execute(
        select(SellBill)
        .join(SellBillItem)
        .options(
            selectinload(SellBill.sell_bill_item)
                .selectinload(SellBillItem.product)
        )
        .where(SellBill.bill_no == bill_no)
    )
    sell_bill_exist = sell_bill_query.scalars().first()

    if not sell_bill_exist:
        raise HTTPException(status_code=409, detail=sell_settings.BILL_NOT_EXISTS)

    
    product_name = await check_product_exist(sell_bill_exist.sell_bill_item[0].product_id, db)
    if not product_name:
        raise HTTPException(status_code=404, detail=product_setting.PRODUCT_NOT_FOUND)
    
    data = {
        "bill_no": sell_bill_exist.bill_no,
        "company_name": sell_bill_exist.company_name,
        "address": sell_bill_exist.address,
        "broker_name": sell_bill_exist.broker_name,
        "truck_no": sell_bill_exist.truck_no,
        "po_no": sell_bill_exist.po_no,
        "bags": sell_bill_exist.bags,
        "bill_date": sell_bill_exist.bill_date,
        "remark": sell_bill_exist.remarks,
        "products": [
                {
                    "product_name": product_name.product_name,
                    "weight": item.weight,
                    "rate": str(item.rate),
                    "expenses": str(item.expense_amount),
                    "gross_amount": str(item.gross_amount),
                    "net_amount": str(item.net_amount),
                }
                for item in sell_bill_exist.sell_bill_item
            ]
    }
    return data


async def update_bill(bill_no, expense, remark, db):
    sell_bill_query = await db.execute(
        select(SellBill)
        .join(SellBillItem)
        .options(
            selectinload(SellBill.sell_bill_item)
            .selectinload(SellBillItem.product)
        )
        .where(SellBill.bill_no == bill_no)
    )

    sell_bill_exist = sell_bill_query.scalars().first()

    if not sell_bill_exist:
        raise HTTPException(
            status_code=409,
            detail=sell_settings.BILL_NOT_EXISTS,
        )

    try:
        # Update bill remark
        sell_bill_exist.remarks = remark

        # Update expense and calculate net amount
        for item in sell_bill_exist.sell_bill_item:
            item.expense_amount = expense
            item.net_amount = item.gross_amount - expense

            if item.net_amount < 0:
                item.net_amount = 0

        await db.flush()

        data = {
            "bill_no": sell_bill_exist.bill_no,
            "company_name": sell_bill_exist.company_name,
            "broker_name": sell_bill_exist.broker_name,
            "truck_no": sell_bill_exist.truck_no,
            "po_no": sell_bill_exist.po_no,
            "bags": sell_bill_exist.bags,
            "bill_date": sell_bill_exist.bill_date,
            "remark": sell_bill_exist.remarks,
            "products": [
                {
                    "product_name": item.product.product_name,
                    "weight": item.weight,
                    "rate": str(item.rate),
                    "expenses": str(item.expense_amount),
                    "gross_amount": str(item.gross_amount),
                    "net_amount": str(item.net_amount),
                }
                for item in sell_bill_exist.sell_bill_item
            ],
        }
        await db.commit()
        return data

    except Exception:
        await db.rollback()
        raise

async def get_next_sell_bill_no(db):

    result = await db.execute(
        select(func.max(SellBill.bill_no))
    )

    max_bill_no = result.scalar()

    if max_bill_no is None:
        return 1

    return max_bill_no + 1