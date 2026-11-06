from datetime import datetime, timezone
from fastapi import HTTPException
import jwt
from sqlalchemy.future import select
from .models import Company, CompanyUser
from .config import auth_setting
from utils.password_hashing import Hash

async def user_register(user_data, db):
    user_query = await db.execute(select(CompanyUser).filter(CompanyUser.email_id == user_data.email))
    user_exist = user_query.scalars().first()

    if user_exist:
        raise HTTPException(status_code=409, detail=auth_setting.USER_EXIST)
    
    new_user = CompanyUser(
        first_name = user_data.first_name,
        last_name = user_data.last_name,
        email_id = user_data.email,
        password = Hash.get_password_hash(user_data.password),
        mobile_number = user_data.mobile_no,
        role_id= user_data.role_id
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {
        "result": "Company user created successfully."
    }

async def get_user(username, db):
    user_exist = await db.execute(select(CompanyUser).filter(CompanyUser.email_id==username))
    user = user_exist.scalars().first()
    return user

async def authenticate_user(username, password, db):
    user = await get_user(username, db)
    if not user:
        return False
    
    check_password = Hash.verify_password(password,user.password)
    if not check_password:
        return False
    
    return user

def create_access_token(data, exp_time):
    to_encode = data.copy()
    if exp_time:
        expire = datetime.now(timezone.utc) + exp_time

    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, auth_setting.SECRET_KEY, algorithm=auth_setting.ALGORITHM)
    return encode_jwt

async def password_change(data, user, db):
    check_password = Hash.verify_password(
        data.current_password,
        user.password,
    )

    if not check_password:
        raise HTTPException(
            status_code=403,
            detail= auth_setting.WRONG_CURRENT_PASSWORD,
        )
    
    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=400,
            detail= auth_setting.SAME_PASSWORD_ERROR
        )

    user.password = Hash.get_password_hash(
        data.new_password
    )

    await db.commit()
    await db.refresh(user)

    return {
        "message": "Password changed successfully."
    }

async def role_change(user_id, updated_role, db):
    user_query = await db.execute(select(CompanyUser).filter(CompanyUser.id == user_id))
    user_exist = user_query.scalars().first()
    if not user_exist:
        raise HTTPException(status_code=404, detail=auth_setting.USER_NOT_FOUND)
    
    user_exist.role_id = updated_role
    await db.commit()
    await db.refresh(user_exist)

    return {
        "message": "User role update successfully."
    }

async def company_user_update(company_user_data, db):
    user_query = await db.execute(select(CompanyUser).filter(CompanyUser.id == company_user_data.id))
    user_exist = user_query.scalars().first()

    if not user_exist:
        raise HTTPException(status_code=404, detail=auth_setting.USER_NOT_FOUND)
    
    user_exist.first_name = company_user_data.first_name
    user_exist.last_name = company_user_data.last_name
    user_exist.email_id = company_user_data.email
    user_exist.mobile_number = company_user_data.mobile_no

    await db.commit()
    await db.refresh(user_exist)

    return {
        "message": "User update successfully."
    }

async def company_register(company_data, db):
    stmt = await db.execute(select(Company).filter(Company.company_name == company_data.company_name))
    company_exist = stmt.scalars().first()

    if company_exist:
        raise HTTPException(status_code=409, detail=auth_setting.COMPANY_EXIST)

    new_company = Company(
            company_name = company_data.company_name
        )
        
    db.add(new_company)
    await db.commit()
    await db.refresh(new_company)

    return {
        "result": "Company created successfully."
    }