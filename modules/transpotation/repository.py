from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from .config import transpotation_setting
from modules.transpotation.models import Truck

async def create_driver_info(driver_data, curr_user, db):
    truck_exist = await db.execute(
        select(Truck).where(
            Truck.truck_number == driver_data.truck_number
        )
    )
    truck_exist = truck_exist.scalars().first()

    if truck_exist:
        raise HTTPException(
            status_code=409,
            detail= transpotation_setting.TRUCK_NO_EXISTS
        )

    truck = Truck(
        truck_number=driver_data.truck_number,
        owner_name=driver_data.owner_name,
        owner_mobile=driver_data.owner_mobile,
        driver_name=driver_data.driver_name,
        driver_mobile=driver_data.driver_mobile,
        created_by=curr_user
    )

    db.add(truck)

    await db.commit()
    await db.refresh(truck)

    return {
        "message": "Truck created successfully.",
        "data": truck
    }

async def update_driver_info(truck_id, driver_data, db):
    result = await db.execute(
        select(Truck).where(Truck.id == truck_id)
    )
    truck = result.scalars().first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail=transpotation_setting.TRUCK_NO_NOT_FOUND
        )

    truck.truck_number = driver_data.truck_number
    truck.owner_name = driver_data.owner_name
    truck.owner_mobile = driver_data.owner_mobile
    truck.driver_name = driver_data.driver_name
    truck.driver_mobile = driver_data.driver_mobile

    await db.commit()
    await db.refresh(truck)

    return {
        "message": "Truck updated successfully.",
        "data": truck
    }

async def get_driver(truck_id, db):
    result = await db.execute(
        select(Truck).where(
            Truck.id == truck_id
        )
    )
    truck = result.scalars().first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail=transpotation_setting.TRUCK_NO_NOT_FOUND
        )
    return {
        "id": truck.id,
        "truck_number": truck.truck_number,
        "owner_name": truck.owner_name,
        "owner_mobile": truck.owner_mobile,
        "driver_name": truck.driver_name,
        "driver_mobile": truck.driver_mobile,
    }

async def get_all_driver(page, page_size, truck_number,db):
    page = max(
        page,
        1
    )

    page_size = min(
        max(page_size, 1),
        100
    )


    # Pagination

    offset = (
        page - 1
    ) * page_size


    # Base query

    truck_query = (
        select(Truck)
    )


    # Search by truck number

    if truck_number:

        truck_query = (
            truck_query.where(
                Truck.truck_number.ilike(
                    f"%{truck_number.strip()}%"
                )
            )
        )


    # Count query

    count_query = (
        select(
            func.count()
        )
        .select_from(
            Truck
        )
    )


    # Apply the same filter
    # to count query

    if truck_number:

        count_query = (
            count_query.where(
                Truck.truck_number.ilike(
                    f"%{truck_number.strip()}%"
                )
            )
        )


    # Get total records

    total_records = (
        await db.execute(
            count_query
        )
    ).scalar_one()


    # Apply pagination

    truck_query = (
        truck_query
        .order_by(
            Truck.truck_number.asc()
        )
        .offset(
            offset
        )
        .limit(
            page_size
        )
    )


    # Execute query

    result = await db.execute(
        truck_query
    )


    trucks = (
        result
        .scalars()
        .all()
    )


    # Response data

    data = []

    for truck in trucks:

        data.append({

            "id":
                truck.id,

            "truck_number":
                truck.truck_number,

            "owner_name":
                truck.owner_name,

            "owner_mobile":
                truck.owner_mobile,

            "driver_name":
                truck.driver_name,

            "driver_mobile":
                truck.driver_mobile,

        })


    # Total pages

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
            data,

    }

async def delete_driver(truck_id, db):
    result = await db.execute(
        select(Truck).where(
            Truck.id == truck_id
        )
    )
    truck = result.scalars().first()

    if not truck:
        raise HTTPException(
            status_code=404,
            detail=transpotation_setting.TRUCK_NO_NOT_FOUND
        )

    await db.delete(truck)
    await db.commit()

    return {
        "message": "Truck deleted successfully."
    }