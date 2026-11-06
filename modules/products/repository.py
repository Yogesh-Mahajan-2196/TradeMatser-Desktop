from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from modules.products.models import Products
from modules.products.config import product_setting


async def product_create(prod_data,current_user_id,db):
    prod_query = await db.execute(select(Products).where(Products.product_name.ilike(prod_data.product_name)))
    prod_exists = prod_query.scalars().first()

    if prod_exists:
        raise HTTPException(status_code=409, detail=product_setting.PRODUCT_EXISTS)

    new_prod = Products(
        product_name = prod_data.product_name.lower(),
        unit = prod_data.unit,
        created_by = current_user_id
    )

    db.add(new_prod)
    await db.commit()
    await db.refresh(new_prod)

    return {
        "message": "Product created successfully.",
        "data": {
            "product_name": prod_data.product_name,
        }
    }

async def product_list(db):
    product_query = await db.execute(select(Products).filter(Products.is_active == True))
    product_exists = product_query.scalars().all()

    if not product_exists:
        return []
    
    prod_list = []
    for data in product_exists:
        res = {
            "produc_id" : data.id,
            "product_name" : data.product_name.title(),
            "unit": data.unit.value
        }
        prod_list.append(res)
    
    return prod_list

async def product_update(update_data,db):
    product_query = await db.execute(
        select(Products).where(
                func.lower(Products.product_name) == update_data.product_name.lower(),
                Products.id != update_data.id,
                Products.is_active.is_(True)
            )
        )
    product_exists = product_query.scalar_one_or_none()

    if product_exists:
        raise HTTPException(status_code=404, detail=product_setting.PRODUCT_EXISTS)
    
    product = await db.get(Products, update_data.id)

    product.product_name = update_data.product_name if update_data.product_name else product.product_name
    product.unit = update_data.unit if update_data.unit else product.unit

    await db.commit()
    await db.refresh(product)

    return {
        "message": "Product name update successfully.",
        "product_name": product.product_name,
        "unit": product.unit
    }
    