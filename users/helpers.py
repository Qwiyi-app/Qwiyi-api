from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm.session import Session
from sqlalchemy import asc, desc
from users.schema import UserBase
from utils.hash import Hash
from models import User
from fastapi_pagination import Page, LimitOffsetPage, paginate, add_pagination

def create_user(db: Session, request: UserBase):
    user = db.query(User).filter(User.email == request.email).first()  # 4
    if user:
        raise HTTPException(  
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    new_user = User(
        user_name = request.username,
        first_name = request.firstname,
        last_name = request.lastname,
        other_name = request.othername,
        email = request.email,
        password = Hash.bcrypt(request.password),
        is_clinician = request.is_clinician,
        job = request.job,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_all_users_paginated(search : str, db: Session):
    user = paginate(db.query(User).filter(User.user_name.contains(search)).order_by(desc(User.id)).all())
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'No User found')
    return  user
    # , "total_articles": total_articles
     
def get_all_users(db: Session):
    return db.query(User).all()

def get_user(db: Session, id: int):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'User {id} not found')
    return user


   

def update_user(id:int, request: UserBase, db:Session):
    user = db.query(User).filter(User.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'User  {id} not found')

    user.update({
        User.user_name : request.username,
        User.email : request.email,
        User.password : Hash.bcrypt(request.password)
    })
    db.commit()
    return 'ok'

def delete_user(db: Session, id: int):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'User  {id} not found')
    db.delete(user)
    db.commit()
    return 'ok'

def get_user_by_username(username: str, db: Session):
    user = db.query(User).filter(User.user_name == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'User {username} with  not found')
    return user

def update_profile_photo(id: int, file_location: str, db: Session):
    user = db.query(User).filter(User.id == id)
    if not user.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail = f'User  {id} not found')

    user.update({
        User.photo : file_location,
        
    })
    db.commit()
    return 'ok'