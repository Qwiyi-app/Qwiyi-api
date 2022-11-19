from fastapi import APIRouter, Depends, UploadFile, File, status
from typing import List
from sqlalchemy.orm.session import Session
from fastapi.responses import FileResponse, JSONResponse
import string
import random
import shutil
# import aiofiles
from users.helpers import create_user, get_all_users, get_user, get_user_by_username, delete_user, update_user, update_profile_photo, get_all_users_paginated
from users.schema import UserBase, UserDisplay
from database.db import get_db
from auth.oauth2 import get_current_user
from fastapi_pagination import Page, LimitOffsetPage, paginate, add_pagination

tags_metadata = [
    {
        "name" : "users",
        "description" : "Users Crud Operation"
    },
    {
        "name" : "items",
        "description" : "Users Crud Operation",
        "externalDocs" : {
            "description" : "Manage items",
            "url" : "https://medicsniche.com",
        }
    }
]

users_routes = APIRouter(
    prefix = '/api_v0.1/users',
    tags = ['users'],
    
)

# Reads all users registered on the platform
@users_routes.get('/', response_model = Page[UserDisplay] )
@users_routes.get('/limit', response_model = LimitOffsetPage[UserDisplay])
async def get_all_users_function(search: str | None = "", db: Session = Depends(get_db)):
    return get_all_users_paginated(search, db)

add_pagination(users_routes)

@users_routes.get("/all/", response_model = List[UserDisplay])
async def get_users(db: Session = Depends(get_db)):
    return get_all_users(db)

@users_routes.post("/", response_model = UserDisplay)
async def register_user(request: UserBase, db: Session = Depends(get_db)):
    return create_user(db, request)

# Read a specific user
@users_routes.get('/{id}', response_model = UserDisplay)
async def get_a_user(id: int, db : Session = Depends(get_db)):
    return get_user(db, id)

@users_routes.put("/{id}")
async def update_a_user(id : int, request : UserBase, db: Session = Depends(get_db)):
    return update_user(id, request, db)


@users_routes.delete("/{id}")
async def delete_a_user(id: int, db: Session = Depends(get_db)):
    return delete_user(db, id)

# @users_routes.get("/me/", response_model=UserDisplay)
# async def read_user_me(current_user: UserDisplay = Depends(get_current_user)):
#     return {"user" : current_user}

@users_routes.get("/person/", response_model=UserDisplay)
async def read_user_by_name(username: str, db: Session = Depends(get_db)):
    return get_user_by_username(username, db)


    

@users_routes.get('/download/{name}', response_class = FileResponse)
async def download_files(name: str):
    path = f'public/{name}'
   
    return path

@users_routes.put('/profile_picture/{id}')
async def send_files(id: int, file: UploadFile = File(...), db : Session = Depends(get_db)):
    file_location = f"public/{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object) 

        response = {"info": f"file '{file.filename}' saved at '{file_location}'"}

        return update_profile_photo(id, file_location, db)

@users_routes.get("/me/", response_model=UserDisplay)
async def read_users_me(current_user: UserDisplay = Depends(get_current_user)):
    return current_user