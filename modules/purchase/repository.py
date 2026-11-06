from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from modules.parties.models import User
from modules.products.models import Products
from .models import PurchaseBill, PurchaseBillItem, Remark
from .config import purchase_settings
from modules.auth.config import auth_setting
from modules.products.config import product_setting
from utils.config import settings

async def purchase_bill(bill_header, bill_details, current_user, db):
    purchase_bill_query = await db.execute(select(PurchaseBill).filter(PurchaseBill.bill_no == bill_header.bill_no))
    purchase_bill_exist = purchase_bill_query.scalars().first()

    if purchase_bill_exist:
        raise HTTPException(status_code=409, detail=purchase_settings.BILL_EXISTS)
    
    supplier_name = bill_header.supplier_name.strip()

    user_query = await db.execute(
        select(User).filter(
            User.party_name == supplier_name
        )
    )

    user_exist = user_query.scalars().first()

    if not user_exist:
        user_exist = User(
            party_name=supplier_name
        )

        db.add(user_exist)
        await db.flush()
    
    product_query = await db.execute(select(Products).filter(Products.id == bill_details.product_id))
    product_exist = product_query.scalars().first()

    if not product_exist:
        raise HTTPException(status_code=404, detail=product_setting.PRODUCT_NOT_FOUND)
    
    purchase_bill_data = PurchaseBill(
        bill_no = bill_header.bill_no,
        supplier_id = user_exist.id,
        vehicle_no = bill_header.vehicle_no,
        remarks = bill_header.remark,
        created_by= current_user
    )

    db.add(purchase_bill_data)
    await db.flush()

    bill_expenses = {
        key: float(value)
        for key, value in bill_details.expenses.items()
    }

    total_expenses = sum(float(value) for value in bill_expenses.values())
    gross_amount = bill_details.weight * bill_details.rate
    total_amount = float(gross_amount) - float(total_expenses)
    unpaid_amount = total_amount - float(bill_details.paid_amount)

    if bill_details.paid_amount > total_amount:
        raise HTTPException(
            status_code=400,
            detail="Paid amount cannot be greater than unpaid amount."
        )
    
    purchase_bill_item_data = PurchaseBillItem(
        product_id = bill_details.product_id,
        weight = bill_details.weight,
        rate = bill_details.rate,
        expenses = bill_expenses,
        paid_amount = bill_details.paid_amount,
        unpaid_amount = unpaid_amount,
        total_amount = total_amount,
        purchase_bill_id = purchase_bill_data.id,
    )

    db.add(purchase_bill_item_data)
    await db.flush()

    data = {
            "id": purchase_bill_data.id,
            "bill_no": purchase_bill_data.bill_no,
            "bill_date": purchase_bill_data.bill_date,
            "supplier_id": purchase_bill_data.supplier_id,
            "supplier_name": user_exist.party_name,
            "vehicle_no": purchase_bill_data.vehicle_no,
            "remark": purchase_bill_data.remarks,
            "product": {
                "product_id": purchase_bill_item_data.product_id,
                "product_name": product_exist.product_name,
                "weight": purchase_bill_item_data.weight,
                "rate": str(purchase_bill_item_data.rate),
                "expenses": bill_expenses,
                "paid_amount": str(purchase_bill_item_data.paid_amount),
                "unpaid_amount": str(purchase_bill_item_data.unpaid_amount),
                "total_amount": str(purchase_bill_item_data.total_amount),
            }
        }
    await db.commit()
    await db.refresh(purchase_bill_data)
    await db.refresh(purchase_bill_item_data)

    return {
        "message": "Purchase bill saved.",
        "data": data
    }

async def bill_exists(bill_no,db):
    purchase_bill_query = await db.execute(
        select(PurchaseBill)
        .options(
            selectinload(PurchaseBill.user),
            selectinload(PurchaseBill.purchase_bill_item)
                .selectinload(PurchaseBillItem.product)
        )
        .where(PurchaseBill.bill_no == bill_no)
    )
    purchase_bill_exist = purchase_bill_query.scalars().first()

    if not purchase_bill_exist:
        raise HTTPException(status_code=404, detail=purchase_settings.BILL_NOT_EXISTS)
    
    return purchase_bill_exist

def bill_data(db_data):
    data = {
        "bill_no": db_data.bill_no,
        "supplier_name": f"{db_data.user.party_name}",
        "vehicle_no": db_data.vehicle_no,
        "remark": db_data.remarks,
        "bill_date": db_data.bill_date,
        "product": db_data.purchase_bill_item.product.product_name,
        "weight": db_data.purchase_bill_item.weight,
        "rate": db_data.purchase_bill_item.rate,
        "expenses": db_data.purchase_bill_item.expenses,
        "paid_amount": db_data.purchase_bill_item.paid_amount,
        "unpaid_amount": db_data.purchase_bill_item.unpaid_amount,
        "total_amount": db_data.purchase_bill_item.total_amount,
    }
    return data

async def get_bill(bill_no, db):
    db_data = await bill_exists(bill_no, db)
    return bill_data(db_data)
    

async def purchase_bill_update(bill_no, updated_bill, db):
    db_data = await bill_exists(bill_no, db)

    item = db_data.purchase_bill_item

    if updated_bill.paid_amount > item.unpaid_amount:
        raise HTTPException(
            status_code=400,
            detail="Paid amount cannot be greater than unpaid amount."
        )

    item.paid_amount += updated_bill.paid_amount
    item.unpaid_amount -= updated_bill.paid_amount

    if item.unpaid_amount == 0:
        db_data.remarks = Remark.PAID
    else:
        db_data.remarks = Remark.UNPAID

    await db.commit()

    res =  bill_data(db_data)
    await db.refresh(db_data)
    return res


async def get_next_purchase_bill_no(db):

    result = await db.execute(
        select(func.max(PurchaseBill.bill_no))
    )

    max_bill_no = result.scalar()

    if max_bill_no is None:
        return 1

    return max_bill_no + 1