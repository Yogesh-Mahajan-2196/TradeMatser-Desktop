from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from modules.parties.models import PartyType, User
from modules.parties.config import parties_setting

async def user_create(user_data,current_user, db):
    user_query = await db.execute(select(User).where(User.mobile_number == user_data.mobile_no))
    user_exist = user_query.scalars().first()

    supplier_id = None
    if user_exist:
        supplier_id = user_exist.id

        return {
            "message": "User record found with this mobile number.",
            "supplier_id": supplier_id
        }
    
    new_user = User(
        party_name = user_data.user_name,
        mobile_number = user_data.mobile_no,
        address = user_data.address,
        city = user_data.city,
        gst_no = user_data.gst if user_data.gst else None,
        pan_no = user_data.pan_no if user_data.pan_no else None,
        party_type = user_data.user_type,
        created_by=current_user.id
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    supplier_id = new_user.id

    return {
            "message": "User record created successfully.",
            "supplier_id": supplier_id
        }

async def customer_data(mob_no,name, party_type, page, page_size, db):
    page = max(
        page,
        1
    )

    page_size = min(
        max(page_size, 1),
        100
    )

    offset = (
        page - 1
    ) * page_size

    customer_query = (
        select(User)
    )

    if name:

        customer_query = (
            customer_query.where(
                User.party_name.ilike(
                    f"%{name.strip()}%"
                )
            )
        )

    if mob_no:

        customer_query = (
            customer_query.where(
                User.mobile_number.ilike(
                    f"%{mob_no.strip()}%"
                )
            )
        )

    if party_type:

        customer_query = (
            customer_query.where(
                User.party_type ==
                party_type
            )
        )

    count_query = (
        select(
            func.count()
        )
        .select_from(
            User
        )
    )

    if name:

        count_query = (
            count_query.where(
                User.party_name.ilike(
                    f"%{name.strip()}%"
                )
            )
        )


    if mob_no:

        count_query = (
            count_query.where(
                User.mobile_number.ilike(
                    f"%{mob_no.strip()}%"
                )
            )
        )


    if party_type:

        count_query = (
            count_query.where(
                User.party_type ==
                party_type
            )
        )

    total_records = (
        await db.execute(
            count_query
        )
    ).scalar_one()

    customer_query = (
        customer_query
        .order_by(
            User.party_name.asc()
        )
        .offset(
            offset
        )
        .limit(
            page_size
        )
    )

    customer_result = (
        await db.execute(
            customer_query
        )
    )


    customers = (
        customer_result
        .scalars()
        .all()
    )

    result = [

        {
            "customer_name":
                customer.party_name.title(),

            "mobile_number":
                customer.mobile_number,

            # "address":
            #     customer.address,

            "city":
                customer.city,

            # "gst_no": (
            #     customer.gst_no
            #     if customer.gst_no
            #     else None
            # ),

            # "pan_no": (
            #     customer.pan_no
            #     if customer.pan_no
            #     else None
            # ),

            "party_type": (
                customer.party_type.name
                if hasattr(
                    customer.party_type,
                    "name"
                )
                else str(
                    customer.party_type
                )
            ),
        }

        for customer in customers

    ]

    total_pages = (
        total_records +
        page_size -
        1
    ) // page_size

    return {

        "page":
            page,

        "page_size":
            page_size,

        "total_records":
            total_records,

        "total_pages":
            total_pages,

        "data":
            result,
    }


async def all_customers_data(db):
    customer_query = await db.execute(select(User))
    customer_data = customer_query.scalars().all()

    if not customer_data:
        return "Customers not found."

    result = [
        {
            "customer_name": data.party_name,
            "mobile_number": data.mobile_number,
            "city": data.city,
            "party_type": data.party_type,
        }
            for data in customer_data  ]

    return result